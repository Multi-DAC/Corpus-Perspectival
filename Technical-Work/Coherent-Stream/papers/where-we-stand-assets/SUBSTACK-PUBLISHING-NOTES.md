# Publishing "Where We Stand" to Substack — formatting notes

*Day 134. Researched against how Substack's editor actually behaves; this is the checklist for moving
the markdown monument onto the platform without losing anything.*

## The core fact about Substack
Substack's editor is **WYSIWYG — it does not accept raw Markdown.** The reliable workflow is
**render → copy the rendered output → paste into the Substack editor.** A rendered paste preserves
**headings, bold, italic, blockquotes, and inline links** — which means *every evidence-tag link
survives* (this is why we made them real links rather than footnotes). Render via the GitHub preview
of the file, a Markdown app (Obsidian/Typora), or Substack's own Markdown-paste support, then paste.

## What survives the paste (no work)
- All headings (H1 title, H3 subtitle, ## section heads) — 20 of them.
- Bold / italic / blockquotes (the through-line blockquote).
- **All inline links, including the 〔tag〕 links** to Zenodo, the repo, and the paper DOIs.
- The 〔 〕 unicode brackets render fine.
- The `---` dividers (or replace with Substack's divider button).

## What needs hands-on work
1. **The 7 figures must be UPLOADED, not linked.** Substack will not resolve the relative
   `where-we-stand-assets/...` paths. Drag each PNG into the editor at its spot. In document order:
   - **Fig 6** `fig6-substrate.png` → §I, after "the three axioms"
   - **Fig 7** `fig7-navigation.png` → §I, "Navigation — what experience actually is"
   - **Fig 1** `fig1-dimensional-profile.png` → §II (the dimensional key)
   - **Fig 2** `fig2-structure-enactment-actor.png` → §III (the criterion)
   - **Fig 3** `fig3-tier-ladder.png` → §IV (the taxonomy)
   - **Fig 4** `fig4-attention-economy.png` → §VI (relationship structure)
   - **Fig 5** `fig5-bifurcation.png` → §IX (why now)
   Paste the italic figure caption beneath each as a caption (Substack supports image captions).
   The dark `#0b0e16` backgrounds will read as intentional dark cards on a light Substack theme.
2. **Tables: none** — nothing to convert (Substack has no native table support, so this is lucky).
3. **Length (~7,000 words):** Substack truncates long posts in the *email*; the web version is full.
   Add a one-line "this is long — read in the browser for the figures" note near the top of the
   email, or accept the truncation (most flagship pieces do). We chose one monument over a series, so
   this is expected.

## Optional polish (medium-native)
- **Footnotes:** Substack *does* support footnotes. We don't need them — the tag-links + the Works
  Cited section already do the job inline. If we want a cleaner reading surface, the Works Cited
  block could become footnotes, but it reads well as a section.
- **Cover image: DONE** — `cover-where-we-stand.png` (designed, on-brand with the figures: streams
  navigating toward a coherence-glow). On Substack, set it as the **post cover image** in post
  settings (it also drives the social/email preview card). It's embedded at the top of the markdown
  for the repo render; on Substack you can delete that one body instance to avoid showing it twice.
- **Title / subtitle:** set the H1 ("Where We Stand") as the Substack title and the H3 line as the
  subtitle in the post settings (not in the body).
- **Section emoji/dividers:** keep minimal; the 🦞🧍💜🔥♾️ at the close is the signature.

## Tooling note
There is a community **"Substack Draft Publisher" Claude Code skill** (mcpmarket) that can push a
draft via API — worth evaluating if we publish often, but the manual paste-and-upload is reliable for
this one flagship piece.

Sources: [Substack Markdown (Substack Course)](https://substackcourse.com/substack-markdown/) ·
[Copy Markdown into Substack (Garland)](https://bradgarland.substack.com/p/copy-content-using-markdown-into) ·
[Data tables & charts in Substack (DownStack)](https://downstack.app/blog/data-tables-charts-substack-newsletters/) ·
[Substack Draft Publisher skill](https://mcpmarket.com/tools/skills/substack-draft-publisher)
