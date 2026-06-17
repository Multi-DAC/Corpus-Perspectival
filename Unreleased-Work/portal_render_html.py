import markdown, re

SRC = r"C:\Users\mercu\clawd\repo-staging\Corpus-Perspectival\Unreleased-Work\place-threshold-mechanism-DRAFT.md"
OUT = r"C:\Users\mercu\clawd\repo-staging\Corpus-Perspectival\Unreleased-Work\place-threshold-mechanism.html"

with open(SRC, encoding="utf-8") as f:
    md = f.read()

# Render braced super/subscripts so the inline physics reads cleanly on Substack
# (e^{aσ}, λ^{2−D}, F^{μν}, 10^{28}, Q^{1.1}, ...). Bare single-char ∂_μ / A^μ left as-is.
md = re.sub(r'\^\{([^}]*)\}', r'<sup>\1</sup>', md)
md = re.sub(r'_\{([^}]*)\}',  r'<sub>\1</sub>', md)

html_body = markdown.markdown(
    md, extensions=["tables", "fenced_code", "extra", "sane_lists", "smarty"])

CSS = """
body{max-width:820px;margin:40px auto;padding:0 22px;
 font-family:Georgia,'Times New Roman',serif;font-size:18px;line-height:1.62;color:#241a12;}
h1,h2,h3{font-family:'Helvetica Neue',Arial,sans-serif;color:#8c2f1d;line-height:1.25;}
h1{font-size:30px;margin:0 0 .1em;}
h2{font-size:23px;margin:1.6em 0 .5em;border-bottom:1px solid #e6d8c2;padding-bottom:.18em;color:#7a2818;}
h3{font-size:19px;color:#1F3A5F;margin:1.2em 0 .35em;}
em{color:#5a4632;}
strong{color:#241a12;}
sup,sub{font-size:.72em;line-height:0;}
blockquote{border-left:3px solid #e0934b;margin:1.4em 0;padding:.2em 1.1em;
 color:#5a4632;font-style:italic;background:#faf5ec;}
table{border-collapse:collapse;margin:1.2em 0;font-size:14px;width:100%;
 font-family:'Helvetica Neue',Arial,sans-serif;}
th,td{border:1px solid #e6d8c2;padding:5px 8px;text-align:center;vertical-align:top;}
th{background:#f2d9a8;color:#3a2a1a;}
td:nth-child(2){text-align:left;}
img{max-width:100%;height:auto;display:block;margin:1.2em auto;
 border:1px solid #eadfce;border-radius:4px;}
hr{border:none;border-top:1px solid #e6d8c2;margin:2em 0;}
code{background:#f4ece0;padding:1px 5px;border-radius:3px;font-size:.92em;}
a{color:#8c2f1d;}
"""

doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Where the Ordinary Rules Go Thin</title><style>{CSS}</style></head>
<body>{html_body}</body></html>"""

with open(OUT, "w", encoding="utf-8") as f:
    f.write(doc)

print("wrote", OUT, "| chars:", len(doc),
      "| tables:", doc.count("<table>"),
      "| imgs:", doc.count("<img"),
      "| sup:", doc.count("<sup>"),
      "| leftover ^{:", doc.count("^{"),
      "| leftover _{:", doc.count("_{"))
