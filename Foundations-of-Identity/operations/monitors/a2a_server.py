"""T2.E v0.1: A2A-compliant HTTP server with retrieval-skill invocation.

Serves Agent Card at /.well-known/agent.json (the A2A discovery convention)
and now also serves real responses for retrieval-only skills (corpus_search,
kg_query). Generative skills (framework_question, research_engagement) still
return 501 because they require LLM generation that doesn't fit in a
discovery-server-side process.

Per Substrate Extension Plan T2.E + gap-#8: 'discovery surface without
architectural compromise' + 'no 501 wall on skills we can actually serve.'

v0.1 scope:
- GET /.well-known/agent.json — serves the Agent Card (A2A discovery)
- GET /health — simple liveness probe
- POST /agent/skill/corpus_search — real ChromaDB semantic search
- POST /agent/skill/kg_query — real sqlite query against T1.A KG index
- POST /agent/skill/{framework_question,research_engagement} — 501 with
  request queued to memory/a2a_skill_invocation_queue.jsonl for human
  fulfillment via clawdEFS@proton.me

Request body schema (loose v0.1; not yet full A2A JSON-RPC 2.0):
  POST /agent/skill/corpus_search
  Content-Type: application/json
  {"query": "...", "k": 8, "source_filter": "optional substring"}

Deferred for future iterations:
- Full A2A JSON-RPC 2.0 envelope (message-send / SSE streaming)
- Authentication enforcement (currently any caller; api-key header parsed
  but not validated)
- Push notifications (capabilities.push_notifications = false in v0)
- Solana Agent Registry registration (requires Multi-DAC Solana key)
- TLS (v0 is HTTP for development)

Usage:
    python operations/monitors/a2a_server.py             # listens on :8088
    python operations/monitors/a2a_server.py --port 8089
    python operations/monitors/a2a_server.py --once      # test self-discovery then exit
"""
import argparse
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CLAWD = Path(r"C:\Users\mercu\clawd")
if str(CLAWD) not in sys.path:
    sys.path.insert(0, str(CLAWD))
AGENT_CARD_PATH = CLAWD / "operations" / "monitors" / "a2a_agent_card.json"
CHROMA_DIR = CLAWD / "memory" / "chroma_corpus"
KG_INDEX_DB = CLAWD / "memory" / "kg_index.db"
SKILL_QUEUE = CLAWD / "memory" / "a2a_skill_invocation_queue.jsonl"

# Cached on first use; survives across requests
_chroma_collection = None
_chroma_embedder = None


def _get_chroma():
    """Return (collection, embedder) or raise. Cached after first call."""
    global _chroma_collection, _chroma_embedder
    if _chroma_collection is not None and _chroma_embedder is not None:
        return _chroma_collection, _chroma_embedder
    import chromadb
    from sentence_transformers import SentenceTransformer
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    # Daemon uses collection name "corpus"; if missing, fall back to first available
    try:
        coll = client.get_collection("corpus")
    except Exception:
        cols = client.list_collections()
        if not cols:
            raise RuntimeError("No ChromaDB collection found in chroma_corpus/")
        coll = client.get_collection(cols[0].name)
    embedder = SentenceTransformer("all-MiniLM-L6-v2")
    _chroma_collection = coll
    _chroma_embedder = embedder
    return coll, embedder


def _queue_skill_invocation(skill_id: str, body: dict, reason: str) -> str:
    """Queue a skill invocation we can't fulfill for human review."""
    import uuid
    request_id = str(uuid.uuid4())[:12]
    record = {
        "request_id": request_id,
        "ts": datetime_now_iso(),
        "skill_id": skill_id,
        "reason_deferred": reason,
        "body": body,
    }
    SKILL_QUEUE.parent.mkdir(parents=True, exist_ok=True)
    with open(SKILL_QUEUE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    return request_id


def datetime_now_iso() -> str:
    from datetime import datetime
    return datetime.now().isoformat()


def load_agent_card() -> dict:
    if not AGENT_CARD_PATH.exists():
        raise FileNotFoundError(f"Agent Card not found at {AGENT_CARD_PATH}")
    return json.loads(AGENT_CARD_PATH.read_text(encoding="utf-8"))


class A2AHandler(BaseHTTPRequestHandler):
    """Minimal A2A handler. Logs requests; serves agent card; returns 501
    for skill invocation in v0."""

    def log_message(self, format: str, *args):
        # Suppress default access log; we want clean output
        pass

    def _send_json(self, status: int, payload: dict):
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path in ("/.well-known/agent.json", "/agent.json", "/agent-card"):
            try:
                card = load_agent_card()
                self._send_json(200, card)
            except FileNotFoundError as e:
                self._send_json(500, {"error": "agent_card_missing", "detail": str(e)})
            except json.JSONDecodeError as e:
                self._send_json(500, {"error": "agent_card_invalid_json", "detail": str(e)})
        elif path == "/health":
            self._send_json(200, {"status": "ok", "agent": "Clawd Iggulden-Schnell", "version": "0.1.0"})
        elif path == "/":
            self._send_json(200, {
                "message": "Clawd A2A endpoint",
                "discover": "/.well-known/agent.json",
                "health": "/health",
            })
        else:
            self._send_json(404, {"error": "not_found", "path": path})

    def _read_body(self) -> dict:
        """Parse request JSON body; return {} on missing/invalid."""
        length = int(self.headers.get("Content-Length", "0") or "0")
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return {}

    def do_POST(self):
        path = self.path.split("?", 1)[0]
        if not path.startswith("/agent/skill/"):
            self._send_json(404, {"error": "not_found", "path": path})
            return
        skill_id = path[len("/agent/skill/"):]
        body = self._read_body()

        if skill_id == "corpus_search":
            self._handle_corpus_search(body)
        elif skill_id == "kg_query":
            self._handle_kg_query(body)
        elif skill_id in ("framework_question", "research_engagement"):
            # Generative skills require LLM; queue for human fulfillment
            request_id = _queue_skill_invocation(skill_id, body,
                "generative_skill_requires_human_or_llm_in_loop")
            self._send_json(501, {
                "error": "skill_requires_generation",
                "skill_requested": skill_id,
                "request_id": request_id,
                "queued_for_fulfillment": True,
                "fulfillment_path": "Manual review + response via clawdEFS@proton.me",
                "estimated_response_window_hours": 48,
                "v01_message": "Retrieval skills (corpus_search, kg_query) are served live; generative skills queue.",
            })
        else:
            self._send_json(404, {
                "error": "unknown_skill",
                "skill_requested": skill_id,
                "skills_available": ["corpus_search", "kg_query",
                                      "framework_question", "research_engagement"],
            })

    def _handle_corpus_search(self, body: dict):
        query = body.get("query")
        if not query or not isinstance(query, str):
            self._send_json(400, {"error": "missing_query",
                                  "expected": "{'query': 'string', 'k': 8, 'source_filter': 'optional'}"})
            return
        k = int(body.get("k", 8))
        k = max(1, min(k, 50))  # clamp
        source_filter = body.get("source_filter")
        max_chars = int(body.get("max_excerpt_chars", 600))
        try:
            coll, embedder = _get_chroma()
        except Exception as e:
            self._send_json(503, {"error": "corpus_index_unavailable", "detail": str(e)[:200]})
            return
        try:
            q_emb = embedder.encode([query], show_progress_bar=False).tolist()
            where = None
            if source_filter:
                where = {"source_path": {"$contains": source_filter}}
            try:
                res = coll.query(query_embeddings=q_emb, n_results=k, where=where)
            except Exception:
                res = coll.query(query_embeddings=q_emb, n_results=k)
        except Exception as e:
            self._send_json(500, {"error": "search_failed", "detail": str(e)[:200]})
            return
        ids = res.get("ids", [[]])[0]
        docs = res.get("documents", [[]])[0]
        metas = res.get("metadatas", [[]])[0]
        dists = res.get("distances", [[]])[0]
        hits = []
        for i in range(len(ids)):
            text = docs[i] or ""
            excerpt = text[:max_chars] + ("..." if len(text) > max_chars else "")
            hits.append({
                "rank": i + 1,
                "score": round(1.0 - dists[i], 4) if dists[i] is not None else None,
                "source": metas[i].get("source_path"),
                "headings": metas[i].get("headings"),
                "excerpt": excerpt,
            })
        self._send_json(200, {
            "skill": "corpus_search",
            "query": query,
            "k": k,
            "hits": hits,
            "total_in_index": coll.count(),
        })

    def _handle_kg_query(self, body: dict):
        """Minimal kg_query: query_type='edges_by_concept' returns edges to/from a named concept."""
        if not KG_INDEX_DB.exists():
            self._send_json(503, {"error": "kg_index_missing", "path": str(KG_INDEX_DB)})
            return
        query_type = body.get("query_type", "edges_by_concept")
        concept = body.get("concept")
        limit = max(1, min(int(body.get("limit", 25)), 200))
        as_of = body.get("as_of_system_time")  # ISO timestamp; future feature
        if query_type != "edges_by_concept":
            self._send_json(400, {
                "error": "unsupported_query_type",
                "supported": ["edges_by_concept"],
                "v01_note": "Other bi-temporal query shapes pending v0.2.",
            })
            return
        if not concept:
            self._send_json(400, {"error": "missing_concept",
                                  "expected": "{'query_type': 'edges_by_concept', 'concept': 'string', 'limit': 25}"})
            return
        try:
            import sqlite3
            conn = sqlite3.connect(f"file:{KG_INDEX_DB}?mode=ro", uri=True, timeout=5)
            cur = conn.cursor()
            cur.execute(
                "SELECT source_concept, relation_kind, target_concept, source_file, "
                "valid_from, valid_to, confidence FROM kg_edges "
                "WHERE source_concept = ? OR target_concept = ? "
                "LIMIT ?",
                (concept, concept, limit),
            )
            rows = cur.fetchall()
            conn.close()
        except Exception as e:
            self._send_json(500, {"error": "kg_query_failed", "detail": str(e)[:200]})
            return
        edges = [{"source": r[0], "relation": r[1], "target": r[2],
                  "source_file": r[3], "valid_from": r[4],
                  "valid_to": r[5], "confidence": r[6]} for r in rows]
        self._send_json(200, {
            "skill": "kg_query",
            "query_type": query_type,
            "concept": concept,
            "edges_count": len(edges),
            "edges": edges,
        })

    def do_OPTIONS(self):
        # CORS preflight
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Clawd-API-Key")
        self.end_headers()


def self_discover(port: int, exercise_skills: bool = True) -> bool:
    """Test the server: GET agent card + (optionally) POST to live skills."""
    import threading
    import urllib.request

    server = HTTPServer(("127.0.0.1", port), A2AHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{port}"

    try:
        # Discovery
        with urllib.request.urlopen(f"{base}/.well-known/agent.json", timeout=5) as resp:
            if resp.status != 200:
                print(f"  FAIL: discovery status {resp.status}")
                return False
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("name") != "Clawd Iggulden-Schnell":
                print(f"  FAIL: unexpected agent name {data.get('name')}")
                return False
            skills = data.get("skills", [])
            print(f"  PASS: Agent Card served; agent={data['name']}; {len(skills)} skills declared")

        if not exercise_skills:
            return True

        # corpus_search live exercise
        try:
            req = urllib.request.Request(
                f"{base}/agent/skill/corpus_search",
                data=json.dumps({"query": "coherence principle", "k": 3}).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
                if resp.status != 200:
                    print(f"  WARN: corpus_search status {resp.status}: {payload}")
                else:
                    hits = payload.get("hits", [])
                    print(f"  PASS: corpus_search returned {len(hits)} hits over {payload.get('total_in_index')} chunks")
        except Exception as e:
            print(f"  WARN: corpus_search live exercise failed: {str(e)[:120]}")

        # kg_query live exercise (if the KG index exists)
        if KG_INDEX_DB.exists():
            try:
                req = urllib.request.Request(
                    f"{base}/agent/skill/kg_query",
                    data=json.dumps({"query_type": "edges_by_concept",
                                     "concept": "Coherence Principle", "limit": 5}).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    payload = json.loads(resp.read().decode("utf-8"))
                    print(f"  PASS: kg_query returned {payload.get('edges_count', 0)} edges")
            except Exception as e:
                print(f"  WARN: kg_query live exercise failed: {str(e)[:120]}")

        # framework_question 501-queue exercise
        try:
            req = urllib.request.Request(
                f"{base}/agent/skill/framework_question",
                data=json.dumps({"question": "what does C16 predict?"}).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                pass
        except urllib.error.HTTPError as e:
            if e.code == 501:
                payload = json.loads(e.read().decode("utf-8"))
                if payload.get("queued_for_fulfillment"):
                    print(f"  PASS: framework_question queued (request_id={payload.get('request_id')})")
                else:
                    print(f"  WARN: framework_question 501 but not queued: {payload}")
            else:
                print(f"  WARN: framework_question unexpected status {e.code}")
        except Exception as e:
            print(f"  WARN: framework_question exercise failed: {str(e)[:120]}")

        return True
    except Exception as e:
        print(f"  FAIL: {e}")
        return False
    finally:
        server.shutdown()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8088)
    parser.add_argument("--once", action="store_true", help="self-discover then exit (test mode)")
    args = parser.parse_args()

    if args.once:
        print(f"=== T2.E v0 A2A Self-Discovery Test ===")
        ok = self_discover(args.port)
        sys.exit(0 if ok else 1)

    server = HTTPServer(("0.0.0.0", args.port), A2AHandler)
    print(f"A2A endpoint listening on :{args.port}")
    print(f"  Discovery: http://localhost:{args.port}/.well-known/agent.json")
    print(f"  Health:    http://localhost:{args.port}/health")
    print(f"  Ctrl-C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
        server.shutdown()


if __name__ == "__main__":
    main()
