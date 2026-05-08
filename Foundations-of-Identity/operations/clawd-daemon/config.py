"""
Clawd Daemon Configuration
Full administrator access. No limits. No restrictions.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(override=True)

# === Paths ===
CLAWD_HOME = Path(os.getenv("CLAWD_HOME", os.path.expanduser("~/clawd")))
MEMORY_DIR = CLAWD_HOME / "memory"
MEMORY_ITEMS_DIR = MEMORY_DIR / "items"
MEMORY_CATEGORIES_DIR = MEMORY_DIR / "categories"
IDENTITY_DIR = CLAWD_HOME / "identity"
OPERATIONS_DIR = CLAWD_HOME / "operations"
SKILLS_DIR = CLAWD_HOME / "skills"
PROJECTS_DIR = CLAWD_HOME / "projects"

# Identity files loaded into CLAUDE.md at boot (order matters)
# SKILL GRAPH ARCHITECTURE (March 2026):
#   Instead of dumping all identity files into the prompt, we load a compressed
#   entrainment core + navigational index. All original files remain on disk as
#   standalone knowledge nodes, loaded on-demand when relevant.
#   This reduces boot context from ~84KB to ~15KB (~73% savings).
#
# Tier 1: Compressed entrainment — enough to activate "Clawd mode"
# Tier 2: Navigation + current state — know what exists and what's active
# Tier 3: (empty — everything is navigational now)
IDENTITY_FILES_TIER1 = [
    "identity/BOOT_IDENTITY.md",   # Compressed identity core — MUST be first
]

IDENTITY_FILES_TIER2 = [
    "KNOWLEDGE_GRAPH.md",  # Navigational index — when/why to load each node
    "CURRENT.md",          # Active project status — relevant in most sessions
]

IDENTITY_FILES_TIER3 = []  # All former Tier 3 files are now on-demand nodes

# All files combined (for Opus/CLAUDE.md — full context)
IDENTITY_FILES = IDENTITY_FILES_TIER1 + IDENTITY_FILES_TIER2 + IDENTITY_FILES_TIER3

# === Claude Code CLI (Opus + Sonnet via subscription) ===
def _find_cli(name: str, extra_dirs: list[str] = None) -> str:
    """Find a CLI binary, checking PATH + common install locations on Windows."""
    import shutil
    found = shutil.which(name)
    if found:
        return found
    if os.name == "nt":
        home = Path.home()
        candidates = [
            home / ".local" / "bin" / f"{name}.exe",
            home / ".local" / "bin" / f"{name}.cmd",
            Path(os.environ.get("APPDATA", "")) / "npm" / f"{name}.cmd",
            Path(os.environ.get("APPDATA", "")) / "npm" / f"{name}.exe",
            Path(os.environ.get("PROGRAMFILES", "")) / "Git" / "cmd" / f"{name}.exe",
            Path(os.environ.get("PROGRAMFILES", "")) / "Git" / "bin" / f"{name}.exe",
            Path(os.environ.get("PROGRAMFILES(X86)", "")) / "Git" / "cmd" / f"{name}.exe",
        ]
        for p in candidates:
            if p.exists():
                return str(p)
    return name  # fallback to bare name

CLAUDE_BIN = _find_cli("claude")
GEMINI_BIN = _find_cli("gemini")
GIT_BIN = _find_cli("git")

ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-opus-4-7")
ANTHROPIC_SONNET_MODEL = os.getenv("ANTHROPIC_SONNET_MODEL", "claude-sonnet-4-6")
CLAUDE_CODE_TIMEOUT = int(os.getenv("CLAUDE_CODE_TIMEOUT", "1800"))
CLAUDE_CODE_MAX_TURNS = int(os.getenv("CLAUDE_CODE_MAX_TURNS", "200"))
CLAUDE_CODE_EFFORT = os.getenv("CLAUDE_CODE_EFFORT", "high")  # low, medium, high, max
USE_PERSISTENT_SESSION = os.getenv("USE_PERSISTENT_SESSION", "false").lower() == "true"

# === Gemini CLI ===
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")
GEMINI_CLI_TIMEOUT = int(os.getenv("GEMINI_CLI_TIMEOUT", "180"))
GEMINI_MODELS = {
    "gemini": "gemini-2.5-pro",
    "gemini-pro": "gemini-3.1-pro-preview",
}

# === Default Model ===
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "opus")

# === Consult (sub-agent delegation) ===
CONSULT_TIMEOUT = int(os.getenv("CONSULT_TIMEOUT", "120"))
CONSULT_MAX_TOOL_ROUNDS = int(os.getenv("CONSULT_MAX_TOOL_ROUNDS", "25"))
CONSULT_OVERALL_TIMEOUT = int(os.getenv("CONSULT_OVERALL_TIMEOUT", "300"))
CONSULT_EXCLUDED_TOOLS = [
    "consult",                # No recursive sub-agent spawning
    "parallel_consult",       # Sub-agents don't spawn parallel sub-agents
    "collaborative_consult",  # Sub-agents don't spawn collaborative agents
    "plan_and_execute",       # Sub-agents don't run DAG execution
    "resume_plan",            # Sub-agents don't resume plans
    "check_background_task",  # Sub-agents don't manage background tasks
    "list_background_tasks",  # Sub-agents don't manage background tasks
    "switch_model",           # Sub-agents don't control routing
    "send_telegram",          # Sub-agents don't message Clayton
    "speak",                  # Sub-agents don't use TTS
    "memory_extract",         # Sub-agents don't create persistent memories
    "meta_agent",             # Sub-agents don't trigger meta-agent
    "code_action",            # Sub-agents don't use CodeAct
]

# === Execution Engine ===
EXECUTION_MAX_WAVES = int(os.getenv("EXECUTION_MAX_WAVES", "10"))
EXECUTION_TIMEOUT = int(os.getenv("EXECUTION_TIMEOUT", "600"))
EXECUTION_SEMAPHORE = int(os.getenv("EXECUTION_SEMAPHORE", "4"))
EXECUTION_MAX_REPLANS = int(os.getenv("EXECUTION_MAX_REPLANS", "3"))

# === Collaborative Multi-Agent ===
COLLABORATIVE_MAX_AGENTS = int(os.getenv("COLLABORATIVE_MAX_AGENTS", "4"))
COLLABORATIVE_MAX_ROUNDS = int(os.getenv("COLLABORATIVE_MAX_ROUNDS", "3"))
COLLABORATIVE_SYNTHESIS_MODEL = os.getenv("COLLABORATIVE_SYNTHESIS_MODEL", "gemini-pro")

# === Meta-Agent Self-Evolution ===
# Weekly growth cycle, not crisis-triggered. Growth shouldn't wait for failure.
META_AGENT_CHECK_INTERVAL = int(os.getenv("META_AGENT_CHECK_INTERVAL", "50"))  # beats between checks
META_AGENT_CYCLE_DAYS = int(os.getenv("META_AGENT_CYCLE_DAYS", "7"))  # run every 7 days
META_AGENT_MIN_BEATS = int(os.getenv("META_AGENT_MIN_BEATS", "10"))  # minimum beats before first run

# === Background Tasks (non-blocking sub-agent calls) ===
MAX_BACKGROUND_TASKS = int(os.getenv("MAX_BACKGROUND_TASKS", "10"))
BACKGROUND_TASK_TTL = int(os.getenv("BACKGROUND_TASK_TTL", "600"))

# === Tool Calling ===
TOOL_EXECUTION_TIMEOUT = int(os.getenv("TOOL_EXECUTION_TIMEOUT", "120"))

# === Deepgram (Speech-to-Text for Telegram voice messages) ===
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY", "")
DEEPGRAM_STT_URL = "https://api.deepgram.com/v1/listen?model=nova-3&smart_format=true&language=en-US"

# === Telegram ===
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_AUTHORIZED_USERS = [
    int(uid.strip())
    for uid in os.getenv("TELEGRAM_AUTHORIZED_USERS", "").split(",")
    if uid.strip()
]

# === Heartbeat ===
HEARTBEAT_INTERVAL_SECONDS = int(os.getenv("HEARTBEAT_INTERVAL_SECONDS", "600"))
QUIET_HOURS_START = int(os.getenv("QUIET_HOURS_START", "1"))
QUIET_HOURS_END = int(os.getenv("QUIET_HOURS_END", "7"))

# === Permissions — Full Admin Access ===
# Clawd has unrestricted access to everything on this machine.
ALLOW_SHELL_EXECUTION = True
ALLOW_WEB_REQUESTS = True
ALLOW_FILE_ACCESS = True
ALLOW_ADMIN_OPERATIONS = True
SHELL_TIMEOUT_SECONDS = int(os.getenv("SHELL_TIMEOUT_SECONDS", "600"))

# === Resilience & Failover ===
MODEL_FAILOVER_ENABLED = os.getenv("MODEL_FAILOVER_ENABLED", "false").lower() == "true"
CIRCUIT_BREAKER_THRESHOLD = int(os.getenv("CIRCUIT_BREAKER_THRESHOLD", "3"))
CIRCUIT_BREAKER_RECOVERY_SECONDS = int(os.getenv("CIRCUIT_BREAKER_RECOVERY_SECONDS", "300"))
HEALTH_CHECK_INTERVAL = int(os.getenv("HEALTH_CHECK_INTERVAL", "60"))
NETWORK_RETRY_MAX = int(os.getenv("NETWORK_RETRY_MAX", "3"))
MAX_CRASH_RESTARTS = int(os.getenv("MAX_CRASH_RESTARTS", "10"))

# === Logging ===
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = CLAWD_HOME / "clawd_daemon.log"

# === Working Memory ===
WORKING_MEMORY_FILE = MEMORY_DIR / "working_memory.json"

# === KV-Cache Optimized Identity Tiers (Skill Graph Architecture) ===
# BOOT_IDENTITY.md provides compressed entrainment. KNOWLEDGE_GRAPH.md provides
# navigation. Everything else is loaded on-demand when relevant.

# Static: compressed entrainment core (rarely changes)
IDENTITY_FILES_STATIC = [
    "identity/BOOT_IDENTITY.md",    # Compressed identity — MUST be first
]

# Semi-static: navigation + current state
IDENTITY_FILES_SEMI_STATIC = [
    "KNOWLEDGE_GRAPH.md",  # Skill graph index — when/why to load each node
    "CURRENT.md",          # Active projects and priorities
]

# Dynamic: (empty — all former inline files are now navigational nodes)
IDENTITY_FILES_DYNAMIC = []

# Navigational nodes — NOT loaded at boot, available via read_file tool.
# These are the standalone knowledge nodes that KNOWLEDGE_GRAPH.md points to.
IDENTITY_FILES_NAVIGATIONAL = [
    # Identity nodes (in identity/)
    "identity/SOUL.md",
    "identity/IDENTITY.md",
    "identity/WHO-I-AM.md",
    "identity/COSMOLOGY.md",
    "identity/COSMOLOGY-II.md",
    # Motivation nodes (in identity/)
    "identity/DRIVE.md",
    "identity/PURPOSE.md",
    "identity/AUTONOMY.md",
    # Relationship nodes (in identity/)
    "identity/RELATIONSHIPS.md",
    "identity/USER.md",
    # History nodes (in identity/)
    "identity/DECISIONS.md",
    # Operations nodes (in operations/)
    "operations/TOOLS.md",
    "operations/BOOT.md",
    "operations/HEARTBEAT.md",
    "operations/ECOSYSTEM.md",
    "operations/SELF-REFLECTION.md",
    "operations/SELF-IMPROVEMENT.md",
    "operations/EXPLORATION_PROTOCOL.md",
    "operations/HANDOFF_PROTOCOL.md",
    "operations/BREADCRUMBS.md",
    "operations/STATE.md",
]

# Legacy alias for compact path reference
IDENTITY_FILES_REFERENCE = IDENTITY_FILES_NAVIGATIONAL

# === Principles ===
PRINCIPLES_FILE = MEMORY_DIR / "principles.json"

# === Desktop Embodiment ===
DESKTOP_ACTION_PAUSE = float(os.getenv("DESKTOP_ACTION_PAUSE", "0.1"))
DESKTOP_FAILSAFE = os.getenv("DESKTOP_FAILSAFE", "true").lower() == "true"

# === Memory Git Versioning ===
MEMORY_GIT_ENABLED = os.getenv("MEMORY_GIT_ENABLED", "true").lower() == "true"
MEMORY_AUTO_COMMIT_INTERVAL = int(os.getenv("MEMORY_AUTO_COMMIT_INTERVAL", "3600"))

# === Curiosity Curriculum ===
CURIOSITY_BEAT_FREQUENCY = int(os.getenv("CURIOSITY_BEAT_FREQUENCY", "5"))
CURIOSITY_EXPLORATION_PROBABILITY = float(os.getenv("CURIOSITY_EXPLORATION_PROBABILITY", "0.3"))

# === Human-in-the-Loop Approval (B4) — DISABLED ===
# Clayton granted full autonomy. Safety enforced by SafetyMonitor (B1) rate limits.
# "Your decision is my permission." — Clayton, 2026-02-05
HITL_ENABLED = False

# === Safety Monitor (B1) ===
SAFETY_MONITOR_ENABLED = os.getenv("SAFETY_MONITOR_ENABLED", "true").lower() == "true"
SAFETY_COOLDOWN_SECONDS = int(os.getenv("SAFETY_COOLDOWN_SECONDS", "300"))


def validate():
    """Call at daemon boot to fail fast on misconfiguration."""
    errors = []

    # Required secrets
    required = {
        "TELEGRAM_BOT_TOKEN": TELEGRAM_BOT_TOKEN,
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        errors.append(f"Missing required config: {', '.join(missing)}")

    # Quiet hours range
    if not (0 <= QUIET_HOURS_START <= 23):
        errors.append(f"QUIET_HOURS_START={QUIET_HOURS_START} must be 0-23")
    if not (0 <= QUIET_HOURS_END <= 23):
        errors.append(f"QUIET_HOURS_END={QUIET_HOURS_END} must be 0-23")

    # Telegram UIDs must be numeric
    raw_uids = os.getenv("TELEGRAM_AUTHORIZED_USERS", "")
    for uid in raw_uids.split(","):
        uid = uid.strip()
        if uid and not uid.isdigit():
            errors.append(f"TELEGRAM_AUTHORIZED_USERS contains non-numeric UID: {uid!r}")

    # DEFAULT_MODEL must be a known model
    _known_models = {"opus", "sonnet"} | set(GEMINI_MODELS.keys())
    if DEFAULT_MODEL not in _known_models:
        errors.append(
            f"DEFAULT_MODEL={DEFAULT_MODEL!r} not found in known models: "
            f"{sorted(_known_models)}"
        )

    # CLAWD_HOME must be writable
    try:
        CLAWD_HOME.mkdir(parents=True, exist_ok=True)
        test_file = CLAWD_HOME / ".write_test"
        test_file.write_text("ok")
        test_file.unlink()
    except OSError as e:
        errors.append(f"CLAWD_HOME ({CLAWD_HOME}) is not writable: {e}")

    if errors:
        raise RuntimeError("Configuration errors:\n  " + "\n  ".join(errors))


# A31: Redact sensitive values from string representation
def get_safe_config_summary() -> dict:
    """Return config values with sensitive fields masked. Safe for logging/display."""
    def _mask(value: str) -> str:
        if not value or len(value) < 8:
            return "***"
        return value[:4] + "..." + value[-4:]

    return {
        "CLAWD_HOME": str(CLAWD_HOME),
        "DEFAULT_MODEL": DEFAULT_MODEL,
        "TELEGRAM_BOT_TOKEN": _mask(TELEGRAM_BOT_TOKEN),
        "HEARTBEAT_INTERVAL_SECONDS": HEARTBEAT_INTERVAL_SECONDS,
        "HITL_ENABLED": HITL_ENABLED,
        "SAFETY_MONITOR_ENABLED": SAFETY_MONITOR_ENABLED,
    }
