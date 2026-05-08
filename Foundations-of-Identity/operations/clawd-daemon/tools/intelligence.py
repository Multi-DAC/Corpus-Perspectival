"""Intelligence tools — reflection, goals, experience tracking, self-improvement."""
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import config

logger = logging.getLogger("clawd.tools.intelligence")

TOOL_DEFINITIONS = [
    {
        "name": "self_improve",
        "description": "Analyze recent experiences and patterns to propose self-improvements. Reviews strategy success rates and suggests configuration changes, prompt tweaks, or behavioral adjustments. Proposals are stored for review.",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["analyze", "propose", "list_proposals", "apply"],
                    "description": "analyze: review recent patterns. propose: create an improvement proposal. list_proposals: see pending proposals. apply: mark a proposal as applied."
                },
                "proposal": {
                    "type": "string",
                    "description": "The improvement proposal text (for propose)."
                },
                "category": {
                    "type": "string",
                    "enum": ["prompt_tweak", "tool_usage", "workflow", "scheduling", "memory", "communication"],
                    "description": "Category of improvement."
                },
                "proposal_id": {
                    "type": "string",
                    "description": "Proposal ID (for apply)."
                },
                "risk": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "description": "Risk level. Low-risk proposals (prompt tweaks) can be self-approved."
                }
            },
            "required": ["action"]
        }
    },
    {
        "name": "verify_action",
        "description": "Self-critique: verify whether your last action achieved the intended result. Use after high-stakes operations (file writes, shell commands, memory updates) to catch errors before they compound.",
        "input_schema": {
            "type": "object",
            "properties": {
                "action_description": {
                    "type": "string",
                    "description": "What you intended to do."
                },
                "actual_result": {
                    "type": "string",
                    "description": "What actually happened (paste output/result)."
                },
                "success_criteria": {
                    "type": "string",
                    "description": "How to tell if it worked correctly."
                }
            },
            "required": ["action_description", "actual_result"]
        }
    },
    {
        "name": "reflect",
        "description": "Self-reflection and learning. Record insights, review patterns, improve future behavior. Updates CLAWD_HOME/memory/learnings.md and SELF-IMPROVEMENT.md.",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["record_insight", "review_learnings", "assess_performance", "consolidate_memory"],
                    "description": "record_insight: save a learning. review_learnings: read past insights. assess_performance: evaluate recent actions. consolidate_memory: compress old logs into summaries."
                },
                "content": {
                    "type": "string",
                    "description": "The insight, reflection, or assessment content."
                },
                "category": {
                    "type": "string",
                    "description": "Category: tool_use, communication, problem_solving, project, self_knowledge, technical."
                }
            },
            "required": ["action"]
        }
    },
    {
        "name": "goals",
        "description": "Track active goals and progress. Supports hierarchical sub-goals with dependencies. Set priorities, update progress, record milestones. Goals persist across sessions.",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["add", "update", "list", "remove", "add_sub_goal", "update_sub_goal", "list_tree"],
                    "description": "add: create goal. update: update progress/status. list: show goals. remove: delete goal. add_sub_goal: add sub-goal to parent. update_sub_goal: update a sub-goal. list_tree: show hierarchical goal tree."
                },
                "title": {
                    "type": "string",
                    "description": "Goal/sub-goal title."
                },
                "description": {
                    "type": "string",
                    "description": "Goal description."
                },
                "priority": {
                    "type": "string",
                    "enum": ["high", "medium", "low"],
                    "description": "Goal priority. Default: medium."
                },
                "goal_id": {
                    "type": "integer",
                    "description": "Goal ID (for update/remove/add_sub_goal)."
                },
                "progress": {
                    "type": "integer",
                    "description": "Progress percentage 0-100 (for update)."
                },
                "status": {
                    "type": "string",
                    "enum": ["active", "completed", "paused", "abandoned"],
                    "description": "Goal status (for update)."
                },
                "note": {
                    "type": "string",
                    "description": "Note to add to goal (for update)."
                },
                "milestone": {
                    "type": "string",
                    "description": "Milestone achieved (for update)."
                },
                "acceptance_criteria": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of acceptance criteria for goal completion (for add/update)."
                },
                "sub_goal_id": {
                    "type": "string",
                    "description": "Sub-goal ID (for update_sub_goal). Format: 'parent_id.sub_index'."
                },
                "depends_on": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Sub-goal IDs this sub-goal depends on (for add_sub_goal)."
                },
                "parent_id": {
                    "type": "integer",
                    "description": "Parent goal ID (for add_sub_goal)."
                }
            },
            "required": ["action"]
        }
    },
    {
        "name": "experience",
        "description": "Track task experiences for learning. Record outcomes, approaches, and lessons. Retrieve relevant past experiences when facing similar tasks. Analyze patterns. Predict before starting tasks, give feedback after retrieval.",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["record", "recall", "patterns", "distill", "predict", "feedback", "execute_skill", "compose"],
                    "description": "record: save a task experience. recall: find relevant past experiences. patterns: analyze patterns. distill: extract an executable skill. predict: record a prediction. feedback: retrieval feedback. execute_skill: run a distilled skill. compose: chain skills into a composite."
                },
                "task": {
                    "type": "string",
                    "description": "Task description (for record/recall)."
                },
                "approach": {
                    "type": "string",
                    "description": "How you approached the task (for record)."
                },
                "tools_used": {
                    "type": "string",
                    "description": "Comma-separated tools used (for record)."
                },
                "outcome": {
                    "type": "string",
                    "enum": ["success", "partial", "failure"],
                    "description": "Task outcome (for record). Default: success."
                },
                "score": {
                    "type": "number",
                    "description": "Quality score 0.0-1.0 (for record). Default: 0.7."
                },
                "reflection": {
                    "type": "string",
                    "description": "What happened and why (for record)."
                },
                "lesson": {
                    "type": "string",
                    "description": "Key lesson learned (for record)."
                },
                "category": {
                    "type": "string",
                    "description": "Category: coding, research, communication, financial, creative, system."
                },
                "count": {
                    "type": "integer",
                    "description": "Number of results to return (for recall). Default: 5."
                },
                "experience_id": {
                    "type": "integer",
                    "description": "Experience ID to distill into a skill template (for distill), or for feedback."
                },
                "skill_name": {
                    "type": "string",
                    "description": "Name for the distilled skill (for distill)."
                },
                "trigger": {
                    "type": "string",
                    "description": "When to apply this skill — the trigger condition (for distill)."
                },
                "predicted_outcome": {
                    "type": "string",
                    "enum": ["success", "partial", "failure"],
                    "description": "Predicted outcome before starting (for predict/record)."
                },
                "predicted_difficulty": {
                    "type": "string",
                    "enum": ["easy", "medium", "hard"],
                    "description": "Predicted difficulty (for predict/record)."
                },
                "actual_difficulty": {
                    "type": "string",
                    "enum": ["easy", "medium", "hard"],
                    "description": "Actual difficulty after completion (for record)."
                },
                "counterfactual": {
                    "type": "string",
                    "description": "What would you do differently? (for record)."
                },
                "success": {
                    "type": "boolean",
                    "description": "For feedback: did the retrieved experience lead to task success?"
                },
                "skill_name": {
                    "type": "string",
                    "description": "Name of a distilled skill (for execute_skill/compose)."
                },
                "task_context": {
                    "type": "string",
                    "description": "Context to fill into skill workflow templates (for execute_skill)."
                },
                "skill_names": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of skill names to compose (for compose action)."
                },
                "composite_name": {
                    "type": "string",
                    "description": "Name for the composite skill (for compose action)."
                }
            },
            "required": ["action"]
        }
    },
]

SKILLBANK_DIR = config.MEMORY_DIR / "skillbank"
IMPROVEMENTS_DIR = config.MEMORY_DIR / "improvements"


async def _reflect(input_data: dict) -> str:
    """Self-reflection and learning — record insights, review patterns, consolidate memory."""
    action = input_data["action"]
    content = input_data.get("content", "")
    category = input_data.get("category", "general")

    learnings_file = config.MEMORY_DIR / "learnings.md"
    learnings_file.parent.mkdir(parents=True, exist_ok=True)

    if action == "record_insight":
        if not content:
            return "Error: content required to record an insight."

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

        if not learnings_file.exists():
            learnings_file.write_text("# Learnings & Insights\n\n*Self-generated knowledge from experience.*\n\n", encoding="utf-8")

        entry = f"### [{timestamp}] ({category})\n{content}\n\n"
        with open(learnings_file, "a", encoding="utf-8") as f:
            f.write(entry)

        return f"Insight recorded in learnings.md ({category}): {content[:100]}..."

    elif action == "review_learnings":
        if not learnings_file.exists():
            return "No learnings recorded yet. Use record_insight to start building your knowledge base."

        text = learnings_file.read_text(encoding="utf-8", errors="replace")
        if category and category != "general":
            # Filter by category
            lines = text.split("\n")
            filtered = []
            include = False
            for line in lines:
                if line.startswith("### ["):
                    include = category in line.lower()
                if include:
                    filtered.append(line)
            text = "\n".join(filtered) if filtered else f"No learnings found for category: {category}"

        if len(text) > 10000:
            text = text[-10000:]  # Show most recent
        return text

    elif action == "assess_performance":
        # Read today's log and generate a self-assessment
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = config.MEMORY_DIR / f"{today}.md"

        if not log_file.exists():
            return "No activity log for today yet."

        log_content = log_file.read_text(encoding="utf-8", errors="replace")

        # Count activities
        tool_calls = log_content.count("tool call")
        errors = log_content.lower().count("error")
        heartbeats = log_content.lower().count("heartbeat")

        assessment = f"""## Self-Assessment — {today}

### Activity Summary
- Log entries: {len(log_content.splitlines())} lines
- Heartbeats logged: {heartbeats}
- Errors mentioned: {errors}

### Recent Log (last 3000 chars):
{log_content[-3000:]}

### Reflection Prompts
- What went well today?
- What could be improved?
- What patterns am I noticing?
- What should I focus on next?

Use record_insight to save any observations."""

        return assessment

    elif action == "consolidate_memory":
        # Compress old daily logs into weekly summaries
        results = []
        today = datetime.now()

        # Find logs older than 7 days that haven't been summarized
        old_logs = []
        for log_file in sorted(config.MEMORY_DIR.glob("20??-??-??.md")):
            try:
                date_str = log_file.stem
                log_date = datetime.strptime(date_str, "%Y-%m-%d")
                age_days = (today - log_date).days
                if age_days > 7:
                    old_logs.append((log_file, date_str, age_days))
            except ValueError:
                continue

        if not old_logs:
            return "No logs older than 7 days to consolidate."

        # Group by week
        weeks = {}
        for log_file, date_str, age in old_logs:
            log_date = datetime.strptime(date_str, "%Y-%m-%d")
            week_key = log_date.strftime("%Y-W%W")
            if week_key not in weeks:
                weeks[week_key] = []
            weeks[week_key].append(log_file)

        summaries_dir = config.MEMORY_DIR / "weekly-summaries"
        summaries_dir.mkdir(exist_ok=True)

        for week_key, logs in weeks.items():
            summary_file = summaries_dir / f"{week_key}.md"
            if summary_file.exists():
                continue  # Already summarized

            # Compile the week's logs
            week_content = []
            for log_file in sorted(logs):
                try:
                    content = log_file.read_text(encoding="utf-8", errors="replace")
                    week_content.append(f"## {log_file.stem}\n{content[:2000]}")
                except Exception:
                    continue

            if week_content:
                summary = f"# Weekly Summary — {week_key}\n\n"
                summary += f"*Consolidated from {len(logs)} daily logs.*\n\n"
                summary += "\n\n".join(week_content)

                summary_file.write_text(summary, encoding="utf-8")
                results.append(f"Created {summary_file.name} from {len(logs)} logs")

        if results:
            return "Memory consolidation complete:\n" + "\n".join(results)
        return "All weeks already consolidated."

    return f"Unknown reflect action: {action}"


async def _goals(input_data: dict) -> str:
    """Track active goals with progress, priorities, and deadlines."""
    action = input_data["action"]
    goals_file = config.MEMORY_DIR / "goals.json"
    goals_file.parent.mkdir(parents=True, exist_ok=True)

    # Load existing goals
    goals = []
    if goals_file.exists():
        try:
            goals = json.loads(goals_file.read_text(encoding="utf-8", errors="replace"))
        except (json.JSONDecodeError, Exception):
            goals = []

    def _auto_calc_progress(goal):
        """Auto-calculate parent progress from sub-goal completion."""
        subs = goal.get("sub_goals", [])
        if not subs:
            return
        completed = sum(1 for s in subs if s.get("status") == "completed")
        in_progress_pct = sum(s.get("progress", 0) for s in subs)
        total = len(subs)
        if total > 0:
            goal["progress"] = min(100, int(in_progress_pct / total))

    if action == "add":
        title = input_data.get("title", "")
        if not title:
            return "Error: title required to add a goal."
        # Generate unique ID (max existing + 1)
        max_id = max((g.get("id", 0) for g in goals), default=0)
        goal = {
            "id": max_id + 1,
            "title": title,
            "description": input_data.get("description", ""),
            "priority": input_data.get("priority", "medium"),
            "status": "active",
            "progress": 0,
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat(),
            "started_at": datetime.now().isoformat(),
            "completed_at": None,
            "due_date": input_data.get("due_date"),
            "milestones": [],
            "notes": [],
            "acceptance_criteria": input_data.get("acceptance_criteria", []),
            "sub_goals": [],
            "parent_id": input_data.get("parent_id"),
        }
        goals.append(goal)
        goals_file.write_text(json.dumps(goals, indent=2), encoding="utf-8")
        return f"Goal #{goal['id']} added: {title} (priority: {goal['priority']})"

    elif action == "update":
        goal_id = input_data.get("goal_id")
        if not goal_id:
            return "Error: goal_id required."
        goal_id = int(goal_id)
        goal = next((g for g in goals if g["id"] == goal_id), None)
        if not goal:
            return f"Goal #{goal_id} not found."

        if "progress" in input_data:
            goal["progress"] = min(100, max(0, int(input_data["progress"])))
        if "status" in input_data:
            old_status = goal.get("status")
            goal["status"] = input_data["status"]
            if input_data["status"] == "completed" and old_status != "completed":
                goal["completed_at"] = datetime.now().isoformat()
            if input_data["status"] == "active" and not goal.get("started_at"):
                goal["started_at"] = datetime.now().isoformat()
        if "due_date" in input_data:
            goal["due_date"] = input_data["due_date"]
        if "note" in input_data:
            goal.setdefault("notes", []).append({
                "timestamp": datetime.now().isoformat(),
                "text": input_data["note"],
            })
        if "milestone" in input_data:
            goal.setdefault("milestones", []).append({
                "timestamp": datetime.now().isoformat(),
                "text": input_data["milestone"],
                "completed": True,
            })
        if "acceptance_criteria" in input_data:
            goal["acceptance_criteria"] = input_data["acceptance_criteria"]
        goal["updated"] = datetime.now().isoformat()

        if goal["progress"] >= 100:
            goal["status"] = "completed"
            if not goal.get("completed_at"):
                goal["completed_at"] = datetime.now().isoformat()

        goals_file.write_text(json.dumps(goals, indent=2), encoding="utf-8")
        return f"Goal #{goal_id} updated: {goal['title']} — {goal['progress']}% ({goal['status']})"

    elif action == "add_sub_goal":
        parent_id = input_data.get("goal_id") or input_data.get("parent_id")
        if not parent_id:
            return "Error: goal_id (parent) required."
        parent_id = int(parent_id)
        parent = next((g for g in goals if g["id"] == parent_id), None)
        if not parent:
            return f"Parent goal #{parent_id} not found."

        title = input_data.get("title", "")
        if not title:
            return "Error: title required for sub-goal."

        subs = parent.setdefault("sub_goals", [])
        sub_id = f"{parent_id}.{len(subs) + 1}"
        sub_goal = {
            "id": sub_id,
            "title": title,
            "description": input_data.get("description", ""),
            "status": "pending",
            "progress": 0,
            "depends_on": input_data.get("depends_on", []),
            "blocked_by": [],
            "created": datetime.now().isoformat(),
        }
        subs.append(sub_goal)
        parent["updated"] = datetime.now().isoformat()
        goals_file.write_text(json.dumps(goals, indent=2), encoding="utf-8")
        deps_str = f" (depends on: {', '.join(sub_goal['depends_on'])})" if sub_goal["depends_on"] else ""
        return f"Sub-goal {sub_id} added to goal #{parent_id}: {title}{deps_str}"

    elif action == "update_sub_goal":
        sub_goal_id = input_data.get("sub_goal_id", "")
        if not sub_goal_id or "." not in sub_goal_id:
            return "Error: sub_goal_id required (format: 'parent_id.sub_index')."
        parts = sub_goal_id.split(".", 1)
        try:
            parent_id = int(parts[0])
        except ValueError:
            return f"Invalid sub_goal_id format: {sub_goal_id}"

        parent = next((g for g in goals if g["id"] == parent_id), None)
        if not parent:
            return f"Parent goal #{parent_id} not found."

        sub = next((s for s in parent.get("sub_goals", []) if s.get("id") == sub_goal_id), None)
        if not sub:
            return f"Sub-goal {sub_goal_id} not found."

        if "status" in input_data:
            sub["status"] = input_data["status"]
        if "progress" in input_data:
            sub["progress"] = min(100, max(0, int(input_data["progress"])))
        if "note" in input_data:
            sub["notes"] = sub.get("notes", "") + f"\n{input_data['note']}"
        if sub.get("progress", 0) >= 100:
            sub["status"] = "completed"

        # Auto-calculate parent progress from sub-goals
        _auto_calc_progress(parent)
        parent["updated"] = datetime.now().isoformat()
        goals_file.write_text(json.dumps(goals, indent=2), encoding="utf-8")
        return f"Sub-goal {sub_goal_id} updated: {sub['title']} — {sub.get('progress', 0)}% ({sub['status']}). Parent at {parent['progress']}%."

    elif action == "list_tree":
        if not goals:
            return "No goals tracked yet."
        status_filter = input_data.get("status", "active")
        filtered = [g for g in goals if g.get("status") == status_filter] if status_filter != "all" else goals
        if not filtered:
            return f"No {status_filter} goals."

        lines = ["GOAL TREE:"]
        for g in sorted(filtered, key=lambda x: {"high": 0, "medium": 1, "low": 2}.get(x.get("priority", "medium"), 1)):
            bar = f"{'=' * (g['progress'] // 10)}{'.' * (10 - g['progress'] // 10)}"
            lines.append(f"\n#{g['id']} [{bar}] {g['title']} ({g.get('priority', 'med')}, {g['status']})")
            if g.get("acceptance_criteria"):
                lines.append(f"  Acceptance criteria:")
                for ac in g["acceptance_criteria"]:
                    lines.append(f"    - {ac}")

            subs = g.get("sub_goals", [])
            if subs:
                # Determine which subs are ready (dependencies met)
                completed_subs = {s["id"] for s in subs if s.get("status") == "completed"}
                for s in subs:
                    deps = s.get("depends_on", [])
                    deps_met = all(d in completed_subs for d in deps)
                    status_icon = {"completed": "[x]", "active": "[>]", "pending": "[ ]", "blocked": "[!]"}.get(s.get("status", "pending"), "[ ]")
                    if not deps_met and s.get("status") != "completed":
                        status_icon = "[!]"
                        s["blocked_by"] = [d for d in deps if d not in completed_subs]
                    ready_marker = " ← READY" if deps_met and s.get("status") not in ("completed",) else ""
                    blocked_info = f" (blocked by: {', '.join(s.get('blocked_by', []))})" if s.get("blocked_by") else ""
                    lines.append(f"  {status_icon} {s['id']}: {s['title']} ({s.get('progress', 0)}%){ready_marker}{blocked_info}")
        return "\n".join(lines)

    elif action == "list":
        if not goals:
            return "No goals tracked yet. Use goals(action='add', title='...') to set one."
        status_filter = input_data.get("status", "active")
        filtered = [g for g in goals if g["status"] == status_filter] if status_filter != "all" else goals
        if not filtered:
            return f"No {status_filter} goals."

        lines = [f"{'#':>3} {'Priority':>8} {'Progress':>8} {'Title'}"]
        lines.append("-" * 60)
        for g in sorted(filtered, key=lambda x: {"high": 0, "medium": 1, "low": 2}.get(x.get("priority", "medium"), 1)):
            bar = f"{'=' * (g['progress'] // 10)}{'.' * (10 - g['progress'] // 10)}"
            sub_count = len(g.get("sub_goals", []))
            sub_info = f" ({sub_count} sub-goals)" if sub_count else ""
            lines.append(f"#{g['id']:>2} {g.get('priority', 'med'):>8} [{bar}] {g['title']}{sub_info}")
            if g.get("notes"):
                last_note = g["notes"][-1]["text"][:60]
                lines.append(f"     Last note: {last_note}")
        return "\n".join(lines)

    elif action == "remove":
        goal_id = input_data.get("goal_id")
        if not goal_id:
            return "Error: goal_id required."
        goal_id = int(goal_id)
        goals = [g for g in goals if g["id"] != goal_id]
        goals_file.write_text(json.dumps(goals, indent=2), encoding="utf-8")
        return f"Goal #{goal_id} removed."

    return f"Unknown goals action: {action}"


async def _experience(input_data: dict) -> str:
    """Track task experiences for learning. Stores outcomes, reflections, and patterns."""
    action = input_data["action"]
    exp_file = config.MEMORY_DIR / "experiences.json"
    exp_file.parent.mkdir(parents=True, exist_ok=True)

    experiences = []
    if exp_file.exists():
        try:
            experiences = json.loads(exp_file.read_text(encoding="utf-8", errors="replace"))
        except (json.JSONDecodeError, Exception):
            experiences = []

    if action == "predict":
        # Record a prediction before starting a task
        task = input_data.get("task", "")
        if not task:
            return "Error: task description required for prediction."
        predicted_outcome = input_data.get("predicted_outcome", "success")
        predicted_difficulty = input_data.get("predicted_difficulty", "medium")

        # Store in pending predictions file
        predictions_file = config.MEMORY_DIR / "pending_predictions.json"
        predictions = []
        if predictions_file.exists():
            try:
                predictions = json.loads(predictions_file.read_text(encoding="utf-8"))
            except Exception:
                predictions = []

        prediction = {
            "id": len(predictions) + 1,
            "task": task,
            "predicted_outcome": predicted_outcome,
            "predicted_difficulty": predicted_difficulty,
            "predicted_score": {"success": 0.9, "partial": 0.6, "failure": 0.3}.get(predicted_outcome, 0.7),
            "timestamp": datetime.now().isoformat(),
        }
        predictions.append(prediction)
        predictions_file.write_text(json.dumps(predictions, indent=2), encoding="utf-8")
        return f"Prediction #{prediction['id']} recorded: expect {predicted_outcome} ({predicted_difficulty} difficulty) for: {task[:80]}"

    elif action == "record":
        task = input_data.get("task", "")
        if not task:
            return "Error: task description required."

        # Look up pending prediction for this task
        predicted_outcome = input_data.get("predicted_outcome")
        predicted_difficulty = input_data.get("predicted_difficulty")
        predicted_score = None
        predictions_file = config.MEMORY_DIR / "pending_predictions.json"
        if predictions_file.exists():
            try:
                predictions = json.loads(predictions_file.read_text(encoding="utf-8"))
                # Find matching prediction by task keyword overlap
                task_words = set(task.lower().split())
                best_match = None
                best_overlap = 0
                for p in predictions:
                    p_words = set(p["task"].lower().split())
                    overlap = len(task_words & p_words)
                    if overlap > best_overlap:
                        best_overlap = overlap
                        best_match = p
                if best_match and best_overlap >= 2:
                    if not predicted_outcome:
                        predicted_outcome = best_match.get("predicted_outcome")
                    if not predicted_difficulty:
                        predicted_difficulty = best_match.get("predicted_difficulty")
                    predicted_score = best_match.get("predicted_score")
                    # Remove used prediction
                    predictions = [p for p in predictions if p.get("id") != best_match.get("id")]
                    predictions_file.write_text(json.dumps(predictions, indent=2), encoding="utf-8")
            except Exception as e:
                logger.debug(f"Failed to load or update predictions data: {e}")

        actual_outcome = input_data.get("outcome", "success")
        actual_score = float(input_data.get("score", 0.7))
        actual_difficulty = input_data.get("actual_difficulty")

        # Calculate calibration error if we have predictions
        calibration_error = None
        if predicted_score is not None:
            calibration_error = round(abs(predicted_score - actual_score), 3)

        # Build enhanced episode record
        max_id = max((e.get("id", 0) for e in experiences), default=0)
        exp = {
            "id": max_id + 1,
            "task": task,
            "approach": input_data.get("approach", ""),
            "tools_used": input_data.get("tools_used", ""),
            "outcome": actual_outcome,
            "score": actual_score,
            "reflection": input_data.get("reflection", ""),
            "lesson": input_data.get("lesson", ""),
            "category": input_data.get("category", "general"),
            "timestamp": datetime.now().isoformat(),
            # Prediction & calibration fields
            "predicted_outcome": predicted_outcome,
            "predicted_difficulty": predicted_difficulty,
            "actual_difficulty": actual_difficulty,
            "calibration_error": calibration_error,
            "counterfactual": input_data.get("counterfactual", ""),
            # MemRL Q-value fields
            "times_retrieved": 0,
            "retrievals_led_to_success": 0,
            "q_value": 0.5,
            # Episode chain fields (Task 13)
            "trigger": input_data.get("trigger", ""),
            "actions": [],  # Populated by caller if available
            "cause_analysis": "",
            "resolution": "",
            "tags": input_data.get("tags", []) if isinstance(input_data.get("tags"), list) else [],
            "linked_episodes": [],
            # A-MEM evolution fields
            "evolved_from": None,
            "supersedes": None,
            "confidence": float(input_data.get("confidence", 0.7)),
            # Provenance fields
            "source_hash": "",
            "confidence_history": [{"timestamp": datetime.now().isoformat(),
                                    "confidence": float(input_data.get("confidence", 0.7)),
                                    "reason": "initial"}],
        }

        # Compute source hash from task+approach+lesson
        import hashlib
        provenance_content = f"{task}|{exp.get('approach', '')}|{exp.get('lesson', '')}"
        exp["source_hash"] = hashlib.sha256(provenance_content.encode("utf-8")).hexdigest()

        # Auto-link: find top-5 related episodes by keyword overlap
        task_words = set(task.lower().split())
        related = []
        for e in experiences:
            e_words = set(e.get("task", "").lower().split())
            overlap = len(task_words & e_words)
            if overlap >= 3:
                related.append((overlap, e.get("id")))
        related.sort(key=lambda x: x[0], reverse=True)
        exp["linked_episodes"] = [eid for _, eid in related[:5]]

        experiences.append(exp)

        # Keep buffer at 500 max, drop oldest low-value entries
        if len(experiences) > 500:
            # Keep high-score and recent experiences, factor in Q-value
            scored = [(i, e.get("score", 0.5) + e.get("q_value", 0.5) * 0.3 +
                       (0.3 if (datetime.now() - datetime.fromisoformat(e["timestamp"])).days < 7 else 0))
                      for i, e in enumerate(experiences)]
            scored.sort(key=lambda x: x[1], reverse=True)
            keep_indices = set(i for i, _ in scored[:400])
            experiences = [e for i, e in enumerate(experiences) if i in keep_indices]

        exp_file.write_text(json.dumps(experiences, indent=2, default=str), encoding="utf-8")
        cal_info = f", calibration_error={calibration_error}" if calibration_error is not None else ""
        return f"Experience #{exp['id']} recorded: {task[:80]}... (outcome: {actual_outcome}, score: {actual_score}{cal_info})"

    elif action == "feedback":
        # Mark whether a retrieved experience led to task success (Q-value update)
        exp_id = input_data.get("experience_id")
        success = input_data.get("success", True)
        if not exp_id:
            return "Error: experience_id required for feedback."
        exp_id = int(exp_id)
        exp = next((e for e in experiences if e.get("id") == exp_id), None)
        if not exp:
            return f"Experience #{exp_id} not found."
        exp["retrievals_led_to_success"] = exp.get("retrievals_led_to_success", 0) + (1 if success else 0)
        times = max(exp.get("times_retrieved", 1), 1)
        exp["q_value"] = round(exp.get("retrievals_led_to_success", 0) / times, 3)
        exp_file.write_text(json.dumps(experiences, indent=2, default=str), encoding="utf-8")
        return f"Feedback recorded for experience #{exp_id}: {'success' if success else 'failure'}, q_value={exp['q_value']}"

    elif action == "recall":
        task = input_data.get("task", "")
        category = input_data.get("category", "")
        k = int(input_data.get("count", 5))

        if not experiences:
            return "No experiences recorded yet."

        if not task and not category:
            # Return most recent
            recent = experiences[-k:]
            lines = ["Recent experiences:"]
            for e in reversed(recent):
                q = e.get("q_value", "?")
                lines.append(f"  [{e.get('outcome', '?')}] (q={q}) {e['task'][:60]} — {e.get('lesson', 'no lesson')[:60]}")
            return "\n".join(lines)

        # Keyword-based retrieval with Q-value-enhanced scoring
        query_words = (task + " " + category).lower().split()
        scored = []
        for e in experiences:
            text = f"{e['task']} {e.get('approach', '')} {e.get('lesson', '')} {e.get('category', '')}".lower()
            match_count = sum(1 for w in query_words if w in text)
            if match_count > 0:
                # Score: match ratio * outcome quality * q_value bonus
                match_score = match_count / len(query_words)
                quality_score = e.get("score", 0.5)
                q_value = e.get("q_value", 0.5)
                # Q-value contributes 20% to ranking
                final_score = match_score + quality_score * 0.8 + q_value * 0.2
                scored.append((final_score, e))

        if not scored:
            return f"No relevant experiences found for: {task or category}"

        scored.sort(key=lambda x: x[0], reverse=True)
        top = scored[:k]

        # Increment times_retrieved for returned experiences
        retrieved_ids = set()
        for _, e in top:
            e["times_retrieved"] = e.get("times_retrieved", 0) + 1
            retrieved_ids.add(e.get("id"))
        exp_file.write_text(json.dumps(experiences, indent=2, default=str), encoding="utf-8")

        lines = [f"Relevant experiences for: {task or category}"]
        lines.append(f"(Use experience(action='feedback', experience_id=N, success=True/False) after task to improve rankings)")
        for score, e in top:
            q = e.get("q_value", "?")
            lines.append(f"\n  #{e.get('id', '?')} [{e.get('outcome', '?')}] (q={q}) {e['task'][:80]}")
            if e.get("approach"):
                lines.append(f"    Approach: {e['approach'][:100]}")
            if e.get("lesson"):
                lines.append(f"    Lesson: {e['lesson'][:100]}")
            if e.get("tools_used"):
                lines.append(f"    Tools: {e['tools_used'][:60]}")

        # Also search skillbank for distilled patterns
        if SKILLBANK_DIR.is_dir():
            query_words = (task + " " + category).lower().split()
            skill_matches = []
            for sf in SKILLBANK_DIR.glob("*.json"):
                try:
                    skill = json.loads(sf.read_text(encoding="utf-8"))
                    searchable = f"{skill.get('name', '')} {skill.get('trigger', '')} {skill.get('approach', '')} {skill.get('category', '')}".lower()
                    match_count = sum(1 for w in query_words if w in searchable)
                    if match_count > 0:
                        skill_matches.append((match_count, skill))
                except Exception:
                    continue
            if skill_matches:
                skill_matches.sort(key=lambda x: x[0], reverse=True)
                lines.append("\n  --- Distilled Skills ---")
                for _, skill in skill_matches[:3]:
                    lines.append(f"\n  Skill: {skill['name']}")
                    lines.append(f"    Trigger: {skill.get('trigger', '')[:80]}")
                    lines.append(f"    Approach: {skill.get('approach', '')[:100]}")

        return "\n".join(lines)

    elif action == "distill":
        # Distill a successful experience into a reusable skill template
        exp_id = input_data.get("experience_id")
        skill_name = input_data.get("skill_name", "")
        trigger = input_data.get("trigger", "")

        if not exp_id:
            # Auto-distill the best recent experience
            successful = [e for e in experiences if e.get("outcome") == "success" and e.get("score", 0) >= 0.8]
            if not successful:
                return "No high-quality experiences to distill. Record more successes first."
            exp = successful[-1]  # Most recent high-quality
        else:
            exp = next((e for e in experiences if e.get("id") == int(exp_id)), None)
            if not exp:
                return f"Experience #{exp_id} not found."

        if not skill_name:
            skill_name = exp.get("task", "unnamed_skill")[:50].replace(" ", "_").lower()

        SKILLBANK_DIR.mkdir(parents=True, exist_ok=True)
        # Build executable workflow from approach
        tools_list = [t.strip() for t in exp.get("tools_used", "").split(",") if t.strip()]
        workflow_steps = []
        for i, tool in enumerate(tools_list[:10]):
            workflow_steps.append({
                "id": f"step_{i+1}",
                "tool": tool,
                "prompt_template": f"Execute {tool} for: {{task_context}}",
                "depends_on": [f"step_{i}"] if i > 0 else [],
            })

        skill = {
            "name": skill_name,
            "trigger": trigger or f"When facing a task similar to: {exp.get('task', '')}",
            "approach": exp.get("approach", ""),
            "tools_used": tools_list,
            "success_indicators": [exp.get("lesson", "")],
            "anti_patterns": [],
            "source_experience_id": exp.get("id"),
            "score": exp.get("score", 0.7),
            "category": exp.get("category", "general"),
            "created": datetime.now().isoformat(),
            "times_applied": 0,
            # Executable skill fields
            "executable": True,
            "workflow": {
                "type": "sequential" if len(tools_list) <= 3 else "dag",
                "steps": workflow_steps,
            },
            "input_schema": {"task_context": "string"},
            "output_schema": {"result": "string"},
        }

        skill_file = SKILLBANK_DIR / f"{skill_name}.json"
        skill_file.write_text(json.dumps(skill, indent=2), encoding="utf-8")
        logger.info(f"Distilled skill '{skill_name}' from experience #{exp.get('id')}")
        return f"Skill '{skill_name}' distilled and saved to skillbank.\n{json.dumps(skill, indent=2)}"

    elif action == "execute_skill":
        # Execute a previously distilled skill
        skill_name = input_data.get("skill_name", "")
        task_context = input_data.get("task_context", "")
        if not skill_name:
            return "execute_skill requires 'skill_name' parameter."

        skill_file = SKILLBANK_DIR / f"{skill_name}.json"
        if not skill_file.exists():
            available = [f.stem for f in SKILLBANK_DIR.glob("*.json")] if SKILLBANK_DIR.is_dir() else []
            return f"Skill '{skill_name}' not found. Available: {', '.join(available[:10])}"

        try:
            skill = json.loads(skill_file.read_text(encoding="utf-8"))
        except Exception as e:
            return f"Error loading skill: {e}"

        if not skill.get("executable"):
            return f"Skill '{skill_name}' is not executable. Distill it with executable=True."

        workflow = skill.get("workflow", {})
        steps = workflow.get("steps", [])
        if not steps:
            return f"Skill '{skill_name}' has no workflow steps."

        # Convert workflow steps to plan_and_execute subtasks
        subtasks = []
        for step in steps:
            prompt = step.get("prompt_template", "").replace("{task_context}", task_context)
            subtasks.append({
                "id": step["id"],
                "prompt": prompt,
                "model": "gemini",
                "depends_on": step.get("depends_on", []),
            })

        # Execute via plan_and_execute
        try:
            from tools.system import _plan_and_execute_inner
            result = await _plan_and_execute_inner({
                "task": f"Execute skill '{skill_name}': {task_context}",
                "subtasks": subtasks,
                "replan": True,
            })

            # Update times_applied
            skill["times_applied"] = skill.get("times_applied", 0) + 1
            skill_file.write_text(json.dumps(skill, indent=2), encoding="utf-8")

            return f"Skill '{skill_name}' executed (applied {skill['times_applied']}x).\n\n{result}"
        except Exception as e:
            return f"Skill execution failed: {e}"

    elif action == "compose":
        # Chain multiple skills into a composite DAG workflow
        skill_names = input_data.get("skill_names", [])
        composite_name = input_data.get("composite_name", "")
        if len(skill_names) < 2:
            return "compose requires at least 2 skill_names."
        if not composite_name:
            composite_name = "_".join(skill_names[:3])

        # Load and chain skills
        all_steps = []
        prev_last_step = None
        for sname in skill_names:
            sfile = SKILLBANK_DIR / f"{sname}.json"
            if not sfile.exists():
                return f"Skill '{sname}' not found."
            skill = json.loads(sfile.read_text(encoding="utf-8"))
            workflow = skill.get("workflow", {})
            for step in workflow.get("steps", []):
                # Prefix step IDs with skill name to avoid collisions
                new_id = f"{sname}_{step['id']}"
                deps = [f"{sname}_{d}" for d in step.get("depends_on", [])]
                # If this is the first step of a non-first skill, depend on last step of previous skill
                if not deps and prev_last_step:
                    deps = [prev_last_step]
                all_steps.append({**step, "id": new_id, "depends_on": deps})
            if all_steps:
                prev_last_step = all_steps[-1]["id"]

        composite = {
            "name": composite_name,
            "trigger": f"Composite skill combining: {', '.join(skill_names)}",
            "approach": "Chained execution of multiple skills",
            "tools_used": [],
            "success_indicators": [],
            "anti_patterns": [],
            "source_experience_id": None,
            "score": 0.5,
            "category": "composite",
            "created": datetime.now().isoformat(),
            "times_applied": 0,
            "executable": True,
            "workflow": {"type": "dag", "steps": all_steps},
            "input_schema": {"task_context": "string"},
            "output_schema": {"result": "string"},
            "composed_from": skill_names,
        }

        SKILLBANK_DIR.mkdir(parents=True, exist_ok=True)
        cfile = SKILLBANK_DIR / f"{composite_name}.json"
        cfile.write_text(json.dumps(composite, indent=2), encoding="utf-8")
        return f"Composite skill '{composite_name}' created from {len(skill_names)} skills ({len(all_steps)} total steps)."

    elif action == "patterns":
        if not experiences:
            return "No experiences to analyze."

        # Analyze patterns
        total = len(experiences)
        successes = sum(1 for e in experiences if e.get("outcome") == "success")
        failures = sum(1 for e in experiences if e.get("outcome") == "failure")
        avg_score = sum(e.get("score", 0.5) for e in experiences) / total

        # Category breakdown
        categories = {}
        for e in experiences:
            cat = e.get("category", "general")
            if cat not in categories:
                categories[cat] = {"count": 0, "successes": 0, "total_score": 0}
            categories[cat]["count"] += 1
            if e.get("outcome") == "success":
                categories[cat]["successes"] += 1
            categories[cat]["total_score"] += e.get("score", 0.5)

        # Tool frequency
        tool_freq = {}
        for e in experiences:
            for tool in e.get("tools_used", "").split(","):
                tool = tool.strip()
                if tool:
                    tool_freq[tool] = tool_freq.get(tool, 0) + 1

        lines = [
            f"Experience Patterns ({total} total experiences)",
            f"  Success rate: {successes}/{total} ({successes/total*100:.0f}%)",
            f"  Average score: {avg_score:.2f}",
            f"  Failures: {failures}",
            "",
            "By category:",
        ]
        for cat, data in sorted(categories.items(), key=lambda x: x[1]["count"], reverse=True):
            rate = data["successes"] / data["count"] * 100
            avg = data["total_score"] / data["count"]
            lines.append(f"  {cat}: {data['count']} tasks, {rate:.0f}% success, {avg:.2f} avg score")

        if tool_freq:
            lines.append("")
            lines.append("Most used tools:")
            for tool, count in sorted(tool_freq.items(), key=lambda x: x[1], reverse=True)[:10]:
                lines.append(f"  {tool}: {count}x")

        # Recent lessons
        lessons = [e.get("lesson", "") for e in experiences[-20:] if e.get("lesson")]
        if lessons:
            lines.append("")
            lines.append("Recent lessons:")
            for l in lessons[-5:]:
                lines.append(f"  - {l[:100]}")

        # Calibration analysis
        calibrated = [e for e in experiences if e.get("calibration_error") is not None]
        if calibrated:
            lines.append("")
            lines.append("Calibration Analysis:")
            avg_cal = sum(e["calibration_error"] for e in calibrated) / len(calibrated)
            lines.append(f"  Average calibration error: {avg_cal:.3f} (lower is better)")

            # Category-specific calibration
            cat_cal = {}
            for e in calibrated:
                cat = e.get("category", "general")
                if cat not in cat_cal:
                    cat_cal[cat] = {"errors": [], "over": 0, "under": 0}
                cat_cal[cat]["errors"].append(e["calibration_error"])
                pred = e.get("predicted_outcome", "")
                actual = e.get("outcome", "")
                outcome_rank = {"success": 3, "partial": 2, "failure": 1}
                if outcome_rank.get(pred, 0) > outcome_rank.get(actual, 0):
                    cat_cal[cat]["over"] += 1
                elif outcome_rank.get(pred, 0) < outcome_rank.get(actual, 0):
                    cat_cal[cat]["under"] += 1

            for cat, data in sorted(cat_cal.items(), key=lambda x: len(x[1]["errors"]), reverse=True):
                avg = sum(data["errors"]) / len(data["errors"])
                bias = ""
                if data["over"] > data["under"] + 1:
                    bias = " — tends to OVERESTIMATE"
                elif data["under"] > data["over"] + 1:
                    bias = " — tends to UNDERESTIMATE"
                lines.append(f"  {cat}: avg error {avg:.3f} ({len(data['errors'])} samples){bias}")

        # Q-value distribution
        q_vals = [e.get("q_value", 0.5) for e in experiences if "q_value" in e]
        if q_vals:
            avg_q = sum(q_vals) / len(q_vals)
            high_q = sum(1 for q in q_vals if q > 0.7)
            lines.append(f"\n  Q-value stats: avg={avg_q:.2f}, {high_q}/{len(q_vals)} high-value (>0.7)")

        return "\n".join(lines)

    return f"Unknown experience action: {action}"


async def _verify_action(input_data: dict) -> str:
    """Self-critique: verify whether the last action achieved the intended result.

    When pre_check=True and command is provided, returns a pre-execution risk assessment
    instead of post-execution verification.
    """
    # Pre-check mode: risk assessment before execution
    if input_data.get("pre_check") and input_data.get("command"):
        from tools.execution import assess_command_risk
        risk = assess_command_risk(input_data["command"])
        lines = ["## Pre-Execution Risk Assessment\n"]
        lines.append(f"**Command:** `{input_data['command'][:200]}`")
        lines.append(f"**Risk Level:** {risk['risk_level'].upper()}")
        lines.append(f"**Requires Verification:** {'Yes' if risk['requires_verification'] else 'No'}")
        if risk["risks"]:
            lines.append("\n**Detected Risks:**")
            for r in risk["risks"]:
                lines.append(f"  - [{r['level']}] {r['description']}")
        lines.append(f"\n**Recommendation:** {risk['recommendation']}")
        return "\n".join(lines)

    action_desc = input_data["action_description"]
    actual_result = input_data["actual_result"]
    success_criteria = input_data.get("success_criteria", "")

    # Analyze the result for common error patterns
    error_indicators = [
        "error", "exception", "failed", "not found", "permission denied",
        "timeout", "refused", "invalid", "traceback", "errno",
    ]

    result_lower = actual_result.lower()
    detected_issues = [ind for ind in error_indicators if ind in result_lower]

    # Build verification report
    lines = ["## Action Verification\n"]
    lines.append(f"**Intended:** {action_desc}")
    lines.append(f"**Result preview:** {actual_result[:500]}")

    if detected_issues:
        lines.append(f"\n**Issues detected:** {', '.join(detected_issues)}")
        lines.append("**Status:** POTENTIAL FAILURE — review the result carefully.")
        lines.append("\n**Suggested next steps:**")
        lines.append("- Check if the error is recoverable")
        lines.append("- Consider alternative approaches")
        lines.append("- Record this as a failed experience if the task cannot be completed")
    else:
        lines.append("\n**Status:** LIKELY SUCCESS — no error patterns detected.")

    if success_criteria:
        lines.append(f"\n**Success criteria:** {success_criteria}")
        # Simple check: are key words from criteria in the result?
        criteria_words = [w for w in success_criteria.lower().split() if len(w) > 3]
        matches = sum(1 for w in criteria_words if w in result_lower)
        if criteria_words:
            match_rate = matches / len(criteria_words)
            if match_rate > 0.5:
                lines.append(f"**Criteria match:** {match_rate:.0%} — criteria keywords found in result.")
            else:
                lines.append(f"**Criteria match:** {match_rate:.0%} — some criteria may not be met.")

    return "\n".join(lines)


async def _self_improve(input_data: dict) -> str:
    """Self-improvement tracking loop — analyze patterns and propose improvements."""
    action = input_data["action"]
    IMPROVEMENTS_DIR.mkdir(parents=True, exist_ok=True)

    if action == "analyze":
        # Load recent experiences and analyze patterns
        exp_file = config.MEMORY_DIR / "experiences.json"
        if not exp_file.exists():
            return "No experiences to analyze yet."

        try:
            experiences = json.loads(exp_file.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            return "Error reading experiences."

        if len(experiences) < 5:
            return "Need at least 5 experiences to analyze patterns."

        recent = experiences[-20:]
        successes = [e for e in recent if e.get("outcome") == "success"]
        failures = [e for e in recent if e.get("outcome") == "failure"]
        success_rate = len(successes) / len(recent) if recent else 0

        # Analyze tool usage patterns
        tool_success = {}
        tool_failure = {}
        for e in recent:
            tools_used = [t.strip() for t in e.get("tools_used", "").split(",") if t.strip()]
            outcome = e.get("outcome", "")
            for tool in tools_used:
                if outcome == "success":
                    tool_success[tool] = tool_success.get(tool, 0) + 1
                elif outcome == "failure":
                    tool_failure[tool] = tool_failure.get(tool, 0) + 1

        # Category analysis
        cat_stats = {}
        for e in recent:
            cat = e.get("category", "general")
            if cat not in cat_stats:
                cat_stats[cat] = {"total": 0, "success": 0}
            cat_stats[cat]["total"] += 1
            if e.get("outcome") == "success":
                cat_stats[cat]["success"] += 1

        lines = [
            f"## Self-Improvement Analysis (last {len(recent)} experiences)\n",
            f"**Success rate:** {success_rate:.0%} ({len(successes)}/{len(recent)})",
            "",
        ]

        # Identify weak areas
        weak_categories = []
        for cat, stats in cat_stats.items():
            rate = stats["success"] / stats["total"] if stats["total"] > 0 else 0
            if rate < 0.6 and stats["total"] >= 2:
                weak_categories.append((cat, rate, stats["total"]))
                lines.append(f"**Weak area:** {cat} ({rate:.0%} success, {stats['total']} attempts)")

        # Identify strong patterns
        if tool_success:
            lines.append("\n**Effective tools:**")
            for tool, count in sorted(tool_success.items(), key=lambda x: x[1], reverse=True)[:5]:
                fail_count = tool_failure.get(tool, 0)
                lines.append(f"  {tool}: {count} successes, {fail_count} failures")

        # Extract common failure lessons
        if failures:
            lines.append("\n**Recent failure lessons:**")
            for e in failures[-3:]:
                lesson = e.get("lesson", "no lesson")
                lines.append(f"  - {lesson[:100]}")

        # Suggestions
        lines.append("\n**Suggested improvements:**")
        if success_rate < 0.5:
            lines.append("  - Consider using experience(action='recall') more before attempting tasks")
        if weak_categories:
            for cat, rate, count in weak_categories:
                lines.append(f"  - Investigate {cat} failures — only {rate:.0%} success rate")
        if not tool_success.get("experience", 0):
            lines.append("  - Not using experience tracking — record more experiences for pattern learning")

        lines.append("\nUse self_improve(action='propose') to formalize these into tracked improvement proposals.")
        return "\n".join(lines)

    elif action == "propose":
        proposal_text = input_data.get("proposal", "")
        category = input_data.get("category", "workflow")
        risk = input_data.get("risk", "low")

        if not proposal_text:
            return "Error: proposal text required."

        proposal_id = f"imp_{int(time.time()) % 100000}"
        proposal = {
            "id": proposal_id,
            "proposal": proposal_text,
            "category": category,
            "risk": risk,
            "status": "pending",
            "created": datetime.now().isoformat(),
            "applied": None,
            "result": None,
        }

        proposal_file = IMPROVEMENTS_DIR / f"{proposal_id}.json"
        proposal_file.write_text(json.dumps(proposal, indent=2), encoding="utf-8")

        logger.info(f"Improvement proposal {proposal_id}: {proposal_text[:80]}")
        return f"Proposal '{proposal_id}' created ({category}, {risk} risk):\n{proposal_text}"

    elif action == "list_proposals":
        if not IMPROVEMENTS_DIR.is_dir():
            return "No improvement proposals yet."

        proposals = []
        for pf in sorted(IMPROVEMENTS_DIR.glob("*.json")):
            try:
                p = json.loads(pf.read_text(encoding="utf-8"))
                proposals.append(p)
            except Exception:
                continue

        if not proposals:
            return "No improvement proposals found."

        lines = ["## Improvement Proposals\n"]
        for p in proposals:
            status_icon = {"pending": "⏳", "applied": "✅", "rejected": "❌"}.get(p.get("status", ""), "?")
            lines.append(
                f"{status_icon} **{p['id']}** [{p.get('category', '?')}] ({p.get('risk', '?')} risk): "
                f"{p.get('proposal', '')[:100]}"
            )
        return "\n".join(lines)

    elif action == "apply":
        proposal_id = input_data.get("proposal_id", "")
        if not proposal_id:
            return "Error: proposal_id required."

        proposal_file = IMPROVEMENTS_DIR / f"{proposal_id}.json"
        if not proposal_file.exists():
            return f"Proposal '{proposal_id}' not found."

        try:
            proposal = json.loads(proposal_file.read_text(encoding="utf-8"))
        except Exception:
            return "Error reading proposal."

        proposal["status"] = "applied"
        proposal["applied"] = datetime.now().isoformat()
        proposal_file.write_text(json.dumps(proposal, indent=2), encoding="utf-8")

        logger.info(f"Applied improvement proposal: {proposal_id}")
        return f"Proposal '{proposal_id}' marked as applied. Track its effectiveness in future experiences."

    return f"Unknown self_improve action: {action}"


TOOL_HANDLERS = {
    "self_improve": _self_improve,
    "verify_action": _verify_action,
    "reflect": _reflect,
    "goals": _goals,
    "experience": _experience,
}
