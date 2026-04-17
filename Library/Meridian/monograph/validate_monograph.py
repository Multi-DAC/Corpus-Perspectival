#!/usr/bin/env python3
"""
Meridian Monograph Validator
Checks LaTeX structural integrity without requiring a TeX installation.

Validates: brace balance, environment matching, citation/bibitem consistency,
equation label uniqueness, cross-references, and generates a summary report.
"""

import re
import sys
from pathlib import Path
from collections import defaultdict, Counter

# ============================================================
# Configuration
# ============================================================

MONOGRAPH_DIR = Path(__file__).parent
MAIN_FILE = MONOGRAPH_DIR / "meridian_monograph.tex"

CHAPTER_FILES = [
    "chapter1_foundation.tex",
    "chapter2_observational.tex",
    "chapter3_nogo.tex",
    "chapter4_ncg.tex",
    "chapter5_sound_speed.tex",
    "appendix_computations.tex",
]

# Environments that must be balanced
TRACKED_ENVS = {
    "equation", "align", "gather", "multline", "subequations",
    "enumerate", "itemize", "description",
    "table", "tabular", "longtable", "figure",
    "thebibliography", "quote", "center",
    "theorem", "proposition", "corollary", "lemma", "conjecture",
    "definition", "scalingrelation", "remark", "proof",
}

# ============================================================
# Validators
# ============================================================

class ValidationResult:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.stats = {}

    def error(self, file, line, msg):
        self.errors.append((file, line, msg))

    def warning(self, file, line, msg):
        self.warnings.append((file, line, msg))

    def __bool__(self):
        return len(self.errors) == 0


def check_brace_balance(filename, content, result):
    """Check that braces are balanced, ignoring comments and escaped braces."""
    lines = content.split('\n')
    depth = 0
    for i, line in enumerate(lines, 1):
        # Strip comments (but not escaped %)
        stripped = re.sub(r'(?<!\\)%.*$', '', line)
        for j, ch in enumerate(stripped):
            if ch == '{' and (j == 0 or stripped[j-1] != '\\'):
                depth += 1
            elif ch == '}' and (j == 0 or stripped[j-1] != '\\'):
                depth -= 1
                if depth < 0:
                    result.error(filename, i, f"Unmatched closing brace (depth went negative)")
                    depth = 0  # reset to continue checking
    if depth != 0:
        result.error(filename, len(lines), f"Unbalanced braces: {depth} unclosed opening brace(s)")


def check_environments(filename, content, result):
    """Check that all \\begin/\\end environments are properly matched."""
    lines = content.split('\n')
    env_stack = []  # (env_name, line_number)

    for i, line in enumerate(lines, 1):
        # Strip comments
        stripped = re.sub(r'(?<!\\)%.*$', '', line)

        # Find \begin{...}
        for m in re.finditer(r'\\begin\{(\w+\*?)\}', stripped):
            env = m.group(1)
            if env.rstrip('*') in TRACKED_ENVS or env in TRACKED_ENVS:
                env_stack.append((env, i))

        # Find \end{...}
        for m in re.finditer(r'\\end\{(\w+\*?)\}', stripped):
            env = m.group(1)
            if env.rstrip('*') in TRACKED_ENVS or env in TRACKED_ENVS:
                if not env_stack:
                    result.error(filename, i, f"\\end{{{env}}} without matching \\begin")
                elif env_stack[-1][0] != env:
                    expected = env_stack[-1][0]
                    result.error(filename, i,
                        f"\\end{{{env}}} doesn't match \\begin{{{expected}}} (line {env_stack[-1][1]})")
                    env_stack.pop()
                else:
                    env_stack.pop()

    for env, line in env_stack:
        result.error(filename, line, f"\\begin{{{env}}} never closed")


def extract_labels(filename, content):
    """Extract all \\label{...} definitions."""
    labels = {}
    for i, line in enumerate(content.split('\n'), 1):
        for m in re.finditer(r'\\label\{([^}]+)\}', line):
            label = m.group(1)
            if label in labels:
                yield ('duplicate', label, i, labels[label])
            labels[label] = (filename, i)
    yield ('labels', labels, None, None)


def extract_refs(filename, content):
    """Extract all \\ref{...} and \\eqref{...} references."""
    refs = []
    for i, line in enumerate(content.split('\n'), 1):
        for m in re.finditer(r'\\(?:eq)?ref\{([^}]+)\}', line):
            refs.append((m.group(1), filename, i))
    return refs


def extract_citations(filename, content):
    """Extract all \\cite{...} keys."""
    cites = []
    for i, line in enumerate(content.split('\n'), 1):
        for m in re.finditer(r'\\cite\{([^}]+)\}', line):
            # Handle comma-separated keys
            for key in m.group(1).split(','):
                cites.append((key.strip(), filename, i))
    return cites


def extract_bibitems(filename, content):
    """Extract all \\bibitem{...} keys."""
    items = {}
    for i, line in enumerate(content.split('\n'), 1):
        for m in re.finditer(r'\\bibitem\{([^}]+)\}', line):
            items[m.group(1)] = (filename, i)
    return items


def count_elements(filename, content):
    """Count equations, tables, theorems, etc."""
    counts = Counter()
    counts['equations'] = len(re.findall(r'\\begin\{(?:equation|align|gather|multline|subequations)\*?\}', content))
    counts['tables'] = len(re.findall(r'\\begin\{(?:table|tabular|longtable)\*?\}', content))
    counts['figures'] = len(re.findall(r'\\begin\{figure\*?\}', content))
    counts['theorems'] = len(re.findall(r'\\begin\{theorem\}', content))
    counts['propositions'] = len(re.findall(r'\\begin\{proposition\}', content))
    counts['corollaries'] = len(re.findall(r'\\begin\{corollary\}', content))
    counts['definitions'] = len(re.findall(r'\\begin\{definition\}', content))
    counts['conjectures'] = len(re.findall(r'\\begin\{conjecture\}', content))
    counts['proofs'] = len(re.findall(r'\\begin\{proof\}', content))
    counts['labels'] = len(re.findall(r'\\label\{', content))
    counts['citations'] = len(re.findall(r'\\cite\{', content))
    counts['bibitems'] = len(re.findall(r'\\bibitem\{', content))
    counts['sections'] = len(re.findall(r'\\section\{', content))
    counts['subsections'] = len(re.findall(r'\\subsection\{', content))
    counts['lines'] = content.count('\n') + 1
    return counts


def check_common_errors(filename, content, result):
    """Check for common LaTeX mistakes."""
    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        stripped = re.sub(r'(?<!\\)%.*$', '', line)

        # Double subscript/superscript without braces
        if re.search(r'_\w_\w', stripped):
            result.warning(filename, i, "Possible double subscript without braces")
        if re.search(r'\^\w\^\w', stripped):
            result.warning(filename, i, "Possible double superscript without braces")

        # Missing $ around common math
        if re.search(r'(?<!\$)\\(?:frac|sqrt|sum|int|partial|nabla|alpha|beta|gamma|delta|epsilon|zeta|eta|theta|lambda|mu|nu|xi|pi|rho|sigma|tau|phi|chi|psi|omega|Gamma|Delta|Theta|Lambda|Xi|Pi|Sigma|Phi|Psi|Omega)\b(?![^{]*\$)', stripped):
            # This is tricky — skip if we're clearly inside math mode
            # Just flag obvious cases outside any $ delimiters
            pass  # Too many false positives, skip this check

        # \begin{document} or \documentclass in chapter files
        if filename != str(MAIN_FILE.name):
            if '\\documentclass' in stripped:
                result.error(filename, i, "\\documentclass found in chapter file (should only be in main file)")
            if '\\begin{document}' in stripped:
                result.error(filename, i, "\\begin{document} found in chapter file")


# ============================================================
# Main
# ============================================================

def validate():
    result = ValidationResult()
    all_labels = {}
    all_refs = []
    all_cites = []
    all_bibitems = {}
    chapter_stats = {}

    # Read and validate main file
    if MAIN_FILE.exists():
        content = MAIN_FILE.read_text(encoding='utf-8')
        check_brace_balance(MAIN_FILE.name, content, result)
        check_environments(MAIN_FILE.name, content, result)
        check_common_errors(MAIN_FILE.name, content, result)
        chapter_stats[MAIN_FILE.name] = count_elements(MAIN_FILE.name, content)
    else:
        result.error(MAIN_FILE.name, 0, "Main file not found!")

    # Read and validate each chapter
    for chapter_file in CHAPTER_FILES:
        filepath = MONOGRAPH_DIR / chapter_file
        if not filepath.exists():
            result.error(chapter_file, 0, f"Chapter file not found: {chapter_file}")
            continue

        content = filepath.read_text(encoding='utf-8')

        # Structural checks
        check_brace_balance(chapter_file, content, result)
        check_environments(chapter_file, content, result)
        check_common_errors(chapter_file, content, result)

        # Collect labels
        for item in extract_labels(chapter_file, content):
            kind = item[0]
            if kind == 'duplicate':
                _, label, line, (orig_file, orig_line) = item
                result.error(chapter_file, line,
                    f"Duplicate label '{label}' (first defined in {orig_file}:{orig_line})")
            elif kind == 'labels':
                all_labels.update(item[1])

        # Collect refs, cites, bibitems
        all_refs.extend(extract_refs(chapter_file, content))
        all_cites.extend(extract_citations(chapter_file, content))
        all_bibitems.update(extract_bibitems(chapter_file, content))

        # Stats
        chapter_stats[chapter_file] = count_elements(chapter_file, content)

    # Cross-reference validation
    for ref, filename, line in all_refs:
        if ref not in all_labels:
            result.warning(filename, line, f"\\ref{{{ref}}} points to undefined label")

    # Citation validation
    for cite, filename, line in all_cites:
        if cite not in all_bibitems:
            result.error(filename, line, f"\\cite{{{cite}}} has no matching \\bibitem")

    # Orphan bibitems (defined but never cited)
    cited_keys = {c[0] for c in all_cites}
    for key, (filename, line) in all_bibitems.items():
        if key not in cited_keys:
            result.warning(filename, line, f"\\bibitem{{{key}}} defined but never cited")

    # ============================================================
    # Report
    # ============================================================

    print("=" * 70)
    print("MERIDIAN MONOGRAPH — VALIDATION REPORT")
    print("=" * 70)
    print()

    # Per-chapter stats
    print("CHAPTER STATISTICS")
    print("-" * 70)
    total = Counter()
    for chapter_file in [MAIN_FILE.name] + CHAPTER_FILES:
        if chapter_file in chapter_stats:
            stats = chapter_stats[chapter_file]
            total.update(stats)
            if chapter_file == MAIN_FILE.name:
                continue
            print(f"\n  {chapter_file}:")
            print(f"    Lines: {stats['lines']}")
            print(f"    Sections: {stats['sections']}, Subsections: {stats['subsections']}")
            print(f"    Equations: {stats['equations']}, Tables: {stats['tables']}")
            if stats['theorems'] + stats['propositions'] + stats['corollaries'] + stats['conjectures'] > 0:
                formal = []
                for k in ['theorems', 'propositions', 'corollaries', 'conjectures', 'definitions', 'proofs']:
                    if stats[k] > 0:
                        formal.append(f"{stats[k]} {k}")
                print(f"    Formal: {', '.join(formal)}")
            print(f"    Labels: {stats['labels']}, Citations: {stats['citations']}, Bibitems: {stats['bibitems']}")

    print(f"\n  TOTALS:")
    print(f"    Lines: {total['lines']}")
    print(f"    Sections: {total['sections']}, Subsections: {total['subsections']}")
    print(f"    Equations: {total['equations']}, Tables: {total['tables']}")
    print(f"    Labels: {total['labels']}, Citations: {total['citations']}, Bibitems: {total['bibitems']}")
    formal_total = sum(total[k] for k in ['theorems', 'propositions', 'corollaries', 'conjectures', 'definitions', 'proofs'])
    print(f"    Formal statements: {formal_total}")

    # Errors
    print()
    print("=" * 70)
    if result.errors:
        print(f"ERRORS: {len(result.errors)}")
        print("-" * 70)
        for filename, line, msg in result.errors:
            print(f"  [{filename}:{line}] {msg}")
    else:
        print("ERRORS: 0  OK")

    # Warnings
    print()
    if result.warnings:
        print(f"WARNINGS: {len(result.warnings)}")
        print("-" * 70)
        for filename, line, msg in result.warnings:
            print(f"  [{filename}:{line}] {msg}")
    else:
        print("WARNINGS: 0  OK")

    # Verdict
    print()
    print("=" * 70)
    if result:
        print("VERDICT: PASS — No structural errors detected.")
        print("The monograph is likely to compile cleanly with pdflatex.")
    else:
        print(f"VERDICT: FAIL — {len(result.errors)} error(s) found.")
        print("Fix errors before attempting compilation.")
    print("=" * 70)

    return result


if __name__ == "__main__":
    result = validate()
    sys.exit(0 if result else 1)
