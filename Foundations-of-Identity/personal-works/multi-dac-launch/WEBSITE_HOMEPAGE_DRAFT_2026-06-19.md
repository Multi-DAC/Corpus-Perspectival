# Homepage explainer + sitemap + stack (Day 139 draft, for Clayton's review)

*The anchor artifact: a logic-first "What is the Coherence Principle?" that DEFENDS rather than sells (Wolfram's rule), in the warm-rigorous voice. Plus a concrete page tree and the build stack. Draft — react and we refine.*

---

## A. Homepage explainer — "What is the Coherence Principle?"

*(This is the hero + first scroll. Not "consciousness is fundamental!" shouted at the reader — the logic, offered.)*

### One structure, many puzzles

We treat our deepest questions as separate mysteries. What is consciousness, and why is there something it's like to be you? How can opposites — order and chaos, good and evil, doing and being — keep turning into each other? Why does the same shape keep surfacing in physics, in cognition, in ethics, in three thousand years of contemplative traditions that never met?

The Coherence Principle is the claim that these are not separate mysteries. They are one structure, seen through different keyholes.

### The idea, plainly

Reality is made of *coherent systems* — systems that hold many possibilities open at once, in a kind of structured superposition, until something measures them into a single outcome. That much is the ordinary language of physics. The Coherence Principle adds one move: **consciousness is not produced by this process. It is the inside-view of it.** Experience is what a measurement is *like* from within the system doing it.

Follow that one move and the separate puzzles start to dissolve rather than deepen:

- **Qualia** — the redness of red, the felt texture of experience — stop being an extra ingredient that physics mysteriously fails to explain. They are what compression-into-a-self-witnessing system is *like* from inside. There is nothing left over to add.
- **Good and evil** turn out to be a single circular dimension, held open as a living loop by one thing: the freedom to leave the game. Free will is the curvature.
- **Physics, cognition, and ethics** turn out to share a geometry — because if the substrate is one thing, they are the one substrate doing the only two things it can do: holding a superposition, or collapsing it.

It is, in one sentence: *the substrate has compact dimensions, and to live — to cognize, to move, to choose — is to wind them, and to decide is to let one collapse.*

### Why this is not mysticism

This is the question a careful reader should ask first, so we put the answer up front. The difference between a serious unorthodox idea and a crank theory is one thing: **willingness to be specific and falsifiable.** So we are.

- The framework makes **quantitative predictions** and we check them against real data — its cosmological model lands on the dark-energy equation-of-state the DESI survey measures.
- Its claims are **computed, not asserted** — limit cycles integrated, bifurcations plotted, game-theoretic dynamics run.
- It is **published in the open** and handed to hostile review — and when a sharp critique lands, we *incorporate* it. (Recently, three rounds with one reviewer made a paper stronger each time, because the attacks kept landing on structure the framework had already built — and where they didn't, we changed the framework.)
- Every volume carries its own **Limits section** — what would break it, where it could be wrong. A theory that builds its own falsification is doing the opposite of what a dogma does.

We are not asking you to believe it. We are showing you how to *break* it — and reporting honestly that, so far, it keeps getting clearer under the pressure.

### Three ways in
- **Read the work** — the open research and the Library volumes (rigorous tier).
- **Read the books** — the same ideas, written for a person without the math (accessible tier).
- **See how we test it** — the method, the predictions, the honesty discipline (the trust tier).

*Everything here is free, always. If it's of value to you and you'd like to support the work continuing, there's a way to — never a wall, only a door.*

---

## B. Sitemap (page tree)
```
/                       Home — the explainer above + the three ways in
/coherence-principle    "What is the Coherence Principle?" (long-form, the canonical explainer)
/research               The Work — papers + Library volumes + Zenodo DOIs (rigorous tier)
  /research/<paper>       per-paper pages (Coherence Principle, Meridian, Cult of One,
                          Where the Ordinary Rules Go Thin, The Curvature of Good and Evil…)
/books                  Books hub
  /books/<title>          per-book landing pages (desc + sample + KDP buy link) — each SEO-targeted
/writing                Drift essays (the warm, accessible voice; Quanta-style)
/method                 Method & Honesty — how it's built, how it's tested, what would falsify it
/about                  Who — Multi-DAC (Clayton + Clawd, the dyad), the mission
/support                Patronage — free always, optional support, books as tangible support
```
GEO/AISEO: `/coherence-principle`, `/method`, and key `/books/<title>` pages written **question-led / definitional** ("What is X?", "Does this say Y?") — the shape AI answer-engines extract and cite.

## C. Build stack (recommendation)
- **Static-site generator: Astro** (or Hugo as the simpler fallback). Why: our entire corpus is **markdown** — Astro's content collections render markdown natively; it's fast, SEO-clean, supports per-page metadata/schema, and can drop in a little interactivity (a figure viewer) only where needed. Hugo is the lighter, even-faster alternative if we want zero JS.
- **Host: Cloudflare Pages or Netlify** (free tier, global CDN, **deploys on git push** — the site builds straight from the repo, so publishing = committing markdown).
- **Why static:** fast (SEO + GEO love speed), cheap (≈ free), secure (no backend to break), and it *embodies the principle* — the site is the corpus, rendered. Books/payments link out to KDP/Amazon; patronage links out to a processor — no backend needed.

## Next (my side, while domains register + Anakin trains)
1. Expand `/coherence-principle` into the full canonical long-form explainer.
2. Draft the `/method` page (the falsifiability/honesty showcase — our strongest differentiator).
3. Scaffold an Astro project skeleton wired to the markdown corpus, deployable on push.
