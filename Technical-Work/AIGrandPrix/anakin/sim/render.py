"""
Anakin training-sim renderer — fast GPU-vectorized 64x64 FPV camera (torch).

Phase 1.2 of anakin/ROADMAP.md. Projects gate geometry into a 64x64 RGB FPV view:
high-contrast gate frames on a desaturated background (VQ1-faithful). Batched over N
envs so DreamerV3 can train in-loop at thousands of FPS (the official FlightSim gives
only 30 Hz over UDP — ~100x too slow for a 10M-step run).

This REUSES the geometry/conventions of ../../vision/synthetic_camera.py (body frame
x=forward, y=left, z=up; optical mapping cam=[-by,-bz,bx]; gate-corner construction) but
REIMPLEMENTS rasterization as a vectorized point-in-quad test over the 64x64 pixel grid,
batched [N envs, G gates] — no Python per-pixel/per-gate loops, no cv2.

What the old reference left as a TODO and this build does: the 20deg camera down-tilt is
threaded through the projection (rotate rel-body points by +tilt about body-Y before the
optical mapping). Sign verified by the __main__ visual test (a level gate dead-ahead lands
ABOVE center because the camera looks down).

State convention matches sim/dynamics.py: state[N,10] = [pos(3), vel(3), quat(4 w x y z)].

Calibration choices (revisit at Phase 4 transfer; DR + VQ1 desaturation cover the gap):
  * 64x64, HFoV=90deg -> fx=fy=32, cx=cy=32 (isotropic square). FlightSim is 640x360
    fx=fy~=320 (HFoV 90); we render square at training res. The deploy adapter (Phase 4)
    resizes FlightSim 640x360 -> 64x64.
  * Gate = bright FRAME: outer 2.7m square minus inner 1.5m hole (spec VADR-TS-002 §3.7).
  * Background desaturated gray + light noise; current gate bright, lookahead gates dim.
"""
import torch

from dynamics import quat_rotate  # batched Hamilton-quat rotate, shared convention
import gate_mask as _gm  # gate-isolation obs transform (env-var gated; Day 134 seg route)

# --- camera / image constants ---
IMG       = 64                 # square training resolution (Dreamer obs)
HFOV_DEG  = 90.0               # horizontal FoV (matches FlightSim fx=fy~=320 @640)
TILT_DEG  = 20.0               # camera down-tilt (VQ1 spec; FPV looks slightly down)
_f        = (IMG / 2.0) / torch.tan(torch.tensor(HFOV_DEG * torch.pi / 180.0 / 2.0))
FX = FY   = float(_f)          # ~= 32.0
CX = CY   = IMG / 2.0
NEAR      = 0.10               # min optical-z to be in front of camera (m)

# --- gate geometry (spec §3.7: outer 2.7 m, inner 1.5 m square) ---
GATE_OUTER = 2.7
GATE_INNER = 1.5

# --- appearance (desaturated VQ1 look), float [0,1] RGB ---
# --- VQ1-measured palette (integration/official_palette_spec.md, Day 131) ---
# Measured from official-sim captures: bg neutral gray ~27/255; gates ORANGE-RED
# hue ~6deg core RGB(229,93,78) with glow halo; cyan-blue track ribbon (89.6% of
# saturated pixels in the official feed) rendered as a RANDOMIZED DISTRACTOR ONLY
# (present ~half of episodes, jittered — never a reliable path signal; VQ2 has none).
BG_GRAY        = 27.0 / 255.0          # measured (was 0.16 ~= 40/255)
BG_JITTER      = 10.0 / 255.0          # per-env brightness randomization (robustness)
GATE_BRIGHT    = (0.90, 0.36, 0.31)    # current target gate — orange-red core (229,93,78)
GATE_DIM       = (0.45, 0.18, 0.15)    # lookahead gates — dimmed orange-red
GATE_GLOW_A    = 0.35                  # halo alpha (approximates official bloom)
BG_NOISE       = 0.03          # uniform +/- noise on background
RIBBON_P       = 0.5                   # probability ribbon present per env
RIBBON_COLOR   = (0.13, 0.45, 0.72)    # cyan-blue, ~hue 198deg (measured median)
RIBBON_W       = (1.0, 2.0)            # width range (m), randomized per env
RIBBON_A       = (0.20, 0.50)          # alpha range, randomized per env
RIBBON_DROP    = 1.0                   # ribbon surface this far below gate centers (m)
RIBBON_JIT     = 0.5                   # per-segment lateral jitter (m) — de-crutching


def _gate_corners(center, fwd, half):
    """Four corners of a square gate, batched.

    center, fwd: [N, G, 3] (world). fwd = gate facing/normal direction (unit-ish).
    half: scalar half-side. Returns [N, G, 4, 3] world corners, CCW seen from the front.
    """
    f = fwd / fwd.norm(dim=-1, keepdim=True).clamp_min(1e-6)
    up_hint = f.new_tensor([0.0, 0.0, 1.0]).expand_as(f)
    # if the gate faces nearly straight up/down, pick a different up reference
    near_vert = (f[..., 2].abs() > 0.99).unsqueeze(-1)
    up_hint = torch.where(near_vert, f.new_tensor([0.0, 1.0, 0.0]).expand_as(f), up_hint)
    right = torch.cross(f, up_hint, dim=-1)
    right = right / right.norm(dim=-1, keepdim=True).clamp_min(1e-6)
    up = torch.cross(right, f, dim=-1)
    up = up / up.norm(dim=-1, keepdim=True).clamp_min(1e-6)
    r = right * half
    u = up * half
    # top-left, top-right, bottom-right, bottom-left  (consistent winding)
    c = center
    return torch.stack([c - r + u, c + r + u, c + r - u, c - r - u], dim=-2)


def _project(corners_world, cam_pos, cam_quat):
    """World corners -> image-plane pixels + per-corner in-front mask, with down-tilt.

    corners_world: [N, G, 4, 3]; cam_pos: [N, 3]; cam_quat: [N, 4] (w x y z).
    Returns px [N, G, 4, 2] (float pixel coords) and infront [N, G, 4] bool.
    """
    N = cam_pos.shape[0]
    # world -> body: rotate (corner - cam_pos) by the inverse drone quat
    rel = corners_world - cam_pos[:, None, None, :]
    qconj = cam_quat * cam_quat.new_tensor([1.0, -1.0, -1.0, -1.0])
    # broadcast qconj over [G,4]
    qb = qconj[:, None, None, :].expand(N, corners_world.shape[1], 4, 4)
    rel_body = quat_rotate(qb, rel)            # [N,G,4,3] body frame (x fwd, y left, z up)

    # camera UP-tilt: vq1_spec.txt:325 "The camera is tilted upwards by 20" (also
    # VQ1_READINESS.md spec 3.7, and Elodin's harness: +20deg up — FPV convention).
    # Day-129 fix: this previously rotated the OTHER way (down-tilt), i.e. the trained
    # camera was 40deg off the official one. Verified by the __main__ visual test: a
    # level gate dead-ahead now projects BELOW image center, which is what a camera
    # pitched 20deg UP must do (its optical axis points above a level-forward object,
    # so that object sits low in the frame).
    t = torch.tensor(TILT_DEG * torch.pi / 180.0, device=rel_body.device, dtype=rel_body.dtype)
    ct, st = torch.cos(t), torch.sin(t)
    bx, by, bz = rel_body.unbind(-1)
    tx = ct * bx + st * bz
    tz = -st * bx + ct * bz
    rel_tilt = torch.stack([tx, by, tz], dim=-1)

    # body(tilted) -> OpenCV optical: x_cam = -y, y_cam = -z, z_cam = x
    cx_ = -rel_tilt[..., 1]
    cy_ = -rel_tilt[..., 2]
    cz_ = rel_tilt[..., 0]
    infront = cz_ > NEAR
    z = cz_.clamp_min(NEAR)
    px = FX * cx_ / z + CX
    py = FY * cy_ / z + CY
    return torch.stack([px, py], dim=-1), infront


def _inside_quad(grid, quad):
    """Vectorized point-in-convex-quad test.

    grid: [P, 2] pixel-center coords. quad: [..., 4, 2] (consistent winding).
    Returns [..., P] bool — pixels inside the quad. Robust to winding direction
    (accepts a pixel that is on the same side of all 4 edges, either sign).
    """
    # edge vectors and the vector from each vertex to each pixel
    v = quad                                   # [...,4,2]
    vn = torch.roll(v, shifts=-1, dims=-2)     # next vertex [...,4,2]
    edge = vn - v                              # [...,4,2]
    # to-pixel: [...,4,P,2] = grid[None..,None,P,2] - v[...,4,1,2]
    to_pix = grid.view(*([1] * (v.dim() - 2)), 1, -1, 2) - v.unsqueeze(-2)
    # 2D cross product (z component): edge.x*to.y - edge.y*to.x  -> [...,4,P]
    cross = edge[..., None, 0] * to_pix[..., 1] - edge[..., None, 1] * to_pix[..., 0]
    # cross is [..., 4, P]: reduce the 4-edges axis (dim=-2), keeping pixels (dim=-1).
    pos = (cross >= 0).all(dim=-2)             # inside if all edges agree (CCW)
    neg = (cross <= 0).all(dim=-2)             # ... or all agree (CW)
    return pos | neg


@torch.no_grad()
def render(state, gate_pos, gate_fwd, cur_idx, n_visible=2, add_noise=True, device=None):
    """Render a batch of FPV frames.

    state:    [N,10]  drone state (pos+vel+quat) — camera rides the drone.
    gate_pos: [N,G,3] gate centers (world).
    gate_fwd: [N,G,3] gate facing directions (world).
    cur_idx:  [N]     index of each env's current target gate.
    n_visible: how many gates from cur_idx onward to draw (current + lookahead).
    Returns:  [N,IMG,IMG,3] uint8 RGB (HWC), VQ1-desaturated.
    """
    dev = device or state.device
    state = state.to(dev)
    gate_pos = gate_pos.to(dev)
    gate_fwd = gate_fwd.to(dev)
    cur_idx = cur_idx.to(dev).long()
    N, G = gate_pos.shape[0], gate_pos.shape[1]
    cam_pos, cam_quat = state[:, 0:3], state[:, 6:10]

    # gather the n_visible gates starting at cur_idx (clamped to last gate)
    offs = torch.arange(n_visible, device=dev)
    idx = (cur_idx[:, None] + offs[None, :]).clamp(max=G - 1)        # [N, n_visible]
    gp = torch.gather(gate_pos, 1, idx[..., None].expand(N, n_visible, 3))
    gf = torch.gather(gate_fwd, 1, idx[..., None].expand(N, n_visible, 3))
    valid_gate = (cur_idx[:, None] + offs[None, :]) < G              # [N, n_visible] not past end

    # outer/inner corners -> pixels
    outer = _gate_corners(gp, gf, GATE_OUTER / 2.0)                  # [N,nv,4,3]
    inner = _gate_corners(gp, gf, GATE_INNER / 2.0)
    po, infront_o = _project(outer, cam_pos, cam_quat)              # [N,nv,4,2], [N,nv,4]
    pi, _         = _project(inner, cam_pos, cam_quat)
    visible = valid_gate & infront_o.all(dim=-1)                    # [N,nv] all corners in front

    # canvas — measured bg 27/255, per-env brightness jitter for robustness
    bg = BG_GRAY + (torch.rand(N, 1, 1, 1, device=dev) * 2 - 1) * BG_JITTER
    img = bg.expand(N, IMG, IMG, 3).clone()
    if add_noise:
        img = img + (torch.rand_like(img) * 2 - 1) * BG_NOISE

    # pixel grid needed by both ribbon and gates
    ys, xs = torch.meshgrid(torch.arange(IMG, device=dev), torch.arange(IMG, device=dev), indexing="ij")
    grid = torch.stack([xs.reshape(-1) + 0.5, ys.reshape(-1) + 0.5], dim=-1)   # [P,2]

    # --- track ribbon: randomized DISTRACTOR (never a reliable signal) ---
    # Quads between consecutive gate centers, dropped below gate height, cyan-blue,
    # translucent; present ~RIBBON_P of envs with randomized width/alpha + per-segment
    # lateral jitter. Painted BEFORE gates so gates always overdraw it.
    if G >= 2:
        ribbon_on = (torch.rand(N, device=dev) < RIBBON_P)                     # [N]
        if ribbon_on.any():
            rb_a = RIBBON_A[0] + torch.rand(N, 1, device=dev) * (RIBBON_A[1] - RIBBON_A[0])   # [N,1]
            rb_w = RIBBON_W[0] + torch.rand(N, 1, device=dev) * (RIBBON_W[1] - RIBBON_W[0])   # [N,1]
            rcol = img.new_tensor(RIBBON_COLOR)
            up = torch.tensor([0.0, 0.0, 1.0], device=dev)
            for s0 in range(G - 1):
                a = gate_pos[:, s0, :].clone()                                  # [N,3]
                b = gate_pos[:, s0 + 1, :].clone()
                a[:, 2] -= RIBBON_DROP
                b[:, 2] -= RIBBON_DROP
                seg = b - a
                lat = torch.cross(seg, up.expand_as(seg), dim=-1)
                lat = lat / (lat.norm(dim=-1, keepdim=True) + 1e-6)             # [N,3]
                jit = (torch.rand(N, 1, device=dev) * 2 - 1) * RIBBON_JIT
                a = a + lat * jit
                b = b + lat * jit
                # vertical band (tube-like, matches the official arcing ribbon's
                # visible height — a flat floor quad reads as a 2px sliver edge-on)
                half = up.expand_as(seg) * (rb_w / 2.0)
                quad = torch.stack([a - half, a + half, b + half, b - half], dim=1)  # [N,4,3]
                pq, infront = _project(quad[:, None], cam_pos, cam_quat)        # [N,1,4,2],[N,1,4]
                vis_r = ribbon_on & infront.squeeze(1).all(dim=-1)
                if not vis_r.any():
                    continue
                in_q = _inside_quad(grid, pq.squeeze(1)) & vis_r[:, None]       # [N,P]
                m = in_q.view(N, IMG, IMG, 1).float() * rb_a[:, :, None, None]
                img = img * (1 - m) + rcol[None, None, None, :] * m

    bright = img.new_tensor(GATE_BRIGHT)
    dim = img.new_tensor(GATE_DIM)

    # Paint far -> near so nearer gates overwrite farther ones. Order by gate-center
    # optical depth; simplest stable proxy: distance from camera.
    dists = (gp - cam_pos[:, None, :]).norm(dim=-1)                 # [N,nv]
    order = torch.argsort(dists, dim=1, descending=True)           # far first

    # glow corner quads: outer expanded, inner shrunk (approximates official bloom)
    glow_o = _gate_corners(gp, gf, GATE_OUTER / 2.0 * 1.18)
    glow_i = _gate_corners(gp, gf, GATE_INNER / 2.0 * 0.82)
    pgo, _ = _project(glow_o, cam_pos, cam_quat)
    pgi, _ = _project(glow_i, cam_pos, cam_quat)

    for slot in range(n_visible):
        g = order[:, slot]                                          # [N] which gate this slot
        bg_q = torch.gather(po, 1, g[:, None, None, None].expand(N, 1, 4, 2)).squeeze(1)  # [N,4,2]
        bi_q = torch.gather(pi, 1, g[:, None, None, None].expand(N, 1, 4, 2)).squeeze(1)
        go_q = torch.gather(pgo, 1, g[:, None, None, None].expand(N, 1, 4, 2)).squeeze(1)
        gi_q = torch.gather(pgi, 1, g[:, None, None, None].expand(N, 1, 4, 2)).squeeze(1)
        vis = torch.gather(visible, 1, g[:, None]).squeeze(1)       # [N] bool
        is_cur = (g == 0)                                           # slot's gate is the current target
        color = torch.where(is_cur[:, None], bright, dim)          # [N,3]
        # glow halo first: wider band, alpha-blended
        in_go = _inside_quad(grid, go_q)
        in_gi = _inside_quad(grid, gi_q)
        halo = (in_go & ~in_gi) & vis[:, None]                     # [N,P]
        hm = halo.view(N, IMG, IMG, 1).float() * GATE_GLOW_A
        img = img * (1 - hm) + color[:, None, None, :] * hm
        # solid frame core on top
        in_o = _inside_quad(grid, bg_q)                             # [N,P]
        in_i = _inside_quad(grid, bi_q)
        frame = (in_o & ~in_i) & vis[:, None]                      # [N,P]
        frame_img = frame.view(N, IMG, IMG, 1)
        img = torch.where(frame_img, color[:, None, None, :], img)

    out = (img.clamp(0, 1) * 255).to(torch.uint8)
    if _gm.enabled():                       # SkyDreamer route: feed gate-isolated obs
        out = _gm.gate_isolate_t(out)
    return out


if __name__ == "__main__":
    import time
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"device={dev}  IMG={IMG} HFOV={HFOV_DEG} FX={FX:.2f} CX={CX} TILT={TILT_DEG}deg")
    print(f"gate outer={GATE_OUTER} inner={GATE_INNER}")

    from dynamics import init_state

    # --- correctness: one drone at origin, level, gate 6 m dead-ahead (+X) ---
    s = init_state(1, dev, (0.0, 0.0, 2.0))
    gp = torch.tensor([[[6.0, 0.0, 2.0], [12.0, 1.5, 2.5]]], device=dev)   # [1,2,3]
    gf = torch.tensor([[[-1.0, 0.0, 0.0], [-1.0, 0.0, 0.0]]], device=dev)  # facing -X (toward drone)
    cur = torch.zeros(1, dtype=torch.long, device=dev)
    frame = render(s, gp, gf, cur)                                  # [1,64,64,3]
    print(f"frame shape={tuple(frame.shape)} dtype={frame.dtype} max={int(frame.max())}")

    # gate-frame pixel stats + tilt-sign check (centroid of bright pixels should be BELOW
    # center: spec camera tilts UP 20deg, so a level gate sits low in the frame)
    # palette-aware gate mask: orange-red core = high R, low-ish B (was mean>150 for
    # the pre-restyle bluish-white — stale threshold caught Day 131)
    f0 = frame[0].float()
    bright_mask = (f0[..., 0] > 180) & (f0[..., 2] < 150)
    ys, xs = torch.where(bright_mask)
    if ys.numel() > 0:
        cy_b = ys.float().mean().item()
        print(f"bright pixels={ys.numel()}  centroid_y={cy_b:.1f} (center={CY}); "
              f"{'BELOW center -> up-tilt sign OK' if cy_b > CY else 'ABOVE -> FLIP TILT SIGN'}")
        # hollow-center check: the geometric center pixel should NOT be bright (it's the hole)
        print(f"center pixel bright? {bool(bright_mask[IMG//2, IMG//2])} (expect False — fly-through hole)")
    else:
        print("WARNING: no bright pixels — gate not visible, check projection")

    # save a few sample frames for eyeballing VQ1-faithfulness (roadmap Phase 1.2 deliverable)
    try:
        from PIL import Image
        import os
        outdir = os.path.join(os.path.dirname(__file__), "render_samples")
        os.makedirs(outdir, exist_ok=True)
        # a short approach: drone flies toward the gate, save frames along the way
        s = init_state(1, dev, (-4.0, 0.0, 2.0))
        from dynamics import step, HOVER
        a = torch.tensor([[2 * HOVER - 1, 0.0, 0.0, 0.0]], device=dev)
        for k in range(5):
            fr = render(s, gp, gf, cur)[0].cpu().numpy()
            Image.fromarray(fr, "RGB").resize((256, 256), Image.NEAREST).save(
                os.path.join(outdir, f"approach_{k}.png"))
            for _ in range(15):
                s = step(s, a + torch.tensor([[0, 0, 0.05, 0]], device=dev))  # gentle pitch fwd
        print(f"saved 5 sample frames -> {outdir}")
    except Exception as e:
        print(f"(sample-frame save skipped: {type(e).__name__}: {e})")

    # --- throughput: batched render at thousands of FPS ---
    for N in (256, 1024, 4096):
        s = init_state(N, dev, (-4.0, 0.0, 2.0))
        gpN = gp.expand(N, 2, 3).contiguous()
        gfN = gf.expand(N, 2, 3).contiguous()
        curN = torch.zeros(N, dtype=torch.long, device=dev)
        if dev == "cuda": torch.cuda.synchronize()
        t0 = time.time()
        for _ in range(100):
            _ = render(s, gpN, gfN, curN)
        if dev == "cuda": torch.cuda.synchronize()
        dt = time.time() - t0
        print(f"THROUGHPUT N={N:5d}: {100*N/dt/1e3:8.1f}k frames/s  ({100/dt:6.1f} batched-renders/s)")
