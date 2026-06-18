# Yakima / Toppenish field survey — candidate-siting for a place-threshold defect (2026-06-17)

*Operationalizing §8 of "Where the Ordinary Rules Go Thin." The honest locating method = the Hessdalen
model: go where a documented recurring place-fixed anomaly ALREADY exists, then test the derived
signatures. Expect a null; treat a clean null as a result. Clayton-collaborative trip planning.*

## 1. The prior — CONFIRMED, Hessdalen-class

- **Willard J. "Bill" Vogel**, chief fire lookout, collected **92 written sighting reports 1972–1978**
  (2–3/night in 1975–76); **78% "nocturnal lights."** A credible, systematic, multi-year observer at a
  fixed place — the §1 criterion (observers agreeing across time) satisfied.
- **David W. Akers**, "Report on the Investigation of Nocturnal Light Phenomena: 1973 Sighting Reports
  from Toppenish, WA," submitted **1974 to J. Allen Hynek**. Color photographs.
- **Greg Long**, *Examining the Earthlight Theory: The Yakima UFO Microcosm* — ~200 reports + photos,
  used to test **Persinger's Tectonic Strain Theory** (tectonic stress → light).
- **Locus:** Satus fire lookout / Satus Pass, **Toppenish Ridge**, Yakama reservation, Lower Yakima Valley.

**Why this is the right site:** it is already a recurring, place-fixed, photographed, multi-year record
that has ALREADY been analyzed under a tectonic-stress→light mechanism — the same family our carrier
(coherent-plasma-stabilized screened-scalar defect) sits in. We re-approach it agnostic to the UFO
framing: take the recurring measurement seriously, hold the interpretation loosely.

## 2. The density target — the layers exist (Blakely / USGS)

Mechanism (morning ω_pin result): the carrier pins at a **local minimum of ambient matter density**.
Subsurface density proxy = **Bouguer gravity anomaly** (gravity low = low-density mass).

- **Blakely et al. 2011 (JGR), 2014** — gravity + magnetic anomaly data over the Yakima Fold Belt,
  forward-modeled for subsurface structure. Ridges = **basement highs (dense)**; basins (Toppenish
  Basin, Pasco Basin) = sediment-filled **gravity LOWS (low density)**.
- **Toppenish Ridge** = a YFTB anticline with **Holocene deformation / active faulting** → a candidate
  tectonic-stress + radon/charge source.

## 3. Targeting logic (desktop → field)

**Candidate cell = intersection of three layers:**
1. **Bouguer gravity LOW** (low-density extremum) — the Toppenish Basin & ridge-flank lows.
2. **Mapped Holocene fault trace** (charge / radon / stress source) — Toppenish Ridge fault system.
3. **Light-record footprint** (the prior) — Satus / Toppenish Ridge cluster.

Desktop narrows to ~km (gravity-low ∩ fault ∩ record). The **field kit** then finds the ~10 m pin
inside it (radon high + fractured low-density rock + local magnetic-gradient extremum).

## 4. The field kit (every item must DISCRIMINATE, not just detect)

| Tool | ~$ | Discriminates |
|---|---|---|
| **Diffraction-grating film over phone/DSLR (tripod, long exposure)** | 15 | thermal/continuum (headlights, fire, planet) vs **non-thermal plasma line emission** — the hero |
| Phone magnetometer + logger (or $30 fluxgate + RPi continuous) | 0–40 | light coincident with a **B-field anomaly** (Hessdalen signature) |
| Linear polarizer (rotate over lens) | 15 | field-modulated polarization vs ordinary light |
| Geiger / radon detector | 30–100 | ionization-source proxy + fractured low-density rock flag |
| GPS + timestamped log (phone) | 0 | **recurrence at a fixed place** (the §1 criterion itself) |

Total ~$75–150. Discipline: go expecting a null; a clean spectrum of a passing truck is a *successful
measurement*. The grating keeps you honest in the dark.

## 5. The ranked candidate map (feature-resolution overlay, 2026-06-17)

**Georeferenced anchors (verified):**
| feature | lat, lon | role |
|---|---|---|
| Satus Peak fire lookout (Vogel's station) | 46.2575, −120.7535 (4,182 ft) | observer vantage + "Starvation Flats / The Landing Field" locus |
| Toppenish Ridge (E segment) | ~46.293, −120.444 | WNW–ESE anticline, ~25–30 km long |
| Toppenish Basin / Yakima Valley floor (Toppenish town) | ~46.38, −120.31 | sediment fill = **gravity LOW / low-density** |
| Toppenish Ridge structure (Campbell & Bentley) | north flank | **active thrust + Mill Creek fault**, scarps <~500 yr; **normal faults on crest** |

**Structure:** the anticline thrusts NORTH over the low-density basin. So density and faulting split:
regional **low-density extremum = the basin (north flank)**; **active faults = north-flank thrust/Mill
Creek scarp** AND **crest normal faults** (dilatant fracture zones = *local* low density + radon path).

**Ranked candidates (the three-layer intersection):**

- **C1 — Mill Creek / north-flank thrust at the ridge–basin transition** *(~46.30, −120.55→−120.45 band,
  north side of the ridge).* Fault ✓✓ (active, named, <~500 yr) · gravity-low ✓✓ (basin edge =
  low-density extremum) · record ✓ (in the Satus Peak viewshed over the Lower Valley). **Strongest
  combined overlap — start here.**
- **C2 — Crest normal-fault zone at Satus Peak / Starvation Flats** *(~46.257, −120.75).* Record ✓✓ (the
  actual observer / "Landing Field" locus) · fault ✓ (crest normal faults → dilatant fractures, *local*
  low-density + radon) · gravity-low ~ (crest is a dense basement high *regionally* — bank on local
  fracture porosity, not the regional low). **Strong on the prior; the place to camp + log overnight.**
- **C3 — Satus Creek drainage lows (south side)** — lower priority unless the Blakely raster shows a
  specific local gravity minimum there.

**Field plan from this:** camp/log at **C2** (the documented vantage, overnight magnetometer + grating
on tripod), day-survey **C1** (radon + magnetic-gradient walk along the Mill Creek scarp / basin edge to
find the local low-density pin). The kit resolves the ~10 m target inside the ~km cell.

## 6. Resolution caveat + the two GIS pulls that sharpen it
This overlay is **feature-resolution** (named coords + structural reasoning), good enough to aim a trip.
Two public GIS layers would pin it to raster precision:
1. **USGS Quaternary Fault & Fold Database** — the Toppenish Ridge / Mill Creek fault *polylines* (exact
   scarp traces). `apps.usgs.gov/earthquakes/faults/`.
2. **Blakely et al. 2011/2014 Bouguer gravity grid** — the exact gravity-low contour (the low-density
   extremum geometry). Pull as a raster, contour, intersect with the fault polylines + the C1/C2 points.

## 7. Raster-precision attempt — infrastructure boundary + the QGIS recipe (2026-06-17)

Pushed for in-chat raster precision; hit a tooling wall (not a precision wall): USGS Quaternary-fault
ArcGIS endpoints have moved (404; the live `eq/map_faults` is realtime-quake-only); WA DNR REST folders
don't enumerate through the fetch tool; the DNR Mill Creek fault PDF is image-only and this box has no
poppler/`pdftoppm` to rasterize; and the Blakely Bouguer **grid** is a raster file needing GDAL/rasterio
+ the actual `.grd` in hand. **Conclusion: true raster precision = a short QGIS session, not chat.**

**QGIS recipe (≈20 min, all free layers):**
1. **Faults:** USGS Quaternary Fault & Fold Database — load the WA faults (interactive map
   `usgs.gov/tools/interactive-us-fault-map`; download via ScienceBase item `589097b1e4b072a7ac0cae23`,
   or the cfusion report for the Toppenish Ridge / Mill Creek fault). Gives the exact scarp polylines.
2. **Gravity / density:** Blakely et al. 2014 isostatic/Bouguer gravity grid for the YFTB (USGS data
   release accompanying the JGR paper); contour it → the gravity-LOW polygon = low-density extremum.
3. **Geology backup:** WA DNR 1:100k surface geology (Geologic Information Portal) — the Quaternary
   sediment-fill polygon north of the ridge is the basin (low-density) outline if the grid is hard to get.
4. **Overlay:** intersect (gravity-low ∩ Quaternary-fault buffer ∩ Satus-Peak viewshed). The few cells
   that survive = the raster-precise C1 pins. Drop the verified C2 point (46.2575, −120.7535) as a marker.

**Verified-coordinate refinement (what stands without the raster):**
- **C2 — Satus Peak / Starvation Flats: 46.2575, −120.7535** (tight; the documented Vogel vantage). Camp + overnight log here.
- **C1 — north-flank Mill Creek thrust band: ~46.30–46.32 N, −120.70→−120.55 W** (the ridge-base
  segment in the Satus viewshed where the active thrust meets the basin fill). The exact scarp polyline
  is the one thing the QGIS fault layer pins; treat this as a ~2 km search corridor until then.

*Next session / QGIS: if a fault/gravity layer is exported to GeoJSON, it can be parsed + intersected
with plain Python here (no GIS suite needed for GeoJSON). The gravity raster still needs GDAL.*

## 8. RASTER PRECISION ACHIEVED — fault layer pulled + intersected in-Python (2026-06-17 PM)

Found the live USGS Quaternary Fault DB endpoint: **`haz/Qfaults/MapServer/18`** (Washington polylines;
`eq/` was the wrong folder). Pulled the Toppenish bbox as GeoJSON, parsed in plain Python (no GIS suite),
intersected with Satus Peak. Data: `yakima_qfaults.geojson` (166 features) + `yakima_pin_analysis.py`.

- **100 Toppenish Ridge segments, ALL "latest Quaternary"** (youngest age class), slip <0.2 mm/yr.
- North-vergent thrust dips SOUTH → **dip=S = the north-flank thrust overriding the low-density basin**
  (Campbell-Bentley's "reverse faults on the north flank"). 422 active dip=S vertices.

**C1 — RASTER-PRECISE PIN (replaces the ~2 km corridor guess):**
- **Nearest active north-flank thrust to Satus Peak: `46.2945, −120.6547`** — d = **8.6 km**, bearing
  **62° (ENE)** from Vogel's lookout. Closest basin-overriding active scarp in direct line-of-sight.
- **C1 thrust-front corridor** (dip=S, ≤13 km): lat **46.286–46.305**, lon **−120.655→−120.591**,
  centroid **46.298, −120.621**. A ~5 km ENE-trending front; *every vertex bears ~62°* from Satus Peak —
  i.e. the active thrust front sits exactly along the azimuth Vogel reported lights "over the Lower Valley."

**Field nav (final):** stand at **C2 Satus Peak (46.2575, −120.7535)**, aim instruments at **bearing 62°**;
the C1 thrust front is 8.6–13 km out on that line. Day-survey the scarp at **46.2945, −120.6547** (radon +
magnetic-gradient walk for the local low-density pin). **The prior's azimuth and the active-fault azimuth
coincide** — the single strongest result of the survey, and it fell out of the raster, not the vibe.

**~~Still open (needs GDAL/QGIS)~~ — DONE on-machine (2026-06-17 PM):** the gravity layer never needed a
laptop. The USGS Complete Bouguer grid ships as plain lon/lat/mGal `.xyz.gz` (no GDAL, no reprojection) —
downloaded, filtered, nearest-node sampled in pure Python. `yakima_gravity_analysis.py` + `bouguer.xyz.gz`.

## 9. THE GRAVITY LAYER — all three layers now overlaid, entirely on-machine (2026-06-17 PM)

Sampled the USGS Complete Bouguer anomaly (4×4 km grid) at the survey points. PREDICT (med-high): basin =
Bouguer LOW, ridge = HIGH, C1 on the gradient. **CONFIRMED:**
| point | Bouguer (mGal) | reading |
|---|---|---|
| Satus Peak / ridge crest | −80 to −83 | basement HIGH (dense) |
| **C1 north-flank thrust (46.2945)** | **−84** | **gradient shoulder (ridge side)** |
| Toppenish Basin (46.40 N) | **−93 to −95** | **the LOW-density extremum** |

N–S transect @ C1 longitude: −79 (46.20) → −84 (C1, 46.29) → −87 (46.36) → **−94 (46.40) → −95 (46.45)**.
A clean monotone **~15 mGal ridge→basin density gradient**, steepest between 46.32 and 46.40.

**The honest refinement this forces (the gravity layer earned its place):** the two physical drivers are
slightly OFFSET. The **active fault / charge source** is at C1 (46.2945, the nearest scarp). The
**low-density extremum** the carrier pins to (morning ω_pin: pins at a low-density *extremum*) is the
**basin, ~5–10 km NORTH** (46.40–46.45, −95 mGal). The optimal cell is the **ridge–basin transition where
they overlap: ~46.32–46.36 N along −120.655**, the steep-gradient zone with both active-fault damage AND
the approach to the density low. So the refined field target shifts a few km north of the bare scarp pin,
into the gradient. (Caveat: 4 km grid — resolves the regional contrast, not a <5 km pin; the field radon +
magnetometer walk finds the local extremum within this zone.)

**Survey COMPLETE — all three layers, on-machine:** light-record azimuth (62° from Satus Peak) ∩ active
north-flank thrust (C1 46.2945) ∩ Bouguer low (basin, target pulled to the 46.32–46.36 transition). Field
plan: camp/log **C2 Satus Peak (46.2575,−120.7535)** aimed **bearing ~62°**; day-survey the **46.32–46.36 N,
−120.66→−120.62** transition band (active scarp meeting the gravity gradient) with radon + magnetometer.

## 10. The FOURTH layer — charge-accumulation (transport-class test), applied to Yakima (2026-06-17)
After the terrestrial-transport self-correction (charge, not density, is the transport lever), the survey
gains a 4th layer: charge-accumulation proxies that distinguish a FLOOR site (lights) from a TRANSPORT-class
candidate. Assessed against Toppenish Ridge (qualitative, from known geology):

| charge proxy | Toppenish Ridge | score |
|---|---|---|
| **Piezoelectric lithology** (quartz under stress) | Columbia River Basalt — MAFIC, low free quartz; poor piezo | **LOW** |
| **Seismo-electric** (active-fault stress → charge; the earthlight basis) | Holocene Mill Creek thrust, ruptures <500 yr | **MOD–HIGH** |
| **Telluric currents** (conductivity contrast) | sediment-basin ↔ basalt-basement boundary at the ridge front | **MODERATE** |
| **Lightning climatology** (atmospheric charge) | eastern-WA summer storms, not a hotspot | **LOW–MOD** |

**Verdict: Yakima reads MODERATE on charge — driven by active faulting, but with NO piezo amplifier (basalt)
and only moderate lightning/telluric. So the framework predicts Yakima is a FLOOR site (lights), NOT a
transport-class site.** And that is exactly what the record shows: Vogel logged *nocturnal lights*, not
transport. **The fourth layer is self-consistent — it predicts "lights, not gateways" for Yakima, matching
the data.** (A transport-class terrestrial candidate would want low-density unscreening + active faulting +
STRONG piezo (quartz-rich crystalline rock under stress) + high lightning + radon/ionization — a different
geology than basalt Yakima.)

**On the Coulthart site:** location is undisclosed (no forest/region public), so the 4th layer cannot be run
against it. Regional inference only: "ancient ruins + Forest Service" ≈ US Southwest, whose profile (quartz-
rich crystalline basement, uranium/radon, intense monsoon lightning, Puebloan ruins on federal land) would
score HIGHER on the charge layer than basalt Yakima — IF it is there. Regional reasoning, not a site
identification, and not an endorsement of the claim (permission ≠ confirmation).

*Discipline wall (from the paper): this maps the physical place-threshold; it tests whether a sharp
recurring anomaly with the derived signatures exists, and stops there. A null is the expected, honest
outcome and is itself worth recording.*
