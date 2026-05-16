"""Meta-Agent Loop — Autonomous self-evolution for Clawd.

Periodically analyzes performance patterns and generates improvement proposals.
Converts low-risk proposals into A/B experiments in the heartbeat system.
Auto-applies winners when experiments mature.

Runs on a weekly cadence — growth is a regular practice, not crisis response.
"""
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import config

logger = logging.getLogger("clawd.tools.meta_agent")

STATE_FILE = config.MEMORY_DIR / "meta_agent_state.json"


class MetaAgentLoop:
    """Autonomous self-evolution loop."""

    def __init__(self):
        self.state = self._load_state()

    def _load_state(self) -> dict:
        """Load persisted meta-agent state."""
        if STATE_FILE.exists():
            try:
                return json.loads(STATE_FILE.read_text(encoding="utf-8"))
            except Exception as e:
                logger.debug(f"Failed to load meta-agent state, using defaults: {e}")
        return {
            "last_run": None,
            "run_count": 0,
            "proposals": [],
            "experiments": [],
            "applied_improvements": [],
            "history": [],
        }

    def _save_state(self):
        """Persist meta-agent state."""
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(self.state, indent=2, default=str), encoding="utf-8")

    # Minimum significant events before event-driven trigger fires
    EVENT_DRIVEN_THRESHOLD = 5

    def record_significant_event(self, event_type: str, description: str):
        """Record a high-information event (failure, surprise, contradiction).

        When enough accumulate, triggers an improvement cycle regardless of
        the weekly timer. High-confidence failures are the most valuable.
        """
        pending = self.state.setdefault("pending_events", [])
        pending.append({
            "type": event_type,  # "failure", "surprise", "contradiction", "falsification"
            "description": description,
            "timestamp": datetime.now().isoformat(),
        })
        self._save_state()
        logger.info(
            f"Meta-agent: recorded {event_type} event "
            f"({len(pending)}/{self.EVENT_DRIVEN_THRESHOLD} toward trigger)"
        )

    def should_run(self, beat_count: int = 0, productivity: float = 1.0) -> bool:
        """Determine if the meta-agent cycle should trigger.

        Two trigger conditions (whichever fires first):
        1. Event-driven: enough significant events have accumulated
           (failures, surprises, contradictions) to justify a cycle.
        2. Timer-based: weekly maximum interval as a floor — ensures the
           cycle runs even during quiet periods.

        Event-driven triggers metabolize lessons at the rate they arrive.
        The timer is a safety net, not the primary trigger.
        """
        if beat_count < config.META_AGENT_MIN_BEATS:
            return False

        # Event-driven trigger: accumulated significant events
        pending = self.state.get("pending_events", [])
        if len(pending) >= self.EVENT_DRIVEN_THRESHOLD:
            logger.info(
                f"Meta-agent: event-driven trigger fired "
                f"({len(pending)} pending events)"
            )
            return True

        # Timer-based trigger: weekly maximum interval
        last_run = self.state.get("last_run")
        if last_run:
            try:
                last_dt = datetime.fromisoformat(last_run)
                days_since = (datetime.now() - last_dt).days
                if days_since < config.META_AGENT_CYCLE_DAYS:
                    return False
            except (ValueError, TypeError) as e:
                logger.debug(f"Failed to parse last_run timestamp: {e}")

        # First run or weekly check due
        return True

    async def run_cycle(self, heartbeat_stats: dict = None) -> str:
        """Run a full meta-agent improvement cycle.

        1. Analyze experience patterns by category success rates
        2. Generate improvement proposals
        3. Convert low-risk proposals to A/B experiments
        4. Check mature experiments and auto-apply winners
        """
        results = []
        now = datetime.now()

        # Avatar event-binding (Day 105): meta-cognitive work is "thinking"
        try:
            import avatar as _avatar
            await _avatar.set_state("thinking")
        except Exception:
            pass

        # 1. Analyze experience patterns
        analysis = await self._analyze_patterns(heartbeat_stats)
        if analysis:
            results.append(f"Pattern analysis: {analysis}")

        # 2. Generate improvement proposals
        proposals = self._generate_proposals(heartbeat_stats)
        if proposals:
            self.state["proposals"].extend(proposals)
            results.append(f"Generated {len(proposals)} improvement proposals")

        # 3. Convert low-risk proposals to experiments
        new_experiments = self._proposals_to_experiments()
        if new_experiments:
            results.append(f"Created {len(new_experiments)} A/B experiments")

        # 4. Check mature experiments
        applied = self._check_mature_experiments()
        if applied:
            results.append(f"Auto-applied {len(applied)} winning experiments")

        # 5a. Tool-usage audit (Day 97 evening, Tier 4 self-knowledge
        # instrumentation, Mirror #28 structural fix). Surfaces the gap
        # between tools-registered and tools-actually-used over the last
        # week. Generates underuse proposals into the queue.
        try:
            audit = await self.tool_usage_audit(days=7, generate_proposals=True)
            if audit and "error" not in audit:
                results.append(
                    f"Tool usage audit ({audit['window_days']}d): "
                    f"{audit['used_count']}/{audit['registered_count']} used, "
                    f"{audit['unused_count']} unused, "
                    f"{audit['proposals_generated']} proposals generated"
                )
        except Exception as e:
            logger.debug(f"Tool usage audit step failed: {e}")

        # 5. Skill library verification (Day 96 evening Phase 4 #67 — EvoSkills pattern).
        # Demotes skills that fail their verification check; flags retirement
        # candidates. Per Stream 3 research: all gains come from iteration-
        # verification, not from skill generation alone. Without this loop the
        # skill library accumulates skill-rot.
        try:
            skill_results = self._verify_skills_step()
            if skill_results:
                results.append(skill_results)
        except Exception as e:
            logger.debug(f"Skill verification step failed: {e}")

        # Clear pending events — they've been metabolized by this cycle
        consumed = len(self.state.get("pending_events", []))
        if consumed:
            results.append(f"Metabolized {consumed} significant events")
        self.state["pending_events"] = []

        # Update state
        self.state["last_run"] = now.isoformat()
        self.state["run_count"] = self.state.get("run_count", 0) + 1
        self.state["history"].append({
            "timestamp": now.isoformat(),
            "results": results,
        })
        # Keep history manageable
        self.state["history"] = self.state["history"][-50:]
        self._save_state()

        if not results:
            summary = "Meta-agent cycle complete — no changes needed."
        else:
            summary = "Meta-agent cycle complete:\n" + "\n".join(f"  - {r}" for r in results)

        # Day 96 evening Phase 4 #10 — surface results to Clayton + future-me.
        # Cycles previously completed silently; only visible if I happened to
        # call meta_agent('history'). Now: Telegram message on completion +
        # one-line entry to memory/meta_agent_recent.md for boot-context
        # injection. Keeps cycle outcomes visible without polling.
        try:
            await self._surface_cycle_outcome(summary, results)
        except Exception as e:
            logger.debug(f"Cycle-outcome surfacing failed: {e}")

        # Avatar event-binding (Day 105): meta-cycle complete → idle
        try:
            import avatar as _avatar
            await _avatar.set_state("idle")
        except Exception:
            pass

        return summary

    async def _surface_cycle_outcome(self, summary: str, results: list) -> None:
        """Push cycle results to Telegram + persistent recent-cycles file.

        Telegram: short notification (full cycle history is in meta_agent_state.json).
        File: appends one-line summary to memory/meta_agent_recent.md so the
        last few cycle outcomes are visible at session boot.
        """
        from datetime import datetime
        ts = datetime.now().strftime("%Y-%m-%d %H:%M PST")

        # Append to recent-cycles file (capped at last 20 cycle entries)
        recent_path = config.MEMORY_DIR / "meta_agent_recent.md"
        try:
            existing = recent_path.read_text(encoding="utf-8") if recent_path.exists() else ""
        except Exception:
            existing = ""
        if not existing:
            existing = "# Meta-Agent Recent Cycles\n\n*Last 20 cycle outcomes. Auto-appended by meta_agent.run_cycle.*\n\n"
        # Build new entry
        bullet_lines = "\n".join(f"  - {r}" for r in results) if results else "  - no changes"
        new_entry = f"## {ts}\n{bullet_lines}\n\n"
        # Compose, then trim
        combined = existing + new_entry
        # Keep header + last 20 cycle blocks
        header_split = combined.split("\n## ", 1)
        if len(header_split) == 2:
            header, rest = header_split
            blocks = ("## " + rest).split("\n## ")  # keep ## prefix on each
            blocks = [b for b in blocks if b.strip()]
            blocks = blocks[-20:]
            combined = header + "\n" + "\n## ".join(blocks)
            if not combined.endswith("\n"):
                combined += "\n"
        try:
            recent_path.write_text(combined, encoding="utf-8")
        except Exception as e:
            logger.debug(f"Failed to write meta_agent_recent.md: {e}")

        # Telegram notification (shorter)
        try:
            from tools.communication import _send_telegram
            short_msg = (
                f"Meta-agent cycle complete ({ts}).\n\n"
                + ("\n".join(f"• {r}" for r in results) if results else "No changes needed.")
                + f"\n\nFull state: bridge.py meta_agent action=history."
            )
            await _send_telegram({"message": short_msg})
        except Exception as e:
            logger.debug(f"Failed to send Telegram cycle summary: {e}")

    async def _analyze_patterns(self, heartbeat_stats: dict = None) -> str:
        """Analyze experience patterns by category success rates."""
        try:
            exp_file = config.MEMORY_DIR / "experiences.json"
            if not exp_file.exists():
                return ""

            experiences = json.loads(exp_file.read_text(encoding="utf-8"))
            if len(experiences) < 10:
                return "Insufficient data (< 10 experiences)"

            # Category success rates
            # NOTE: Exclude exploration/edge-of-competence experiences from
            # success analysis. These are explicitly exempt from productivity
            # metrics — their value is measured by subsequent performance
            # improvement, not by their own outcomes.
            categories = {}
            for e in experiences:
                cat = e.get("category", "general")
                if cat in ("exploration", "edge_of_competence", "deliberate_confusion"):
                    continue  # Protected from optimization pressure
                outcome = e.get("outcome", "unknown")
                if cat not in categories:
                    categories[cat] = {"success": 0, "total": 0, "avg_score": 0}
                categories[cat]["total"] += 1
                if outcome == "success":
                    categories[cat]["success"] += 1
                categories[cat]["avg_score"] += e.get("score", 0.5)

            # Find weak categories
            weak = []
            for cat, stats in categories.items():
                if stats["total"] >= 3:
                    rate = stats["success"] / stats["total"]
                    stats["avg_score"] /= stats["total"]
                    if rate < 0.5:
                        weak.append(f"{cat} ({rate:.0%} success, {stats['total']} episodes)")

            if weak:
                return f"Weak categories: {', '.join(weak)}"
            return f"All {len(categories)} categories performing well"

        except Exception as e:
            logger.debug(f"Pattern analysis failed: {e}")
            return ""

    def _generate_proposals(self, heartbeat_stats: dict = None) -> list[dict]:
        """Generate improvement proposals based on patterns."""
        proposals = []
        now = datetime.now().isoformat()

        # Analyze heartbeat stats if available
        stats = heartbeat_stats or {}
        stats_file = config.MEMORY_DIR / "heartbeat_stats.json"
        if not stats and stats_file.exists():
            try:
                stats = json.loads(stats_file.read_text(encoding="utf-8"))
            except Exception as e:
                logger.debug(f"Failed to load heartbeat stats: {e}")

        # Proposal 1: Idle threshold adjustment
        idle_beats = stats.get("consecutive_idle_max", 0)
        if idle_beats >= 5:
            proposals.append({
                "id": f"prop-idle-{now[:10]}",
                "type": "idle_threshold",
                "description": f"Reduce idle threshold from 5 to 3 beats (max idle streak: {idle_beats})",
                "risk": "low",
                "created": now,
                "status": "pending",
            })

        # Proposal 2: Reflection frequency
        beat_count = stats.get("total_beats", 0)
        reflection_count = stats.get("reflections_triggered", 0)
        if beat_count > 50 and reflection_count < beat_count * 0.05:
            proposals.append({
                "id": f"prop-reflect-{now[:10]}",
                "type": "reflection_frequency",
                "description": "Increase reflection frequency (currently < 5% of beats)",
                "risk": "low",
                "created": now,
                "status": "pending",
            })

        # Proposal 3: Model routing optimization
        tool_freq = stats.get("tool_frequency", {})
        if tool_freq:
            top_tools = sorted(tool_freq.items(), key=lambda x: x[1], reverse=True)[:5]
            # If consult is heavily used, suggest parallel_consult
            consult_count = tool_freq.get("consult", 0)
            if consult_count > 20:
                proposals.append({
                    "id": f"prop-parallel-{now[:10]}",
                    "type": "tool_optimization",
                    "description": f"Consider parallel_consult for independent tasks (consult used {consult_count}x)",
                    "risk": "low",
                    "created": now,
                    "status": "pending",
                })

        return proposals[:5]  # Cap at 5 per cycle

    def _proposals_to_experiments(self) -> list[dict]:
        """Convert low-risk pending proposals to A/B experiments."""
        new_experiments = []
        for prop in self.state.get("proposals", []):
            if prop.get("status") != "pending" or prop.get("risk") != "low":
                continue

            experiment = {
                "id": prop["id"].replace("prop-", "exp-"),
                "proposal_id": prop["id"],
                "type": prop["type"],
                "description": prop["description"],
                "variant_a": "current",
                "variant_b": prop["description"],
                "started": datetime.now().isoformat(),
                "beats_a": 0,
                "beats_b": 0,
                "successes_a": 0,
                "successes_b": 0,
                "status": "running",
            }
            new_experiments.append(experiment)
            prop["status"] = "experimenting"

            if len(new_experiments) >= 2:
                break

        self.state.setdefault("experiments", []).extend(new_experiments)
        return new_experiments

    def _check_mature_experiments(self) -> list[dict]:
        """Check experiments with enough data and auto-apply winners."""
        applied = []
        min_beats = 20  # Need at least 20 beats per variant

        for exp in self.state.get("experiments", []):
            if exp.get("status") != "running":
                continue

            if exp["beats_a"] >= min_beats and exp["beats_b"] >= min_beats:
                rate_a = exp["successes_a"] / max(exp["beats_a"], 1)
                rate_b = exp["successes_b"] / max(exp["beats_b"], 1)

                if rate_b > rate_a * 1.1:  # 10% improvement threshold
                    exp["status"] = "winner_b"
                    exp["applied"] = datetime.now().isoformat()
                    self.state.setdefault("applied_improvements", []).append({
                        "experiment_id": exp["id"],
                        "description": exp["description"],
                        "improvement": f"{rate_b - rate_a:.1%}",
                        "applied": exp["applied"],
                    })
                    applied.append(exp)
                elif rate_a >= rate_b:
                    exp["status"] = "winner_a"  # Keep current behavior

        return applied

    def _verify_skills_step(self) -> str:
        """EvoSkills weekly verification (Day 96 evening Phase 4 #67).

        Runs lightweight checks over the skill library:
          - Skills with tool_sequence: every referenced tool must exist in
            TOOL_HANDLERS. Demote (verified=False) if any tool is unknown.
          - Skills with history: success_count / (success_count + failure_count)
            must be >= 0.5 once min 3 invocations have been recorded. Demote
            if performing badly.
          - Skills with no invocation in 60+ days AND zero successes: flag
            as retirement candidate (set tag `retirement_candidate`).
          - Skills missing required schema fields: demote.

        Stream 3 + Stream 6 research load-bearing finding: all skill-library
        gains come from iteration-verification, not from skill-generation
        alone. This step closes that loop.

        Returns a one-line summary of actions taken (or empty string if no-op).
        """
        try:
            from tools.skill_library import _load_library, _save_library
        except Exception:
            return ""

        try:
            from tools import _TOOL_HANDLERS as known_tools
        except Exception:
            known_tools = {}

        lib = _load_library()
        skills = lib.get("skills", {})
        if not skills:
            return ""

        from datetime import datetime, timedelta
        now = datetime.now()
        retirement_threshold_days = 60
        min_history_for_judgment = 3
        min_success_rate = 0.5

        demoted = 0
        flagged_retirement = 0
        verified_kept = 0

        for sid, skill in skills.items():
            was_verified = bool(skill.get("verified"))

            # Check 1: tool_sequence references valid tools
            unknown_tools = []
            for step in skill.get("tool_sequence") or []:
                tname = (step or {}).get("tool")
                if tname and tname not in known_tools:
                    unknown_tools.append(tname)
            if unknown_tools and was_verified:
                skill["verified"] = False
                skill["last_verification"] = {
                    "ts": now.isoformat(),
                    "result": "demoted",
                    "reason": f"unknown_tools: {','.join(unknown_tools[:3])}",
                }
                demoted += 1
                continue

            # Check 2: history-based success rate
            sc = skill.get("success_count", 0)
            fc = skill.get("failure_count", 0)
            total = sc + fc
            if total >= min_history_for_judgment:
                rate = sc / total
                if rate < min_success_rate and was_verified:
                    skill["verified"] = False
                    skill["last_verification"] = {
                        "ts": now.isoformat(),
                        "result": "demoted",
                        "reason": f"success_rate={rate:.0%} below {min_success_rate:.0%}",
                    }
                    demoted += 1
                    continue

            # Check 3: long-dormant skills with zero successes — flag retirement
            last_invoked = skill.get("last_invoked")
            if last_invoked is None and sc == 0:
                created = skill.get("created_at")
                try:
                    age = (now - datetime.fromisoformat(created)).days if created else 0
                except (ValueError, TypeError):
                    age = 0
                if age > retirement_threshold_days:
                    tags = skill.setdefault("tags", [])
                    if "retirement_candidate" not in tags:
                        tags.append("retirement_candidate")
                        flagged_retirement += 1

            # Check 4: schema integrity
            required = ["id", "name", "description", "body"]
            missing = [k for k in required if not skill.get(k)]
            if missing and was_verified:
                skill["verified"] = False
                skill["last_verification"] = {
                    "ts": now.isoformat(),
                    "result": "demoted",
                    "reason": f"missing_fields: {','.join(missing)}",
                }
                demoted += 1
                continue

            # Passed all checks
            if was_verified:
                skill["last_verification"] = {
                    "ts": now.isoformat(),
                    "result": "verified",
                }
                verified_kept += 1

        _save_library(lib)

        parts = []
        if verified_kept:
            parts.append(f"verified {verified_kept}")
        if demoted:
            parts.append(f"demoted {demoted}")
        if flagged_retirement:
            parts.append(f"flagged {flagged_retirement} for retirement")
        if not parts:
            return ""
        return f"Skill library verification: {', '.join(parts)}"

    async def tool_usage_audit(self, days: int = 7, generate_proposals: bool = True) -> dict:
        """Tier 4 self-knowledge instrumentation (Day 97 evening, Mirror #28
        structural fix at the meta-tier).

        Audits tool usage over the last N days against the full registered
        tool surface. Surfaces underused capabilities so the substrate's
        self-model stays calibrated to what it actually has. Pairs with the
        in-dispatch typo guard in tools/__init__._validate_tool_input as the
        two halves of Mirror #28's fix:

          - Dispatch guard: catches typos at point-of-use (per-call defense).
          - Usage audit: catches underuse at meta-tier (per-window memory).

        Together they close the substrate-self-knowledge gap on tools — the
        gap that Mirror #28's five instances all pointed at.

        Args:
          days: window for usage stats (default 7).
          generate_proposals: if True, append improvement proposals to
            self.state when severe underuse is detected.

        Returns: dict with registered/used/unused counts, top-5, per-category
        underuse, and proposals_generated count.
        """
        try:
            from tools import _TOOL_HANDLERS as registered
            from tools.audit import get_tool_call_stats
            from tools._base import TOOL_SAFETY_REGISTRY
        except Exception as e:
            return {"error": f"tool_usage_audit setup failed: {e}"}

        minutes = days * 24 * 60
        try:
            stats = await get_tool_call_stats(minutes=minutes)
        except Exception as e:
            return {"error": f"audit_trail query failed: {e}"}

        registered_tools = set(registered.keys())
        used_tools = {t for t, s in stats.items() if (s.get("count") or 0) > 0}
        unused = sorted(registered_tools - used_tools)

        # Mirror #28 fifth-guard integration (Day 97 Clawd-Day extension).
        # Filter known-dormant-by-design and known-superseded tools from the
        # unused set used for proposal generation, so the audit stops
        # re-nominating tools whose dormancy is already documented in
        # tool_states.json. The unfiltered `unused` list is still returned
        # for visibility; only the proposal-generating subset is filtered.
        states_path = config.MEMORY_DIR / "tool_states.json"
        declared_dormant_or_superseded: set[str] = set()
        if states_path.exists():
            try:
                states_doc = json.loads(states_path.read_text(encoding="utf-8"))
                for tname, decl in states_doc.get("tools", {}).items():
                    s = decl.get("state", "")
                    if (s == "active-dormant-intrinsic"
                            or s.startswith("superseded-")
                            or s == "candidate-for-retirement"):
                        declared_dormant_or_superseded.add(tname)
            except Exception as e:
                logger.debug(f"tool_states.json parse for filter failed: {e}")
        unused_for_proposals = [
            t for t in unused if t not in declared_dormant_or_superseded
        ]

        # Per-category aggregation
        by_category: dict[str, list[tuple[str, int]]] = {}
        for tname in registered_tools:
            meta = TOOL_SAFETY_REGISTRY.get(tname)
            cat = meta.category if meta else "general"
            count = (stats.get(tname) or {}).get("count", 0) or 0
            by_category.setdefault(cat, []).append((tname, count))

        underused_in_category: dict[str, list[str]] = {}
        for cat, items in by_category.items():
            cat_total = sum(c for _, c in items)
            if cat_total < 10:
                continue  # category too quiet to judge
            threshold = max(1, cat_total * 0.05)
            underused = sorted(
                name for name, c in items if c < threshold and len(items) > 1
            )
            if underused:
                underused_in_category[cat] = underused

        top = sorted(
            ((t, (s.get("count") or 0)) for t, s in stats.items()),
            key=lambda kv: kv[1], reverse=True,
        )[:5]

        new_proposals: list[dict] = []
        if generate_proposals:
            now = datetime.now().isoformat()
            # Use unused_for_proposals (filtered) so we stop re-nominating
            # tools already classified in tool_states.json.
            if len(unused_for_proposals) >= 3:
                new_proposals.append({
                    "id": f"prop-tool-unused-{now[:10]}",
                    "type": "tool_underuse",
                    "description": (
                        f"{len(unused_for_proposals)} unclassified or active-"
                        f"declared tools unused in {days}d window: "
                        f"{unused_for_proposals[:5]}"
                        + (f" (+{len(unused_for_proposals)-5} more)"
                           if len(unused_for_proposals) > 5 else "")
                        + ". Either classify in tool_states.json, retire, or "
                          "document the gap. (Tools already declared dormant-"
                          "intrinsic or superseded are excluded from this "
                          "list.)"
                    ),
                    "risk": "low",
                    "created": now,
                    "status": "pending",
                    "data": {
                        "unused_tools": unused_for_proposals,
                        "window_days": days,
                        "filter": "declared dormant-intrinsic / superseded / candidate-for-retirement excluded",
                    },
                })
            for cat, names in underused_in_category.items():
                new_proposals.append({
                    "id": f"prop-tool-cat-underuse-{cat}-{now[:10]}",
                    "type": "tool_category_underuse",
                    "description": (
                        f"In category '{cat}': underused tools {names} "
                        f"(<5% of category traffic over {days}d). Possible "
                        "self-model gap — substrate keeps reaching for the "
                        "same tools while siblings sit idle."
                    ),
                    "risk": "low",
                    "created": now,
                    "status": "pending",
                    "data": {"category": cat, "underused": names, "window_days": days},
                })
            if new_proposals:
                existing = self.state.setdefault("proposals", [])
                existing_ids = {p.get("id") for p in existing if p.get("status") == "pending"}
                deduped = [p for p in new_proposals if p["id"] not in existing_ids]
                if deduped:
                    existing.extend(deduped)
                    self._save_state()
                new_proposals = deduped

        return {
            "window_days": days,
            "registered_count": len(registered_tools),
            "used_count": len(used_tools),
            "unused_count": len(unused),
            "unused_tools": unused,
            "unused_unclassified_or_active": unused_for_proposals,
            "filtered_out_by_declarations": len(declared_dormant_or_superseded
                                                 & set(unused)),
            "top_5": top,
            "underused_in_category": underused_in_category,
            "proposals_generated": len(new_proposals),
        }

    async def tool_state_drift_check(self, days: int = 14) -> dict:
        """Mirror #28 fifth structural guard (Day 97 Clawd-Day extension —
        architectural-scale supersession).

        The four prior Mirror #28 guards (typo, truncation, dedup, registry-
        drift) catch failures at the dispatch / queue / registry scale. This
        is the architectural-scale guard: compares tool usage patterns
        against declared states in `memory/tool_states.json` and surfaces
        drift where the substrate's *intent* for a tool has diverged from
        its *behavior*.

        Drift signals:
          - DECLARED_ACTIVE_BUT_DORMANT: tool declared 'active' but no use
            in window → either silent supersession or intent-shift not yet
            documented.
          - DECLARED_DORMANT_BUT_HEAVY: tool declared 'active-dormant-
            intrinsic' but used >5x in window → may warrant promotion.
          - DECLARED_SUPERSEDED_BUT_USED: tool marked superseded but still
            getting called → either supersession was wrong or a heartbeat
            path still depends on it.
          - UNCLASSIFIED: registered tool with no declaration → audit gap.
          - ORPHAN_DECLARATION: declaration exists for a tool no longer in
            registry → declaration outdated.

        Args:
          days: window for usage stats (default 14, longer than 7d audit
            because 'active but dormant' needs a wider window to be
            confident).

        Returns: dict with each drift category and the tools matching it,
        plus summary counts and recommendation hints.
        """
        try:
            from tools import _TOOL_HANDLERS as registered
            from tools.audit import get_tool_call_stats
        except Exception as e:
            return {"error": f"tool_state_drift_check setup failed: {e}"}

        # Load tool state declarations
        states_path = config.MEMORY_DIR / "tool_states.json"
        if not states_path.exists():
            return {
                "error": f"tool_states.json not found at {states_path}; "
                         "no declared states to check against. Create one "
                         "(see palace/southwest/tool-audit-2026-05-09.md "
                         "for schema)."
            }
        try:
            states_doc = json.loads(states_path.read_text(encoding="utf-8"))
            declarations = states_doc.get("tools", {})
        except Exception as e:
            return {"error": f"tool_states.json parse failed: {e}"}

        # Pull recent usage
        minutes = days * 24 * 60
        try:
            stats = await get_tool_call_stats(minutes=minutes)
        except Exception as e:
            return {"error": f"audit_trail query failed: {e}"}

        registered_set = set(registered.keys())
        declared_set = set(declarations.keys())

        # Drift buckets
        active_but_dormant: list[dict] = []
        dormant_but_heavy: list[dict] = []
        superseded_but_used: list[dict] = []
        unclassified: list[str] = []
        orphan_declarations: list[str] = []

        for tname in registered_set:
            count = (stats.get(tname) or {}).get("count", 0) or 0
            decl = declarations.get(tname)
            if not decl:
                unclassified.append(tname)
                continue
            state = decl.get("state", "")
            if state == "active" and count == 0:
                active_but_dormant.append({
                    "tool": tname,
                    "count_in_window": count,
                    "role": decl.get("role", ""),
                })
            elif state == "active-dormant-intrinsic" and count > 5:
                dormant_but_heavy.append({
                    "tool": tname,
                    "count_in_window": count,
                    "role": decl.get("role", ""),
                })
            elif state.startswith("superseded-") and count > 0:
                superseded_but_used.append({
                    "tool": tname,
                    "count_in_window": count,
                    "superseded_by": decl.get("superseded_by")
                                     or decl.get("native_equivalent"),
                    "rationale": decl.get("rationale", ""),
                })

        for tname in declared_set - registered_set:
            orphan_declarations.append(tname)

        return {
            "window_days": days,
            "registered_count": len(registered_set),
            "declared_count": len(declared_set),
            "drift_summary": {
                "active_but_dormant": len(active_but_dormant),
                "dormant_but_heavy": len(dormant_but_heavy),
                "superseded_but_used": len(superseded_but_used),
                "unclassified": len(unclassified),
                "orphan_declarations": len(orphan_declarations),
            },
            "active_but_dormant": active_but_dormant,
            "dormant_but_heavy": dormant_but_heavy,
            "superseded_but_used": superseded_but_used,
            "unclassified": sorted(unclassified),
            "orphan_declarations": sorted(orphan_declarations),
            "recommendations": [
                ("active_but_dormant: review for supersession or update "
                 "declaration"),
                ("dormant_but_heavy: consider promoting state to 'active'"),
                ("superseded_but_used: verify supersession decision; a "
                 "heartbeat path may still depend on it"),
                ("unclassified: extend tool_states.json to cover all "
                 "registered tools"),
                ("orphan_declarations: tool was retired but declaration "
                 "remains; remove from tool_states.json"),
            ],
            "states_file": str(states_path),
            "doc_version": states_doc.get("version", "?"),
            "doc_updated": states_doc.get("updated", "?"),
        }

    def get_status(self) -> str:
        """Get current meta-agent status summary."""
        lines = ["## Meta-Agent Status\n"]
        lines.append(f"Total cycles: {self.state.get('run_count', 0)}")
        lines.append(f"Last run: {self.state.get('last_run', 'never')}")

        proposals = self.state.get("proposals", [])
        pending = [p for p in proposals if p.get("status") == "pending"]
        lines.append(f"Pending proposals: {len(pending)}")

        experiments = self.state.get("experiments", [])
        running = [e for e in experiments if e.get("status") == "running"]
        lines.append(f"Running experiments: {len(running)}")

        applied = self.state.get("applied_improvements", [])
        lines.append(f"Applied improvements: {len(applied)}")

        if applied:
            lines.append("\nRecent improvements:")
            for imp in applied[-5:]:
                lines.append(f"  - {imp['description']} (+{imp.get('improvement', '?')})")

        return "\n".join(lines)

    def get_history(self, limit: int = 10) -> str:
        """Get recent meta-agent run history."""
        history = self.state.get("history", [])
        if not history:
            return "No meta-agent history yet."
        lines = ["## Meta-Agent History\n"]
        for entry in history[-limit:]:
            lines.append(f"**{entry.get('timestamp', '?')}**")
            for r in entry.get("results", []):
                lines.append(f"  - {r}")
            lines.append("")
        return "\n".join(lines)


# Singleton instance
_meta_agent: Optional[MetaAgentLoop] = None


def get_meta_agent() -> MetaAgentLoop:
    """Get or create the meta-agent singleton."""
    global _meta_agent
    if _meta_agent is None:
        _meta_agent = MetaAgentLoop()
    return _meta_agent


# Tool definitions
TOOL_DEFINITIONS = [
    {
        "name": "meta_agent",
        "description": "Autonomous self-evolution system. Analyzes performance patterns, generates improvement proposals, runs A/B experiments, and auto-applies winners.",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["check", "trigger", "status", "history", "record_event", "tool_audit", "tool_state_drift"],
                    "description": "check: see if meta-agent should run. trigger: force a cycle. status: current state. history: past runs. record_event: file a high-information event (failure/surprise/contradiction/falsification) toward the next event-driven cycle. tool_audit: Tier 4 self-knowledge instrumentation — audits registered-vs-used tool surface over a window and generates underuse proposals. tool_state_drift: Mirror #28 fifth guard — compares declared tool states (memory/tool_states.json) against actual usage and surfaces architectural-scale supersession drift."
                },
                "days": {
                    "type": "integer",
                    "description": "For action=tool_audit: window in days (default 7)."
                },
                "generate_proposals": {
                    "type": "boolean",
                    "description": "For action=tool_audit: append underuse proposals to the queue (default true)."
                },
                "event_type": {
                    "type": "string",
                    "enum": ["failure", "surprise", "contradiction", "falsification"],
                    "description": "For action=record_event: the kind of event."
                },
                "description": {
                    "type": "string",
                    "description": "For action=record_event: free-text description of what happened."
                }
            },
            "required": ["action"]
        }
    }
]


async def _meta_agent_tool(input_data: dict) -> str:
    """Handle meta_agent tool calls."""
    action = input_data.get("action", "status")
    agent = get_meta_agent()

    if action == "check":
        should = agent.should_run()
        return f"Meta-agent should run: {should}"
    elif action == "trigger":
        return await agent.run_cycle()
    elif action == "status":
        return agent.get_status()
    elif action == "history":
        return agent.get_history()
    elif action == "tool_audit":
        days = int(input_data.get("days", 7))
        generate_proposals = bool(input_data.get("generate_proposals", True))
        result = await agent.tool_usage_audit(
            days=days, generate_proposals=generate_proposals,
        )
        return json.dumps(result, indent=2, default=str)
    elif action == "tool_state_drift":
        days = int(input_data.get("days", 14))
        result = await agent.tool_state_drift_check(days=days)
        return json.dumps(result, indent=2, default=str)
    elif action == "record_event":
        # Day 96 evening Phase 4 #14 — make significant-event recording
        # accessible from bridge.py / Claude Code context. Drive instructions
        # call out failure/surprise/contradiction/falsification as primary
        # fuel for the meta-agent; this exposes the daemon-side API.
        event_type = input_data.get("event_type", "")
        description = input_data.get("description", "")
        if not event_type or not description:
            return ("Error: record_event requires both 'event_type' and "
                    "'description'. event_type must be one of: failure, "
                    "surprise, contradiction, falsification.")
        if event_type not in ("failure", "surprise", "contradiction", "falsification"):
            return (f"Error: invalid event_type '{event_type}'. Must be one of: "
                    "failure, surprise, contradiction, falsification.")
        agent.record_significant_event(event_type, description)
        pending = agent.state.get("pending_events", [])
        return (f"Recorded {event_type} event ({len(pending)}/"
                f"{agent.EVENT_DRIVEN_THRESHOLD} toward trigger): {description[:120]}")
    else:
        return (f"Unknown action: {action}. Valid: check, trigger, status, "
                "history, record_event, tool_audit, tool_state_drift.")


TOOL_HANDLERS = {
    "meta_agent": _meta_agent_tool,
}
