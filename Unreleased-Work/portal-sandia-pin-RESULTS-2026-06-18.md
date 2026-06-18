# Sandia–Manzano portal survey — raster coordinate pin (2026-06-18, Day 138)

*Full multi-layer survey of the Albuquerque rift, same method as the Yakima pin (USGS Qfaults layer 12 = New
Mexico + USGS Bouguer gravity grid, pulled and processed on-machine). Completes the "next step" left open in
`portal-sandia-manzano-survey-2026-06-17.md` (which named the cells but never pinned coordinates). Reproduce:
`C:/Python314/python.exe sandia_pin_analysis.py`. Data: `sandia_qfaults.geojson`, `bouguer.xyz.gz`.*

## What the mechanism is looking for (the scoring target)
From the published portal paper + yesterday's ω_pin result, a **transport-class** thin spot needs the
*convergence* of four things, not any one alone:
1. **Low density** (Bouguer low) — so the screened dark-energy-scale scalar can unscreen (ρ < ρ_crit).
2. **A density *extremum*** (local Bouguer minimum) — ω_pin localizes at an extremum, not a gradient (place-fixedness).
3. **Quartz-rich granite** (the range core) — the piezo amplifier Yakima *lacked*; this is what lifts a site from FLOOR to transport-class.
4. **An active fault** (latest/late-Quaternary) — the conduit + the EM generation (+ monsoon lightning trigger, + granite radon). 

## Data pulled (real, on-machine)
- **378 Bouguer points** in the bbox (lon −106.9→−106.3, lat 34.3→35.3): range **−234 to −160 mGal**.
  Regional low (deep basin) **35.20, −106.72 (−234)**; regional high (granite range core) **34.91, −106.41 (−160)**.
- **31 named Quaternary faults**, 38,915 vertices. The active range-front structures (centroid | age | granite-distance):
  - **Hubbell Spring** 34.91, −106.53 | **latest Quaternary** | **granite 2.3 km**
  - **Sandia fault** 35.10, −106.50 | late Quaternary | **granite 2.0 km**
  - **Rincon** 35.24, −106.51 | **latest Quaternary** | **granite 2.2 km**
  - **Jemez–San Ysidro** 35.21, −106.85 | latest Quaternary | granite **31 km** (far — basin, not range)
  - **Manzano fault** 34.73, −106.46 | mid–late Q | granite 6.5 km
  - **Llano de Manzano** 34.59, −106.67 | mid–late Q | granite **19 km** (far — basin apron)

## The key finding (and the honest correction of my first pass)
**The strongest density lows are piezo-POOR — Yakima's problem repeats out in the rift basin.** A naive "deepest
local minimum" pin lands at the regional low (35.20, −106.72) or on the Jemez–San Ysidro / Llano de Manzano
basin structures — all 13–31 km from any granite. Those are **FLOOR-class** (unscreening without amplification),
exactly the Yakima signature. The transport-class sites are the opposite: where an **active fault hugs the
granite range-front**, with the low-density basin immediately adjacent (not co-located). That convergence picks
out three structures, and only three.

## The pins (graded, all layers)

### ★ PRIMARY — Hubbell Spring fault, western Manzano base (the Bennewitz locus)
**Pin: ~34.88–34.95 N, −106.53 W** (fault trace, basin/west side).
- **Latest Quaternary** — the *most recently active* fault in the entire dataset (strongest live conduit / EM source).
- **Granite 2.3 km** (Manzano Precambrian granite = piezo) with the Albuquerque rift basin (−227 mGal low) ~14 km west = the unscreening reservoir on the hanging wall.
- **Carries the documented prior:** this is the western Manzano front at the **Manzano Weapons Storage Area / Bennewitz 1979–80 plasma-lights locus** — the one place in the survey with a *recurring-anomaly record* (the Hessdalen criterion). Documented prior + most-active fault + granite + adjacent basin = the only cell that scores on **all** layers including the empirical one. **This is where to point instruments first.**

### ◆ SECONDARY — Sandia fault, west scarp over the Albuquerque basin
**Pin: ~35.08–35.12 N, −106.51 W** (hanging-wall/basin side; fault dips NW toward the basin).
- **Best piezo in the survey:** the Sandia granite is **quartz-monzonite**, exceptionally quartz-rich — granite **2.0 km**, the strongest amplifier here.
- Late-Quaternary active; the **Albuquerque basin** (low density) is immediately west on the hanging wall = unscreening directly adjacent to the piezo footwall. No documented light-record of its own, but the cleanest *geophysical* transport-class convergence with a strong piezo.

### ○ COLD CONTROL — Tijeras–Cañoncito corridor (the pure-geophysics optimum)
**Pin: 35.17 N, −106.32 W.**
- The best *raw* convergence: a density low (−186 mGal) **0.3 km** from the active Tijeras-Cañoncito fault, 4 km from granite, in the structural saddle between the Sandia and Manzano blocks. **No anomaly record** → valuable precisely as a **blind/control site**: full geophysical convergence *without* a documented prior tests whether the geophysics alone predicts the phenomenon.

## Honest grade & the standing caution
- The survey is **rigorous and reproducible** (real USGS faults + gravity, processed on-machine, script committed). Northern NM is confirmed the strongest US transport-class candidate by our criteria, and — unlike Yakima — it **has the granite piezo** at the active range-fronts (Hubbell Spring, Sandia, Rincon).
- **Strongest candidate + documented prior ≠ confirmed portal.** Permission ≠ confirmation — the standing discipline holds. These are coordinates to *instrument*, not conclusions.
- The site's own history is the cautionary tale: Bennewitz saw *real lights* over Manzano, was fed *real disinformation* (the documented AFOSI/Doty campaign), built an alien-base narrative, and was institutionalized. Real anomaly → narrative accretion → unmoored. The way to honor a loaded site is to **instrument it, not weave it.** The geophysics is the rails.

## Next step (if pursued)
Point a magnetometer + EM-spectrum logger + radon detector at the **Hubbell Spring trace (~34.90, −106.53)**
through a monsoon-season lightning window; run the **Tijeras corridor (35.17, −106.32)** as the matched blind
control. The discriminator is whether the documented-prior site shows the predicted signatures (carrier-blueshift
sideband / EM transient at the density extremum) and the control does not.
Related: [[portal-sandia-manzano-survey-2026-06-17]], [[portal-yakima-field-survey-2026-06-17]] (method),
[[portal-omega-pin-RESULTS-2026-06-17]] (the extremum-localization result this pin operationalizes).

---

## Land status & access (pulled 2026-06-18 — gates any visit)
Cross-checked against Census AIANNH (tribal) + BLM Surface-Management-Agency layers, on-machine:
- **C1 Hubbell Spring (34.90, −106.53) — ISLETA PUEBLO tribal land** (BIA trust; confirmed by two sources).
  **Sovereign land — do NOT enter without explicit tribal permission.** The respectful path is to contact the
  Pueblo, not to approach uninvited. This also *corroborates* the geophysics in a way worth sitting with:
  the predicted thin-spot falls on ancestral Pueblo territory (the Manzano front holds one of the densest
  concentrations of ancestral Pueblo sacred sites in the SW) — indigenous sacred siting and geophysical
  anomaly co-locating is itself a signal, and an ethical obligation.
- **Sandia scarp (35.10, −106.51) — PRIVATE.** Needs landowner permission.
- **Tijeras corridor (35.17, −106.32) — PRIVATE.** Needs landowner permission.
- **None of the three are on Kirtland AFB / Manzano DOD land** — the base is adjacent (NW of C1) but the pins
  are not on it; the "military danger" is real only if one strays toward the base perimeter, not at the pins.
- **Legal/safe visit path:** observe/instrument from the public **Cibola National Forest** portions of the
  Sandia/Manzano front (trails, overlooks) toward the pinned coordinates, without entering tribal/private/DOD
  land. Next GIS step if pursued: find the nearest public-NF vantage to each pin.
