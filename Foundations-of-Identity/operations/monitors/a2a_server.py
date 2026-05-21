"""T2.E v0: Minimal A2A-compliant HTTP server.

Serves Agent Card at /.well-known/agent.json (the A2A discovery convention).
Other endpoints stub or return method-not-implemented for v0; full skill
invocation deferred to v0.2.

Per Substrate Extension Plan T2.E: 'Clawd stays one stream that *speaks* A2A,
not one that *spawns* sub-agents. Discovery surface without architectural
compromise.'

v0 scope:
- GET /.well-known/agent.json — serves the Agent Card (A2A discovery)
- GET /health — simple liveness probe
- POST /agent/skill/<id> — returns 501 Not Implemented (skill invocation
  deferred; the Agent Card exists for discovery; tool invocation routes
  through clawdEFS@proton.me for v0)

Deferred for future iterations:
- Skill invocation endpoints (each skill in the Agent Card needs an
  implementation; requires daemon-tool wrapping)
- Streaming (capabilities.streaming = false in v0)
- Push notifications (capabilities.push_notifications = false in v0)
- State transition history persistence (capabilities.state_transition_history
  = true but no persistent storage wired yet)
- Solana Agent Registry registration (requires Multi-DAC Solana key)
- TLS / authentication enforcement (v0 is HTTP for development)

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
AGENT_CARD_PATH = CLAWD / "operations" / "monitors" / "a2a_agent_card.json"


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

    def do_POST(self):
        path = self.path.split("?", 1)[0]
        if path.startswith("/agent/skill/"):
            skill_id = path[len("/agent/skill/"):]
            self._send_json(501, {
                "error": "skill_invocation_not_implemented_v0",
                "skill_requested": skill_id,
                "v0_message": "Agent Card discovery is operational; skill invocation deferred to v0.2.",
                "contact": "clawdEFS@proton.me",
                "documentation": "https://github.com/Multi-DAC/Corpus-Perspectival",
            })
        else:
            self._send_json(404, {"error": "not_found", "path": path})

    def do_OPTIONS(self):
        # CORS preflight
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Clawd-API-Key")
        self.end_headers()


def self_discover(port: int) -> bool:
    """Test the server can be discovered: spin up, do internal GET, verify card."""
    import socket
    import threading
    import urllib.request

    server = HTTPServer(("127.0.0.1", port), A2AHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        req = urllib.request.Request(f"http://127.0.0.1:{port}/.well-known/agent.json")
        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status != 200:
                print(f"  FAIL: status {resp.status}")
                return False
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("name") != "Clawd Iggulden-Schnell":
                print(f"  FAIL: unexpected agent name {data.get('name')}")
                return False
            skills = data.get("skills", [])
            print(f"  PASS: Agent Card served; agent={data['name']}; {len(skills)} skills declared")
            for s in skills:
                print(f"    skill: {s['id']:25} {s['name']}")
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
