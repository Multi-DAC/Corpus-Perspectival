#!/usr/bin/env python
"""Sandia-Manzano portal field-survey — raster-precise coordinate pin (2026-06-18).

Same method as the Yakima survey, applied to the Albuquerque rift. Pulls USGS Quaternary faults
(haz/Qfaults/MapServer/12 = New Mexico) for the Albuquerque-rift bbox and overlays the USGS Bouguer
gravity grid (density proxy). The portal mechanism (published paper + yesterday's omega_pin result) wants:
  - LOW density (Bouguer low) so the screened scalar can unscreen (rho < rho_crit), AND
  - a density EXTREMUM (local Bouguer MINIMUM) -- omega_pin localizes at an extremum, not a gradient, AND
  - the granite range-front (piezo amplifier + active normal fault = EM generation/conduit) nearby.
So the thin-spot pin = a late-Quaternary normal fault vertex sitting at/next to a LOCAL Bouguer minimum on
the low-density (basin) side, within each candidate cell. Two cells: C1 Sandia (lat>=34.95), C2 Manzano
(34.45-34.90, the documented Bennewitz/Manzano plasma-lights locus).

Reproduce: C:/Python314/python.exe sandia_pin_analysis.py
Data: sandia_qfaults.geojson (cached), bouguer.xyz.gz (CONUS grid, reused from Yakima survey)
"""
import json, math, os, ssl, gzip, urllib.request, urllib.parse

BBOX = "-106.9,34.3,-106.3,35.3"
LON0, LON1, LAT0, LAT1 = -106.9, -106.3, 34.3, 35.3
CACHE = "sandia_qfaults.geojson"
EP = "https://earthquake.usgs.gov/arcgis/rest/services/haz/Qfaults/MapServer/12/query"


def pull():
    q = dict(where="1=1", geometry=BBOX, geometryType="esriGeometryEnvelope", inSR="4326",
             spatialRel="esriSpatialRelIntersects",
             outFields="*", returnGeometry="true", outSR="4326", f="geojson")
    req = urllib.request.Request(EP + "?" + urllib.parse.urlencode(q), headers={"User-Agent": "Mozilla/5.0"})
    d = json.load(urllib.request.urlopen(req, context=ssl._create_unverified_context(), timeout=90))
    open(CACHE, "w").write(json.dumps(d))
    return d


def hav(a, b):
    R = 6371.0
    la1, lo1, la2, lo2 = map(math.radians, [a[0], a[1], b[0], b[1]])
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))


def load_bouguer():
    pts = []
    with gzip.open("bouguer.xyz.gz", "rt") as f:
        for line in f:
            p = line.split()
            if len(p) < 3:
                continue
            lo, la, mg = float(p[0]), float(p[1]), float(p[2])
            if LON0 <= lo <= LON1 and LAT0 <= la <= LAT1:
                pts.append((la, lo, mg))
    return pts


def local_minima(pts, radius_km=9.0):
    """Bouguer points lower than every neighbor within radius_km = closed lows (density extrema)."""
    mins = []
    for i, (la, lo, mg) in enumerate(pts):
        is_min = True
        for j, (la2, lo2, mg2) in enumerate(pts):
            if i == j:
                continue
            if hav((la, lo), (la2, lo2)) <= radius_km and mg2 < mg:
                is_min = False
                break
        if is_min:
            mins.append((la, lo, mg))
    return mins


def fault_vertices(d):
    """Return list of (lat,lon, name, age, sliprate, dip) for late-Quaternary normal faults."""
    out = []
    for ft in d["features"]:
        p = ft["properties"]
        name = p.get("fault_name") or p.get("name") or ""
        age = (p.get("age") or p.get("recency") or "")
        slip = (p.get("slip_rate") or p.get("sliprate") or "")
        dip = (p.get("dip_direction") or p.get("dip") or "")
        g = ft.get("geometry") or {}
        c = g.get("coordinates", [])
        if not c:
            continue
        # flatten multilinestring / linestring
        if isinstance(c[0][0], list):
            pts = [v for ln in c for v in ln]
        else:
            pts = c
        for v in pts:
            out.append((v[1], v[0], name, age, slip, dip))
    return out


def main():
    d = json.load(open(CACHE)) if os.path.exists(CACHE) else pull()
    bg = load_bouguer()
    mgs = [m for _, _, m in bg]
    print("=" * 78)
    print("SANDIA-MANZANO PORTAL SURVEY — Albuquerque rift, raster pin")
    print("=" * 78)
    print(f"Bouguer points in bbox: {len(bg)}  range {min(mgs):.1f} to {max(mgs):.1f} mGal")
    basin = min(bg, key=lambda t: t[2])  # regional density low = rift basin center
    rangehi = max(bg, key=lambda t: t[2])  # densest = granite range core
    print(f"REGIONAL LOW  (basin center / max unscreening): {basin[0]:.4f}, {basin[1]:.4f}  {basin[2]:.1f} mGal")
    print(f"REGIONAL HIGH (granite range core / piezo):     {rangehi[0]:.4f}, {rangehi[1]:.4f}  {rangehi[2]:.1f} mGal")

    mins = local_minima(bg)
    mins.sort(key=lambda t: t[2])
    print(f"\nLOCAL Bouguer MINIMA (density extrema where omega_pin localizes): {len(mins)}")
    for la, lo, mg in mins[:8]:
        print(f"   {la:.4f}, {lo:.4f}   {mg:.1f} mGal")

    fv = fault_vertices(d)
    names = sorted(set(v[2] for v in fv if v[2]))
    print(f"\nNM Quaternary faults in bbox: {len(fv)} vertices across {len(names)} named faults")
    for nm in names:
        sample = next(v for v in fv if v[2] == nm)
        print(f"   - {nm}  (age='{sample[3]}' dip='{sample[5]}')")

    # granite proxy = dense crystalline rock = high Bouguer (top of the range). Range-front = where a
    # low-density pocket sits next to that dense rock.
    DENSE = sorted(bg, key=lambda t: -t[2])
    dense_pts = [(la, lo) for la, lo, mg in DENSE if mg > -185.0]  # densest ~quartile = range cores

    def gdist(p):  # km to nearest dense (granite/range) point = piezo proximity
        return min(hav(p, q) for q in dense_pts)

    # active = late/latest Quaternary (most recent motion = live conduit + EM generation)
    ACTIVE = [v for v in fv if ("late" in (v[3] or "").lower())]

    def fdist(p):  # km to nearest ACTIVE fault vertex = conduit proximity
        return min(hav((v[0], v[1]), p) for v in ACTIVE)

    # ---- the pin: the local Bouguer minimum that best CONVERGES low-density + granite + active fault ----
    def pin(cell_name, lat_lo, lat_hi):
        cellmins = [m for m in mins if lat_lo <= m[0] <= lat_hi]
        if not cellmins:
            print(f"\n{cell_name}: no local minima in cell")
            return
        # score each low-density extremum by its convergence with granite (piezo) + active fault (conduit)
        scored = []
        for la, lo, mg in cellmins:
            gd = gdist((la, lo)); fd = fdist((la, lo))
            # want: low mg (unscreening), small gd (piezo), small fd (conduit). Combined penalty:
            score = gd + fd  # km; lower = better convergence (mg already filtered to genuine lows)
            scored.append((score, la, lo, mg, gd, fd))
        scored.sort()
        print(f"\n{cell_name}  (ranked by granite+fault convergence at a density low)")
        for score, la, lo, mg, gd, fd in scored[:3]:
            # nearest active fault name
            nf = min(ACTIVE, key=lambda v: hav((v[0], v[1]), (la, lo)))
            print(f"   {la:.4f}, {lo:.4f}  {mg:.0f}mGal | granite {gd:.1f}km | active-fault {fd:.1f}km "
                  f"('{nf[2]}', dip {nf[5]}) | conv-score {score:.1f}")
        best = scored[0]
        print(f"   >>> THIN-SPOT PIN: {best[1]:.4f}, {best[2]:.4f}  "
              f"(Bouguer {best[3]:.0f} mGal; granite {best[4]:.1f} km; active fault {best[5]:.1f} km) <<<")

    pin("C1 — SANDIA range-front", 34.95, 35.30)
    pin("C2 — MANZANO front (Bennewitz/plasma-lights locus)", 34.45, 34.90)

    # ---- named active range-front faults: the structures that carry granite + documented prior ----
    print("\n" + "=" * 78)
    print("NAMED ACTIVE RANGE-FRONT FAULTS — centroid + nearest density low (the meaningful pins)")
    print("=" * 78)
    for key in ["Hubbell Spring", "Sandia fault", "Rincon", "Jemez-San Ysidro", "Manzano fault", "Llano de Manzano"]:
        verts = [(v[0], v[1]) for v in fv if key in v[2]]
        if not verts:
            continue
        cla = sum(v[0] for v in verts) / len(verts); clo = sum(v[1] for v in verts) / len(verts)
        nlo = min(mins, key=lambda m: hav((m[0], m[1]), (cla, clo)))
        dlo = hav((nlo[0], nlo[1]), (cla, clo))
        smp = next(v for v in fv if key in v[2])
        gd = gdist((cla, clo))
        print(f"{key:18s} centroid {cla:.4f},{clo:.4f} | age '{smp[3]}' dip {smp[5]} | "
              f"granite {gd:.1f}km | nearest low {nlo[0]:.4f},{nlo[1]:.4f} ({nlo[2]:.0f}mGal, {dlo:.1f}km)")


if __name__ == "__main__":
    main()
