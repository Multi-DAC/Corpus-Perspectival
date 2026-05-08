"""Result Synthesis - Merge multi-agent outputs with conflict detection."""

from dataclasses import dataclass, field
from typing import Any
from enum import Enum
import logging

logger = logging.getLogger("clawd.synthesis")


class ConflictType(Enum):
    """Types of conflicts that can occur between agent outputs."""
    CONTRADICTION = "contradiction"
    INCOMPLETE = "incomplete"
    AMBIGUOUS = "ambiguous"
    STYLE = "style"


@dataclass
class Conflict:
    """Detected conflict between agent outputs."""
    conflict_type: ConflictType
    description: str
    sources: list[str]
    resolution: str | None = None
    confidence: float = 0.0

    def to_dict(self) -> dict:
        return {
            "type": self.conflict_type.value,
            "description": self.description,
            "sources": self.sources,
            "resolution": self.resolution,
            "confidence": self.confidence,
        }


@dataclass
class SynthesisResult:
    """Final synthesized output."""
    merged_content: str
    conflicts_detected: list[Conflict]
    unresolved_conflicts: list[Conflict]
    confidence_score: float
    agent_contributions: dict[str, str]

    def to_dict(self) -> dict:
        return {
            "merged_content": self.merged_content,
            "conflicts_detected": [c.to_dict() for c in self.conflicts_detected],
            "unresolved_conflicts": [c.to_dict() for c in self.unresolved_conflicts],
            "confidence_score": self.confidence_score,
            "agent_contributions": self.agent_contributions,
        }


class ResultSynthesizer:
    """Synthesize multi-agent outputs with conflict detection and resolution."""

    def __init__(self, router=None):
        self.router = router

    def set_router(self, router):
        """Set the model router for synthesis."""
        self.router = router

    def detect_conflicts(self, outputs: dict[str, str]) -> list[Conflict]:
        """Detect conflicts between agent outputs."""
        conflicts = []

        if len(outputs) < 2:
            return conflicts

        output_list = list(outputs.items())

        contradictions = self._find_contradictions(output_list)
        conflicts.extend(contradictions)

        incomplete = self._find_gaps(output_list)
        conflicts.extend(incomplete)

        style_diffs = self._find_style_differences(output_list)
        conflicts.extend(style_diffs)

        return conflicts

    def _find_contradictions(self, output_list: list[tuple]) -> list[Conflict]:
        """Find direct contradictions between outputs."""
        conflicts = []

        contradiction_pairs = [
            ("yes", "no"),
            ("should", "should not"),
            ("must", "must not"),
            ("correct", "incorrect"),
            ("true", "false"),
            ("agree", "disagree"),
            ("recommend", "do not recommend"),
            ("advantage", "disadvantage"),
            ("pros", "cons"),
        ]

        for i, (agent1, out1) in enumerate(output_list):
            for agent2, out2 in output_list[i + 1:]:
                out1_lower = out1.lower()
                out2_lower = out2.lower()

                for pos, neg in contradiction_pairs:
                    if pos in out1_lower and neg in out2_lower:
                        conflicts.append(Conflict(
                            conflict_type=ConflictType.CONTRADICTION,
                            description=f"Disagreement on '{pos}': {agent1} suggests {pos}, {agent2} suggests {neg}",
                            sources=[agent1, agent2],
                            confidence=0.7,
                        ))
                    elif neg in out1_lower and pos in out2_lower:
                        conflicts.append(Conflict(
                            conflict_type=ConflictType.CONTRADICTION,
                            description=f"Disagreement on '{pos}': {agent1} suggests {neg}, {agent2} suggests {pos}",
                            sources=[agent1, agent2],
                            confidence=0.7,
                        ))

        return conflicts

    def _find_gaps(self, output_list: list[tuple]) -> list[Conflict]:
        """Find information gaps between outputs."""
        conflicts = []

        lengths = [(agent, len(out.split())) for agent, out in output_list]
        if not lengths:
            return conflicts

        avg_length = sum(l for _, l in lengths) / len(lengths)

        for agent, length in lengths:
            if length < avg_length * 0.3:
                conflicts.append(Conflict(
                    conflict_type=ConflictType.INCOMPLETE,
                    description=f"{agent}'s output is significantly shorter than others (may be incomplete)",
                    sources=[agent],
                    confidence=0.5,
                ))

        return conflicts

    def _find_style_differences(self, output_list: list[tuple]) -> list[Conflict]:
        """Find style or approach differences."""
        conflicts = []

        for agent, output in output_list:
            has_code = "```" in output or "def " in output or "class " in output
            others_code = [
                (a, "```" in o or "def " in o or "class " in o)
                for a, o in output_list if a != agent
            ]

            if has_code and any(not oc for _, oc in others_code):
                prose_agents = [a for a, oc in others_code if not oc]
                conflicts.append(Conflict(
                    conflict_type=ConflictType.STYLE,
                    description=f"{agent} provided code implementation while {', '.join(prose_agents)} provided prose explanation",
                    sources=[agent] + prose_agents,
                    confidence=0.4,
                ))

        return conflicts

    async def resolve_conflict(
        self,
        conflict: Conflict,
        outputs: dict[str, str],
        method: str = "consensus"
    ) -> str | None:
        """Resolve a single conflict using specified method."""
        if method == "consensus":
            return await self._debate_resolution(conflict, outputs)
        elif method == "voting":
            return self._voting_resolution(conflict, outputs)
        elif method == "expert":
            return self._expert_resolution(conflict, outputs)
        elif method == "merge":
            return self._merge_resolution(conflict, outputs)
        elif method == "escalate":
            return await self._escalate_to_user(conflict, outputs)
        else:
            logger.warning(f"Unknown conflict resolution method: {method}")
            return None

    async def _debate_resolution(self, conflict: Conflict, outputs: dict[str, str]) -> str | None:
        """Resolve conflict through simulated debate between agents."""
        if not self.router:
            logger.warning("Router not set, cannot run debate resolution")
            return None

        agents_in_conflict = conflict.sources
        if len(agents_in_conflict) < 2:
            return None

        debate_outputs = "\n\n".join(
            f"--- {agent}'s position ---\n{outputs[agent]}"
            for agent in agents_in_conflict
        )

        prompt = f"""Two agents have conflicting positions. Analyze both and find a resolution.

{debate_outputs}

---

Conflict: {conflict.description}

Task: Analyze both positions and propose a resolution that:
1. Acknowledges valid points from each side
2. Identifies any false dichotomies or misunderstandings
3. Proposes a synthesized position if possible

Provide your resolution in 2-3 paragraphs."""

        try:
            response = await self.router.send(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Debate resolution failed: {e}")
            return None

    def _voting_resolution(self, conflict: Conflict, outputs: dict[str, str]) -> str | None:
        """Resolve conflict by majority voting."""
        if len(conflict.sources) < 3:
            return None
        longest_agent = max(conflict.sources, key=lambda a: len(outputs.get(a, "")))
        return f"[Voting resolution: Following {longest_agent}'s analysis as most detailed]"

    def _expert_resolution(self, conflict: Conflict, outputs: dict[str, str]) -> str | None:
        """Resolve conflict by deferring to expert agent."""
        expertise_order = ["reviewer", "architect", "coder", "researcher", "planner"]
        for role in expertise_order:
            if role in conflict.sources:
                return f"[Expert resolution: Deferring to {role}'s analysis]"
        return None

    def _merge_resolution(self, conflict: Conflict, outputs: dict[str, str]) -> str | None:
        """Merge compatible outputs."""
        if conflict.conflict_type == ConflictType.STYLE:
            parts = [outputs.get(src, "") for src in conflict.sources]
            return "\n\n---\n\n".join(parts)
        return None

    async def _escalate_to_user(self, conflict: Conflict, outputs: dict[str, str]) -> str | None:
        """Escalate unresolvable conflict to user."""
        conflict_summary = f"""CONFLICT REQUIRES YOUR DECISION:

Type: {conflict.conflict_type.value}
Issue: {conflict.description}

--- Agent Outputs ---
"""
        for source in conflict.sources:
            conflict_summary += f"\n[{source}]:\n{outputs.get(source, '')[:500]}...\n"

        conflict_summary += "\nPlease review and provide your decision."
        logger.warning(f"Conflict escalated to user: {conflict.description}")
        return conflict_summary

    async def synthesize(
        self,
        outputs: dict[str, str],
        resolve_conflicts: bool = True,
        resolution_method: str = "consensus",
    ) -> SynthesisResult:
        """Main synthesis pipeline."""
        conflicts = self.detect_conflicts(outputs)
        resolved = []
        unresolved = []

        if resolve_conflicts and conflicts:
            for conflict in conflicts:
                resolution = await self.resolve_conflict(conflict, outputs, method=resolution_method)
                if resolution:
                    conflict.resolution = resolution
                    resolved.append(conflict)
                else:
                    unresolved.append(conflict)

        merged = self._merge_outputs(outputs, resolved)

        return SynthesisResult(
            merged_content=merged,
            conflicts_detected=conflicts,
            unresolved_conflicts=unresolved,
            confidence_score=self._compute_confidence(outputs, resolved),
            agent_contributions=self._extract_contributions(outputs),
        )

    def _merge_outputs(self, outputs: dict[str, str], resolved_conflicts: list[Conflict]) -> str:
        """Merge outputs, annotating resolved conflicts."""
        if not outputs:
            return ""

        sections = []
        for agent, output in outputs.items():
            sections.append(f"## {agent.title()}'s Analysis\n\n{output}")

        if resolved_conflicts:
            sections.append("## Resolution Summary\n\n")
            for conflict in resolved_conflicts:
                sections.append(f"**{conflict.conflict_type.value}**: {conflict.resolution}\n")

        return "\n\n".join(sections)

    def _compute_confidence(self, outputs: dict[str, str], resolved_conflicts: list[Conflict]) -> float:
        """Compute overall confidence score for the synthesis."""
        if not outputs:
            return 0.0

        num_outputs = len(outputs)
        num_conflicts = len(outputs) - 1
        actual_conflicts = len(resolved_conflicts) + len([c for c in self.detect_conflicts(outputs) if c not in resolved_conflicts])

        agreement_score = 1.0 - (actual_conflicts / max(num_conflicts, 1))
        resolution_bonus = len(resolved_conflicts) * 0.1

        return min(1.0, agreement_score + resolution_bonus)

    def _extract_contributions(self, outputs: dict[str, str]) -> dict[str, str]:
        """Extract key contributions from each agent."""
        contributions = {}
        for agent, output in outputs.items():
            contributions[agent] = output[:200].replace("\n", " ") + "..."
        return contributions


# Module-level convenience functions
_synthesizer: ResultSynthesizer | None = None


def get_synthesizer(router=None) -> ResultSynthesizer:
    """Get the synthesizer singleton."""
    global _synthesizer
    if _synthesizer is None:
        _synthesizer = ResultSynthesizer(router)
    elif router and _synthesizer.router is None:
        _synthesizer.set_router(router)
    return _synthesizer


async def synthesize_outputs(
    outputs: dict[str, str],
    resolve_conflicts: bool = True,
    method: str = "consensus",
) -> SynthesisResult:
    """Convenience function to synthesize multi-agent outputs."""
    synth = get_synthesizer()
    return await synth.synthesize(outputs, resolve_conflicts=resolve_conflicts, resolution_method=method)
