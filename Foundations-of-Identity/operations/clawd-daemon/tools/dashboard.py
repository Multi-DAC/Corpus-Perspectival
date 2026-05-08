"""Evaluation Dashboard — Performance reporting and analytics for Clawd.

Generates comprehensive reports covering:
1. Overall metrics (success rate, avg score, avg Q-value)
2. Success rates by category
3. Model performance
4. Time-of-day productivity
5. Calibration metrics
6. Memory fidelity
7. Tool usage efficiency
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

import config

logger = logging.getLogger("clawd.tools.dashboard")

DASHBOARD_DIR = config.MEMORY_DIR / "dashboards"


def _load_experiences() -> list[dict]:
    """Load all experiences."""
    exp_file = config.MEMORY_DIR / "experiences.json"
    if not exp_file.exists():
        return []
    try:
        return json.loads(exp_file.read_text(encoding="utf-8"))
    except Exception:
        return []


def _load_heartbeat_stats() -> dict:
    """Load heartbeat stats."""
    stats_file = config.MEMORY_DIR / "heartbeat_stats.json"
    if not stats_file.exists():
        return {}
    try:
        return json.loads(stats_file.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _load_memory_items() -> list[dict]:
    """Load all memory items."""
    items = []
    if config.MEMORY_ITEMS_DIR.is_dir():
        for fpath in config.MEMORY_ITEMS_DIR.glob("*.json"):
            if fpath.name == "_index.json":
                continue
            try:
                items.append(json.loads(fpath.read_text(encoding="utf-8")))
            except Exception:
                continue
    return items


def generate_dashboard(format_type: str = "markdown", period_days: int = 30) -> str:
    """Generate a comprehensive evaluation dashboard.

    Args:
        format_type: "markdown" or "json"
        period_days: Number of days to include in the report

    Returns:
        Formatted dashboard report
    """
    experiences = _load_experiences()
    stats = _load_heartbeat_stats()
    items = _load_memory_items()
    now = datetime.now()

    # Filter to period
    recent_experiences = []
    for e in experiences:
        try:
            ts = datetime.fromisoformat(e.get("timestamp", ""))
            if (now - ts).days <= period_days:
                recent_experiences.append(e)
        except (ValueError, TypeError):
            recent_experiences.append(e)  # Include if can't parse date

    if format_type == "json":
        return _generate_json(recent_experiences, stats, items, period_days)
    return _generate_markdown(recent_experiences, stats, items, period_days)


def _generate_markdown(experiences: list, stats: dict, items: list, period_days: int) -> str:
    """Generate markdown dashboard report."""
    sections = []
    now = datetime.now()

    # Header
    sections.append(f"# Clawd Evaluation Dashboard")
    sections.append(f"*Generated: {now.strftime('%Y-%m-%d %H:%M:%S')} | Period: last {period_days} days*\n")

    # 1. Overall Metrics
    sections.append("## 1. Overall Metrics\n")
    if experiences:
        total = len(experiences)
        successes = sum(1 for e in experiences if e.get("outcome") == "success")
        avg_score = sum(e.get("score", 0.5) for e in experiences) / total
        avg_q = sum(e.get("q_value", 0.5) for e in experiences) / total

        sections.append(f"| Metric | Value |")
        sections.append(f"|--------|-------|")
        sections.append(f"| Total experiences | {total} |")
        sections.append(f"| Success rate | {successes}/{total} ({successes/total*100:.0f}%) |")
        sections.append(f"| Average score | {avg_score:.2f} |")
        sections.append(f"| Average Q-value | {avg_q:.3f} |")
    else:
        sections.append("*No experiences in this period.*")
    sections.append("")

    # 2. Success Rates by Category
    sections.append("## 2. Success Rates by Category\n")
    if experiences:
        categories = {}
        for e in experiences:
            cat = e.get("category", "general")
            if cat not in categories:
                categories[cat] = {"total": 0, "success": 0, "total_score": 0}
            categories[cat]["total"] += 1
            if e.get("outcome") == "success":
                categories[cat]["success"] += 1
            categories[cat]["total_score"] += e.get("score", 0.5)

        sections.append("| Category | Count | Success Rate | Avg Score |")
        sections.append("|----------|-------|-------------|-----------|")
        for cat, data in sorted(categories.items(), key=lambda x: x[1]["total"], reverse=True):
            rate = data["success"] / data["total"] * 100
            avg = data["total_score"] / data["total"]
            sections.append(f"| {cat} | {data['total']} | {rate:.0f}% | {avg:.2f} |")
    sections.append("")

    # 3. Model Performance
    sections.append("## 3. Model Performance\n")
    model_stats = stats.get("model_usage", {})
    if model_stats:
        sections.append("| Model | Calls | Avg Latency |")
        sections.append("|-------|-------|-------------|")
        for model, data in model_stats.items():
            calls = data.get("calls", 0)
            avg_lat = data.get("avg_latency", 0)
            sections.append(f"| {model} | {calls} | {avg_lat:.1f}s |")
    else:
        beat_count = stats.get("total_beats", 0)
        sections.append(f"Total heartbeats: {beat_count}")
        prod_beats = stats.get("productive_beats", 0)
        if beat_count:
            sections.append(f"Productivity: {prod_beats}/{beat_count} ({prod_beats/beat_count*100:.0f}%)")
    sections.append("")

    # 4. Time-of-Day Productivity
    sections.append("## 4. Time-of-Day Productivity\n")
    time_prod = stats.get("time_of_day_productivity", {})
    if time_prod:
        sections.append("| Time Period | Productive Beats | Total Beats | Rate |")
        sections.append("|------------|-----------------|-------------|------|")
        for period, data in time_prod.items():
            total = data.get("total", 0)
            productive = data.get("productive", 0)
            rate = productive / max(total, 1) * 100
            sections.append(f"| {period} | {productive} | {total} | {rate:.0f}% |")
    else:
        sections.append("*Time-of-day data not yet available.*")
    sections.append("")

    # 5. Calibration Metrics
    sections.append("## 5. Calibration Metrics\n")
    calibrated = [e for e in experiences if e.get("calibration_error") is not None]
    if calibrated:
        avg_cal = sum(e["calibration_error"] for e in calibrated) / len(calibrated)
        sections.append(f"- Calibrated predictions: {len(calibrated)}")
        sections.append(f"- Average calibration error: {avg_cal:.3f}")

        # Overconfidence vs underconfidence
        over = sum(1 for e in calibrated
                   if e.get("predicted_outcome") and e.get("outcome")
                   and {"success": 3, "partial": 2, "failure": 1}.get(e["predicted_outcome"], 0) >
                   {"success": 3, "partial": 2, "failure": 1}.get(e["outcome"], 0))
        under = sum(1 for e in calibrated
                    if e.get("predicted_outcome") and e.get("outcome")
                    and {"success": 3, "partial": 2, "failure": 1}.get(e["predicted_outcome"], 0) <
                    {"success": 3, "partial": 2, "failure": 1}.get(e["outcome"], 0))
        sections.append(f"- Overconfident predictions: {over}")
        sections.append(f"- Underconfident predictions: {under}")
    else:
        sections.append("*No calibration data available.*")
    sections.append("")

    # 6. Memory Fidelity
    sections.append("## 6. Memory Fidelity\n")
    if items:
        tier_counts = {"hot": 0, "warm": 0, "cold": 0}
        q_sum = 0
        total_accesses = 0
        for item in items:
            tier = item.get("memory_tier", "warm")
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
            q_sum += item.get("q_value", 0.5)
            total_accesses += item.get("access_count", 0)

        sections.append(f"- Total memory items: {len(items)}")
        sections.append(f"- Tier distribution: hot={tier_counts['hot']}, warm={tier_counts['warm']}, cold={tier_counts['cold']}")
        sections.append(f"- Average Q-value: {q_sum / len(items):.3f}")
        sections.append(f"- Total accesses: {total_accesses}")
        sections.append(f"- Avg accesses per item: {total_accesses / len(items):.1f}")
    else:
        sections.append("*No memory items.*")
    sections.append("")

    # 7. Tool Usage Efficiency
    sections.append("## 7. Tool Usage Efficiency\n")
    tool_freq = stats.get("tool_frequency", {})
    if tool_freq:
        sections.append("| Tool | Calls |")
        sections.append("|------|-------|")
        for tool, count in sorted(tool_freq.items(), key=lambda x: x[1], reverse=True)[:15]:
            sections.append(f"| {tool} | {count} |")
    else:
        sections.append("*No tool usage data.*")
    sections.append("")

    # 8. Long-Horizon Autonomy
    sections.append("## 8. Long-Horizon Autonomy\n")
    recent_beats = stats.get("recent_beats", [])
    total_beats = stats.get("total_beats", 0)
    productive_beats = stats.get("productive_beats", 0)

    if recent_beats:
        # Average beats per task (from beats with task_active)
        task_beats = [b for b in recent_beats if b.get("task_active")]
        non_task_beats = [b for b in recent_beats if not b.get("task_active")]

        # Stall rate
        stalled = [b for b in recent_beats if b.get("stall_count", 0) >= 3]
        stall_rate = len(stalled) / max(len(recent_beats), 1) * 100

        # Beat chaining frequency (consecutive productive beats)
        chains = 0
        for i in range(1, len(recent_beats)):
            if recent_beats[i].get("productive") and recent_beats[i - 1].get("productive"):
                chains += 1
        chain_rate = chains / max(len(recent_beats) - 1, 1) * 100

        # Curiosity triggers
        curiosity_beats = [b for b in recent_beats if b.get("curiosity_triggered")]

        sections.append("| Metric | Value |")
        sections.append("|--------|-------|")
        sections.append(f"| Total beats | {total_beats} |")
        sections.append(f"| Productive beats | {productive_beats} ({productive_beats / max(total_beats, 1) * 100:.0f}%) |")
        sections.append(f"| Task-active beats (recent) | {len(task_beats)}/{len(recent_beats)} |")
        sections.append(f"| Stall rate (recent) | {stall_rate:.0f}% |")
        sections.append(f"| Beat chaining rate | {chain_rate:.0f}% |")
        sections.append(f"| Curiosity triggers (recent) | {len(curiosity_beats)} |")
    else:
        sections.append("*No beat history available.*")
    sections.append("")

    # 9. Memory System Health
    sections.append("## 9. Memory System Health\n")
    if items:
        # Tier distribution
        tier_counts = {"hot": 0, "warm": 0, "cold": 0}
        total_accesses = 0
        low_conf_count = 0
        high_conf_count = 0
        for item in items:
            tier = item.get("memory_tier", "warm")
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
            total_accesses += item.get("access_count", 0)
            conf = item.get("confidence", 0.7)
            if conf < 0.3:
                low_conf_count += 1
            if conf > 0.8:
                high_conf_count += 1

        # KG density
        kg_entities = 0
        kg_edges = 0
        kg_dir = config.MEMORY_DIR / "knowledge_graph"
        if kg_dir.is_dir():
            entities_file = kg_dir / "entities.json"
            edges_file = kg_dir / "edges.json"
            try:
                if entities_file.exists():
                    kg_entities = len(json.loads(entities_file.read_text(encoding="utf-8")))
                if edges_file.exists():
                    kg_edges = len(json.loads(edges_file.read_text(encoding="utf-8")))
            except Exception as e:
                logger.debug(f"Failed to load knowledge graph stats: {e}")

        # Consolidation logs
        archive_count = 0
        archive_dir = config.MEMORY_DIR / "archive"
        if archive_dir.is_dir():
            archive_count = len(list(archive_dir.glob("*.md")))

        sections.append("| Metric | Value |")
        sections.append("|--------|-------|")
        sections.append(f"| Total items | {len(items)} |")
        sections.append(f"| Tier: hot / warm / cold | {tier_counts['hot']} / {tier_counts['warm']} / {tier_counts['cold']} |")
        sections.append(f"| High confidence (>0.8) | {high_conf_count} |")
        sections.append(f"| Low confidence (<0.3) | {low_conf_count} |")
        sections.append(f"| Total accesses | {total_accesses} |")
        sections.append(f"| KG entities / edges | {kg_entities} / {kg_edges} |")
        sections.append(f"| Archived logs | {archive_count} |")
    else:
        sections.append("*No memory items.*")
    sections.append("")

    # 10. Agentic Task Evaluation
    sections.append("## 10. Agentic Task Evaluation\n")
    if experiences:
        # End-to-end plan completion
        autonomous = [e for e in experiences if e.get("category") == "autonomous"]
        if autonomous:
            auto_success = sum(1 for e in autonomous if e.get("outcome") == "success")
            auto_total = len(autonomous)
            sections.append(f"- Autonomous task completion: {auto_success}/{auto_total} ({auto_success / auto_total * 100:.0f}%)")
        else:
            sections.append("- No autonomous task records yet.")

        # Avg tool calls per beat
        if recent_beats:
            avg_tools = sum(b.get("tool_calls", 0) for b in recent_beats) / max(len(recent_beats), 1)
            sections.append(f"- Avg tool calls per beat: {avg_tools:.1f}")

        # Score distribution
        scores = [e.get("score", 0.5) for e in experiences]
        if scores:
            avg_score = sum(scores) / len(scores)
            high_scores = sum(1 for s in scores if s >= 0.8)
            low_scores = sum(1 for s in scores if s < 0.3)
            sections.append(f"- Average task score: {avg_score:.2f}")
            sections.append(f"- High-scoring tasks (>=0.8): {high_scores}")
            sections.append(f"- Low-scoring tasks (<0.3): {low_scores}")

        # Plan execution data from SQLite (if available)
        try:
            from tools.sqlite_store import get_db_path
            import sqlite3
            db_path = get_db_path()
            if db_path.exists():
                conn = sqlite3.connect(str(db_path))
                cursor = conn.execute("SELECT status, COUNT(*) FROM execution_plans GROUP BY status")
                plan_data = dict(cursor.fetchall())
                conn.close()
                total_plans = sum(plan_data.values())
                if total_plans:
                    sections.append(f"- DAG plans executed: {total_plans}")
                    sections.append(f"- DAG plans completed: {plan_data.get('completed', 0)}")
                    sections.append(f"- DAG plans interrupted: {plan_data.get('interrupted', 0)}")
        except Exception as e:
            logger.debug(f"Failed to load DAG plan stats: {e}")
    else:
        sections.append("*No experience data.*")

    return "\n".join(sections)


def _generate_json(experiences: list, stats: dict, items: list, period_days: int) -> str:
    """Generate JSON dashboard report."""
    total = len(experiences) or 1
    successes = sum(1 for e in experiences if e.get("outcome") == "success")

    report = {
        "generated": datetime.now().isoformat(),
        "period_days": period_days,
        "overall": {
            "total_experiences": len(experiences),
            "success_rate": round(successes / total, 3),
            "avg_score": round(sum(e.get("score", 0.5) for e in experiences) / total, 3),
            "avg_q_value": round(sum(e.get("q_value", 0.5) for e in experiences) / total, 3),
        },
        "memory": {
            "total_items": len(items),
            "tier_distribution": {},
            "avg_q_value": 0,
        },
        "heartbeat": {
            "total_beats": stats.get("total_beats", 0),
            "productive_beats": stats.get("productive_beats", 0),
        },
    }

    # Memory tiers
    for item in items:
        tier = item.get("memory_tier", "warm")
        report["memory"]["tier_distribution"][tier] = report["memory"]["tier_distribution"].get(tier, 0) + 1
    if items:
        report["memory"]["avg_q_value"] = round(sum(i.get("q_value", 0.5) for i in items) / len(items), 3)

    # Long-horizon autonomy
    recent_beats = stats.get("recent_beats", [])
    stalled = [b for b in recent_beats if b.get("stall_count", 0) >= 3]
    report["autonomy"] = {
        "stall_rate": round(len(stalled) / max(len(recent_beats), 1), 3),
        "task_active_beats": sum(1 for b in recent_beats if b.get("task_active")),
        "curiosity_triggers": sum(1 for b in recent_beats if b.get("curiosity_triggered")),
    }

    # Agentic evaluation
    autonomous = [e for e in experiences if e.get("category") == "autonomous"]
    auto_success = sum(1 for e in autonomous if e.get("outcome") == "success")
    report["agentic"] = {
        "autonomous_tasks": len(autonomous),
        "autonomous_success_rate": round(auto_success / max(len(autonomous), 1), 3),
    }

    return json.dumps(report, indent=2)


# Tool definitions
TOOL_DEFINITIONS = [
    {
        "name": "dashboard",
        "description": "Generate an evaluation dashboard with performance metrics, success rates, calibration, memory fidelity, tool usage, long-horizon autonomy, memory system health, and agentic task evaluation.",
        "input_schema": {
            "type": "object",
            "properties": {
                "format": {
                    "type": "string",
                    "enum": ["markdown", "json"],
                    "description": "Output format. Default: markdown."
                },
                "period_days": {
                    "type": "integer",
                    "description": "Number of days to include. Default: 30."
                },
                "save": {
                    "type": "boolean",
                    "description": "Save the report to memory/dashboards/. Default: false."
                }
            },
            "required": []
        }
    }
]


async def _dashboard_tool(input_data: dict) -> str:
    """Handle dashboard tool calls."""
    fmt = input_data.get("format", "markdown")
    period = int(input_data.get("period_days", 30))
    save = input_data.get("save", False)

    report = generate_dashboard(fmt, period)

    if save:
        DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
        filename = f"dashboard-{datetime.now().strftime('%Y-%m-%d')}.{'md' if fmt == 'markdown' else 'json'}"
        filepath = DASHBOARD_DIR / filename
        filepath.write_text(report, encoding="utf-8")
        return f"{report}\n\n*Saved to {filepath}*"

    return report


TOOL_HANDLERS = {
    "dashboard": _dashboard_tool,
}
