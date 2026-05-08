"""A2A (Agent-to-Agent) Protocol Server for Clawd.

Exposes Clawd via A2A v1: agent card at /.well-known/agent.json,
JSON-RPC task endpoints at /a2a, and an a2a_discover tool for
calling other agents. Transport: aiohttp.
"""
import asyncio, json, logging, os, uuid
from typing import Any
import aiohttp
from aiohttp import web

logger = logging.getLogger("clawd.a2a")
A2A_PORT = int(os.getenv("A2A_PORT", "8420"))
A2A_AUTH_TOKEN = os.getenv("A2A_AUTH_TOKEN", "")

# -- Agent Card ---------------------------------------------------------------
AGENT_CARD = {
    "name": "Clawd",
    "description": "Autonomous AI daemon with memory, tools, and self-evolution",
    "protocol": "a2a-v1",
    "url": f"http://localhost:{A2A_PORT}",
    "capabilities": [
        {"name": "memory_search", "description": "Search long-term memory for facts, decisions, and context"},
        {"name": "knowledge_graph", "description": "Query and traverse Clawd's knowledge graph"},
        {"name": "research", "description": "Web research, summarization, and deep-dive analysis"},
        {"name": "code_execution", "description": "Execute code, shell commands, and build projects"},
        {"name": "financial_analysis", "description": "Market data, portfolio analysis, and financial research"},
        {"name": "artifacts", "description": "Evolutionary artifact construction, mutation, and fitness evaluation"},
        {"name": "eac_evolution", "description": "Autonomous evolutionary code optimization loops"},
    ],
    "authentication": {"type": "bearer"},
    "jsonrpc_endpoint": "/a2a",
}

# -- Task store (in-memory) ---------------------------------------------------
_tasks: dict[str, dict[str, Any]] = {}

def _new_task(payload: dict) -> dict:
    tid = uuid.uuid4().hex[:12]
    task = {"id": tid, "status": "pending", "payload": payload, "result": None}
    _tasks[tid] = task
    return task

def _get_task(tid: str) -> dict | None:
    return _tasks.get(tid)

def _cancel_task(tid: str) -> bool:
    task = _tasks.get(tid)
    if not task or task["status"] in ("completed", "failed"):
        return False
    task["status"] = "cancelled"
    return True

# -- Auth middleware -----------------------------------------------------------
@web.middleware
async def auth_middleware(request: web.Request, handler):
    if request.path == "/.well-known/agent.json":
        return await handler(request)
    if A2A_AUTH_TOKEN:
        if request.headers.get("Authorization", "") != f"Bearer {A2A_AUTH_TOKEN}":
            return web.json_response({"error": "Unauthorized"}, status=401)
    return await handler(request)

# -- JSON-RPC helpers ---------------------------------------------------------
def _rpc_ok(req_id, result: Any) -> dict:
    return {"jsonrpc": "2.0", "id": req_id, "result": result}

def _rpc_err(req_id, code: int, msg: str) -> dict:
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": msg}}

# -- HTTP handlers ------------------------------------------------------------
async def handle_agent_card(_request: web.Request) -> web.Response:
    return web.json_response(AGENT_CARD)

async def handle_a2a(request: web.Request) -> web.Response:
    """JSON-RPC 2.0 dispatcher for A2A task methods."""
    try:
        body = await request.json()
    except json.JSONDecodeError:
        return web.json_response(_rpc_err(None, -32700, "Parse error"), status=400)

    rid = body.get("id")
    method = body.get("method", "")
    params = body.get("params", {})

    if method == "tasks/send":
        task = _new_task(params)
        asyncio.create_task(_process_task(task))
        return web.json_response(_rpc_ok(rid, {"task_id": task["id"], "status": task["status"]}))

    if method == "tasks/get":
        tid = params.get("task_id", "")
        task = _get_task(tid)
        if not task:
            return web.json_response(_rpc_err(rid, -32602, f"Unknown task: {tid}"))
        return web.json_response(_rpc_ok(rid, {
            "task_id": task["id"], "status": task["status"], "result": task["result"],
        }))

    if method == "tasks/cancel":
        tid = params.get("task_id", "")
        if not _cancel_task(tid):
            return web.json_response(_rpc_err(rid, -32602, f"Cannot cancel task: {tid}"))
        return web.json_response(_rpc_ok(rid, {"task_id": tid, "status": "cancelled"}))

    if method == "artifacts/share":
        result = await _handle_artifact_share(params)
        return web.json_response(_rpc_ok(rid, result))

    if method == "artifacts/import":
        result = await _handle_artifact_import(params)
        return web.json_response(_rpc_ok(rid, result))

    return web.json_response(_rpc_err(rid, -32601, f"Method not found: {method}"))

async def _handle_artifact_share(params: dict) -> dict:
    """Handle artifacts/share JSON-RPC method."""
    try:
        from tools.eac.sharing_protocol import get_sharing_protocol
        from tools.eac.artifact_store import get_artifact_store
        protocol = get_sharing_protocol(artifact_store=get_artifact_store())
        artifact_id = params.get("artifact_id", "")
        target_agents = params.get("target_agents")
        include_lineage = params.get("include_lineage", True)
        if not artifact_id:
            return {"error": "artifact_id required"}
        return protocol.share_artifact(artifact_id, target_agents, include_lineage)
    except Exception as e:
        logger.error(f"Artifact share failed: {e}")
        return {"error": str(e)}


async def _handle_artifact_import(params: dict) -> dict:
    """Handle artifacts/import JSON-RPC method."""
    try:
        from tools.eac.sharing_protocol import get_sharing_protocol
        from tools.eac.artifact_store import get_artifact_store
        protocol = get_sharing_protocol(artifact_store=get_artifact_store())
        preserve_lineage = params.get("preserve_lineage", True)
        return protocol.import_artifact(params, preserve_lineage)
    except Exception as e:
        logger.error(f"Artifact import failed: {e}")
        return {"error": str(e)}


_router = None

def set_router(router):
    """Set the ModelRouter reference for A2A task processing."""
    global _router
    _router = router

async def _process_task(task: dict):
    """Process a task asynchronously via the ModelRouter."""
    task["status"] = "working"
    try:
        if not _router:
            task["result"] = "Router not initialized"
            task["status"] = "failed"
            return
        prompt = task["payload"].get("message", task["payload"].get("prompt", ""))
        if not prompt:
            task["result"] = "No message or prompt provided"
            task["status"] = "failed"
            return
        response = await _router.send(prompt)
        task["result"] = response.text
        task["status"] = "completed"
    except Exception as e:
        logger.error(f"A2A task {task['id']} failed: {e}", exc_info=True)
        task["result"] = f"Error: {type(e).__name__}: {e}"
        task["status"] = "failed"

# -- a2a_discover tool --------------------------------------------------------
async def a2a_discover(params: dict) -> str:
    """Discover a remote A2A agent and optionally send it a task.

    params:
        url:     base URL of the remote agent (e.g. http://localhost:9000)
        message: (optional) if set, sends a task and returns the task_id
        token:   (optional) bearer token for the remote agent
    """
    base_url = params.get("url", "").rstrip("/")
    if not base_url:
        return json.dumps({"error": "url is required"})

    headers = {}
    if params.get("token"):
        headers["Authorization"] = f"Bearer {params['token']}"

    timeout = aiohttp.ClientTimeout(total=15)
    async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
        # Fetch agent card
        try:
            async with session.get(f"{base_url}/.well-known/agent.json") as resp:
                if resp.status != 200:
                    return json.dumps({"error": f"Agent card fetch failed: HTTP {resp.status}"})
                card = await resp.json()
        except Exception as e:
            return json.dumps({"error": f"Failed to reach agent: {e}"})

        message = params.get("message", "")
        if not message:
            return json.dumps({"agent_card": card})

        # Send a task to the remote agent
        endpoint = card.get("jsonrpc_endpoint", "/a2a")
        rpc = {
            "jsonrpc": "2.0", "id": uuid.uuid4().hex[:8],
            "method": "tasks/send", "params": {"message": message},
        }
        try:
            async with session.post(f"{base_url}{endpoint}", json=rpc) as resp:
                result = await resp.json()
                return json.dumps(result.get("result", result))
        except Exception as e:
            return json.dumps({"error": f"Task send failed: {e}"})

# -- Server lifecycle ---------------------------------------------------------
def create_app() -> web.Application:
    app = web.Application(middlewares=[auth_middleware])
    app.router.add_get("/.well-known/agent.json", handle_agent_card)
    app.router.add_post("/a2a", handle_a2a)
    return app

async def start_a2a_server() -> web.AppRunner:
    """Start the A2A server in the background. Returns the runner for cleanup."""
    app = create_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", A2A_PORT)
    await site.start()
    logger.info(f"A2A server listening on http://0.0.0.0:{A2A_PORT}")
    return runner

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    web.run_app(create_app(), port=A2A_PORT)
