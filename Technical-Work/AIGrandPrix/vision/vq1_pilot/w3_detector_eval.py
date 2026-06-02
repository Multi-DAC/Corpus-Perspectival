#
# W3: validate the VQ1 gate detector on the REAL auto-labeled frames (ROADMAP_v3 W3).
# For each labeled frame: run the red-gate detector + PnP, compare to ground truth
# (leaked gate pose + ego pose). Measures detection-rate-vs-range, PnP range error, and
# bearing error (via NED->camera projection, auto-validated against detected centers).
# Output: a measured detector error model -> PerceptionObsWrapper.set_error_model().
#
import os, sys, glob, json, math
import numpy as np, cv2
HERE = os.path.dirname(os.path.abspath(__file__)); VIS = os.path.dirname(HERE)
sys.path.insert(0, VIS); sys.path.insert(0, os.path.join(VIS, "..", "sim"))
from gate_detector import GateDetector, GateDetectorConfig
from drone_env_v2 import quat_rotate_np

FX = FY = 320.0; CX, CY = 320.0, 180.0
TILT_DEG = 20.0   # camera tilted UP 20 deg (sign auto-checked below)


def red_mask(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    m = cv2.inRange(hsv, np.array([0,80,50]), np.array([12,255,255])) | \
        cv2.inRange(hsv, np.array([160,80,50]), np.array([180,255,255]))
    k = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, k)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT,(3,3)))
    return m


def make_detector():
    cfg = GateDetectorConfig(); cfg.use_brightness_mode = False
    cfg.gate_width = cfg.gate_height = 2.7; cfg.min_contour_area = 60
    det = GateDetector(cfg); det.set_camera_params(FX, FY, CX, CY)
    det._create_gate_mask = red_mask
    return det


def Ry(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c,0,s],[0,1,0],[-s,0,c]])


def project_true(gate_ned, ego_ned, q_ned, tilt_sign):
    """True gate pixel + range via NED -> body(FRD) -> camera(tilt) -> OpenCV -> pixel."""
    q_conj = np.array([q_ned[0], -q_ned[1], -q_ned[2], -q_ned[3]])
    rel_frd = quat_rotate_np(q_conj, np.array(gate_ned) - np.array(ego_ned))   # x-fwd,y-right,z-down
    rel_cam_frd = Ry(tilt_sign * math.radians(TILT_DEG)) @ rel_frd             # tilt optical axis up
    cam = np.array([rel_cam_frd[1], rel_cam_frd[2], rel_cam_frd[0]])           # OpenCV: right,down,fwd
    rng = float(np.linalg.norm(rel_frd))
    if cam[2] <= 0.1:
        return None, rng
    u = CX + FX * cam[0]/cam[2]; v = CY + FY * cam[1]/cam[2]
    return np.array([u, v]), rng


def load_frames():
    out = []
    for d in sorted(glob.glob(os.path.join(HERE, "w2_dataset_*")) + glob.glob(os.path.join(HERE, "w2_forward_*"))):
        lab = os.path.join(d, "labels.jsonl")
        if not os.path.exists(lab): continue
        seen = {}
        for line in open(lab):
            r = json.loads(line); seen.setdefault(r["frame_id"], r)
        for r in seen.values():
            g = r["gates"].get(str(r["active_gate"])) or r["gates"].get(r["active_gate"])
            if not g: continue
            rng = float(np.linalg.norm(np.array(g) - np.array(r["ego"]["pos_ned"])))
            if 3.0 <= rng <= 45.0:
                out.append((os.path.join(d, "frames", f"f{r['frame_id']:06d}.jpg"), r, g, rng))
    return out


def main():
    frames = load_frames()
    print(f"labeled frames in 3-45m: {len(frames)}")
    det = make_detector()

    # auto-pick tilt sign: minimize median |projected_center - detected_center| on a sample
    sample = frames[::max(1, len(frames)//120)]
    def resid(sign):
        es = []
        for path, r, g, rng in sample:
            img = cv2.imread(path)
            if img is None: continue
            ds = det.detect(img)
            if not ds or not ds[0].found: continue
            pt, _ = project_true(g, r["ego"]["pos_ned"], r["ego"]["q_ned"], sign)
            if pt is None: continue
            es.append(np.linalg.norm(pt - ds[0].center_2d))
        return np.median(es) if es else 1e9, len(es)
    rp, np_ = resid(+1.0); rn, nn = resid(-1.0)
    tilt_sign = 1.0 if rp <= rn else -1.0
    print(f"tilt-sign check: +1 median_pxresid={rp:.1f}(n={np_})  -1={rn:.1f}(n={nn}) -> using {tilt_sign:+.0f}")

    # full pass — associate each detection to the NEAREST in-frame true gate (removes the
    # active-gate-vs-largest-blob mismatch that polluted the first pass).
    bins = [(3,8),(8,12),(12,18),(18,25),(25,35),(35,45)]
    stat = {b: {"n":0,"det":0,"rangeerr":[],"pxerr":[]} for b in bins}
    for path, r, g, rng in frames:
        img = cv2.imread(path)
        if img is None: continue
        # project ALL gates; keep those in-frame
        proj = []
        for gid, gp in r["gates"].items():
            pt, grng = project_true(gp, r["ego"]["pos_ned"], r["ego"]["q_ned"], tilt_sign)
            if pt is not None and 0 <= pt[0] < 640 and 0 <= pt[1] < 360:
                proj.append((pt, grng))
        if not proj: continue                      # no gate in view -> not a detection opportunity
        # bin by the NEAREST in-frame gate's range
        pt_near, rng_near = min(proj, key=lambda x: x[1])
        b = next((b for b in bins if b[0] <= rng_near < b[1]), None)
        if b is None: continue
        s = stat[b]; s["n"] += 1
        ds = det.detect(img); d = ds[0] if ds else None
        if d and d.found and d.distance and d.center_2d is not None:
            # associate detection to nearest projected gate by pixel center
            mpt, mrng = min(proj, key=lambda x: np.linalg.norm(x[0] - d.center_2d))
            pxerr = float(np.linalg.norm(mpt - d.center_2d))
            if pxerr < 120:                        # plausible association (≈21° at fx=320)
                s["det"] += 1
                s["rangeerr"].append((d.distance - mrng)/mrng)
                s["pxerr"].append(pxerr)

    print("\n range-bin   n   det%   range_err(med,iqr)     bearing_px(med)  bearing_deg(med)")
    all_re=[]; all_px=[]
    for b in bins:
        s = stat[b]
        if s["n"] == 0: continue
        detr = s["det"]/s["n"]
        re = np.array(s["rangeerr"]); px = np.array(s["pxerr"])
        all_re += list(re); all_px += list(px)
        remed = np.median(np.abs(re)) if len(re) else float('nan')
        reiqr = (np.percentile(re,75)-np.percentile(re,25)) if len(re) else float('nan')
        pxmed = np.median(px) if len(px) else float('nan')
        degmed = math.degrees(pxmed/FX) if len(px) else float('nan')
        print(f"  {b[0]:2d}-{b[1]:2d}m  {s['n']:4d}  {detr*100:4.0f}%   |err|={remed:.3f} iqr={reiqr:.3f}     {pxmed:5.1f}px        {degmed:.2f}")

    re = np.array(all_re); px = np.array(all_px)
    range_sigma = float(np.std(re)) if len(re) else 0.0
    bearing_sigma = float(np.std(px/FX)) if len(px) else 0.0
    overall_det = sum(s["det"] for s in stat.values())/max(1,sum(s["n"] for s in stat.values()))
    model = {"range_sigma_frac": round(range_sigma,3),
             "bearing_sigma_rad": round(bearing_sigma,3),
             "dropout_prob": round(1.0-overall_det,3),
             "max_range_m": 40.0,
             "note": "measured on real VQ1 frames (W3)"}
    print(f"\nMEASURED ERROR MODEL: {json.dumps(model)}")
    json.dump(model, open(os.path.join(HERE, "w3_error_model.json"), "w"), indent=2)
    print(f"-> w3_error_model.json (feed PerceptionObsWrapper.set_error_model(**model))")


if __name__ == "__main__":
    main()
