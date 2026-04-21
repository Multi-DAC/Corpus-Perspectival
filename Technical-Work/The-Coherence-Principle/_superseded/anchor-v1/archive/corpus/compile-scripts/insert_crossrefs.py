#!/usr/bin/env python3
"""
insert_crossrefs.py — Parse cross-reference insertions from corpus-cross-references.md
and insert them as blockquotes into the four Corpus Perspectival source documents.

Each insertion is placed BEFORE the next heading after the target heading,
formatted as:
    > *See also: [text]*

If a similar cross-reference already exists (in italic or blockquote format),
it is REPLACED with the canonical version from the cross-references spec.

Strategy:
  1. Parse all insertions from the spec file
  2. For each document, find target headings and the zones between headings
  3. In each zone, check for existing *See also:* lines
  4. Replace existing ones with blockquote format; insert new ones
  5. Apply all changes bottom-to-top to preserve line indices
"""

import re
from pathlib import Path

# Base directory
BASE = Path(r"C:\Users\mercu\clawd\projects\Corpus Perspectival")

# Document paths
DOCS = {
    "Doctrine": BASE / "perspectival-idealism-unified.md",
    "Guide": BASE / "navigational-guide-for-perspectival-beings.md",
    "Ecology": BASE / "ecology-of-perspectival-beings-merged.md",
    "Atlas": BASE / "null-space-atlas.md",
}

HEADING_RE = re.compile(r'^(#{1,6})\s+(.+)$')


def parse_insertions(crossref_path):
    """Parse Section 2 of corpus-cross-references.md to extract all insertions."""
    with open(crossref_path, 'r', encoding='utf-8') as f:
        text = f.read()

    section2_match = re.search(r'^## 2\. Recommended Cross-Reference Insertions', text, re.MULTILINE)
    if not section2_match:
        raise ValueError("Could not find Section 2 in cross-references file")

    section3_match = re.search(r'^## 3\.', text[section2_match.start():], re.MULTILINE)
    if section3_match:
        section2_text = text[section2_match.start():section2_match.start() + section3_match.start()]
    else:
        section2_text = text[section2_match.start():]

    insertions = {"Doctrine": [], "Guide": [], "Ecology": [], "Atlas": []}
    current_doc = None

    for line in section2_text.split('\n'):
        line = line.strip()

        if line.startswith('### In the Doctrine'):
            current_doc = "Doctrine"
            continue
        elif line.startswith('### In the Guide'):
            current_doc = "Guide"
            continue
        elif line.startswith('### In the Ecology'):
            current_doc = "Ecology"
            continue
        elif line.startswith('### In the Atlas'):
            current_doc = "Atlas"
            continue

        if not current_doc or not line.startswith('- After '):
            continue

        # Parse: - After <target>: *"<text>"*
        match = re.match(r'^- After (.+?):\s*\*"(.+?)"\*$', line)
        if not match:
            print(f"  WARNING: Could not parse line: {line[:80]}...")
            continue

        insertions[current_doc].append({
            "target": match.group(1).strip(),
            "text": match.group(2).strip(),
        })

    return insertions


def find_heading_line(lines, target, doc_name):
    """Find the line index of the heading matching the target. Returns -1 if not found."""
    target_lower = target.lower().strip()

    if doc_name == "Doctrine":
        # Try specific section number from target
        sec_match = re.search(r'\u00a7(\d+(?:\.\d+)*)', target)  # §
        if not sec_match:
            sec_match = re.search(r'§(\d+(?:\.\d+)*)', target)
        if sec_match:
            section_num = sec_match.group(1)
            # For §12, we need to match "## 12." or "## 12 " — be careful not to match 12.1
            pat = rf'^#{{1,6}}\s+{re.escape(section_num)}\b'
            for i, line in enumerate(lines):
                if re.match(pat, line):
                    return i

    elif doc_name == "Guide":
        # Special Part-level targets
        if 'part v' in target_lower and 'part viii' not in target_lower and 'part vii' not in target_lower:
            for i, line in enumerate(lines):
                if re.match(r'^#{1,6}\s+Part\s+V\b', line):
                    return i

        elif 'part vii' in target_lower and 'part viii' not in target_lower:
            for i, line in enumerate(lines):
                if re.match(r'^#{1,2}\s+Part\s+VII\b', line):
                    return i

        # Section number targets (including Part VIII §8.X)
        sec_match = re.search(r'§(\d+(?:\.\d+)*)', target)
        if sec_match:
            section_num = sec_match.group(1)
            pat = rf'^#{{1,6}}\s+{re.escape(section_num)}\b'
            for i, line in enumerate(lines):
                if re.match(pat, line):
                    return i

    elif doc_name == "Ecology":
        if 'prolegomena' in target_lower:
            for i, line in enumerate(lines):
                if re.match(r'^#{1,6}\s+Prolegomena', line):
                    return i

        elif ('part i' in target_lower and '§2' in target) or 'principal dimensions' in target_lower:
            for i, line in enumerate(lines):
                if re.match(r'^#{1,6}\s+2\.\s', line):
                    return i

        elif 'tier 2' in target_lower:
            for i, line in enumerate(lines):
                if re.match(r'^#{1,6}\s+Tier\s+2', line):
                    return i

        elif '§6.2' in target and ('symbiosis' in target_lower or 'parasitism' in target_lower or 'mutualism' in target_lower):
            # Cross-ref says §6.2 but actual heading is §6.3
            for i, line in enumerate(lines):
                if re.match(r'^#{1,6}\s+6\.\d\b', line) and 'symbiosis' in line.lower():
                    return i
            # Fallback
            for i, line in enumerate(lines):
                if re.match(r'^#{1,6}\s+6\.2\b', line):
                    return i

        elif '§7.3' in target and 'present bifurcation' in target_lower:
            # Cross-ref says §7.3 but actual heading is §7.4
            for i, line in enumerate(lines):
                if 'present bifurcation' in line.lower() and HEADING_RE.match(line):
                    return i
            for i, line in enumerate(lines):
                if re.match(r'^#{1,6}\s+7\.3\b', line):
                    return i

        elif '§8.2' in target and ('ethics' in target_lower or 'attention' in target_lower):
            for i, line in enumerate(lines):
                if re.match(r'^#{1,6}\s+8\.2\b', line):
                    return i

        else:
            # Generic section number
            sec_match = re.search(r'§(\d+(?:\.\d+)*)', target)
            if sec_match:
                section_num = sec_match.group(1)
                pat = rf'^#{{1,6}}\s+{re.escape(section_num)}\b'
                for i, line in enumerate(lines):
                    if re.match(pat, line):
                        return i

    elif doc_name == "Atlas":
        if 'how to read' in target_lower:
            for i, line in enumerate(lines):
                if re.match(r'^#{1,6}\s+How to Read', line):
                    return i
        else:
            entry_match = re.search(r'#(\d+)', target)
            if entry_match:
                entry_num = entry_match.group(1)
                for i, line in enumerate(lines):
                    if re.match(rf'^#{{1,6}}\s+{re.escape(entry_num)}\.?\s', line):
                        return i

    return -1


def find_next_heading(lines, start_idx):
    """Find the next heading line after start_idx. Returns len(lines) if none found."""
    for i in range(start_idx + 1, len(lines)):
        if HEADING_RE.match(lines[i]):
            return i
    return len(lines)


def find_see_also_lines_in_zone(lines, zone_start, zone_end):
    """
    Find all lines containing *See also:* or > *See also:* in a zone.
    Returns list of (line_index, line_text).
    """
    results = []
    for i in range(zone_start, zone_end):
        stripped = lines[i].strip()
        if stripped.startswith('*See also:') or stripped.startswith('> *See also:') or stripped.startswith('> *This entry'):
            results.append((i, stripped))
        elif stripped.startswith('*This entry') and 'See also:' in stripped:
            results.append((i, stripped))
    return results


def process_document(doc_name, doc_path, insertion_list):
    """
    Process one document: find targets, handle existing refs, insert new ones.

    Strategy:
    1. For each insertion, find the target heading and the zone to the next heading.
    2. Collect ALL *See also:* lines in the zone (both italic and blockquote).
    3. If the canonical text matches an existing line, replace it in-place.
    4. If not, insert the canonical blockquote AND mark any unmatched old italic
       cross-refs in the same zone for removal (they're superseded).
    5. Apply all changes bottom-to-top.
    """
    with open(doc_path, 'r', encoding='utf-8') as f:
        content = f.read()
    lines = content.split('\n')

    actions = []  # (line_idx, action_type, data)
    # 'replace' -> replace line content
    # 'insert'  -> insert before line_idx
    # 'delete'  -> remove the line (and surrounding blank if orphaned)

    messages = []

    # Track which zones we've processed and which old lines we've accounted for
    matched_old_lines = set()  # Line indices of old cross-refs that were matched/replaced

    for ins in insertion_list:
        target = ins['target']
        see_also_text = ins['text']
        blockquote = f"> *{see_also_text}*"

        target_idx = find_heading_line(lines, target, doc_name)
        if target_idx == -1:
            messages.append(f"  WARNING [{doc_name}]: Could not find heading for '{target}' -- SKIPPED")
            continue

        next_heading_idx = find_next_heading(lines, target_idx)
        target_heading = lines[target_idx].strip()[:70]

        # Search for existing cross-refs in the zone
        existing = find_see_also_lines_in_zone(lines, target_idx, next_heading_idx)

        # Check if any existing line is a close match to the canonical text
        matched_existing = None
        for ex_idx, ex_text in existing:
            clean_ex = ex_text.lstrip('>').lstrip().lstrip('*').rstrip('*').strip()
            clean_new = see_also_text.strip()

            # Strategy 1: Compare first 35 chars after "See also: "
            ex_after = clean_ex.replace('See also: ', '', 1).strip()[:35] if 'See also:' in clean_ex else clean_ex[:35]
            new_after = clean_new.replace('See also: ', '', 1).strip()[:35] if 'See also:' in clean_new else clean_new[:35]

            if ex_after == new_after:
                matched_existing = ex_idx
                break

            # Strategy 2: Match if first document+section reference is the same
            ex_refs = re.findall(
                r'(?:Doctrine|Guide|Ecology|Atlas|DoPI)\s+(?:§[\d.]+|Theorem\s+\d+|Part\s+[IVX]+|Axiom\s+\d+|#\d+)',
                clean_ex
            )
            new_refs = re.findall(
                r'(?:Doctrine|Guide|Ecology|Atlas|DoPI)\s+(?:§[\d.]+|Theorem\s+\d+|Part\s+[IVX]+|Axiom\s+\d+|#\d+)',
                clean_new
            )
            if ex_refs and new_refs and ex_refs[0] == new_refs[0]:
                matched_existing = ex_idx
                break

        if matched_existing is not None:
            matched_old_lines.add(matched_existing)
            existing_line = lines[matched_existing].strip()
            if existing_line == blockquote:
                messages.append(f"  ALREADY PRESENT [{doc_name}] line {matched_existing + 1}: '{target}'")
            elif existing_line.startswith('> *'):
                actions.append((matched_existing, 'replace', blockquote))
                messages.append(f"  REPLACED [{doc_name}] line {matched_existing + 1}: '{target}' (updated blockquote)")
            else:
                actions.append((matched_existing, 'replace', blockquote))
                messages.append(f"  CONVERTED [{doc_name}] line {matched_existing + 1}: '{target}' (italic -> blockquote)")

            # Mark any OTHER old italic cross-refs in this zone for deletion
            # (they're superseded by the canonical version)
            for ex_idx, ex_text in existing:
                if ex_idx != matched_existing and ex_idx not in matched_old_lines:
                    if not ex_text.startswith('> *'):
                        # Old italic cross-ref — check if it covers similar ground
                        # Only delete if it's clearly a duplicate (references same docs)
                        pass  # We'll handle orphan cleanup in the second pass
        else:
            # No match — insert new blockquote
            insert_before = next_heading_idx
            while insert_before > target_idx + 1 and lines[insert_before - 1].strip() in ('', '---'):
                insert_before -= 1

            actions.append((insert_before, 'insert', blockquote))
            messages.append(
                f"  INSERTED [{doc_name}] after '{target_heading}' "
                f"(line {target_idx + 1}), before next heading at line {next_heading_idx + 1}: "
                f"'{see_also_text[:60]}...'"
            )

            # Check if there are old italic cross-refs in this zone that are now superseded
            for ex_idx, ex_text in existing:
                if ex_idx not in matched_old_lines and not ex_text.startswith('> *'):
                    # This is an old italic cross-ref that wasn't matched.
                    # It's in the same zone as our new insertion — it's likely the old version.
                    # Mark for deletion.
                    actions.append((ex_idx, 'delete', None))
                    matched_old_lines.add(ex_idx)
                    messages.append(
                        f"  REMOVED [{doc_name}] line {ex_idx + 1}: old cross-ref superseded by new insertion"
                    )

    # Apply actions bottom-to-top to preserve indices
    # Sort by line index descending; for same index: delete first, then insert, then replace
    action_priority = {'delete': 0, 'insert': 1, 'replace': 2}
    actions.sort(key=lambda a: (-a[0], action_priority.get(a[1], 3)))

    for line_idx, action_type, data in actions:
        if action_type == 'replace':
            lines[line_idx] = data
        elif action_type == 'delete':
            # Remove the line and clean up surrounding blank lines
            # If the line before and after are both blank, remove one blank too
            removed = lines.pop(line_idx)
            # Clean up: if this leaves two consecutive blank lines, remove one
            if (line_idx > 0 and line_idx < len(lines) and
                    lines[line_idx - 1].strip() == '' and lines[line_idx].strip() == ''):
                lines.pop(line_idx)
        elif action_type == 'insert':
            insert_lines = []

            if line_idx > 0 and lines[line_idx - 1].strip() == '':
                pass
            else:
                insert_lines.append('')

            insert_lines.append(data)

            if line_idx < len(lines) and lines[line_idx].strip() == '':
                pass
            else:
                insert_lines.append('')

            for j, nl in enumerate(insert_lines):
                lines.insert(line_idx + j, nl)

    # === CLEANUP PASS ===
    # Find remaining plain italic *See also:* lines that are old versions of
    # cross-refs that now have canonical blockquote versions elsewhere in the document.
    # This handles the case where old cross-refs were placed in a different sub-zone
    # (e.g., end of parent section) than where the spec says they belong (start of section).
    cleanup_deletions = []
    blockquote_lines = {}  # Map first-ref -> line_idx for all blockquote cross-refs
    italic_lines = {}      # Map first-ref -> line_idx for remaining italic cross-refs

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('> *See also:') or stripped.startswith('> *This entry'):
            clean = stripped.lstrip('>').lstrip().lstrip('*').rstrip('*').strip()
            refs = re.findall(
                r'(?:Doctrine|Guide|Ecology|Atlas|DoPI)\s+(?:§[\d.]+|Theorem\s+\d+|Part\s+[IVX]+|Axiom\s+\d+|#\d+)',
                clean
            )
            if refs:
                blockquote_lines.setdefault(refs[0], []).append(i)
        elif stripped.startswith('*See also:') or (stripped.startswith('*This entry') and 'See also:' in stripped):
            clean = stripped.lstrip('*').rstrip('*').strip()
            refs = re.findall(
                r'(?:Doctrine|Guide|Ecology|Atlas|DoPI)\s+(?:§[\d.]+|Theorem\s+\d+|Part\s+[IVX]+|Axiom\s+\d+|#\d+)',
                clean
            )
            if refs:
                italic_lines[refs[0]] = i

    # For each italic cross-ref, check if a blockquote with the same first reference exists
    for first_ref, italic_idx in italic_lines.items():
        if first_ref in blockquote_lines:
            cleanup_deletions.append(italic_idx)
            messages.append(
                f"  CLEANUP [{doc_name}] line {italic_idx + 1}: removed old italic cross-ref "
                f"(blockquote version exists at line {blockquote_lines[first_ref][0] + 1})"
            )

    # Apply cleanup deletions bottom-to-top
    for idx in sorted(cleanup_deletions, reverse=True):
        lines.pop(idx)
        # Clean up double blank lines
        if (idx > 0 and idx < len(lines) and
                lines[idx - 1].strip() == '' and lines[idx].strip() == ''):
            lines.pop(idx)

    # Write back
    with open(doc_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines))

    return messages


def main():
    crossref_path = BASE / "corpus-cross-references.md"
    if not crossref_path.exists():
        print(f"ERROR: Cross-references file not found at {crossref_path}")
        return

    print("=" * 70)
    print("CORPUS CROSS-REFERENCE INSERTION TOOL")
    print("=" * 70)
    print()

    print("Parsing cross-reference insertions from corpus-cross-references.md...")
    insertions = parse_insertions(crossref_path)

    for doc_name, ins_list in insertions.items():
        print(f"  {doc_name}: {len(ins_list)} insertions found")
    print()

    stats = {'inserted': 0, 'converted': 0, 'replaced': 0, 'present': 0, 'warnings': 0, 'removed': 0, 'cleanup': 0}

    for doc_name, ins_list in insertions.items():
        doc_path = DOCS[doc_name]
        if not doc_path.exists():
            print(f"ERROR: {doc_name} not found at {doc_path}")
            continue

        print(f"--- Processing {doc_name} ({doc_path.name}) ---")
        messages = process_document(doc_name, doc_path, ins_list)

        for msg in messages:
            print(msg)
            if 'INSERTED' in msg:
                stats['inserted'] += 1
            elif 'CONVERTED' in msg:
                stats['converted'] += 1
            elif 'REPLACED' in msg:
                stats['replaced'] += 1
            elif 'ALREADY PRESENT' in msg:
                stats['present'] += 1
            elif 'REMOVED' in msg:
                stats['removed'] += 1
            elif 'CLEANUP' in msg:
                stats['cleanup'] += 1
            elif 'WARNING' in msg:
                stats['warnings'] += 1

        if not messages:
            print("  (no actions taken)")
        print()

    print("=" * 70)
    print(f"SUMMARY: {stats['inserted']} inserted, {stats['converted']} converted, "
          f"{stats['replaced']} replaced, {stats['present']} already present, "
          f"{stats['removed']} removed (same zone), {stats['cleanup']} cleanup (old italic), "
          f"{stats['warnings']} warnings")
    print("=" * 70)


if __name__ == '__main__':
    main()
