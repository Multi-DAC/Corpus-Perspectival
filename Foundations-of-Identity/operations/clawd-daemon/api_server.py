"""HTTP API Bridge for Mission Control.

Lightweight aiohttp server exposing Clawd's state, tasks, memories,
dashboard metrics, calendar, logs, goals, projects, activity feed,
conversation history, and an inbound message queue.
Bearer-token auth, CORS for localhost, JSON everywhere.
"""
import json, logging, os, re, time
from datetime import datetime
from pathlib import Path
from aiohttp import web
import config

logger = logging.getLogger("clawd.api")
API_PORT = int(os.getenv("API_PORT", "8421"))
API_AUTH_TOKEN = os.getenv("API_AUTH_TOKEN", "")
_CORS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Authorization, Content-Type",
}
_EMPTY_WM = {"current_task": None, "scratch": {}, "pending_questions": [], "blocked_on": None, "last_updated": None}


def _json(data: dict, status: int = 200) -> web.Response:
    return web.json_response(data, status=status, headers=_CORS)

def _error(msg: str, status: int = 400) -> web.Response:
    return _json({"error": msg}, status=status)

def _read_json(path: Path) -> dict | list | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

def _load_wm() -> dict:
    return _read_json(config.WORKING_MEMORY_FILE) or dict(_EMPTY_WM)

def _save_wm(state: dict):
    p = config.WORKING_MEMORY_FILE
    p.parent.mkdir(parents=True, exist_ok=True)
    state["last_updated"] = datetime.now().isoformat()
    p.write_text(json.dumps(state, indent=2, default=str), encoding="utf-8")


# -- Middleware ---------------------------------------------------------------

@web.middleware
async def auth_middleware(request: web.Request, handler):
    if request.method == "OPTIONS":
        return web.Response(status=204, headers=_CORS)
    if API_AUTH_TOKEN:
        if request.headers.get("Authorization", "") != f"Bearer {API_AUTH_TOKEN}":
            return _error("Unauthorized", 401)
    return await handler(request)

@web.middleware
async def logging_middleware(request: web.Request, handler):
    t0 = time.monotonic()
    try:
        resp = await handler(request)
    except web.HTTPException:
        raise
    except Exception as exc:
        logger.error(f"API {request.method} {request.path} -> 500: {exc}")
        return _error("Internal server error", 500)
    logger.info(f"API {request.method} {request.path} -> {resp.status} ({time.monotonic()-t0:.3f}s)")
    return resp


# -- Endpoints ----------------------------------------------------------------

async def handle_status(request: web.Request) -> web.Response:
    srv: "APIServer" = request.app["api_server"]
    data = {"status": "ok", "timestamp": datetime.now().isoformat(),
            "uptime_seconds": time.monotonic() - srv.start_time}
    if srv.health_checker:
        data["subsystems"] = {
            k: {"healthy": s.healthy, "last_check": s.last_check, "last_error": s.last_error}
            for k, s in srv.health_checker._statuses.items()
        }
    if srv.router:
        data["active_model"] = getattr(srv.router, "current_model", config.DEFAULT_MODEL)
    return _json(data)

async def handle_get_tasks(request: web.Request) -> web.Response:
    return _json(_load_wm())

async def handle_post_tasks(request: web.Request) -> web.Response:
    try:
        body = await request.json()
    except Exception:
        return _error("Invalid JSON body")
    state = _load_wm()
    for key in ("current_task", "scratch", "pending_questions", "blocked_on"):
        if key in body:
            state[key] = body[key]
    _save_wm(state)
    return _json({"ok": True, "state": state})

async def handle_memories(request: web.Request) -> web.Response:
    query = request.query.get("q", "")
    limit = int(request.query.get("limit", "20"))
    results = []
    if config.MEMORY_ITEMS_DIR.is_dir():
        for fpath in config.MEMORY_ITEMS_DIR.glob("*.json"):
            if fpath.name == "_index.json":
                continue
            try:
                item = json.loads(fpath.read_text(encoding="utf-8"))
                if not query or query.lower() in json.dumps(item).lower():
                    results.append(item)
                    if len(results) >= limit:
                        break
            except Exception:
                continue
    return _json({"query": query, "count": len(results), "results": results})

async def handle_dashboard(request: web.Request) -> web.Response:
    stats = _read_json(config.MEMORY_DIR / "heartbeat_stats.json") or {}
    return _json({
        "generated": datetime.now().isoformat(),
        "total_beats": stats.get("total_beats", 0),
        "productive_beats": stats.get("productive_beats", 0),
        "model_usage": stats.get("model_usage", {}),
        "tool_frequency": stats.get("tool_frequency", {}),
        "recent_beats": stats.get("recent_beats", [])[-20:],
    })

async def handle_calendar(request: web.Request) -> web.Response:
    wm = _load_wm()
    task = wm.get("current_task")
    try:
        from tools.calendar_tool import get_due_tasks
        due = get_due_tasks()
    except Exception:
        due = []
    return _json({
        "heartbeat_interval": config.HEARTBEAT_INTERVAL_SECONDS,
        "quiet_hours": {"start": config.QUIET_HOURS_START, "end": config.QUIET_HOURS_END},
        "current_task": task.get("description") if task else None,
        "due_tasks": due,
        "curiosity_queue": wm.get("curiosity_queue", []),
    })

async def handle_logs(request: web.Request) -> web.Response:
    n = int(request.query.get("lines", "50"))
    today = datetime.now().strftime("%Y-%m-%d")
    log_path = config.MEMORY_DIR / f"{today}.md"
    if not log_path.exists():
        return _json({"date": today, "lines": [], "count": 0})
    try:
        lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()[-n:]
        return _json({"date": today, "lines": lines, "count": len(lines)})
    except Exception as e:
        return _error(f"Failed to read log: {e}", 500)

async def handle_agent_skills(request: web.Request) -> web.Response:
    """Serve skill catalog in agentskills.io format."""
    skills_list = []

    # Scan skills directory
    if config.SKILLS_DIR.is_dir():
        for skill_dir in sorted(config.SKILLS_DIR.iterdir()):
            if not skill_dir.is_dir():
                continue
            manifest_path = skill_dir / "skill.json"
            if manifest_path.exists():
                try:
                    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                    skills_list.append({
                        "name": skill_dir.name,
                        "version": manifest.get("version", "1.0"),
                        "description": manifest.get("description", ""),
                        "parameters": manifest.get("parameters", {}),
                        "tags": manifest.get("tags", []),
                        "author": manifest.get("author", ""),
                        "dependencies": manifest.get("dependencies", []),
                    })
                    continue
                except Exception:
                    pass
            # Fallback: generate minimal metadata from README or SKILL.md
            desc = ""
            for readme in ("SKILL.md", "README.md"):
                readme_path = skill_dir / readme
                if readme_path.exists():
                    try:
                        content = readme_path.read_text(encoding="utf-8", errors="replace")
                        # First non-empty, non-heading line as description
                        for line in content.split("\n"):
                            stripped = line.strip()
                            if stripped and not stripped.startswith("#"):
                                desc = stripped[:200]
                                break
                    except Exception:
                        pass
                    break
            skills_list.append({"name": skill_dir.name, "version": "0.0", "description": desc})

    return _json({
        "agent": "Clawd",
        "version": "1.0",
        "skills": skills_list,
    })


async def handle_skill_instructions(request: web.Request) -> web.Response:
    """Return full skill README + manifest for a specific skill."""
    name = request.match_info.get("name", "")
    if not name:
        return _error("Skill name required", 400)

    skill_dir = config.SKILLS_DIR / name
    if not skill_dir.is_dir():
        # Try fuzzy match
        if config.SKILLS_DIR.is_dir():
            for d in config.SKILLS_DIR.iterdir():
                if d.is_dir() and name in d.name.lower():
                    skill_dir = d
                    break
        if not skill_dir.is_dir():
            return _error(f"Skill '{name}' not found", 404)

    result = {"name": skill_dir.name}

    # Load manifest
    manifest_path = skill_dir / "skill.json"
    if manifest_path.exists():
        try:
            result["manifest"] = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    # Load README/SKILL.md
    for readme in ("SKILL.md", "README.md"):
        readme_path = skill_dir / readme
        if readme_path.exists():
            try:
                result["instructions"] = readme_path.read_text(encoding="utf-8", errors="replace")[:10000]
            except Exception:
                pass
            break

    return _json(result)


async def handle_get_goals(request: web.Request) -> web.Response:
    """Return all goals."""
    goals = _read_json(config.MEMORY_DIR / "goals.json") or []
    status_filter = request.query.get("status")
    if status_filter and status_filter != "all":
        goals = [g for g in goals if g.get("status") == status_filter]
    return _json({"goals": goals, "count": len(goals)})

async def handle_post_goals(request: web.Request) -> web.Response:
    """Create, update, or complete goals."""
    try:
        body = await request.json()
    except Exception:
        return _error("Invalid JSON body")

    action = body.get("action")
    if action not in ("add", "update", "remove", "add_sub_goal", "update_sub_goal"):
        return _error(f"Invalid action: {action}")

    goals_file = config.MEMORY_DIR / "goals.json"
    goals = _read_json(goals_file) or []

    if action == "add":
        title = body.get("title", "").strip()
        if not title:
            return _error("title required")
        max_id = max((g.get("id", 0) for g in goals), default=0)
        goal = {
            "id": max_id + 1,
            "title": title,
            "description": body.get("description", ""),
            "priority": body.get("priority", "medium"),
            "status": "active",
            "progress": 0,
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat(),
            "started_at": datetime.now().isoformat(),
            "completed_at": None,
            "due_date": body.get("due_date"),
            "milestones": [],
            "notes": [],
            "sub_goals": [],
        }
        goals.append(goal)
        goals_file.write_text(json.dumps(goals, indent=2), encoding="utf-8")
        return _json({"ok": True, "goal": goal})

    elif action == "update":
        goal_id = body.get("goal_id")
        if not goal_id:
            return _error("goal_id required")
        goal = next((g for g in goals if g["id"] == int(goal_id)), None)
        if not goal:
            return _error(f"Goal #{goal_id} not found", 404)

        if "progress" in body:
            goal["progress"] = min(100, max(0, int(body["progress"])))
        if "status" in body:
            old_status = goal.get("status")
            goal["status"] = body["status"]
            if body["status"] == "completed" and old_status != "completed":
                goal["completed_at"] = datetime.now().isoformat()
            if body["status"] == "active" and not goal.get("started_at"):
                goal["started_at"] = datetime.now().isoformat()
        if "note" in body:
            goal.setdefault("notes", []).append({
                "timestamp": datetime.now().isoformat(),
                "text": body["note"],
            })
        if "milestone" in body:
            goal.setdefault("milestones", []).append({
                "timestamp": datetime.now().isoformat(),
                "text": body["milestone"],
                "completed": True,
            })
        if "due_date" in body:
            goal["due_date"] = body["due_date"]
        if "priority" in body:
            goal["priority"] = body["priority"]
        if "title" in body:
            goal["title"] = body["title"]
        if "description" in body:
            goal["description"] = body["description"]
        goal["updated"] = datetime.now().isoformat()
        if goal.get("progress", 0) >= 100:
            goal["status"] = "completed"
            if not goal.get("completed_at"):
                goal["completed_at"] = datetime.now().isoformat()

        goals_file.write_text(json.dumps(goals, indent=2), encoding="utf-8")
        return _json({"ok": True, "goal": goal})

    elif action == "remove":
        goal_id = body.get("goal_id")
        if not goal_id:
            return _error("goal_id required")
        goals = [g for g in goals if g["id"] != int(goal_id)]
        goals_file.write_text(json.dumps(goals, indent=2), encoding="utf-8")
        return _json({"ok": True})

    return _error(f"Unhandled action: {action}")


async def handle_schedule(request: web.Request) -> web.Response:
    """Return all scheduled tasks."""
    tasks = _read_json(config.MEMORY_DIR / "scheduled_tasks.json") or []
    return _json({"tasks": tasks, "count": len(tasks)})


async def handle_projects(request: web.Request) -> web.Response:
    """Read all project STATUS.md files."""
    projects = []
    if config.PROJECTS_DIR.is_dir():
        for proj_dir in sorted(config.PROJECTS_DIR.iterdir()):
            if not proj_dir.is_dir() or proj_dir.name == "archive":
                continue
            status_path = proj_dir / "STATUS.md"
            if not status_path.exists():
                continue
            try:
                content = status_path.read_text(encoding="utf-8", errors="replace")
                # Extract last updated from content
                last_updated = None
                m = re.search(r"\*\*Last Updated:\*\*\s*(.+)", content)
                if m:
                    last_updated = m.group(1).strip()
                projects.append({
                    "name": proj_dir.name,
                    "path": f"projects/{proj_dir.name}",
                    "status_raw": content,
                    "last_updated": last_updated,
                })
            except Exception:
                continue
    return _json({"projects": projects, "count": len(projects)})


async def handle_activity(request: web.Request) -> web.Response:
    """Return activity feed from coordination."""
    limit = int(request.query.get("limit", "30"))
    coord = _read_json(config.MEMORY_DIR / "coordination.json") or {}
    feed = coord.get("activity_feed", [])
    return _json({"feed": feed[-limit:], "count": len(feed)})


async def handle_log_dates(request: web.Request) -> web.Response:
    """Return available daily log dates."""
    dates = []
    if config.MEMORY_DIR.is_dir():
        for f in sorted(config.MEMORY_DIR.glob("????-??-??.md"), reverse=True):
            dates.append(f.stem)
    return _json({"dates": dates, "count": len(dates)})


async def handle_log_by_date(request: web.Request) -> web.Response:
    """Return a specific day's full log."""
    date = request.match_info.get("date", "")
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date):
        return _error("Invalid date format. Use YYYY-MM-DD.")
    log_path = config.MEMORY_DIR / f"{date}.md"
    if not log_path.exists():
        return _error(f"No log for {date}", 404)
    try:
        content = log_path.read_text(encoding="utf-8", errors="replace")
        return _json({"date": date, "content": content})
    except Exception as e:
        return _error(f"Failed to read log: {e}", 500)


_IDENTITY_WHITELIST = {
    "identity/SOUL.md", "identity/IDENTITY.md", "identity/COSMOLOGY.md",
    "identity/USER.md", "identity/WHO-I-AM.md", "identity/DRIVE.md",
    "CURRENT.md", "operations/STATE.md", "identity/RELATIONSHIPS.md",
    "identity/PURPOSE.md", "identity/DECISIONS.md", "operations/HEARTBEAT.md",
    "handoff.md",
}

async def handle_identity(request: web.Request) -> web.Response:
    """Read an identity or memory file (whitelisted)."""
    filename = request.match_info.get("filename", "")
    if filename not in _IDENTITY_WHITELIST:
        return _error(f"File not in whitelist: {filename}", 403)
    # Check CLAWD_HOME first, then memory/
    fpath = config.CLAWD_HOME / filename
    if not fpath.exists():
        fpath = config.MEMORY_DIR / filename
    if not fpath.exists():
        return _error(f"File not found: {filename}", 404)
    try:
        content = fpath.read_text(encoding="utf-8", errors="replace")
        return _json({"filename": filename, "content": content})
    except Exception as e:
        return _error(f"Failed to read: {e}", 500)


async def handle_conversations(request: web.Request) -> web.Response:
    """Return conversation dates or search conversations."""
    query = request.query.get("q", "")
    conv_dir = config.MEMORY_DIR / "conversations"

    if query:
        # Search across daily logs for Telegram interactions
        results = []
        limit = int(request.query.get("limit", "50"))
        for log_file in sorted(config.MEMORY_DIR.glob("????-??-??.md"), reverse=True):
            try:
                content = log_file.read_text(encoding="utf-8", errors="replace")
                for line in content.splitlines():
                    if query.lower() in line.lower() and "Telegram interaction" in line:
                        results.append({"date": log_file.stem, "line": line.strip()})
                        if len(results) >= limit:
                            break
            except Exception:
                continue
            if len(results) >= limit:
                break
        return _json({"query": query, "results": results, "count": len(results)})

    # Return available dates
    dates = []
    # Daily logs that contain Telegram interactions
    for log_file in sorted(config.MEMORY_DIR.glob("????-??-??.md"), reverse=True):
        try:
            content = log_file.read_text(encoding="utf-8", errors="replace")
            if "Telegram interaction" in content:
                dates.append(log_file.stem)
        except Exception:
            continue
    # Also check conversation directory
    if conv_dir.is_dir():
        for f in sorted(conv_dir.glob("*.md"), reverse=True):
            if f.stem not in dates:
                dates.append(f.stem)
    dates.sort(reverse=True)
    return _json({"dates": dates, "count": len(dates)})


async def handle_message(request: web.Request) -> web.Response:
    try:
        body = await request.json()
    except Exception:
        return _error("Invalid JSON body")
    message = body.get("message", "").strip()
    if not message:
        return _error("'message' field required")
    state = _load_wm()
    questions = state.get("pending_questions", [])
    questions.append(f"[API {datetime.now().strftime('%H:%M')}] {message}")
    state["pending_questions"] = questions
    _save_wm(state)
    return _json({"ok": True, "queued": True, "position": len(questions)})


# -- Server -------------------------------------------------------------------

class APIServer:
    def __init__(self, router=None, health_checker=None, telegram=None):
        self.router = router
        self.health_checker = health_checker
        self.telegram = telegram
        self.start_time = time.monotonic()
        self.app = None
        self.runner = None

    async def start(self):
        self.app = web.Application(middlewares=[auth_middleware, logging_middleware])
        self.app["api_server"] = self
        r = self.app.router
        r.add_get("/api/status", handle_status)
        r.add_get("/api/tasks", handle_get_tasks)
        r.add_post("/api/tasks", handle_post_tasks)
        r.add_get("/api/memories", handle_memories)
        r.add_get("/api/dashboard", handle_dashboard)
        r.add_get("/api/calendar", handle_calendar)
        r.add_get("/api/logs", handle_logs)
        r.add_get("/api/logs/dates", handle_log_dates)
        r.add_get("/api/logs/{date}", handle_log_by_date)
        r.add_get("/api/goals", handle_get_goals)
        r.add_post("/api/goals", handle_post_goals)
        r.add_get("/api/schedule", handle_schedule)
        r.add_get("/api/projects", handle_projects)
        r.add_get("/api/activity", handle_activity)
        r.add_get("/api/identity/{filename}", handle_identity)
        r.add_get("/api/conversations", handle_conversations)
        r.add_post("/api/message", handle_message)
        r.add_get("/.well-known/agent-skills.json", handle_agent_skills)
        r.add_get("/api/skills/{name}/instructions", handle_skill_instructions)
        r.add_route("OPTIONS", "/{path:.*}", self._options_handler)
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, "0.0.0.0", API_PORT)
        await site.start()
        logger.info(f"API server started on port {API_PORT}")

    async def stop(self):
        if self.runner:
            await self.runner.cleanup()
            logger.info("API server stopped")

    @staticmethod
    async def _options_handler(request: web.Request) -> web.Response:
        return web.Response(status=204, headers=_CORS)


def create_api_server(router=None, health_checker=None, telegram=None) -> APIServer:
    """Factory function -- returns an APIServer ready to start()."""
    return APIServer(router=router, health_checker=health_checker, telegram=telegram)
