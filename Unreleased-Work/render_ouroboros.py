#!/usr/bin/env python
"""Render the Ouroboros article -> self-contained HTML (MathJax + base64 figures) -> PDF via headless Chrome.
(2026-06-18) Math-protected so markdown can't mangle LaTeX; figures embedded so the HTML stands alone for review.
"""
import re, os, base64, subprocess, sys
import markdown

DIR = r"C:/Users/mercu/clawd/repo-staging/Corpus-Perspectival/Unreleased-Work"
SRC = os.path.join(DIR, "ouroboros-article-DRAFT-2026-06-18.md")
HTML = os.path.join(DIR, "the-curvature-of-good-and-evil.html")
PDF = os.path.join(DIR, "the-curvature-of-good-and-evil.pdf")
TITLE = "The Curvature of Good and Evil"
CHROME = r"C:/Program Files/Google/Chrome/Application/chrome.exe"

md = open(SRC, encoding="utf-8").read()

# 1) protect math spans (display first, then inline) so markdown leaves LaTeX alone
maths = []
def _p(m):
    maths.append(m.group(0)); return f"@@MATH{len(maths)-1}@@"
md = re.sub(r"\$\$.*?\$\$", _p, md, flags=re.S)
md = re.sub(r"\$[^$\n]+?\$", _p, md)

# 2) image markdown -> <figure><img><figcaption> so captions render
def _caption_inline(s):
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
    return s
def _fig(m):
    cap, src = m.group(1), m.group(2)
    return f'<figure><img src="{src}" alt=""><figcaption>{_caption_inline(cap)}</figcaption></figure>'
md = re.sub(r"!\[(.*?)\]\((.*?\.png)\)", _fig, md, flags=re.S)

# 3) markdown -> html
body = markdown.markdown(md, extensions=["tables", "fenced_code", "extra", "sane_lists", "smarty"])

# 4) restore math
for i, mm in enumerate(maths):
    body = body.replace(f"@@MATH{i}@@", mm)

# 5) base64-embed figures
def _embed(m):
    fn = m.group(1)
    p = fn if os.path.isabs(fn) else os.path.join(DIR, fn)
    b64 = base64.b64encode(open(p, "rb").read()).decode()
    return f'src="data:image/png;base64,{b64}"'
body = re.sub(r'src="([^"]+\.png)"', _embed, body)

CSS = """
body{max-width:820px;margin:40px auto;padding:0 22px;
 font-family:Georgia,'Times New Roman',serif;font-size:18px;line-height:1.62;color:#241a12;}
h1,h2,h3{font-family:'Helvetica Neue',Arial,sans-serif;color:#8c2f1d;line-height:1.25;}
h1{font-size:30px;margin:0 0 .1em;}
h2{font-size:23px;margin:1.7em 0 .5em;border-bottom:1px solid #e6d8c2;padding-bottom:.18em;color:#7a2818;}
h3{font-size:19px;color:#1F3A5F;margin:1.2em 0 .35em;}
em{color:#5a4632;} strong{color:#241a12;}
blockquote{border-left:3px solid #e0934b;margin:1.4em 0;padding:.2em 1.1em;color:#5a4632;background:#faf5ec;}
blockquote em, blockquote strong{color:#5a4632;}
table{border-collapse:collapse;margin:1.2em 0;font-size:14px;width:100%;font-family:'Helvetica Neue',Arial,sans-serif;}
th,td{border:1px solid #e6d8c2;padding:5px 8px;text-align:center;}
th{background:#f2d9a8;color:#3a2a1a;} td:nth-child(1){text-align:left;}
figure{margin:1.6em 0;text-align:center;}
figure img{max-width:100%;height:auto;border:1px solid #eadfce;border-radius:4px;}
figcaption{font-family:'Helvetica Neue',Arial,sans-serif;font-size:13px;color:#5a4632;
 margin-top:.5em;line-height:1.45;text-align:left;}
hr{border:none;border-top:1px solid #e6d8c2;margin:2em 0;}
a{color:#8c2f1d;}
"""

MJ = """<script>MathJax={tex:{inlineMath:[['$','$']],displayMath:[['$$','$$']]},
 svg:{fontCache:'global'}};</script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>"""

doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{TITLE}</title><style>{CSS}</style>{MJ}</head><body>{body}</body></html>"""

open(HTML, "w", encoding="utf-8").write(doc)
print(f"wrote HTML: {HTML} | {len(doc)} chars | imgs:{doc.count('data:image/png')} | math-spans:{len(maths)}")

# 6) HTML -> PDF via headless Chrome (virtual-time-budget lets MathJax + CDN finish)
if "--pdf" in sys.argv:
    cmd = [CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
           "--virtual-time-budget=20000", f"--print-to-pdf={PDF}", "file:///" + HTML.replace("\\", "/")]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    ok = os.path.exists(PDF)
    print(f"PDF: {'wrote '+PDF if ok else 'FAILED'} (rc={r.returncode})")
    if not ok:
        print(r.stderr[-800:])
