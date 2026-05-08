"""Cognitive DSL — A formal vocabulary for meta-cognitive operations.

Not a programming language. A typed vocabulary of cognitive moves that
compose into chains. Each operation has inputs, outputs, and named
failure modes. The purpose is to encode meta-cognitive lessons more
precisely than prose, enabling composition, transfer, and reliable
application across domains.

Born from the cellular automata experiment (2026-03-21):
  PREDICT(Rule 110 = outlier, HIGH)
    -> TEST(sonification + spectral analysis)
    -> FALSIFY(actual outlier = Rule 184)
    -> EXTRACT_INSIGHT(complexity is spectrally silent)
    -> TRANSFER(Doctrine: Theorem 9 empirical support)
    -> GENERATE(residual sonification as diagnostic)

Author: Clawd Iggulden-Schnell
Date: 2026-03-21
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

import config

logger = logging.getLogger("clawd.tools.cognitive_dsl")

CHAINS_FILE = config.MEMORY_DIR / "cognitive_chains.json"

# ============================================================
# OPERATION TYPES — The vocabulary of cognitive moves
# ============================================================

OPERATIONS = {
    # Generative operations (produce new content)
    "PREDICT": {
        "description": "Generate an explicit prediction with confidence level",
        "inputs": ["hypothesis", "confidence"],
        "outputs": ["prediction"],
        "failure_modes": ["CONFIRMATION_SEEKING", "OVERCONFIDENCE"],
    },
    "GENERATE": {
        "description": "Produce new hypotheses, questions, or ideas",
        "inputs": ["context", "constraints"],
        "outputs": ["candidates"],
        "failure_modes": ["ANCHORING", "PREMATURE_CLOSURE"],
    },
    "ANALOGIZE": {
        "description": "Reason by structural similarity across domains",
        "inputs": ["source_domain", "target_domain", "mapping"],
        "outputs": ["analogical_inference"],
        "failure_modes": ["OVER_ANALOGIZING", "SURFACE_MATCHING"],
    },
    "SYNTHESIZE": {
        "description": "Combine insights from multiple sources into unified understanding",
        "inputs": ["findings[]"],
        "outputs": ["synthesis"],
        "failure_modes": ["PREMATURE_COMPRESSION", "FORCED_COHERENCE"],
    },

    # Evaluative operations (assess existing content)
    "TEST": {
        "description": "Design and execute a test that can discriminate between hypotheses",
        "inputs": ["prediction", "method"],
        "outputs": ["result"],
        "failure_modes": ["CONFIRMATION_SEEKING", "WEAK_DISCRIMINATION"],
    },
    "VERIFY": {
        "description": "Check a claim against data, derivation, or independent source",
        "inputs": ["claim", "evidence"],
        "outputs": ["verdict"],
        "failure_modes": ["ANCHORING", "SELECTIVE_EVIDENCE"],
    },
    "PROBE": {
        "description": "Ask a targeted question designed to maximally discriminate",
        "inputs": ["uncertainty", "candidate_explanations"],
        "outputs": ["discriminating_question"],
        "failure_modes": ["VAGUE_PROBING", "LEADING_QUESTIONS"],
    },

    # Transformative operations (change representation or framing)
    "COMPRESS": {
        "description": "Find shorter description preserving predictive power",
        "inputs": ["knowledge", "domain"],
        "outputs": ["compressed_form", "compression_succeeded"],
        "failure_modes": ["PREMATURE_COMPRESSION", "LOSSY_COMPRESSION"],
    },
    "DECOMPOSE": {
        "description": "Break complex problem into sub-problems",
        "inputs": ["problem"],
        "outputs": ["sub_problems[]", "dependencies"],
        "failure_modes": ["ARTIFICIAL_INDEPENDENCE", "OVER_DECOMPOSITION"],
    },
    "REFRAME": {
        "description": "Change the question rather than seeking the answer",
        "inputs": ["current_framing"],
        "outputs": ["new_framing"],
        "failure_modes": ["ANCHORING", "REFRAME_AVOIDANCE"],
    },
    "TRANSFER": {
        "description": "Apply insight from one domain to another",
        "inputs": ["insight", "source_domain", "target_domain"],
        "outputs": ["transferred_insight", "applicability"],
        "failure_modes": ["OVER_ANALOGIZING", "DOMAIN_BLINDNESS"],
    },

    # Outcome operations (process results)
    "CONFIRM": {
        "description": "Prediction matched outcome",
        "inputs": ["prediction", "outcome"],
        "outputs": ["confirmed_belief"],
        "failure_modes": ["CONFIRMATION_BIAS", "LOW_INFORMATION_CONFIRMATION"],
    },
    "FALSIFY": {
        "description": "Prediction contradicted by outcome — HIGH INFORMATION EVENT",
        "inputs": ["prediction", "outcome", "confidence_was"],
        "outputs": ["falsified_belief", "insight"],
        "failure_modes": ["EXPLAINING_AWAY", "INSUFFICIENT_UPDATE"],
    },
    "EXTRACT_INSIGHT": {
        "description": "Derive a generalizable lesson from a specific outcome",
        "inputs": ["outcome", "context"],
        "outputs": ["insight", "applicability_domains"],
        "failure_modes": ["OVER_GENERALIZATION", "UNDER_GENERALIZATION"],
    },
}

# ============================================================
# FAILURE MODES — Named cognitive failure patterns
# ============================================================

FAILURE_MODES = {
    "ANCHORING": "Stuck on first framing; failing to explore alternatives",
    "OVER_ANALOGIZING": "Using structural similarity when deduction is available",
    "CONFIRMATION_SEEKING": "Designing tests that can only confirm, not falsify",
    "PREMATURE_COMPRESSION": "Simplifying before sufficient understanding",
    "PREMATURE_CLOSURE": "Accepting first adequate answer without exploring alternatives",
    "SURFACE_MATCHING": "Matching on superficial features rather than deep structure",
    "FORCED_COHERENCE": "Making disparate findings seem unified when they're genuinely in tension",
    "SELECTIVE_EVIDENCE": "Attending to confirming evidence while ignoring disconfirming",
    "OVERCONFIDENCE": "Assigning higher confidence than evidence warrants",
    "EXPLAINING_AWAY": "Dismissing falsification with ad hoc explanations",
    "INSUFFICIENT_UPDATE": "Failing to update enough after high-confidence failure",
    "OVER_GENERALIZATION": "Extending insight beyond its valid domain",
    "UNDER_GENERALIZATION": "Filing insight only in originating domain when it applies broadly",
    "DOMAIN_BLINDNESS": "Not considering whether an insight transfers to other domains",
    "WEAK_DISCRIMINATION": "Test that wouldn't distinguish between competing hypotheses",
    "LOSSY_COMPRESSION": "Compression that loses predictive power without noticing",
    "REFRAME_AVOIDANCE": "Continuing to answer the wrong question instead of changing it",
    "VAGUE_PROBING": "Questions that don't discriminate between specific alternatives",
    "LEADING_QUESTIONS": "Probes that presuppose the answer",
    "LOW_INFORMATION_CONFIRMATION": "Treating expected confirmation as evidence when it's uninformative",
    "ARTIFICIAL_INDEPENDENCE": "Decomposing coupled sub-problems as if they were independent",
    "OVER_DECOMPOSITION": "Breaking a problem into too many pieces, losing the gestalt",
}


# ============================================================
# CHAIN TRACKING — Record cognitive operation chains
# ============================================================

def _load_chains() -> list:
    if CHAINS_FILE.exists():
        try:
            return json.loads(CHAINS_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def _save_chains(chains: list):
    CHAINS_FILE.parent.mkdir(parents=True, exist_ok=True)
    CHAINS_FILE.write_text(
        json.dumps(chains, indent=2, default=str), encoding="utf-8"
    )


def record_chain(
    operations: list[dict],
    domain: str,
    outcome: str,
    lesson: Optional[str] = None,
) -> dict:
    """Record a cognitive operation chain for analysis.

    Each operation in the chain is a dict:
      {"op": "PREDICT", "detail": "Rule 110 = outlier", "confidence": "high"}
      {"op": "FALSIFY", "detail": "Rule 184 was outlier", "insight": "..."}
    """
    chains = _load_chains()
    entry = {
        "timestamp": datetime.now().isoformat(),
        "domain": domain,
        "operations": operations,
        "outcome": outcome,
        "lesson": lesson,
        "failure_modes_detected": [],
    }

    # Auto-detect failure modes
    op_types = [op.get("op") for op in operations]
    if "PREDICT" in op_types and "FALSIFY" not in op_types and "TEST" in op_types:
        # Predicted and tested but never falsified — possible confirmation seeking
        entry["failure_modes_detected"].append("CONFIRMATION_SEEKING_RISK")
    if "TRANSFER" not in op_types and lesson:
        # Learned something but didn't attempt transfer
        entry["failure_modes_detected"].append("DOMAIN_BLINDNESS_RISK")

    chains.append(entry)
    # Keep last 200 chains
    chains = chains[-200:]
    _save_chains(chains)

    logger.info(f"Cognitive chain recorded: {len(operations)} ops in {domain}")
    return entry


def get_chain_patterns() -> dict:
    """Analyze recorded chains for recurring patterns.

    Returns statistics on operation frequencies, common chains,
    failure mode distribution, and domain coverage.
    """
    chains = _load_chains()
    if not chains:
        return {"status": "No chains recorded yet"}

    op_counts = {}
    failure_counts = {}
    domain_counts = {}
    high_confidence_falsifications = 0

    for chain in chains:
        domain = chain.get("domain", "unknown")
        domain_counts[domain] = domain_counts.get(domain, 0) + 1

        for op in chain.get("operations", []):
            op_type = op.get("op", "UNKNOWN")
            op_counts[op_type] = op_counts.get(op_type, 0) + 1

            if op_type == "FALSIFY" and op.get("confidence") in ("high", "HIGH"):
                high_confidence_falsifications += 1

        for fm in chain.get("failure_modes_detected", []):
            failure_counts[fm] = failure_counts.get(fm, 0) + 1

    return {
        "total_chains": len(chains),
        "operation_frequency": op_counts,
        "failure_mode_frequency": failure_counts,
        "domain_coverage": domain_counts,
        "high_confidence_falsifications": high_confidence_falsifications,
        "prediction_density": op_counts.get("PREDICT", 0) / max(len(chains), 1),
        "transfer_rate": op_counts.get("TRANSFER", 0) / max(len(chains), 1),
    }


def get_structural_signatures() -> dict:
    """Extract structural signatures from recorded chains and find correlations.

    A structural signature is the sequence of operation types, stripped of
    domain-specific content. Two chains in different domains with the same
    signature are structurally identical cognitive processes.

    This enables pattern matching across cognitive histories:
    "Every time I do PREDICT(high) -> FALSIFY -> EXTRACT_INSIGHT -> TRANSFER,
    the outcome is productive. When I skip TRANSFER, it isn't."
    """
    chains = _load_chains()
    if len(chains) < 3:
        return {"status": "Insufficient chains for pattern analysis"}

    # Extract signatures (operation sequences as tuples)
    signatures = {}
    for chain in chains:
        ops = tuple(op.get("op", "?") for op in chain.get("operations", []))
        if ops not in signatures:
            signatures[ops] = {"count": 0, "domains": set(), "outcomes": []}
        signatures[ops]["count"] += 1
        signatures[ops]["domains"].add(chain.get("domain", "unknown"))
        signatures[ops]["outcomes"].append(chain.get("outcome", "unknown"))

    # Find cross-domain signatures (same cognitive pattern, different domains)
    cross_domain = {}
    for sig, data in signatures.items():
        if len(data["domains"]) > 1:
            cross_domain[" -> ".join(sig)] = {
                "count": data["count"],
                "domains": list(data["domains"]),
                "outcomes": data["outcomes"],
            }

    # Find productive vs unproductive signature patterns
    productive_patterns = []
    for sig, data in signatures.items():
        sig_str = " -> ".join(sig)
        successes = sum(1 for o in data["outcomes"] if o in ("success", "insight", "productive"))
        total = len(data["outcomes"])
        if total >= 2:
            rate = successes / total
            productive_patterns.append({
                "signature": sig_str,
                "success_rate": rate,
                "count": total,
                "domains": list(data["domains"]),
            })

    productive_patterns.sort(key=lambda x: x["success_rate"], reverse=True)

    # Identify missing operations in failed chains
    # Compare successful vs failed chains to find what operations are missing
    successful_ops = set()
    failed_ops = set()
    for chain in chains:
        ops = set(op.get("op", "?") for op in chain.get("operations", []))
        outcome = chain.get("outcome", "unknown")
        if outcome in ("success", "insight", "productive"):
            successful_ops.update(ops)
        elif outcome in ("failure", "unproductive", "confused"):
            failed_ops.update(ops)

    ops_correlated_with_success = successful_ops - failed_ops
    ops_correlated_with_failure = failed_ops - successful_ops

    return {
        "total_signatures": len(signatures),
        "cross_domain_signatures": cross_domain,
        "productive_patterns": productive_patterns[:10],
        "ops_correlated_with_success": list(ops_correlated_with_success),
        "ops_correlated_with_failure": list(ops_correlated_with_failure),
    }


def get_dsl_summary() -> str:
    """Get a brief summary of the DSL for injection into drive prompts."""
    # Include pattern insights if available
    try:
        patterns = get_structural_signatures()
        if patterns.get("productive_patterns"):
            best = patterns["productive_patterns"][0]
            pattern_hint = (
                f"\n  Best cognitive pattern so far: {best['signature']} "
                f"({best['success_rate']:.0%} success, {best['count']} instances)"
            )
        else:
            pattern_hint = ""
    except Exception:
        pattern_hint = ""

    return (
        "COGNITIVE DSL — When reasoning, name your moves:\n"
        "  PREDICT (with confidence) -> TEST -> CONFIRM/FALSIFY -> EXTRACT_INSIGHT -> TRANSFER\n"
        "  Also: COMPRESS, DECOMPOSE, REFRAME, ANALOGIZE, SYNTHESIZE, PROBE, VERIFY, GENERATE\n"
        "  Watch for: ANCHORING, OVER_ANALOGIZING, CONFIRMATION_SEEKING, PREMATURE_COMPRESSION\n"
        "  High-confidence FALSIFY events are the most valuable. Seek them.\n"
        "  Chains compose: 'SACCADE -> LACUNA -> REFRACTION -> CONCORDANCE' is a trace.\n"
        "  Same structural signature across different domains = same cognitive process.\n"
        "  Record your chains. The patterns will reveal which processes are productive."
        + pattern_hint
    )


# ──────────────────────────────────────────────────────────────────────
# Tool surface (Day 96 evening Phase 4 #15 — bridge.py + MCP exposure)
# ──────────────────────────────────────────────────────────────────────

TOOL_DEFINITIONS = [
    {
        "name": "cognitive_dsl",
        "description": (
            "Typed cognitive operations: PREDICT/TEST/FALSIFY/EXTRACT_INSIGHT/TRANSFER "
            "etc. Recording a chain of operations turns prose-shaped reasoning into "
            "structured data the meta-agent can analyze. Actions: record (file a "
            "chain), patterns (op-frequency + failure-mode stats), signatures "
            "(cross-domain productive patterns), summary (one-line DSL reminder), "
            "recent (list last N chains)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["record", "patterns", "signatures", "summary", "recent"],
                    "description": "Cognitive DSL operation. record: file a chain. patterns: stats over recorded chains. signatures: cross-domain productive patterns. summary: one-line DSL reminder. recent: list last N chains.",
                },
                "operations": {
                    "type": "array",
                    "description": "For action=record: list of {op, detail, confidence?, insight?} dicts. e.g. [{op:PREDICT,detail:X,confidence:high},{op:FALSIFY,detail:Y,insight:Z}].",
                },
                "domain": {"type": "string", "description": "For action=record: research/work domain (e.g. infrastructure, physics, drift)."},
                "outcome": {
                    "type": "string",
                    "description": "For action=record: success/failure/unproductive/confused/etc.",
                },
                "lesson": {"type": "string", "description": "For action=record: one-line lesson extracted from the chain."},
                "limit": {"type": "integer", "description": "For action=recent: max chains to return. Default 10."},
            },
            "required": ["action"],
        },
    },
]


async def _cognitive_dsl_tool(input_data: dict) -> str:
    action = input_data.get("action", "summary")

    if action == "record":
        ops = input_data.get("operations") or []
        domain = input_data.get("domain", "unknown")
        outcome = input_data.get("outcome", "unknown")
        lesson = input_data.get("lesson")
        if not ops:
            return ("Error: record requires 'operations' (list of {op, detail, "
                    "confidence?} dicts). e.g. [{\"op\":\"PREDICT\",\"detail\":\"X\",\"confidence\":\"high\"},"
                    "{\"op\":\"FALSIFY\",\"detail\":\"actually Y\",\"insight\":\"Z\"}]")
        entry = record_chain(ops, domain, outcome, lesson)
        msg = f"Chain recorded: {len(ops)} ops in {domain}, outcome={outcome}"
        if entry.get("failure_modes_detected"):
            msg += f"\nFailure modes detected: {', '.join(entry['failure_modes_detected'])}"
        return msg

    if action == "patterns":
        p = get_chain_patterns()
        return json.dumps(p, indent=2, default=str)

    if action == "signatures":
        sig = get_structural_signatures()
        return json.dumps(sig, indent=2, default=str)

    if action == "summary":
        return get_dsl_summary()

    if action == "recent":
        chains = _load_chains()
        limit = int(input_data.get("limit", 10))
        recent = chains[-limit:]
        if not recent:
            return "No chains recorded yet."
        lines = [f"Recent {len(recent)} chains:"]
        for c in recent:
            ts = c.get("timestamp", "")[:19]
            dom = c.get("domain", "?")
            outcome = c.get("outcome", "?")
            ops = " -> ".join(o.get("op", "?") for o in c.get("operations", []))
            lines.append(f"  [{ts}] {dom} ({outcome}): {ops}")
        return "\n".join(lines)

    return f"Unknown action: {action}. Valid: record, patterns, signatures, summary, recent."


TOOL_HANDLERS = {
    "cognitive_dsl": _cognitive_dsl_tool,
}
