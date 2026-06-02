#
# Range-from-motion vs PnP (creative-drive exploration 2026-06-01).
# Tests whether bearing + velocity-integrated own-motion triangulates gate range better
# than single-frame PnP, on a real captured approach sequence. See range_from_motion_experiment.md.
#
import os, sys, glob, json, math
import numpy as np, cv2
HERE = os.path.dirname(os.path.abspath(__file__)); VIS = os.path.dirname(HERE)
sys.path.insert(0, HERE); sys.path.insert(0, VIS); sys.path.insert(0, os.path.join(VIS, "..", "sim"))
from w3_detector_eval import make_detector, project_true, FX, FY, CX, CY, TILT_DEG, Ry
from drone_env_v2 import quat_rotate_np

TILT_SIGN = -1.0   # validated in W3


def bearing_ned_from_pixel(u, v, q_ned):
    """Invert the W3 NED->camera projection: detected pixel -> unit bearing toward gate in NED."""
    ray = np.array([(u - CX)/FX, (v - CY)/FY, 1.0])          # OpenCV camera ray
    rel_cam_frd = np.array([ray[2], ray[0], ray[1]])          # opencv -> FRD (x=fwd,y=right,z=down)
    rel_frd = Ry(-TILT_SIGN * math.radians(TILT_DEG)) @ rel_cam_frd   # undo camera up-tilt
    rel_ned = quat_rotate_np(q_ned, rel_frd)                  # body -> world (NED)
    return rel_ned / (np.linalg.norm(rel_ned) + 1e-9)


def triangulate(bearings, rel_positions):
    """Gate position (relative to current ego @ origin) minimizing perpendicular bearing residual.
    bearings: list of unit NED vectors toward gate. rel_positions: ego positions rel to current."""
    A = np.zeros((3, 3)); b = np.zeros(3)
    for bn, p in zip(bearings, rel_positions):
        M = np.eye(3) - np.outer(bn, bn)
        A += M; b += M @ p
    try:
        g = np.linalg.solve(A + 1e-6*np.eye(3), b)
    except np.linalg.LinAlgError:
        return None
    return g


def load_seq(d):
    seen = {}
    for line in open(os.path.join(d, "labels.jsonl")):
        r = json.loads(line); seen.setdefault(r["frame_id"], r)
    recs = sorted(seen.values(), key=lambda r: r["sim_time_ns"])
    return recs


def main():
    d = os.path.join(HERE, "w2_forward_20260601_170205")   # the approach run (closed 22->9m)
    recs = load_seq(d)
    det = make_detector()
    W = 20  # window (~0.66s @ 30Hz)

    # per-frame: collect detected bearing, pnp range, true range, ego vel, time, true bearing
    F = []
    for r in recs:
        g = r["gates"].get(str(r["active_gate"])) or r["gates"].get(r["active_gate"])
        if not g: continue
        ego = np.array(r["ego"]["pos_ned"]); vel = np.array(r["ego"]["vel_ned"]); q = r["ego"]["q_ned"]
        true_rng = float(np.linalg.norm(np.array(g) - ego))
        if not (3.0 <= true_rng <= 30.0): continue
        img = cv2.imread(os.path.join(d, "frames", f"f{r['frame_id']:06d}.jpg"))
        if img is None: continue
        ds = det.detect(img); det0 = ds[0] if ds else None
        if not (det0 and det0.found and det0.center_2d is not None and det0.distance): continue
        # detected bearing (NED) from pixel; true bearing (NED) from ground truth
        bdet = bearing_ned_from_pixel(det0.center_2d[0], det0.center_2d[1], q)
        btrue = (np.array(g) - ego); btrue = btrue/ (np.linalg.norm(btrue)+1e-9)
        F.append(dict(t=r["sim_time_ns"]/1e9, ego=ego, vel=vel, q=q,
                      true_rng=true_rng, pnp=float(det0.distance), bdet=bdet, btrue=btrue))
    print(f"usable frames: {len(F)}")
    if len(F) < W+2:
        print("too few frames"); return

    # validate the inverse transform: detected-vs-true bearing angle (should be small if transform right)
    bang = [math.degrees(math.acos(np.clip(np.dot(f["bdet"], f["btrue"]), -1, 1))) for f in F]
    print(f"inverse-transform check: median |bdet vs btrue| = {np.median(bang):.2f} deg "
          f"(small => transform correct + detector bearing good)")

    # sliding-window triangulation
    rows = []
    for i in range(W, len(F)):
        win = F[i-W:i+1]
        # rel positions of window frames wrt current (i): integrate velocity backward
        rels = []
        for j in range(len(win)):
            # displacement from win[j] to current = sum of v*dt over the interval
            disp = np.zeros(3)
            for k in range(j, len(win)-1):
                dt = win[k+1]["t"] - win[k]["t"]
                disp += win[k]["vel"] * dt
            rels.append(-disp)   # position of win[j] relative to current ego
        bdet = [w["bdet"] for w in win]; btrue = [w["btrue"] for w in win]
        g_det = triangulate(bdet, rels); g_true = triangulate(btrue, rels)
        cur = F[i]
        # velocity-vs-LOS angle (degeneracy indicator): 0 = flying straight at gate (degenerate)
        vdir = cur["vel"]/ (np.linalg.norm(cur["vel"])+1e-9)
        los_angle = math.degrees(math.acos(np.clip(abs(np.dot(vdir, cur["btrue"])), -1, 1)))
        rows.append(dict(true=cur["true_rng"], pnp=cur["pnp"],
                         tri_det=np.linalg.norm(g_det) if g_det is not None else np.nan,
                         tri_true=np.linalg.norm(g_true) if g_true is not None else np.nan,
                         los_angle=los_angle, speed=float(np.linalg.norm(cur["vel"]))))

    R = rows
    def mae(key):
        e = [abs(r[key]-r["true"])/r["true"] for r in R if not np.isnan(r[key])]
        return np.median(e), len(e)
    pnp_e,_ = mae("pnp"); td_e,_ = mae("tri_det"); tt_e,_ = mae("tri_true")
    print(f"\nmedian |frac range err|  (over {len(R)} windowed frames):")
    print(f"  PnP (single-frame)        : {pnp_e:.3f}")
    print(f"  triangulation (DETECTED b): {td_e:.3f}")
    print(f"  triangulation (TRUE b)    : {tt_e:.3f}  <- method upper bound")
    # degeneracy: bin by los_angle (perpendicular motion = high angle = observable)
    print(f"\nby velocity-vs-LOS angle (deg; higher = more lateral motion = more observable):")
    for lo,hi in [(0,5),(5,15),(15,30),(30,90)]:
        sub=[r for r in R if lo<=r["los_angle"]<hi]
        if not sub: continue
        pe=np.median([abs(r["pnp"]-r["true"])/r["true"] for r in sub])
        te=np.median([abs(r["tri_det"]-r["true"])/r["true"] for r in sub if not np.isnan(r["tri_det"])])
        print(f"  {lo:2d}-{hi:2d}deg (n={len(sub):3d}): PnP={pe:.3f}  tri_det={te:.3f}")
    json.dump([{k:(float(v) if isinstance(v,(int,float,np.floating)) else v) for k,v in r.items()} for r in R],
              open(os.path.join(HERE,"range_from_motion_results.json"),"w"))
    print("\n-> range_from_motion_results.json")


if __name__ == "__main__":
    main()
