#!/usr/bin/env python
"""Yakima/Toppenish portal survey — the GRAVITY layer, sampled on Clawd's own machine (2026-06-17).

The layer I'd wrongly ceded to "needs QGIS on your laptop." It does not: the USGS Complete Bouguer
anomaly grid ships as a plain lon/lat/mGal .xyz.gz (no GDAL, no reprojection). Download, filter to the
bbox, nearest-node sample. Confirms the low-density extremum (mechanism: carrier pins at a low-density
extremum) and where C1 (the active north-flank thrust) sits on the density gradient.

Source: https://mrdata.usgs.gov/gravity/bouguer/bouguer.xyz.gz  (4x4 km grid, mGal, geographic).
Reproduce: C:/Python314/python.exe yakima_gravity_analysis.py   (uses cached bouguer.xyz.gz if present)
"""
import gzip, math, os, ssl, urllib.request

URL = "https://mrdata.usgs.gov/gravity/bouguer/bouguer.xyz.gz"
CACHE = "bouguer.xyz.gz"


def ensure():
    if not os.path.exists(CACHE):
        req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
        open(CACHE, "wb").write(urllib.request.urlopen(req, context=ssl._create_unverified_context(), timeout=120).read())


def load_local(lon0=-121.6, lon1=-119.4, lat0=45.4, lat1=47.1):
    pts = []
    for L in gzip.open(CACHE, "rt"):
        s = L.split()
        if len(s) < 3:
            continue
        lo, la, v = float(s[0]), float(s[1]), float(s[2])
        if lon0 < lo < lon1 and lat0 < la < lat1:
            pts.append((la, lo, v))
    return pts


def near(pts, la, lo):
    b = min(pts, key=lambda p: (p[0] - la) ** 2 + (p[1] - lo) ** 2)
    d = math.hypot((b[0] - la) * 111, (b[1] - lo) * 111 * math.cos(math.radians(la)))
    return b[2], d


def main():
    ensure()
    pts = load_local()
    print(f"local Bouguer grid nodes: {len(pts)}  (mGal; more negative = lower density)")
    q = {"C1 north-flank thrust (46.2945,-120.6547)": (46.2945, -120.6547),
         "Toppenish BASIN N of ridge (46.40,-120.50)": (46.40, -120.50),
         "Ridge CREST near Satus (46.255,-120.70)": (46.255, -120.70),
         "Satus Peak C2 (46.2575,-120.7535)": (46.2575, -120.7535)}
    for n, (la, lo) in q.items():
        v, d = near(pts, la, lo)
        print(f"  {n}: {v:+7.1f} mGal (node {d:.1f} km)")
    print("N-S transect @ lon -120.655 (C1 longitude):")
    for la in [46.20, 46.24, 46.255, 46.27, 46.2945, 46.32, 46.36, 46.40, 46.45]:
        v, _ = near(pts, la, -120.655)
        print(f"  lat {la:.3f}: {v:+7.1f} mGal")


if __name__ == "__main__":
    main()
