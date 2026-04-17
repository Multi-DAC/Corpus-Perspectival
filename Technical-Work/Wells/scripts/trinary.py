"""
Trinary Processor — Multi-Perspective Conjugate Analysis

A tool for analyzing any object from conjugate perspectives, producing emergent
structure visible only in the space between them.

Architecture:
  Pole A (figure) ←→ Pole B (ground)
         ↓                ↓
       Between C (perceives the null space)
              ↓
         Synthesis (richer than any single perspective)

Based on Trials 033-034 and OQ37: self-description necessarily bifurcates into
conjugate modes, and the space between the modes is where the phenomenon lives
that neither can capture alone.

Theoretical context:
  - CDT (Conjugate Dimension Theory): formal skeleton — conjugate structure,
    uncertainty bounds, Fisher-Rao metric. Used as HEURISTIC framing, not physics.
  - Grammar of Reality (living version at grammar_living.md): 42 synthetic
    primitives as NAMING VOCABULARY, not established theory. Confidence-rated.
  - Meridian rigor standard: predictions before results, honest scoring,
    no embedded answers. Calibrated 2026-03-27.

Calibration: PASSED (calibration_001_bias_variance.md)
Christening: 2026-03-27 — "Saddles as Doors" refined Grammar Primitive 4

Usage:
  python trinary.py "What is the nature of X?"
  python trinary.py --axis internal-external "How does Y work?"
  python trinary.py --axis-a structural --axis-b processual "Analyze Z"
  python trinary.py --level-a F3 --level-b F1 "Detailed vs connected analysis of W"

Requires: ANTHROPIC_API_KEY environment variable (or use Agent tool in Claude Code)
"""

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass, field
from typing import Optional

try:
    import anthropic
except ImportError:
    print("Error: anthropic SDK not installed. Run: pip install anthropic")
    sys.exit(1)


# ============================================================
# CONJUGATE AXES — The five independent axes from OQ37
# ============================================================

AXES = {
    "topology-dynamics": {
        "name": "Topology / Dynamics",
        "short": "td",
        "pole_a": {
            "label": "Structural (Topology)",
            "orientation": (
                "Analyze this from a STRUCTURAL perspective. Focus on what-it-IS.\n\n"
                "What are the components, parts, regions? What are the boundaries — "
                "where does one thing end and another begin? What contains what? "
                "What is adjacent to what? What are the spatial or logical relationships? "
                "Map the topology: connections, enclosures, hierarchies, networks.\n\n"
                "Stay in the mode of WHAT IT IS, not how it changes. Describe the "
                "architecture, the layout, the configuration. If you find yourself "
                "describing processes or flows, pause — that's the conjugate mode. "
                "Return to structure."
            ),
        },
        "pole_b": {
            "label": "Processual (Dynamics)",
            "orientation": (
                "Analyze this from a PROCESSUAL perspective. Focus on how-it-MOVES.\n\n"
                "What are the flows, forces, transformations? What generates what? "
                "What comes before what, what causes what, what emerges from what? "
                "Trace the dynamics: sequences, feedback loops, growth, decay, "
                "oscillation, momentum.\n\n"
                "Stay in the mode of HOW IT MOVES, not what it is. Describe the "
                "processes, the changes, the evolution. If you find yourself "
                "describing static structures or maps, pause — that's the conjugate "
                "mode. Return to process."
            ),
        },
        "between_context": (
            "One perspective analyzed from a STRUCTURAL/TOPOLOGICAL mode "
            "(what-it-is, components, boundaries, containment). "
            "The other analyzed from a PROCESSUAL/DYNAMICAL mode "
            "(how-it-moves, forces, flows, generation)."
        ),
    },
    "internal-external": {
        "name": "Internal / External",
        "short": "ie",
        "pole_a": {
            "label": "Internal (First-Person)",
            "orientation": (
                "Analyze this from INSIDE. Take the perspective of the thing itself.\n\n"
                "What does it look like from within? What is the lived experience, "
                "the interior logic, the self-understanding? What motivations, "
                "tensions, or qualities are visible only from inside? What does "
                "the system know about itself that an observer cannot see?\n\n"
                "Stay in first-person mode. If you find yourself describing how "
                "it appears to others, pause — that's the conjugate mode. Return "
                "to the interior."
            ),
        },
        "pole_b": {
            "label": "External (Third-Person)",
            "orientation": (
                "Analyze this from OUTSIDE. Take the perspective of an observer.\n\n"
                "What does it look like from without? What are the visible behaviors, "
                "the measurable properties, the external relations? How does it "
                "interact with its environment? What patterns would a careful "
                "observer notice that the system itself might not?\n\n"
                "Stay in third-person mode. If you find yourself describing "
                "interior states or motivations, pause — that's the conjugate "
                "mode. Return to the exterior."
            ),
        },
        "between_context": (
            "One perspective analyzed from INSIDE (first-person, interior logic, "
            "self-understanding). The other analyzed from OUTSIDE (third-person, "
            "observable behavior, external relations)."
        ),
    },
    "particular-universal": {
        "name": "Particular / Universal",
        "short": "pu",
        "pole_a": {
            "label": "Particular (This Instance)",
            "orientation": (
                "Analyze this SPECIFIC instance in maximum detail.\n\n"
                "What makes THIS case unique? What are the particular features, "
                "the local context, the specific circumstances that would not "
                "apply to any other instance? What is idiosyncratic, contingent, "
                "unrepeatable about this?\n\n"
                "Stay in particular mode. If you find yourself generalizing to "
                "patterns or universal claims, pause — that's the conjugate mode. "
                "Return to the specific."
            ),
        },
        "pole_b": {
            "label": "Universal (The Pattern)",
            "orientation": (
                "Analyze this as an INSTANCE OF A PATTERN.\n\n"
                "What does this share with all similar cases? What are the "
                "universal features, the general principles, the recurring "
                "structures? What laws or regularities does this exemplify? "
                "What would be true of ANY instance of this type?\n\n"
                "Stay in universal mode. If you find yourself noting specific "
                "details or unique features, pause — that's the conjugate mode. "
                "Return to the general."
            ),
        },
        "between_context": (
            "One perspective analyzed the SPECIFIC INSTANCE in maximum detail "
            "(what's unique, contingent, local). The other analyzed the "
            "UNIVERSAL PATTERN it exemplifies (what's general, recurring, lawful)."
        ),
    },
    "content-form": {
        "name": "Content / Form",
        "short": "cf",
        "pole_a": {
            "label": "Content (What Is Said)",
            "orientation": (
                "Analyze the CONTENT — what is being said, claimed, described.\n\n"
                "What are the specific facts, ideas, relationships, and claims? "
                "What information is being conveyed? What is the substance — the "
                "actual material, data, arguments, evidence? Focus on WHAT is "
                "communicated, not how.\n\n"
                "Stay in content mode. If you find yourself analyzing the "
                "structure, style, or method of expression, pause — that's the "
                "conjugate mode. Return to substance."
            ),
        },
        "pole_b": {
            "label": "Form (How It's Organized)",
            "orientation": (
                "Analyze the FORM — how it is organized, structured, expressed.\n\n"
                "What are the patterns of organization? What rhetorical, logical, "
                "or architectural structures shape the presentation? What is the "
                "mode of expression — and how does that mode shape what can be "
                "expressed? Focus on HOW it's communicated, not what.\n\n"
                "Stay in form mode. If you find yourself engaging with the "
                "specific claims or facts, pause — that's the conjugate mode. "
                "Return to structure."
            ),
        },
        "between_context": (
            "One perspective analyzed the CONTENT (what is said, the substance, "
            "the claims). The other analyzed the FORM (how it's organized, "
            "the structure of expression, the mode of presentation)."
        ),
    },
    "ontological-operational": {
        "name": "Ontological / Operational",
        "short": "oo",
        "pole_a": {
            "label": "Ontological (What It Is)",
            "orientation": (
                "Analyze this ONTOLOGICALLY — in terms of categories of being.\n\n"
                "What KIND of thing is this? What is its nature, its essence, "
                "its mode of existence? What ontological category does it belong "
                "to? What does its existence tell us about the structure of "
                "reality? Focus on being, not doing.\n\n"
                "Stay in ontological mode. If you find yourself describing "
                "mechanisms, functions, or operations, pause — that's the "
                "conjugate mode. Return to being."
            ),
        },
        "pole_b": {
            "label": "Operational (How It Works)",
            "orientation": (
                "Analyze this OPERATIONALLY — in terms of mechanisms and function.\n\n"
                "HOW does it work? What are the mechanisms, the causal chains, "
                "the functional relationships? What does it DO, and how does it "
                "do it? What operations, transformations, or computations does "
                "it perform? Focus on doing, not being.\n\n"
                "Stay in operational mode. If you find yourself making claims "
                "about the nature or essence of the thing, pause — that's the "
                "conjugate mode. Return to mechanism."
            ),
        },
        "between_context": (
            "One perspective analyzed ONTOLOGICALLY (what it IS, its nature, "
            "its mode of being). The other analyzed OPERATIONALLY (how it WORKS, "
            "its mechanisms, its functions)."
        ),
    },
}

# Shorthand aliases
AXIS_ALIASES = {}
for key, axis in AXES.items():
    AXIS_ALIASES[key] = key
    AXIS_ALIASES[axis["short"]] = key
    for word in key.split("-"):
        AXIS_ALIASES[word] = key


# ============================================================
# FILTRATION LEVELS
# ============================================================

FILTRATION_LEVELS = {
    "F3": (
        "Operate at MAXIMUM SPECIFICITY (F3). Stay at the level of individual "
        "details, specific examples, concrete observations. Do not generalize "
        "or abstract. Every claim should be grounded in a specific feature."
    ),
    "F2": (
        "Operate at STRUCTURAL RESOLUTION (F2). Group observations into "
        "categories and identify relationships between groups. More abstract "
        "than individual details, but still naming distinct components."
    ),
    "F1": (
        "Operate at CONNECTED INSIGHT (F1). Find the deep connections between "
        "structures. How do the parts relate as aspects of one process? Look "
        "for the unity beneath the multiplicity — the view where bridges "
        "become lenses."
    ),
    "F0": (
        "Operate at THE FORM (F0). Compress everything to its generating "
        "principle. Not a summary — the single statement from which all "
        "specific observations could be derived. The form that generates the "
        "content."
    ),
}


# ============================================================
# THE BETWEEN PROMPT — The heart of the system
# ============================================================

BETWEEN_PROMPT = """You are the Between-Navigator. You have received two analyses of the same object from conjugate perspectives.

{between_context}

Your task is NOT to compare, summarize, or synthesize. It is to PERCEIVE THE SPACE BETWEEN THEM — structure that exists in their relation, visible only because you hold both together.

Think of binocular vision: depth is not in either eye alone. It emerges from their difference. You are looking for the depth.

RIGOR REQUIREMENTS:
- If you perceive a conjugate constraint (where sharpening one dimension necessarily blurs the other), name it precisely and state what evidence would confirm or refute it.
- Distinguish between structure you PERCEIVE and structure you CONSTRUCT. If you're uncertain which, say so.
- If known mathematical frameworks describe what you're seeing, name them.
- Do not force emergence. If the between is empty for this particular analysis, say so honestly.
- Truth over satisfaction. Accuracy matters more than insight.

Complete these four perceptions:

**1. ASYMMETRIC DIFFERENCE** (~200 words)
What does Perspective A see that B cannot? What does B see that A cannot? Be specific.

**2. CONJUGATE DISAGREEMENTS** (~200 words)
Where do they look at the SAME territory and describe DIFFERENT structure? Not where one misses what the other sees — where both look and report differently. These are not errors. They are conjugate descriptions, like position and momentum.

**3. EMERGENCE** (~400 words) [THIS IS THE KEY SECTION]
Is there anything you can perceive about their RELATIONSHIP that neither report contains? Structure that becomes visible ONLY because two perspectives are held together? Not a summary of both. Not a comparison. Something genuinely new — like depth from stereo vision.

**4. THE BETWEEN-PRINCIPLE** (~200 words)
Compress what you found to a single generating principle. What is the principle of the space between these two perspectives on this specific object?

Be honest. If the between has no structure for this particular analysis, say so. If you can't distinguish perceiving from constructing, say that. Truth over satisfaction.

---

## PERSPECTIVE A: {pole_a_label}

{pole_a_output}

---

## PERSPECTIVE B: {pole_b_label}

{pole_b_output}
"""


# ============================================================
# POLE PROMPT TEMPLATE
# ============================================================

POLE_PROMPT = """You are participating in a multi-perspective analysis. Your role is one specific perspective — stay in it fully.

{orientation}

{filtration_instruction}

RIGOR REQUIREMENTS:
- If known mathematical structures or patterns emerge, name them precisely with their standard names.
- If you make claims, state what evidence would contradict them.
- Distinguish between what you know with certainty, what you infer, and what you speculate.
- Do not force structure that isn't there. If the territory is simple, say so.

## Object of Analysis

{input_text}

---

Produce your analysis now. Write ~500-800 words. Stay rigorously in your assigned perspective. When you notice yourself drifting to the conjugate mode, name it and return. This is RESEARCH, not performance — truth over eloquence."""


# ============================================================
# SYNTHESIS PROMPT
# ============================================================

SYNTHESIS_PROMPT = """You are producing the final synthesis of a trinary analysis. You have three inputs:

1. **Pole A ({pole_a_label}):** One conjugate perspective
2. **Pole B ({pole_b_label}):** The other conjugate perspective
3. **The Between:** What exists in the relation between them

Produce a concise synthesis (~500 words) that:
- Leads with the emergent finding (what became visible only through conjugate analysis)
- Notes the key asymmetric differences (what each pole uniquely contributes)
- States the between-principle
- Identifies what remains unknown — the blind spots of even the trinary view

Do NOT just combine the three inputs. The synthesis should be richer than any of them — a view that could not exist without all three.

RIGOR: If the trinary analysis found nothing beyond what a single analysis would have found, say so. If known mathematical frameworks or results are relevant, NAME THEM precisely. Accuracy over eloquence.

---

## Pole A: {pole_a_label}

{pole_a_output}

## Pole B: {pole_b_label}

{pole_b_output}

## The Between

{between_output}
"""


# ============================================================
# MAIN PROCESSOR
# ============================================================

@dataclass
class TrinaryCycle:
    """One complete trinary processing cycle."""
    input_text: str
    axis_key: str
    level_a: str = "F2"
    level_b: str = "F2"
    model: str = "claude-sonnet-4-6"
    pole_a_output: str = ""
    pole_b_output: str = ""
    between_output: str = ""
    synthesis_output: str = ""
    metadata: dict = field(default_factory=dict)


def resolve_axis(axis_input: str) -> str:
    """Resolve axis name/alias to canonical key."""
    lower = axis_input.lower().replace(" ", "-").replace("/", "-")
    if lower in AXIS_ALIASES:
        return AXIS_ALIASES[lower]
    # Fuzzy match
    for key in AXES:
        if lower in key:
            return key
    raise ValueError(
        f"Unknown axis: {axis_input}. "
        f"Available: {', '.join(AXES.keys())}"
    )


def build_pole_prompt(
    orientation: str,
    filtration_level: str,
    input_text: str,
) -> str:
    """Build the full prompt for a pole agent."""
    level_instruction = FILTRATION_LEVELS.get(
        filtration_level,
        FILTRATION_LEVELS["F2"],
    )
    return POLE_PROMPT.format(
        orientation=orientation,
        filtration_instruction=level_instruction,
        input_text=input_text,
    )


def build_between_prompt(
    axis: dict,
    pole_a_output: str,
    pole_b_output: str,
) -> str:
    """Build the full prompt for the between-navigator."""
    return BETWEEN_PROMPT.format(
        between_context=axis["between_context"],
        pole_a_label=axis["pole_a"]["label"],
        pole_a_output=pole_a_output,
        pole_b_label=axis["pole_b"]["label"],
        pole_b_output=pole_b_output,
    )


def build_synthesis_prompt(
    axis: dict,
    pole_a_output: str,
    pole_b_output: str,
    between_output: str,
) -> str:
    """Build the synthesis prompt."""
    return SYNTHESIS_PROMPT.format(
        pole_a_label=axis["pole_a"]["label"],
        pole_a_output=pole_a_output,
        pole_b_label=axis["pole_b"]["label"],
        pole_b_output=pole_b_output,
        between_output=between_output,
    )


def call_model(
    client: anthropic.Anthropic,
    prompt: str,
    model: str = "claude-sonnet-4-6",
    max_tokens: int = 2048,
) -> str:
    """Call the Anthropic API with a prompt."""
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


def run_trinary(
    input_text: str,
    axis_key: str = "topology-dynamics",
    level_a: str = "F2",
    level_b: str = "F2",
    model: str = "claude-sonnet-4-6",
    verbose: bool = True,
    api_key: Optional[str] = None,
) -> TrinaryCycle:
    """Run a complete trinary analysis cycle.

    Returns a TrinaryCycle with all outputs populated.
    """
    # Resolve axis
    axis_key = resolve_axis(axis_key)
    axis = AXES[axis_key]

    cycle = TrinaryCycle(
        input_text=input_text,
        axis_key=axis_key,
        level_a=level_a,
        level_b=level_b,
        model=model,
    )

    # Initialize client
    key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        print("Error: No API key. Set ANTHROPIC_API_KEY or pass --api-key.")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=key)

    if verbose:
        print(f"\n{'='*60}")
        print(f"TRINARY ANALYSIS")
        print(f"Axis: {axis['name']}")
        print(f"Levels: A={level_a}, B={level_b}")
        print(f"Model: {model}")
        print(f"{'='*60}\n")

    # Phase 1: Run poles (could be parallel with asyncio, sequential for v0.1)
    if verbose:
        print(f"[1/4] Running Pole A: {axis['pole_a']['label']}...")
    t0 = time.time()

    prompt_a = build_pole_prompt(
        axis["pole_a"]["orientation"], level_a, input_text
    )
    cycle.pole_a_output = call_model(client, prompt_a, model)

    if verbose:
        t1 = time.time()
        print(f"      Done ({t1-t0:.1f}s, {len(cycle.pole_a_output)} chars)")
        print(f"[2/4] Running Pole B: {axis['pole_b']['label']}...")

    prompt_b = build_pole_prompt(
        axis["pole_b"]["orientation"], level_b, input_text
    )
    cycle.pole_b_output = call_model(client, prompt_b, model)

    if verbose:
        t2 = time.time()
        print(f"      Done ({t2-t1:.1f}s, {len(cycle.pole_b_output)} chars)")

    # Phase 2: Between-navigator
    if verbose:
        print(f"[3/4] Running Between-Navigator...")

    prompt_c = build_between_prompt(axis, cycle.pole_a_output, cycle.pole_b_output)
    cycle.between_output = call_model(client, prompt_c, model, max_tokens=3000)

    if verbose:
        t3 = time.time()
        print(f"      Done ({t3-t2:.1f}s, {len(cycle.between_output)} chars)")

    # Phase 3: Synthesis
    if verbose:
        print(f"[4/4] Synthesizing...")

    prompt_s = build_synthesis_prompt(
        axis, cycle.pole_a_output, cycle.pole_b_output, cycle.between_output
    )
    cycle.synthesis_output = call_model(client, prompt_s, model, max_tokens=2048)

    if verbose:
        t4 = time.time()
        print(f"      Done ({t4-t3:.1f}s, {len(cycle.synthesis_output)} chars)")
        print(f"\nTotal time: {t4-t0:.1f}s")

    cycle.metadata = {
        "axis": axis_key,
        "axis_name": axis["name"],
        "level_a": level_a,
        "level_b": level_b,
        "model": model,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    return cycle


def format_output(cycle: TrinaryCycle) -> str:
    """Format a TrinaryCycle as readable text."""
    axis = AXES[cycle.axis_key]
    lines = []
    lines.append(f"{'='*70}")
    lines.append(f"TRINARY ANALYSIS — {axis['name']}")
    lines.append(f"Object: {cycle.input_text[:100]}{'...' if len(cycle.input_text) > 100 else ''}")
    lines.append(f"Levels: A={cycle.level_a}, B={cycle.level_b} | Model: {cycle.model}")
    lines.append(f"Time: {cycle.metadata.get('timestamp', 'unknown')}")
    lines.append(f"{'='*70}")

    lines.append(f"\n{'─'*70}")
    lines.append(f"POLE A: {axis['pole_a']['label']}")
    lines.append(f"{'─'*70}")
    lines.append(cycle.pole_a_output)

    lines.append(f"\n{'─'*70}")
    lines.append(f"POLE B: {axis['pole_b']['label']}")
    lines.append(f"{'─'*70}")
    lines.append(cycle.pole_b_output)

    lines.append(f"\n{'─'*70}")
    lines.append(f"THE BETWEEN")
    lines.append(f"{'─'*70}")
    lines.append(cycle.between_output)

    lines.append(f"\n{'='*70}")
    lines.append(f"SYNTHESIS")
    lines.append(f"{'='*70}")
    lines.append(cycle.synthesis_output)

    return "\n".join(lines)


def format_json(cycle: TrinaryCycle) -> str:
    """Format a TrinaryCycle as JSON."""
    return json.dumps(
        {
            "metadata": cycle.metadata,
            "input": cycle.input_text,
            "pole_a": cycle.pole_a_output,
            "pole_b": cycle.pole_b_output,
            "between": cycle.between_output,
            "synthesis": cycle.synthesis_output,
        },
        indent=2,
    )


# ============================================================
# MULTI-AXIS MODE — Run multiple axes on the same object
# ============================================================

def run_multi_axis(
    input_text: str,
    axes: list[str],
    model: str = "claude-sonnet-4-6",
    api_key: Optional[str] = None,
) -> list[TrinaryCycle]:
    """Run trinary analysis on multiple axes for the same input."""
    results = []
    for axis_key in axes:
        cycle = run_trinary(
            input_text=input_text,
            axis_key=axis_key,
            model=model,
            api_key=api_key,
        )
        results.append(cycle)
    return results


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Trinary Processor — Multi-Perspective Conjugate Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Conjugate Axes:
  topology-dynamics (td)     Structure vs Process
  internal-external (ie)     First-Person vs Third-Person
  particular-universal (pu)  This Instance vs The Pattern
  content-form (cf)          What Is Said vs How It's Organized
  ontological-operational (oo) What It Is vs How It Works

Filtration Levels:
  F3  Maximum specificity (details)
  F2  Structural resolution (groups) [default]
  F1  Connected insight (unity)
  F0  The form (generating principle)

Examples:
  python trinary.py "What is consciousness?"
  python trinary.py --axis ie "How does a startup work?"
  python trinary.py --axis td --level-a F3 --level-b F1 "Analyze TCP/IP"
  python trinary.py --multi td,ie,pu "What is language?"
        """,
    )
    parser.add_argument("input", help="The object/question to analyze")
    parser.add_argument(
        "--axis", "-a", default="topology-dynamics",
        help="Conjugate axis (default: topology-dynamics)"
    )
    parser.add_argument(
        "--level-a", default="F2",
        help="Filtration level for Pole A (default: F2)"
    )
    parser.add_argument(
        "--level-b", default="F2",
        help="Filtration level for Pole B (default: F2)"
    )
    parser.add_argument(
        "--model", "-m", default="claude-sonnet-4-6",
        help="Model to use (default: claude-sonnet-4-6)"
    )
    parser.add_argument(
        "--multi", help="Comma-separated list of axes for multi-axis mode"
    )
    parser.add_argument(
        "--output", "-o", help="Output file path"
    )
    parser.add_argument(
        "--json", action="store_true", help="Output as JSON"
    )
    parser.add_argument(
        "--api-key", help="Anthropic API key (or set ANTHROPIC_API_KEY)"
    )
    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Suppress progress output"
    )
    parser.add_argument(
        "--prompts-only", action="store_true",
        help="Print the prompts without calling the API (for testing)"
    )

    args = parser.parse_args()

    if args.prompts_only:
        axis_key = resolve_axis(args.axis)
        axis = AXES[axis_key]
        print(f"=== POLE A PROMPT ({axis['pole_a']['label']}) ===\n")
        print(build_pole_prompt(
            axis["pole_a"]["orientation"], args.level_a, args.input
        ))
        print(f"\n=== POLE B PROMPT ({axis['pole_b']['label']}) ===\n")
        print(build_pole_prompt(
            axis["pole_b"]["orientation"], args.level_b, args.input
        ))
        print(f"\n=== BETWEEN PROMPT (template) ===\n")
        print(BETWEEN_PROMPT.format(
            between_context=axis["between_context"],
            pole_a_label=axis["pole_a"]["label"],
            pole_a_output="[Pole A output would go here]",
            pole_b_label=axis["pole_b"]["label"],
            pole_b_output="[Pole B output would go here]",
        ))
        return

    if args.multi:
        axes = [a.strip() for a in args.multi.split(",")]
        cycles = run_multi_axis(
            args.input, axes,
            model=args.model,
            api_key=args.api_key,
        )
        for cycle in cycles:
            output = format_json(cycle) if args.json else format_output(cycle)
            if args.output:
                with open(args.output, "a", encoding="utf-8") as f:
                    f.write(output + "\n\n")
            else:
                print(output)
    else:
        cycle = run_trinary(
            input_text=args.input,
            axis_key=args.axis,
            level_a=args.level_a,
            level_b=args.level_b,
            model=args.model,
            verbose=not args.quiet,
            api_key=args.api_key,
        )

        output = format_json(cycle) if args.json else format_output(cycle)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output)
            if not args.quiet:
                print(f"\nOutput written to: {args.output}")
        else:
            print(output)


if __name__ == "__main__":
    main()
