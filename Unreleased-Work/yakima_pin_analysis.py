#!/usr/bin/env python
"""Yakima/Toppenish portal field-survey — raster-precise C1 pin (2026-06-17).

Pulls the USGS Quaternary Fault DB (haz/Qfaults/MapServer/18 = Washington polylines) for the Toppenish
bbox and intersects with Satus Peak (Vogel's documented light-record vantage). The mechanism wants the
active NORTH-FLANK thrust (overrides the low-density basin); a north-vergent thrust dips SOUTH, so
dip='S' Toppenish segments are the target. Output: nearest active scarp to Satus Peak + the thrust-front
corridor + the bearing (which coincides with the prior's reported azimuth).

Reproduce:
  C:/Python314/python.exe yakima_pin_analysis.py        # re-pull + analyze
Data cache: yakima_qfaults.geojson
"""
import json, math, os, ssl, urllib.request, urllib.parse

SP = (46.2575, -120.7535)  # Satus Peak fire lookout (Vogel station), lat, lon
BBOX = "-120.95,46.10,-120.30,46.55"
CACHE = "yakima_qfaults.geojson"
EP = "https://earthquake.usgs.gov/arcgis/rest/services/haz/Qfaults/MapServer/18/query"


def pull():
    q = dict(where="1=1", geometry=BBOX, geometryType="esriGeometryEnvelope", inSR="4326",
             spatialRel="esriSpatialRelIntersects",
             outFields="fault_name,age,slip_rate,dip_direction,strike,linetype",
             returnGeometry="true", outSR="4326", f="geojson")
    req = urllib.request.Request(EP + "?" + urllib.parse.urlencode(q), headers={"User-Agent": "Mozilla/5.0"})
    d = json.load(urllib.request.urlopen(req, context=ssl._create_unverified_context(), timeout=60))
    open(CACHE, "w").write(json.dumps(d))
    return d


def hav(a, b):
    R = 6371.0
    la1, lo1, la2, lo2 = map(math.radians, [a[0], a[1], b[0], b[1]])
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))


def bearing(a, b):
    la1, la2, dlo = math.radians(a[0]), math.radians(b[0]), math.radians(b[1] - a[1])
    y = math.sin(dlo) * math.cos(la2)
    x = math.cos(la1) * math.sin(la2) - math.sin(la1) * math.cos(la2) * math.cos(dlo)
    return math.degrees(math.atan2(y, x)) % 360


def main():
    d = json.load(open(CACHE)) if os.path.exists(CACHE) else pull()
    south = []  # dip=S = north-vergent thrust = north flank (basin side)
    for ft in d["features"]:
        p = ft["properties"]
        if "Toppenish" not in (p.get("fault_name") or ""):
            continue
        if p.get("dip_direction") != "S":
            continue
        g = ft.get("geometry") or {}
        c = g.get("coordinates", [])
        pts = [v for ln in c for v in ln] if (c and isinstance(c[0][0], list)) else c
        for v in pts:
            south.append((v[1], v[0]))
    south.sort(key=lambda v: hav(SP, v))
    print(f"active north-flank thrust (dip=S) vertices: {len(south)}")
    print(f"C1 PIN (nearest active scarp to Satus Peak): {south[0][0]:.4f}, {south[0][1]:.4f}"
          f"  d={hav(SP, south[0]):.1f} km  bearing={bearing(SP, south[0]):.0f} deg")
    corr = [v for v in south if hav(SP, v) <= 13]
    la = [v[0] for v in corr]; lo = [v[1] for v in corr]
    print(f"C1 corridor (<=13 km): {len(corr)} verts  lat[{min(la):.4f},{max(la):.4f}] "
          f"lon[{min(lo):.4f},{max(lo):.4f}]  centroid {sum(la)/len(la):.4f},{sum(lo)/len(lo):.4f}")
    bs = [bearing(SP, v) for v in corr]
    print(f"corridor bearing range: {min(bs):.0f}-{max(bs):.0f} deg (tight ~62 = the prior's azimuth)")


if __name__ == "__main__":
    main()
