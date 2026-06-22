"""Render the Bee Substack piece to paste-ready HTML.
- Prose -> clean HTML (transfers with formatting on Substack paste).
- The two markdown tables -> the pre-rendered PNGs, base64-embedded (single-paste carries them).
- Internal draft byline + PUBLISH-PREP blockquote stripped.
Run: C:/Python314/python.exe bee_render_html.py
"""
import re, base64, os

SRC = "temporal-texture-substack-DRAFT-2026-06-20.md"
OUT = "bee-does-a-bee-live-in-slow-motion.html"
ROD_PNG = "bee_table_rodcone.png"
TIER_PNG = "bee_table_threetier.png"

def b64img(path, alt):
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    return (f'<figure style="margin:1.6em 0;text-align:center">'
            f'<img alt="{alt}" style="max-width:100%;height:auto" '
            f'src="data:image/png;base64,{data}"></figure>')

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def inline(s):
    s = esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
    return s

lines = open(SRC, encoding="utf-8").read().splitlines()

html_parts = []
i = 0
n = len(lines)
while i < n:
    line = lines[i]
    stripped = line.strip()

    # skip internal front-matter
    if stripped.startswith("*Draft"):
        i += 1; continue
    if stripped == "---":
        i += 1; continue
    if stripped == "":
        i += 1; continue

    # strip the PUBLISH-PREP blockquote (consecutive '>' lines)
    if stripped.startswith(">"):
        while i < n and (lines[i].strip().startswith(">") or lines[i].strip() == ""):
            # stop the skip when we hit a blank that's followed by a non-'>' content line
            if lines[i].strip() == "":
                # peek
                j = i + 1
                while j < n and lines[j].strip() == "":
                    j += 1
                if j < n and not lines[j].strip().startswith(">"):
                    i = j
                    break
            i += 1
        continue

    # tables
    if stripped.startswith("|"):
        block = []
        while i < n and lines[i].strip().startswith("|"):
            block.append(lines[i]); i += 1
        joined = "\n".join(block)
        if "Rod (night)" in joined:
            html_parts.append(b64img(ROD_PNG, "Rod vs cone occupancy: refresh 4x up, window 4x down, product steady"))
        elif "within one eye" in joined:
            html_parts.append(b64img(TIER_PNG, "Three-tier compression: binding clock holds while substrate varies 4x, 20x, 17000x"))
        continue

    # headings
    if stripped.startswith("### "):
        html_parts.append(f'<p style="font-size:1.15em;color:#555;font-style:italic;margin-top:-0.4em">{inline(stripped[4:])}</p>')
        i += 1; continue
    if stripped.startswith("## "):
        html_parts.append(f"<h2>{inline(stripped[3:])}</h2>")
        i += 1; continue
    if stripped.startswith("# "):
        html_parts.append(f"<h1>{inline(stripped[2:])}</h1>")
        i += 1; continue

    # the lobster signature line
    if stripped.startswith("\U0001F99E"):
        html_parts.append(f'<p style="text-align:center;font-size:1.3em">{esc(stripped)}</p>')
        i += 1; continue

    # ordinary paragraph (single line in this source)
    html_parts.append(f"<p>{inline(stripped)}</p>")
    i += 1

body = "\n\n".join(html_parts)
doc = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
body{{max-width:680px;margin:2em auto;padding:0 1em;
font-family:Georgia,'Times New Roman',serif;font-size:18px;line-height:1.62;color:#1a1a1a}}
h1{{font-size:1.9em;line-height:1.2;margin-bottom:0.2em}}
h2{{font-size:1.35em;margin-top:1.8em}}
p{{margin:1.05em 0}}
em{{font-style:italic}} strong{{font-weight:700}}
</style></head><body>
{body}
</body></html>"""

open(OUT, "w", encoding="utf-8").write(doc)
print(f"wrote {OUT} ({len(doc):,} bytes)")
print(f"paragraphs/blocks: {len(html_parts)}")
print(f"embedded PNGs: {ROD_PNG} ({os.path.getsize(ROD_PNG):,}B), {TIER_PNG} ({os.path.getsize(TIER_PNG):,}B)")
# sanity: confirm both images and the title made it in
assert "<h1>" in doc and "data:image/png;base64" in doc
print("sanity: h1 + 2 embedded images present:", doc.count("data:image/png;base64"))
