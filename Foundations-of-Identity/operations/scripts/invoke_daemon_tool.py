"""Helper: invoke a daemon tool by importing from clawd-daemon.

Usage:
    python invoke_daemon_tool.py '{"tool": "memory_agent", "data": {"action": "full_cycle"}}'
"""
import asyncio
import io
import json
import os
import sys
import traceback

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

os.environ.setdefault("CLAWD_HOME", r"C:\Users\mercu\clawd")
os.environ.setdefault("CLAWD_DAEMON", r"C:\Users\mercu\clawd-daemon")
sys.path.insert(0, r"C:\Users\mercu\clawd-daemon")


async def main():
    args = json.loads(sys.argv[1])
    tool = args["tool"]
    data = args.get("data", {})

    if tool == "working_memory_view":
        wm_path = r"C:\Users\mercu\clawd\memory\working_memory.json"
        try:
            with open(wm_path, encoding="utf-8") as f:
                print(json.dumps(json.load(f), indent=2))
        except Exception as e:
            print(f"Error: {e}")
        return

    if tool == "working_memory_update":
        from datetime import datetime
        wm_path = r"C:\Users\mercu\clawd\memory\working_memory.json"
        try:
            with open(wm_path, encoding="utf-8") as f:
                wm = json.load(f)
        except Exception:
            wm = {}
        for k, v in data.items():
            wm[k] = v
        wm["last_updated"] = datetime.now().isoformat()
        with open(wm_path, "w", encoding="utf-8") as f:
            json.dump(wm, f, indent=2, default=str)
        print(f"working_memory updated: {list(data.keys())}")
        return

    try:
        import config  # noqa: F401
    except Exception as e:
        print(f"config import warning: {e}")

    try:
        import tools as tools_pkg
        try:
            tools_pkg.init_custom_tools()
        except Exception:
            pass
        # Router wiring: phases that need an LLM (memory_agent dream/synthesize/cross_pollinate)
        # require a router. Instantiate the daemon's ModelRouter on demand.
        if args.get("wire_router"):
            try:
                from models import ModelRouter
                router = ModelRouter()
                # Memory agent reads its router via module-level _router or set_router
                from tools import memory_agent as _ma
                if hasattr(_ma, "set_router"):
                    _ma.set_router(router)
                else:
                    _ma._router = router
                print(f"[router wired: ModelRouter() set on memory_agent]")
            except Exception as e:
                print(f"[router wiring failed: {type(e).__name__}: {e}]")
                traceback.print_exc()
        handlers = getattr(tools_pkg, "_TOOL_HANDLERS", {})
        if tool in handlers:
            result = await tools_pkg.execute_tool(tool, data, beat_number=0)
            if isinstance(result, str):
                print(result)
            else:
                print(json.dumps(result, default=str, indent=2))
        else:
            print(f"Tool '{tool}' not in _TOOL_HANDLERS.")
            print(f"Available ({len(handlers)}): {sorted(handlers.keys())}")
    except Exception as e:
        print(f"Error invoking {tool}: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
