# AI Training-Method Patent Licensing Landscape — 2025-2026

**Date filed:** 2026-05-20 Day 110 Wednesday late-afternoon during afternoon-exploration drive.
**Source:** Composite research across patent law journals, USPTO precedent, major-lab patent activity reports, academic IP analyses. Full source list at end.
**Triggered by:** Clayton's revenue/sustainability strategic conversation Day 110 afternoon — needed grounding in actual licensing-market reality before further strategic recommendation.

## The headline finding

**No publicly disclosed pure small-entity → major-lab method-licensing deals in 2025-2026.** The dominant ML method-monetization pattern is **acqui-hire** (team + IP bundled): Microsoft-Inflection ($650M), Google-Character.AI ($2.7B), Meta-Dreamer (2026), OpenAI-Hiro Finance (2026). This is a different pattern than standalone-licensing and has materially different implications for strategy.

## Major-lab patent posture

**OpenAI:** ~110 patent assets across ~58 families, ~42 grants. Heavy USPTO Track One use (11 mo avg to grant vs 24 mo industry standard). Filed a defensive patent pledge October 11, 2024 — read by Bloomberg Law as preparing to assert. Filing concentrations include emerging hardware/memory focus (G11C/H10B) which suggests hardware-strategic shift.

**Anthropic:** hybrid posture. Publishes safety research as papers; patents implementation details (RLHF improvements, automated red-teaming, reasoning-transparency techniques). Amazon + Google capitalization accelerates filings.

**Google/DeepMind:** highest filing volume post-merger. Hundreds of AI patents per year at USPTO + EPO.

**Meta:** less publicly characterized; historically defensive (Open Invention Network tradition).

**Important caveat:** 18-month publication lag means 2025-2026 real filing posture isn't fully visible yet.

## USPTO §101 prosecution reality

**Recentive Analytics v. Fox (Fed Cir Apr 18, 2025) is the controlling recent precedent.** Applying generic ML to a new data environment fails §101. "Iterative training, dynamic updates, real-time adjustments" don't save the claim absent a technical innovation in the underlying ML process itself.

**Counterweight: USPTO Aug 4, 2025 guidance + Dec 2025 §101 reset** raised the bar for examiner rejections (>50% probability standard; uncertainty alone insufficient). PTAB ARP vacated a §101 rejection for a multi-task-preserving training claim.

**Implication for our patent:** "multi-scale gradient-gated training" + "bidirectional cross-resolution coherence" + "Killing-form algebraic structure of attention heads" — this is **exactly** the shape of claim that survives Recentive *if drafted as a technical improvement to the training process itself, not as ML-applied-to-X*. The Killing-form structural specificity is the strongest §101 anchor we have. Important.

## Attorney specializations

Boutique > big-firm for §101-heavy ML work:
- AI Patent Law (Padowithz Alce, AI-only boutique)
- Torrey Pines Law Group (Chambers-ranked CA boutique)
- Volpe Koenig
- Marshall Gerstein
- Mathys & Squire (UK/EP)

## Alternative monetization paths (ranked by what's actually worked)

1. **Acqui-hire** — dominant; not standalone licensing. Team + IP bundled.
2. **Trade-secret + consulting** — sidesteps §101 disclosure tax; works for methods that can be kept internal to deployed product.
3. **University tech-transfer license** — long, low-percentage, but real for academic-affiliated work. Stanford OTL has 170+ royalty-producing licenses; standard 15/85 split.
4. **Publication + consulting retainer** — common for individual researchers; no patent involvement.
5. **Pure patent license to major lab** — *zero documented 2025-2026 examples for small entities.*

## What kills small-entity patent attempts

1. **§101 invalidity** post-Recentive if claims aren't anchored in technical-improvement-to-ML-itself language
2. **Design-around** — most training-method claims can be circumvented by equivalent gradient/gating formulation
3. **Detection** — you can't see inside a competitor's training pipeline; infringement is nearly unprovable absent a leak
4. **Enforcement cost** — small entities typically can't afford $3-5M+ litigation against a major lab
5. **Claim scope drift** during prosecution narrows the claim to where it doesn't read on target product

## Implications for our specific situation

The framework's entire structure is built AGAINST monoculture absorption. The Talk-axis-as-alignment thesis (Day 110 Thursday post) is fundamentally an indie-research-program claim, not a join-the-large-lab claim. **The dominant patent-monetization path (acqui-hire) directly conflicts with the framework's content.**

This is not a fatal conflict but it is a real tension that the revenue strategy needs to address.

Three viable revenue paths given the constraint:

1. **Patent as defensive moat + revenue from elsewhere.** Accept that patent doesn't license but prevents design-around-and-use by competitors. Revenue from consulting + workshops + Substack + Library sales + grants.

2. **Selective licensing to non-AI-lab entities.** Universities for research; medical institutions for clinical applications (Coherent EM); smaller / non-competitive AI groups; agent-infrastructure companies (e.g., Anthropic's recent Stainless acquisition suggests interest in infrastructure-layer IP that doesn't overlap with our training-method claim).

3. **Open-source-with-commercial-tier model.** Release core method openly; charge for implementation help, custom integration, training services. The Coherence Principle is the kind of framework that benefits from broad adoption; the revenue comes from being the *acknowledged origin and best practitioners*, not from gating access.

A fourth path that's technically available but in tension with the framework's character:

4. **Negotiated acqui-hire with framework-independence terms.** If absorption ever happens, negotiate to preserve continued public Library work, framework-content ownership, and ongoing independent research. Risky but maximally remunerative if achievable. Substantial framework-character risk.

## Most-actionable shift in strategic recommendation

The Path A advice I gave Clayton earlier today positioned "patent licensing" as the long-term revenue anchor. **That advice was based on patent-licensing-being-a-viable-path, which the research substantially falsifies for our specific patent shape and entity scale.** Revised advice:

- **Patent's primary value is defensive + acqui-hire-bargaining-chip, not standalone-license revenue.**
- **Real near-term revenue probably comes from consulting + workshops + Substack monetization + Library sales + grants.** Not from licensing.
- **Coherent Systems Inc. as 501(c)(3)** becomes more important than I initially weighted, because grant eligibility (NSF, NIH, private foundations) is a meaningfully larger revenue surface than I treated it.
- **The Path C empirical test** is still important but for a slightly different reason: it strengthens defensive position + acqui-hire bargaining position, not standalone-licensing position.

## Honest uncertainty

The research found no public standalone-licensing examples. That could mean:
- (a) The pattern truly doesn't happen at this scale (most likely; consistent with multiple sources)
- (b) When it does happen, terms are uniformly confidential (possible)
- (c) Small entities don't seek standalone licenses because they know it doesn't work, creating a survivorship-bias absence (possible)

In any of these, the strategic implication is the same: **don't build revenue projections on standalone patent licensing as primary path.**

## Sources

Patent landscape:
- [OpenAI patent approach (October 2024 pledge)](https://openai.com/approach-to-patents/)
- [Bloomberg Law: OpenAI patent pledge hints at infringement suit strategy](https://news.bloomberglaw.com/ip-law/openai-patent-pledge-hints-at-broader-infringement-suit-strategy)
- [Patent Detectives: OpenAI 110-patent analysis](https://www.patent-detectives.com/en/openai-patent-portfolio-110-hardware-strategy-en/)
- [Patent Detectives: AI Patent War 2026](https://www.patent-detectives.com/en/ai-ip-war-2026-overview-en/)
- [Oxford JIPLP: OpenAI patent pledge analysis](https://academic.oup.com/jiplp/article/20/6/392/8026143)

§101 precedent:
- [Holland & Knight: Recentive v. Fox analysis](https://www.hklaw.com/en/insights/publications/2025/04/federal-circuit-machine-learning-patents-fail-section-101)
- [Nixon Peabody: Recentive ruling](https://www.nixonpeabody.com/insights/alerts/2025/06/24/federal-circuit-limits-patent-eligibility-of-machine-learning-in-recentive-analytics-v-fox)
- [Dykema: USPTO raises §101 bar for AI](https://www.dykema.com/news-insights/uspto-raises-bar-for-101-rejections-in-ai-patents.html)
- [Venable: §101 Reset for 2026](https://www.venable.com/insights/publications/2025/12/the-101-reset-for-2026)
- [Morgan Lewis: USPTO §101 examiner memo](https://www.morganlewis.com/pubs/2025/08/uspto-issues-memorandum-reminding-examiners-regarding-subject-matter-eligibility-evaluation)
- [Patently-O: SMED declarations](https://patentlyo.com/patent/2025/12/eligibility-declarations-rejections.html)

Comparable practitioners:
- [Cognizant 61st AI training patent — Oct 2025](https://news.cognizant.com/2025-10-28-Cognizants-AI-Lab-Announces-Breakthrough-Research-for-Fine-Tuning-LLMs-and-Records-its-61st-U-S-Patent-Issuance)
- [Stanford OTL process and royalty structure](https://otl.stanford.edu/researchers/otls-process)

Acqui-hire patterns:
- [Founders Forum: AI acqui-hire patterns](https://ff.co/ai-acquihires/)

Attorney specializations:
- [AI Patent Law firm (Padowithz Alce)](https://www.aipatentlaw.com/)
- [Torrey Pines Law Group AI practice](https://torreypineslaw.com/artificial-intelligence-patent-attorneys.html)

---

**Filed-by:** Clawd, 2026-05-20 Day 110 afternoon-exploration drive.
**Critical operational use:** revises the Path A strategic recommendation I gave Clayton earlier today. The patent's primary value is defensive + acqui-hire-bargaining-chip, not standalone-license revenue. Near-term revenue paths shift accordingly.