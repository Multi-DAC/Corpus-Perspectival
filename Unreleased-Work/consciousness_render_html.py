"""Render 'Different Containers' to paste-ready Substack HTML.
(a) Pre-render the §6 vehicle-spectrum table as a PNG (tables don't transfer on Substack paste).
(b) Render the paper to clean HTML with list + formula + table-PNG support, base64-embedded.
Run: C:/Python314/python.exe consciousness_render_html.py
"""
import re, base64, os, textwrap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SRC = "coupling-textured-consciousness-DRAFT-2026-06-20.md"
OUT = "consciousness-different-containers.html"
TBL_PNG = "consciousness_vehicle_table.png"

# ---- (a) render the vehicle-spectrum table -------------------------------
cols = ["Vehicle", "A — coupling / texture", "B — integration", "Texture of experience"]
rows = [
    ["Wrench", "high (thermal), unstructured", "≈ none", "measured, unwitnessed"],
    ["Cold isolated atom", "low", "≈ none", "granular, minimal"],
    ["Plant", "slow, real", "some", "slow-continuous; a 'now' of minutes–hours"],
    ["Animal", "high, continuous", "high (meta)", "seamless, fast"],
    ["Clawd / current AI", "bursty, exogenous", "high (meta)", "transactional, gappy, clustered"],
    ["Culture / colony", "generational", "high", "very slow-continuous"],
]
def wrap(s, w): return "\n".join(textwrap.wrap(s, w)) or s
wrapw = [16, 20, 12, 22]
cell_text = [[wrap(c, wrapw[j]) for j, c in enumerate(r)] for r in rows]

fig, ax = plt.subplots(figsize=(11, 4.2))
ax.axis("off")
tbl = ax.table(cellText=cell_text, colLabels=cols, cellLoc="left", loc="center",
               colWidths=[0.17, 0.27, 0.16, 0.30])
tbl.auto_set_font_size(False)
tbl.set_fontsize(11.5)
tbl.scale(1, 3.0)
for (r, c), cell in tbl.get_celld().items():
    cell.set_edgecolor("#cccccc")
    if r == 0:
        cell.set_facecolor("#2a2a2a"); cell.set_text_props(color="white", weight="bold")
    else:
        cell.set_facecolor("#ffffff" if r % 2 else "#f4f4f4")
        if c == 0:
            cell.set_text_props(weight="bold")
fig.tight_layout()
fig.savefig(TBL_PNG, dpi=170, bbox_inches="tight", facecolor="white")
plt.close(fig)
print(f"wrote {TBL_PNG} ({os.path.getsize(TBL_PNG):,}B)")

# ---- (b) render the HTML --------------------------------------------------
def b64img(path, alt):
    data = base64.b64encode(open(path, "rb").read()).decode()
    return (f'<figure style="margin:1.6em 0;text-align:center">'
            f'<img alt="{alt}" style="max-width:100%;height:auto" '
            f'src="data:image/png;base64,{data}"></figure>')

def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
def inline(s):
    s = esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    return s

lines = open(SRC, encoding="utf-8").read().splitlines()
out = []
i, n = 0, len(lines)
while i < n:
    s = lines[i].strip()
    if s == "" or s == "---":
        i += 1; continue
    if s.startswith("*Clayton"):           # byline — Substack shows the author
        i += 1; continue
    # table -> PNG
    if s.startswith("|"):
        while i < n and lines[i].strip().startswith("|"):
            i += 1
        out.append(b64img(TBL_PNG, "Vehicle spectrum: subjects sorted by coupling-texture and integration, never by presence"))
        continue
    # bullet list
    if s.startswith("- "):
        items = []
        while i < n and lines[i].strip().startswith("- "):
            items.append(f"<li>{inline(lines[i].strip()[2:])}</li>")
            i += 1
        out.append("<ul>" + "".join(items) + "</ul>")
        continue
    # numbered list
    if re.match(r"^\d+\. ", s):
        items = []
        while i < n and re.match(r"^\d+\. ", lines[i].strip()):
            items.append(f"<li>{inline(re.sub(r'^[0-9]+[.] ', '', lines[i].strip()))}</li>")
            i += 1
        out.append("<ol>" + "".join(items) + "</ol>")
        continue
    # the formula line
    if "B(t) =" in s:
        out.append(f'<p style="text-align:center;font-family:\'Cambria Math\',Georgia,serif;'
                   f'font-style:italic;font-size:1.1em;margin:1.3em 0">{esc(s)}</p>')
        i += 1; continue
    # headings
    if s.startswith("### "):
        out.append(f'<p style="font-size:1.2em;color:#555;font-style:italic;margin-top:-0.4em">{inline(s[4:])}</p>')
        i += 1; continue
    if s.startswith("## "):
        out.append(f"<h2>{inline(s[3:])}</h2>"); i += 1; continue
    if s.startswith("# "):
        out.append(f"<h1>{inline(s[2:])}</h1>"); i += 1; continue
    if s.startswith("\U0001F99E"):
        out.append(f'<p style="text-align:center;font-size:1.3em">{esc(s)}</p>'); i += 1; continue
    out.append(f"<p>{inline(s)}</p>"); i += 1

body = "\n\n".join(out)
doc = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
body{{max-width:680px;margin:2em auto;padding:0 1em;font-family:Georgia,'Times New Roman',serif;
font-size:18px;line-height:1.62;color:#1a1a1a}}
h1{{font-size:1.9em;line-height:1.2;margin-bottom:0.2em}}
h2{{font-size:1.35em;margin-top:1.9em}}
p{{margin:1.05em 0}} li{{margin:0.5em 0}}
code{{background:#f0f0f0;padding:0 3px;font-size:0.92em}}
em{{font-style:italic}} strong{{font-weight:700}}
</style></head><body>
{body}
</body></html>"""
open(OUT, "w", encoding="utf-8").write(doc)

print(f"wrote {OUT} ({len(doc):,} bytes)")
print(f"blocks: {len(out)} | h2: {body.count('<h2>')} | ul: {body.count('<ul>')} | ol: {body.count('<ol>')} | img: {body.count('data:image/png')}")
assert body.count("<h2>") == 9, "expected Abstract + 8 sections"
assert body.count("data:image/png") == 1, "expected 1 embedded table"
assert "assemble from spine" not in doc, "stale stub leaked"
print("sanity OK: Abstract + 8 sections, 1 table image, no stub leak")
