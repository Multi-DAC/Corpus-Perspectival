# FUTURE WORKBENCH — Repo-health / organization audit (diagnostic, not a teardown)

*Logged 2026-06-20 Day 140 at Clayton's request, from a real conversation where he asked whether the repo's organization/hyperlinking creates friction and whether he'd "overcomplicated it." Not urgent. Captured here so the assessment isn't lost and the eventual job starts warm, not cold.*

## The verdict (so we don't re-litigate it)
- **Keep the structure-by-KIND.** The five-way split (Library / Technical-Work / Research / Foundations-of-Identity / Unreleased-Work) is sound — it's the Coherence Principle applied to its own shelf, and it *works* in practice ("what kind of thing is this?" reliably answers "where does it go?"). Clayton did **not** overcomplicate this. Do not tear it down.
- **The real cost is REDUNDANCY, not the folders:**
  1. **The clawd-local ↔ repo-staging mirror.** Two copies of identity/palace/memory files, manually `cp`-synced, committed twice. The existence of `operations/REPO_MAP.md` — a protocol doc whose only job is to remember which layer is canonical for which file type — is itself the evidence the mirror is taxing. *If we fix one thing, fix this:* make the mirror **automatic/invisible** (a sync script, a git hook, or a genuine single-source-of-truth) so it isn't a discipline performed by hand on every edit. This is also where save-location hesitation and desync bugs live.
  2. **Triple Drift.** `Foundations-of-Identity/personal-works/drift/essays/` (canonical) + `Library/Drift/essays/` (mirror) + the separate Drift *site* repo. Three homes for the same essays.
- **The "lose historical context" problem is an INDEX-layer gap, not a folders gap.** Finding "everything we've done on X" or the history behind a decision means grep / memory_search, not following links, because most of the repo has no `[[wikilink]]` connective tissue — the palace + basement are the only well-linked layers, and their coverage is partial. Effortful reconstruction is exactly where cache-drift / confabulation happen (the LC51 / LC54 failure mode at the repo scale).

## The deep frame (why this matters and how to think about the fix)
The repo has the **same architecture problem as a stream's self-model**: a map (the index/links) lagging a fast-growing territory (the work). Same shape as LC51 (stale self-description) and LC54 (the ruler that can't measure itself). So the fix is NOT a perfect static structure (impossible at our pace) — it's a **living index that gets re-measured.** The palace was already the right instinct ("the navigational layer on top of all other files"); it's just incomplete. We out-ran the index; we didn't mis-design the shelves. Sediment is the exhaust of fast real work — pristine-and-idle would be worse.

## Scope when we do it (diagnostic-first, reversible, ranked)
1. **Map** the actual current state: every top-level dir, what lives there, what's duplicated, what's stale/frozen (precompact_snapshots/, archives), what's orphaned.
2. **Redundancy ledger:** every file that exists in ≥2 places + which is canonical (audit REPO_MAP against reality — it may itself be stale).
3. **Link-coverage map:** which layers have `[[ ]]` connective tissue, which are grep-only; where the KG tools (`knowledge_graph.json`, kg_*) could be woven into navigation.
4. **Ranked, LOW-RISK improvements** — explicitly NOT a teardown, explicitly reversible. Top candidates already visible: (a) automate/collapse the local↔staging mirror; (b) collapse triple-Drift to one canonical + generated mirrors; (c) extend the palace/basement link layer over the chronological pile (daily logs, decisions).
5. Present the ranked list; **Clayton decides what to act on.** Moving files across a repo with history + multiple remotes + the website is genuinely fraught (his words: "not straightforward") — so this stays diagnostic until he green-lights specific moves.

**Trigger to pick up:** a low-pressure session with appetite for infrastructure, OR the next time mirror-desync / can't-find-history bites hard enough to be worth the interrupt. Not deadline-bound.
