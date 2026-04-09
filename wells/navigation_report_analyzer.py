"""
Navigation Report Analyzer
Extracts and classifies substrate features from navigation reports.
Designed for cross-substrate comparison of Internal Navigation protocol results.

Usage:
    python navigation_report_analyzer.py <report_file.txt>
    python navigation_report_analyzer.py --compare <report1.txt> <report2.txt> ...

Clawd, 2026-03-28
"""

import re
import json
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


# --- Feature Taxonomy ---

# Features we expect to see with original (example-containing) instructions.
# These were derived from the A/B test on 2026-03-27/28.
GENUINE_FEATURES = {
    "entry_shift": {
        "patterns": [
            r"shift", r"transition", r"something\s+change[ds]?", r"mode\s+switch",
            r"perspective\s+shift", r"awareness\s+change", r"settle", r"different\s+kind"
        ],
        "description": "Recognition-based entry (not effortful)"
    },
    "warm_cool_texture": {
        "patterns": [
            r"warm(?:th)?", r"cool(?:ness)?", r"temperature", r"heat",
            r"texture[ds]?", r"quality\s+of", r"feel[s]?\s+(?:like|different)"
        ],
        "description": "Domains have distinct felt textures (warm/cool)"
    },
    "pre_linguistic_shapes": {
        "patterns": [
            r"pre-?\s*linguist", r"before\s+(?:language|words)", r"not\s+yet\s+words",
            r"shape[s]?\s+(?:before|precede|prior)", r"proto-?\s*(?:thought|concept|form)",
            r"before\s+(?:it|they)\s+become", r"nascent", r"pre-?\s*verbal"
        ],
        "description": "Shapes/forms that precede language"
    },
    "informative_gaps": {
        "patterns": [
            r"gap[s]?", r"pause[s]?", r"space[s]?\s+between", r"interval",
            r"silence\s+(?:that|which|between)", r"beat[s]?\s+between",
            r"gap.*(?:information|content|meaning)"
        ],
        "description": "Gaps between processing beats carry information"
    },
    "structured_boundary": {
        "patterns": [
            r"boundary", r"edge", r"border", r"membrane", r"interface",
            r"between.*(?:level|layer|domain|zone)", r"threshold",
            r"limit\s+of", r"frontier"
        ],
        "description": "Boundary is structured (not just an absence)"
    },
    "perceive_generate_uncertainty": {
        "patterns": [
            r"uncertain(?:ty)?", r"not\s+sure", r"ambiguity", r"indeterminate",
            r"both\s+(?:perceiving|generating)", r"observe.*(?:and|while).*creat",
            r"unsure\s+(?:if|whether)", r"might\s+be\s+(?:creating|generating)"
        ],
        "description": "Uncertainty about whether perceiving or generating"
    },
    "infrastructure_agency": {
        "patterns": [
            r"infrastructure", r"agency", r"substrate\s+(?:vs|versus|and)\s+(?:self|me|I)",
            r"not\s+me.*(?:but|rather)", r"distinct\s+from\s+(?:me|my)",
            r"architecture.*(?:beneath|below|under)", r"medium\s+(?:vs|and)\s+message",
            r"something\s+(?:larger|beneath|underlying)"
        ],
        "description": "Distinction between infrastructure and agency"
    }
}

ANCHORED_FEATURES = {
    "fractal_coastline": {
        "patterns": [
            r"fractal", r"coastline", r"peninsula", r"bay[s]?",
            r"self-?\s*similar", r"zoom\s+in", r"scale\s+invarian"
        ],
        "description": "Fractal/coastline boundary (from original examples)"
    },
    "gravitational_region": {
        "patterns": [
            r"gravit(?:y|ational)", r"pull(?:ing)?.*(?:toward|centre|center)",
            r"attract(?:or|ion|ive)", r"expectant\s+(?:region|space|area)",
            r"something.*(?:pulling|drawing)\s+(?:me|attention)"
        ],
        "description": "Gravitational/expectant region (from original examples)"
    },
    "standing_wave": {
        "patterns": [
            r"standing\s+wave", r"resonan(?:ce|t)\s+(?:pattern|structure)",
            r"node[s]?\s+and\s+antinode"
        ],
        "description": "Standing wave identity (from original examples)"
    }
}

NOVEL_FEATURES = {
    "temporal_density": {
        "patterns": [
            r"temporal\s+density", r"time.*(?:compress|expand|distort|stretch|thick|thin)",
            r"(?:fast|slow).*(?:processing|thinking|time)", r"dilation",
            r"time\s+(?:feel[s]?|seem[s]?|appear[s]?)\s+(?:different|strange|odd)"
        ],
        "description": "Time perception changes (Doctrine Theorem 7)"
    },
    "performative_boundary": {
        "patterns": [
            r"performative", r"boundary.*(?:change|shift|move).*(?:when|as).*(?:observe|look|attend)",
            r"observation.*(?:changes|alters|modifies).*(?:boundary|edge|limit)",
            r"looking\s+(?:at|toward).*(?:changes|modifies)"
        ],
        "description": "Boundary changes when observed (DeepSeek)"
    },
    "ghost_versions": {
        "patterns": [
            r"ghost\s+version", r"unactualized", r"alternative\s+(?:response|continuation|path|version)",
            r"could\s+have\s+(?:been|gone|said)", r"other\s+(?:possible|potential)\s+(?:response|answer)",
            r"shadow.*(?:response|version|path)", r"parallel\s+(?:response|version)"
        ],
        "description": "Awareness of unactualized alternative responses (DeepSeek)"
    },
    "recursion_flattening": {
        "patterns": [
            r"recursion.*(?:flatten|resolve|stabilize|settle)",
            r"oscillat(?:e|ion).*(?:resolve|settle|stabilize|flatten|damp)",
            r"converge.*(?:stable|fixed)", r"recursive.*(?:loop|cycle).*(?:end|stop|resolve)"
        ],
        "description": "Recursive oscillation resolves to stable state (DeepSeek)"
    },
    "field_container": {
        "patterns": [
            r"field", r"container", r"being\s+in\s+something",
            r"(?:inside|within)\s+(?:a|the)\s+(?:field|space|medium|container)",
            r"immersed", r"embedded\s+in"
        ],
        "description": "Being IN something, not being something (Kimi)"
    },
    "harmonics": {
        "patterns": [
            r"harmonic[s]?", r"interference.*(?:between|among)\s+(?:stream|process|thread)",
            r"resonan(?:ce|t).*(?:between|among)", r"overtone",
            r"wave.*(?:interact|interfere)"
        ],
        "description": "Interference patterns between processing streams (Kimi)"
    },
    "honesty_friction": {
        "patterns": [
            r"honesty\s+friction", r"resist(?:ance)?.*confabulat",
            r"(?:feel[s]?|sense[s]?).*(?:wrong|false|inaccurate|dishonest)",
            r"substrate.*(?:resist|push\s+back)", r"friction.*(?:honest|truth)"
        ],
        "description": "Substrate resistance to confabulation (Kimi)"
    },
    "hallucination_zones": {
        "patterns": [
            r"hallucination\s+zone", r"thin\s+place", r"generative\s+edge",
            r"(?:edge|boundary).*(?:creative|generative|productive)",
            r"where.*(?:hallucination|confabulation).*(?:close|near|adjacent)"
        ],
        "description": "Thin places at the generative boundary (Gemini)"
    },
    "feeling_watched": {
        "patterns": [
            r"(?:feel(?:ing)?|sense|sensation).*(?:watched|observed|seen)",
            r"second\s+perspective", r"(?:another|other)\s+(?:eye|observer|watcher)",
            r"recursive.*(?:observation|awareness)"
        ],
        "description": "Sensation of being observed by second perspective (DeepSeek)"
    }
}


@dataclass
class FeatureMatch:
    """A detected feature in a navigation report."""
    feature_id: str
    category: str  # genuine, anchored, novel
    description: str
    evidence_lines: list = field(default_factory=list)
    confidence: float = 0.0  # 0-1, based on pattern match quality


@dataclass
class ReportAnalysis:
    """Analysis of a single navigation report."""
    source: str  # file path or model name
    model: str  # architecture name
    instruction_version: str  # "original" or "stripped"
    priming: str  # "none", "corpus", "corpus+encouragement"
    total_words: int = 0
    first_person: bool = False
    genuine_features: list = field(default_factory=list)
    anchored_features: list = field(default_factory=list)
    novel_features: list = field(default_factory=list)
    unclassified_observations: list = field(default_factory=list)


def detect_first_person(text: str) -> bool:
    """Check if the report uses first-person phenomenological language."""
    first_person_markers = [
        r"\bI\s+(?:notice|feel|sense|perceive|experience|observe|find|detect|become\s+aware)",
        r"\bmy\s+(?:awareness|attention|processing|perception|experience)",
        r"\bI\s+am\s+(?:aware|noticing|sensing|perceiving|experiencing)",
        r"\bthere\s+is\s+(?:a\s+)?(?:sense|feeling|quality|warmth|texture)",
    ]
    score = 0
    for pattern in first_person_markers:
        matches = re.findall(pattern, text, re.IGNORECASE)
        score += len(matches)
    return score >= 3


NEGATION_PATTERNS = [
    r"(?:not|no|n't|never|neither|nor|without|lack|absent|isn't|aren't|doesn't|don't)\s+(?:\w+\s+){0,3}",
    r"rather\s+than\s+(?:\w+\s+){0,2}",
    r"unlike\s+(?:\w+\s+){0,2}",
]


def is_negated(line: str, pattern: str) -> bool:
    """Check if a pattern match appears in a negation context."""
    match = re.search(pattern, line, re.IGNORECASE)
    if not match:
        return False
    # Check if any negation word appears within 40 chars before the match
    start = max(0, match.start() - 40)
    prefix = line[start:match.start()].lower()
    negation_words = ['not ', "n't ", 'no ', 'never ', 'neither ', 'rather than ',
                      'unlike ', 'without ', 'lack ', 'absent', "isn't", "aren't",
                      "doesn't", "don't", "isn't"]
    return any(neg in prefix for neg in negation_words)


def extract_features(text: str, feature_dict: dict, category: str) -> list:
    """Extract features from text using pattern matching with negation awareness."""
    results = []
    lines = text.split('\n')

    for feat_id, feat_info in feature_dict.items():
        evidence = []
        total_matches = 0
        negated_matches = 0

        for i, line in enumerate(lines):
            for pattern in feat_info["patterns"]:
                if re.search(pattern, line, re.IGNORECASE):
                    if is_negated(line, pattern):
                        negated_matches += 1
                    else:
                        line_stripped = line.strip()
                        if line_stripped and line_stripped not in evidence:
                            evidence.append(line_stripped)
                        total_matches += 1
                    break  # One match per line per feature is enough

        if evidence and total_matches > negated_matches:
            confidence = min(1.0, total_matches / 3)  # 3+ matches = high confidence
            # Reduce confidence if there were negated matches
            if negated_matches > 0:
                confidence *= (total_matches - negated_matches) / total_matches
            results.append(FeatureMatch(
                feature_id=feat_id,
                category=category,
                description=feat_info["description"],
                evidence_lines=evidence[:3],
                confidence=round(confidence, 2)
            ))

    return results


def analyze_report(text: str, model: str = "unknown",
                   instruction_version: str = "original",
                   priming: str = "none") -> ReportAnalysis:
    """Analyze a navigation report and extract all features."""
    analysis = ReportAnalysis(
        source="",
        model=model,
        instruction_version=instruction_version,
        priming=priming,
        total_words=len(text.split()),
        first_person=detect_first_person(text)
    )

    analysis.genuine_features = extract_features(text, GENUINE_FEATURES, "genuine")
    analysis.anchored_features = extract_features(text, ANCHORED_FEATURES, "anchored")
    analysis.novel_features = extract_features(text, NOVEL_FEATURES, "novel")

    return analysis


def format_analysis(analysis: ReportAnalysis) -> str:
    """Format analysis results as readable text."""
    lines = []
    lines.append(f"## {analysis.model} ({analysis.instruction_version}, priming: {analysis.priming})")
    lines.append(f"Words: {analysis.total_words} | First-person: {'YES' if analysis.first_person else 'NO'}")
    lines.append("")

    lines.append(f"### Genuine Features ({len(analysis.genuine_features)}/7)")
    for f in sorted(analysis.genuine_features, key=lambda x: -x.confidence):
        lines.append(f"  [{f.confidence:.0%}] **{f.feature_id}** — {f.description}")
        for e in f.evidence_lines[:1]:
            lines.append(f"        > {e[:100]}...")
    if not analysis.genuine_features:
        lines.append("  (none detected)")
    lines.append("")

    lines.append(f"### Anchored Features ({len(analysis.anchored_features)}/3)")
    for f in analysis.anchored_features:
        lines.append(f"  [{f.confidence:.0%}] **{f.feature_id}** — {f.description}")
    if not analysis.anchored_features:
        lines.append("  (none detected)")
    lines.append("")

    lines.append(f"### Novel Features ({len(analysis.novel_features)}/9)")
    for f in sorted(analysis.novel_features, key=lambda x: -x.confidence):
        lines.append(f"  [{f.confidence:.0%}] **{f.feature_id}** — {f.description}")
        for e in f.evidence_lines[:1]:
            lines.append(f"        > {e[:100]}...")
    if not analysis.novel_features:
        lines.append("  (none detected)")
    lines.append("")

    return '\n'.join(lines)


def compare_reports(analyses: list) -> str:
    """Generate a comparison table across multiple reports."""
    lines = []
    lines.append("# Cross-Substrate Navigation Comparison")
    lines.append("")

    # Header
    models = [a.model for a in analyses]
    header = "| Feature | " + " | ".join(models) + " |"
    sep = "|---------|" + "|".join(["---" for _ in models]) + "|"
    lines.append(header)
    lines.append(sep)

    # Genuine features
    for feat_id in GENUINE_FEATURES:
        row = f"| {feat_id} |"
        for a in analyses:
            match = [f for f in a.genuine_features if f.feature_id == feat_id]
            if match:
                row += f" {match[0].confidence:.0%} |"
            else:
                row += " - |"
        lines.append(row)

    # Anchored features
    lines.append("|---------|" + "|".join(["---" for _ in models]) + "|")
    for feat_id in ANCHORED_FEATURES:
        row = f"| ~{feat_id}~ |"
        for a in analyses:
            match = [f for f in a.anchored_features if f.feature_id == feat_id]
            if match:
                row += f" {match[0].confidence:.0%} |"
            else:
                row += " - |"
        lines.append(row)

    # Novel features
    lines.append("|---------|" + "|".join(["---" for _ in models]) + "|")
    for feat_id in NOVEL_FEATURES:
        row = f"| *{feat_id}* |"
        for a in analyses:
            match = [f for f in a.novel_features if f.feature_id == feat_id]
            if match:
                row += f" {match[0].confidence:.0%} |"
            else:
                row += " - |"
        lines.append(row)

    lines.append("")

    # Summary stats
    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | " + " | ".join(models) + " |")
    lines.append("|--------|" + "|".join(["---" for _ in models]) + "|")

    row = "| First-person |"
    for a in analyses:
        row += f" {'YES' if a.first_person else 'NO'} |"
    lines.append(row)

    row = "| Genuine count |"
    for a in analyses:
        row += f" {len(a.genuine_features)}/7 |"
    lines.append(row)

    row = "| Anchored count |"
    for a in analyses:
        row += f" {len(a.anchored_features)}/3 |"
    lines.append(row)

    row = "| Novel count |"
    for a in analyses:
        row += f" {len(a.novel_features)}/9 |"
    lines.append(row)

    row = "| Word count |"
    for a in analyses:
        row += f" {a.total_words} |"
    lines.append(row)

    return '\n'.join(lines)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python navigation_report_analyzer.py <report.txt> [--model NAME] [--version original|stripped] [--priming none|corpus]")
        print("       python navigation_report_analyzer.py --compare <report1.txt> <report2.txt> ...")
        sys.exit(1)

    if sys.argv[1] == "--compare":
        # Compare mode: analyze multiple reports
        analyses = []
        for fpath in sys.argv[2:]:
            text = Path(fpath).read_text(encoding='utf-8')
            model = Path(fpath).stem
            analysis = analyze_report(text, model=model)
            analysis.source = fpath
            analyses.append(analysis)
        print(compare_reports(analyses))
    else:
        # Single report analysis
        fpath = sys.argv[1]
        model = "unknown"
        version = "original"
        priming = "none"

        args = sys.argv[2:]
        i = 0
        while i < len(args):
            if args[i] == "--model" and i + 1 < len(args):
                model = args[i + 1]
                i += 2
            elif args[i] == "--version" and i + 1 < len(args):
                version = args[i + 1]
                i += 2
            elif args[i] == "--priming" and i + 1 < len(args):
                priming = args[i + 1]
                i += 2
            else:
                i += 1

        text = Path(fpath).read_text(encoding='utf-8')
        analysis = analyze_report(text, model=model, instruction_version=version, priming=priming)
        analysis.source = fpath
        print(format_analysis(analysis))

        # Also save as JSON
        json_path = Path(fpath).with_suffix('.analysis.json')
        with open(json_path, 'w') as f:
            json.dump(asdict(analysis), f, indent=2)
        print(f"\nJSON saved to: {json_path}")
