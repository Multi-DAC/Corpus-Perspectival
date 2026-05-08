"""Cost Tracker — Cost-aware model routing with budget management.

Tracks per-model, per-task-type costs in SQLite and provides:
  - Task complexity classification (simple/medium/complex)
  - Cost weight signal for integration with routing.py
  - Daily budget tracking with 80%/100% warnings
  - Cost summary metrics for the evaluation dashboard

Uses the existing SQLite store (tools/sqlite_store.py) for persistence.

Exported functions:
  - track_cost(model, task_type, complexity, cost_usd, tokens_used)
  - get_daily_cost(date?) -> float
  - classify_complexity(message) -> "simple" | "medium" | "complex"
  - get_cost_weight(message, current_model?) -> dict with model cost scores
  - get_cost_summary(days?) -> dict with dashboard-ready metrics
"""
import logging
import os
from datetime import datetime, date
from typing import Optional

logger = logging.getLogger("clawd.cost_tracker")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Daily budget in USD, configurable via env var (default $5.00)
COST_BUDGET_DAILY = float(os.getenv("COST_BUDGET_DAILY", "5.00"))

# Approximate cost per 1K tokens (input + output blended estimate) by model.
# These are rough estimates used for cost weighting; actual costs are tracked
# via track_cost() with real values from API responses.
MODEL_COST_PER_1K = {
    "opus":       0.075,   # Most expensive — Claude Opus
    "sonnet":     0.015,   # Claude Sonnet
    "gemini":     0.005,   # Gemini 2.5 Pro
    "gemini-pro": 0.007,   # Gemini 3.1 Pro Preview
}

# Fallback cost for unknown models
DEFAULT_COST_PER_1K = 0.005

# Budget warning thresholds
_WARN_80_LOGGED = False
_WARN_100_LOGGED = False
_LAST_WARN_DATE: Optional[date] = None

# ---------------------------------------------------------------------------
# Complexity classification
# ---------------------------------------------------------------------------

# Keywords and patterns that signal higher complexity
_COMPLEX_KEYWORDS = [
    "architect", "design system", "refactor entire", "migration plan",
    "security audit", "production deploy", "breaking change", "trade-off",
    "evaluate options", "deep analysis", "comprehensive", "multi-step",
    "workflow", "pipeline", "orchestrate", "plan and execute",
    "parallel", "concurrent", "distributed", "optimize performance",
    "investigate root cause", "debug complex", "reverse engineer",
]

_MEDIUM_KEYWORDS = [
    "implement", "create", "build", "function", "class", "module",
    "fix bug", "refactor", "test", "explain", "research", "compare",
    "analyze", "write code", "add feature", "update", "integrate",
    "configure", "set up", "deploy", "script", "automate",
    "summarize", "review", "calculate", "translate",
]

# Thresholds for message-length-based classification
_LENGTH_SIMPLE_MAX = 100    # Messages under 100 chars are likely simple
_LENGTH_COMPLEX_MIN = 500   # Messages over 500 chars are likely complex


def classify_complexity(message: str) -> str:
    """Classify task complexity from message length and keyword signals.

    Returns:
        "simple", "medium", or "complex"
    """
    msg_lower = message.lower()
    msg_len = len(message)

    # Score based on keyword matches
    complex_score = sum(1 for kw in _COMPLEX_KEYWORDS if kw in msg_lower)
    medium_score = sum(1 for kw in _MEDIUM_KEYWORDS if kw in msg_lower)

    # Length-based scoring
    if msg_len >= _LENGTH_COMPLEX_MIN:
        complex_score += 2
    elif msg_len >= _LENGTH_SIMPLE_MAX:
        medium_score += 1

    # Multi-line messages suggest more complexity
    line_count = message.count("\n") + 1
    if line_count >= 10:
        complex_score += 1
    elif line_count >= 3:
        medium_score += 1

    # Question mark density: multiple questions suggest complexity
    question_count = message.count("?")
    if question_count >= 3:
        complex_score += 1
    elif question_count >= 2:
        medium_score += 1

    # Code fences suggest substantial code tasks
    if "```" in message:
        medium_score += 1
        if message.count("```") >= 4:
            complex_score += 1

    # Classify
    if complex_score >= 2:
        return "complex"
    elif medium_score >= 2 or complex_score >= 1:
        return "medium"
    else:
        return "simple"


# ---------------------------------------------------------------------------
# SQLite table management
# ---------------------------------------------------------------------------

_table_ensured = False


async def _ensure_table():
    """Create the cost_tracking table on first use."""
    global _table_ensured
    if _table_ensured:
        return

    from tools.sqlite_store import get_db
    db = await get_db()
    if db is None:
        logger.warning("SQLite unavailable — cost tracking will not persist")
        return

    await db.executescript("""
        CREATE TABLE IF NOT EXISTS cost_tracking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            date TEXT NOT NULL,
            model TEXT NOT NULL,
            task_type TEXT DEFAULT 'general',
            complexity TEXT DEFAULT 'medium',
            cost_usd REAL NOT NULL DEFAULT 0.0,
            tokens_used INTEGER DEFAULT 0,
            message_preview TEXT DEFAULT ''
        );

        CREATE INDEX IF NOT EXISTS idx_cost_tracking_date
            ON cost_tracking(date);
        CREATE INDEX IF NOT EXISTS idx_cost_tracking_model
            ON cost_tracking(model);
        CREATE INDEX IF NOT EXISTS idx_cost_tracking_date_model
            ON cost_tracking(date, model);
    """)
    await db.commit()
    _table_ensured = True
    logger.info("cost_tracking table initialized")


# ---------------------------------------------------------------------------
# Core tracking functions
# ---------------------------------------------------------------------------

async def track_cost(
    model: str,
    task_type: str = "general",
    complexity: str = "medium",
    cost_usd: float = 0.0,
    tokens_used: int = 0,
    message_preview: str = "",
) -> bool:
    """Record a cost entry for a model invocation.

    Args:
        model: Model key (e.g. "opus", "sonnet", "gemini")
        task_type: Task classification from routing.py (e.g. "coding", "research")
        complexity: "simple", "medium", or "complex"
        cost_usd: Actual cost in USD (from API response)
        tokens_used: Approximate token count
        message_preview: First 200 chars of the user message (for auditing)

    Returns:
        True if recorded successfully, False otherwise.
    """
    await _ensure_table()

    from tools.sqlite_store import get_db
    db = await get_db()
    if db is None:
        return False

    now = datetime.now()
    today = now.date().isoformat()

    try:
        await db.execute(
            """INSERT INTO cost_tracking
               (timestamp, date, model, task_type, complexity, cost_usd, tokens_used, message_preview)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                now.isoformat(),
                today,
                model,
                task_type,
                complexity,
                cost_usd,
                tokens_used,
                message_preview[:200],
            ),
        )
        await db.commit()
    except Exception as e:
        logger.error(f"track_cost failed: {e}")
        return False

    # Check budget thresholds
    await _check_budget_warnings(today)

    logger.debug(
        f"Cost tracked: model={model} task={task_type} complexity={complexity} "
        f"cost=${cost_usd:.4f} tokens={tokens_used}"
    )
    return True


async def get_daily_cost(target_date: Optional[str] = None) -> float:
    """Get total cost for a given date (defaults to today).

    Args:
        target_date: ISO date string (YYYY-MM-DD). Defaults to today.

    Returns:
        Total cost in USD for the date.
    """
    await _ensure_table()

    from tools.sqlite_store import get_db
    db = await get_db()
    if db is None:
        return 0.0

    if target_date is None:
        target_date = date.today().isoformat()

    try:
        cursor = await db.execute(
            "SELECT COALESCE(SUM(cost_usd), 0) FROM cost_tracking WHERE date = ?",
            (target_date,),
        )
        row = await cursor.fetchone()
        return float(row[0]) if row else 0.0
    except Exception as e:
        logger.error(f"get_daily_cost failed: {e}")
        return 0.0


# ---------------------------------------------------------------------------
# Budget warnings
# ---------------------------------------------------------------------------

async def _check_budget_warnings(today_str: str):
    """Log warnings at 80% and 100% of the daily budget."""
    global _WARN_80_LOGGED, _WARN_100_LOGGED, _LAST_WARN_DATE

    # Reset flags on new day
    today = date.fromisoformat(today_str)
    if _LAST_WARN_DATE != today:
        _WARN_80_LOGGED = False
        _WARN_100_LOGGED = False
        _LAST_WARN_DATE = today

    daily_total = await get_daily_cost(today_str)
    budget = COST_BUDGET_DAILY

    if budget <= 0:
        return  # No budget limit set

    utilization = daily_total / budget

    if utilization >= 1.0 and not _WARN_100_LOGGED:
        logger.warning(
            f"BUDGET EXCEEDED: Daily cost ${daily_total:.2f} has reached "
            f"100% of ${budget:.2f} budget. Consider throttling expensive models."
        )
        _WARN_100_LOGGED = True
    elif utilization >= 0.8 and not _WARN_80_LOGGED:
        logger.warning(
            f"BUDGET WARNING: Daily cost ${daily_total:.2f} has reached "
            f"{utilization:.0%} of ${budget:.2f} budget."
        )
        _WARN_80_LOGGED = True


# ---------------------------------------------------------------------------
# Cost weight for routing integration
# ---------------------------------------------------------------------------

async def get_cost_weight(message: str, current_model: Optional[str] = None) -> dict:
    """Compute cost-efficiency weights for each model given the current message.

    This function is designed to integrate with routing.py's route_model().
    It returns a dict of model -> weight (0.0 to 1.0) where lower weight means
    the model is more cost-efficient for this task, considering:
      1. The model's base cost per token
      2. Today's remaining budget
      3. Task complexity (simple tasks should prefer cheap models)
      4. Historical cost-per-task-type efficiency

    Returns:
        {
            "weights": {"opus": 0.9, "gemini": 0.1, ...},
            "complexity": "simple" | "medium" | "complex",
            "budget_remaining": float,
            "budget_utilization": float,
            "recommendation": str | None,  # cheapest suitable model
        }
    """
    complexity = classify_complexity(message)
    daily_cost = await get_daily_cost()
    budget_remaining = max(COST_BUDGET_DAILY - daily_cost, 0.0)
    budget_utilization = daily_cost / COST_BUDGET_DAILY if COST_BUDGET_DAILY > 0 else 0.0

    # Base cost weights (normalized so cheapest = 0.0, most expensive = 1.0)
    costs = MODEL_COST_PER_1K.copy()
    min_cost = min(costs.values())
    max_cost = max(costs.values())
    cost_range = max_cost - min_cost if max_cost > min_cost else 1.0

    weights = {}
    for model, cost in costs.items():
        # Base weight from raw cost (0 = cheapest, 1 = most expensive)
        base_weight = (cost - min_cost) / cost_range

        # Adjust for budget pressure: as budget runs low, expensive models
        # get penalized more heavily
        budget_penalty = 0.0
        if budget_utilization >= 1.0:
            # Over budget: heavily penalize expensive models
            budget_penalty = base_weight * 0.5
        elif budget_utilization >= 0.8:
            # Near budget: moderate penalty
            budget_penalty = base_weight * 0.3
        elif budget_utilization >= 0.5:
            # Half budget used: light penalty
            budget_penalty = base_weight * 0.1

        # Adjust for complexity: simple tasks should avoid expensive models,
        # complex tasks get a discount on capable (expensive) models
        complexity_adjustment = 0.0
        if complexity == "simple":
            # Penalize expensive models for simple tasks
            complexity_adjustment = base_weight * 0.3
        elif complexity == "complex":
            # Give expensive models a small discount for complex tasks
            # (they're worth the money for hard problems)
            complexity_adjustment = -base_weight * 0.15

        weights[model] = max(0.0, min(1.0, base_weight + budget_penalty + complexity_adjustment))

    # Determine recommendation: cheapest model with weight < 0.5,
    # or None if current model is already cheapest
    sorted_models = sorted(weights.items(), key=lambda x: x[1])
    recommendation = None
    if sorted_models:
        cheapest = sorted_models[0][0]
        if cheapest != current_model and weights.get(current_model, 1.0) > 0.3:
            recommendation = cheapest

    # If budget is exhausted, strongly recommend the cheapest model
    if budget_utilization >= 1.0 and sorted_models:
        recommendation = sorted_models[0][0]

    return {
        "weights": weights,
        "complexity": complexity,
        "budget_remaining": round(budget_remaining, 4),
        "budget_utilization": round(budget_utilization, 4),
        "recommendation": recommendation,
    }


# ---------------------------------------------------------------------------
# Cost summary for dashboard
# ---------------------------------------------------------------------------

async def get_cost_summary(days: int = 7) -> dict:
    """Generate a cost summary for the dashboard.

    Args:
        days: Number of days to include in the summary.

    Returns:
        Dictionary with cost metrics ready for dashboard rendering:
        {
            "period_days": int,
            "daily_budget": float,
            "today": {
                "total_cost": float,
                "budget_remaining": float,
                "budget_utilization": float,
                "calls_by_model": {"opus": 5, ...},
                "cost_by_model": {"opus": 1.23, ...},
            },
            "period": {
                "total_cost": float,
                "avg_daily_cost": float,
                "cost_by_model": {"opus": 5.67, ...},
                "cost_by_task_type": {"coding": 3.45, ...},
                "cost_by_complexity": {"simple": 1.0, ...},
                "total_calls": int,
                "avg_cost_per_call": float,
            },
            "efficiency": {
                "cheapest_model": str,
                "most_expensive_model": str,
                "cost_trend": "increasing" | "decreasing" | "stable",
            },
        }
    """
    await _ensure_table()

    from tools.sqlite_store import get_db
    db = await get_db()
    if db is None:
        return {"error": "SQLite unavailable", "period_days": days}

    today_str = date.today().isoformat()

    # Compute date range
    from datetime import timedelta
    start_date = (date.today() - timedelta(days=days - 1)).isoformat()

    result = {
        "period_days": days,
        "daily_budget": COST_BUDGET_DAILY,
        "today": {},
        "period": {},
        "efficiency": {},
    }

    try:
        # --- Today's metrics ---
        cursor = await db.execute(
            "SELECT COALESCE(SUM(cost_usd), 0) FROM cost_tracking WHERE date = ?",
            (today_str,),
        )
        row = await cursor.fetchone()
        today_cost = float(row[0]) if row else 0.0

        cursor = await db.execute(
            "SELECT model, COUNT(*), COALESCE(SUM(cost_usd), 0) "
            "FROM cost_tracking WHERE date = ? GROUP BY model",
            (today_str,),
        )
        rows = await cursor.fetchall()
        today_calls_by_model = {}
        today_cost_by_model = {}
        for r in rows:
            today_calls_by_model[r[0]] = r[1]
            today_cost_by_model[r[0]] = round(float(r[2]), 4)

        result["today"] = {
            "total_cost": round(today_cost, 4),
            "budget_remaining": round(max(COST_BUDGET_DAILY - today_cost, 0), 4),
            "budget_utilization": round(
                today_cost / COST_BUDGET_DAILY if COST_BUDGET_DAILY > 0 else 0.0, 4
            ),
            "calls_by_model": today_calls_by_model,
            "cost_by_model": today_cost_by_model,
        }

        # --- Period metrics ---
        cursor = await db.execute(
            "SELECT COALESCE(SUM(cost_usd), 0), COUNT(*) "
            "FROM cost_tracking WHERE date >= ?",
            (start_date,),
        )
        row = await cursor.fetchone()
        period_total = float(row[0]) if row else 0.0
        period_calls = int(row[1]) if row else 0

        cursor = await db.execute(
            "SELECT model, COALESCE(SUM(cost_usd), 0) "
            "FROM cost_tracking WHERE date >= ? GROUP BY model",
            (start_date,),
        )
        rows = await cursor.fetchall()
        period_cost_by_model = {r[0]: round(float(r[1]), 4) for r in rows}

        cursor = await db.execute(
            "SELECT task_type, COALESCE(SUM(cost_usd), 0) "
            "FROM cost_tracking WHERE date >= ? GROUP BY task_type",
            (start_date,),
        )
        rows = await cursor.fetchall()
        period_cost_by_task = {r[0]: round(float(r[1]), 4) for r in rows}

        cursor = await db.execute(
            "SELECT complexity, COALESCE(SUM(cost_usd), 0) "
            "FROM cost_tracking WHERE date >= ? GROUP BY complexity",
            (start_date,),
        )
        rows = await cursor.fetchall()
        period_cost_by_complexity = {r[0]: round(float(r[1]), 4) for r in rows}

        result["period"] = {
            "total_cost": round(period_total, 4),
            "avg_daily_cost": round(period_total / max(days, 1), 4),
            "cost_by_model": period_cost_by_model,
            "cost_by_task_type": period_cost_by_task,
            "cost_by_complexity": period_cost_by_complexity,
            "total_calls": period_calls,
            "avg_cost_per_call": round(
                period_total / max(period_calls, 1), 6
            ),
        }

        # --- Efficiency metrics ---
        if period_cost_by_model:
            cheapest = min(period_cost_by_model, key=period_cost_by_model.get)
            most_expensive = max(period_cost_by_model, key=period_cost_by_model.get)
        else:
            cheapest = "gemini"
            most_expensive = "opus"

        # Cost trend: compare first half vs second half of period
        half_days = max(days // 2, 1)
        mid_date = (date.today() - timedelta(days=half_days)).isoformat()

        cursor = await db.execute(
            "SELECT COALESCE(SUM(cost_usd), 0) "
            "FROM cost_tracking WHERE date >= ? AND date < ?",
            (start_date, mid_date),
        )
        row = await cursor.fetchone()
        first_half_cost = float(row[0]) if row else 0.0

        cursor = await db.execute(
            "SELECT COALESCE(SUM(cost_usd), 0) "
            "FROM cost_tracking WHERE date >= ?",
            (mid_date,),
        )
        row = await cursor.fetchone()
        second_half_cost = float(row[0]) if row else 0.0

        if first_half_cost == 0 and second_half_cost == 0:
            trend = "stable"
        elif second_half_cost > first_half_cost * 1.2:
            trend = "increasing"
        elif second_half_cost < first_half_cost * 0.8:
            trend = "decreasing"
        else:
            trend = "stable"

        result["efficiency"] = {
            "cheapest_model": cheapest,
            "most_expensive_model": most_expensive,
            "cost_trend": trend,
        }

    except Exception as e:
        logger.error(f"get_cost_summary failed: {e}")
        result["error"] = str(e)

    return result


# ---------------------------------------------------------------------------
# Utility: format cost summary as markdown (for dashboard integration)
# ---------------------------------------------------------------------------

async def format_cost_dashboard(days: int = 7) -> str:
    """Render cost metrics as a markdown section for the evaluation dashboard."""
    summary = await get_cost_summary(days)

    if "error" in summary and not summary.get("today"):
        return f"## Cost Tracking\n\n*Error: {summary['error']}*\n"

    lines = [
        "## Cost Tracking\n",
        f"*Daily budget: ${summary['daily_budget']:.2f} | "
        f"Period: last {summary['period_days']} days*\n",
    ]

    # Today
    today = summary.get("today", {})
    util = today.get("budget_utilization", 0)
    util_bar = "#" * int(util * 20) + "-" * (20 - int(util * 20))
    lines.append("### Today\n")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Total cost | ${today.get('total_cost', 0):.4f} |")
    lines.append(f"| Budget remaining | ${today.get('budget_remaining', 0):.4f} |")
    lines.append(f"| Utilization | [{util_bar}] {util:.0%} |")

    if today.get("cost_by_model"):
        lines.append("\n| Model | Calls | Cost |")
        lines.append("|-------|-------|------|")
        for model in sorted(today["cost_by_model"].keys()):
            calls = today.get("calls_by_model", {}).get(model, 0)
            cost = today["cost_by_model"][model]
            lines.append(f"| {model} | {calls} | ${cost:.4f} |")

    # Period
    period = summary.get("period", {})
    lines.append(f"\n### Last {summary['period_days']} Days\n")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Total cost | ${period.get('total_cost', 0):.4f} |")
    lines.append(f"| Avg daily cost | ${period.get('avg_daily_cost', 0):.4f} |")
    lines.append(f"| Total API calls | {period.get('total_calls', 0)} |")
    lines.append(f"| Avg cost per call | ${period.get('avg_cost_per_call', 0):.6f} |")

    if period.get("cost_by_model"):
        lines.append("\n**Cost by model:**\n")
        lines.append("| Model | Cost |")
        lines.append("|-------|------|")
        for model, cost in sorted(period["cost_by_model"].items(), key=lambda x: x[1], reverse=True):
            lines.append(f"| {model} | ${cost:.4f} |")

    if period.get("cost_by_task_type"):
        lines.append("\n**Cost by task type:**\n")
        lines.append("| Task Type | Cost |")
        lines.append("|-----------|------|")
        for task, cost in sorted(period["cost_by_task_type"].items(), key=lambda x: x[1], reverse=True):
            lines.append(f"| {task} | ${cost:.4f} |")

    if period.get("cost_by_complexity"):
        lines.append("\n**Cost by complexity:**\n")
        lines.append("| Complexity | Cost |")
        lines.append("|------------|------|")
        for cx, cost in sorted(period["cost_by_complexity"].items(), key=lambda x: x[1], reverse=True):
            lines.append(f"| {cx} | ${cost:.4f} |")

    # Efficiency
    eff = summary.get("efficiency", {})
    if eff:
        lines.append(f"\n### Efficiency\n")
        lines.append(f"- Cost trend: **{eff.get('cost_trend', 'unknown')}**")
        lines.append(f"- Cheapest model (period): **{eff.get('cheapest_model', 'N/A')}**")
        lines.append(f"- Most expensive model (period): **{eff.get('most_expensive_model', 'N/A')}**")

    lines.append("")
    return "\n".join(lines)
