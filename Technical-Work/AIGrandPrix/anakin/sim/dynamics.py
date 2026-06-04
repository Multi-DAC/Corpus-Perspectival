"""
Anakin training-sim dynamics — CTBR kinematic quadrotor, GPU-vectorized (torch).

Flight model calibrated to the official AI-GP FlightSim (system-identified 2026-06-01;
refs: ../../ue5_sim/DRONE_DYNAMICS.md, ../../vision/vq1_pilot/CALIB_FIT_2026-06-01.md).

CTBR = collective thrust + body rates, with perfect-rate-tracking (ACRO). This matches BOTH
the Dream-to-Fly action space AND FlightSim's set_attitude_target interface, and is far cheaper
to batch than the 4-motor/inertia model (drone_env_v2) — body rates ARE the control, integrated
directly into orientation (no torque/inertia loop).

Units: SI (m, s, rad). State per drone: [pos(3), vel(3), quat(4, w x y z)] = 10.
Action per drone: [collective, wx, wy, wz] in [-1,1]^4 (tanh policy output, Dream-to-Fly style).
Batched: tensors are [N, ...] on `device`; N parallel drones step in lockstep.

CONVENTION (self-consistent, right-handed, Z-up; thrust along body +Z):
  This is the TRAINING frame. The policy learns to fly in it. The deploy adapter (Phase 4) maps
  this CTBR output to FlightSim's set_attitude_target with the validated sign table from
  DRONE_DYNAMICS.md — kept EXPLICIT and SEPARATE (the L17#6 sign-inversion landmine: a wrong
  sign inverts flight; it wrecked the first competition run). Do not assume train==deploy signs.
"""
import torch

# --- calibrated constants (FlightSim sysID, W1 re-probe 2026-06-01) ---
G        = 9.81           # gravity, m/s^2
TWR      = 3.95           # thrust-to-weight at collective=1.0 (CALIB_FIT_2026-06-01.md)
TMAX     = TWR * G        # max thrust acceleration, m/s^2  (~38.7)
HOVER    = 1.0 / TWR      # collective fraction for hover  (~0.253)
CD       = 0.30           # linear drag, 1/s  (kept at 0.3 pending a dedicated drag probe)
OMEGA_XY = 15.0           # max roll/pitch body rate, rad/s
OMEGA_Z  = 2.5            # max yaw body rate, rad/s (yaw NOT tightly limited — W1 hit 2.4 @cmd 1.0)


def quat_mult(q1, q2):
    """Hamilton product, batched. q[...,4] = (w,x,y,z)."""
    w1, x1, y1, z1 = q1.unbind(-1)
    w2, x2, y2, z2 = q2.unbind(-1)
    return torch.stack([
        w1*w2 - x1*x2 - y1*y2 - z1*z2,
        w1*x2 + x1*w2 + y1*z2 - z1*y2,
        w1*y2 - x1*z2 + y1*w2 + z1*x2,
        w1*z2 + x1*y2 - y1*x2 + z1*w2,
    ], dim=-1)


def quat_rotate(q, v):
    """Rotate v[...,3] by unit quat q[...,4]."""
    qv = torch.cat([torch.zeros_like(v[..., :1]), v], dim=-1)
    qc = q * q.new_tensor([1., -1., -1., -1.])
    return quat_mult(quat_mult(q, qv), qc)[..., 1:]


def map_action(action):
    """[-1,1]^4 -> (collective_accel[...,1], omega[...,3] rad/s)."""
    a = action.clamp(-1.0, 1.0)
    collective = (a[..., 0:1] + 1.0) * 0.5 * TMAX                 # [-1,1] -> [0, TMAX]
    omega = a[..., 1:4] * a.new_tensor([OMEGA_XY, OMEGA_XY, OMEGA_Z])
    return collective, omega


def step(state, action, dt=0.02, substeps=4):
    """Advance [N,10] state by one control tick (dt) using `substeps` physics substeps.
    Returns new [N,10] state. Semi-implicit Euler. Pure-functional (no in-place on input)."""
    collective, omega = map_action(action)
    g_vec = state.new_tensor([0., 0., -G])
    h = dt / substeps
    p = state[..., 0:3]
    v = state[..., 3:6]
    q = state[..., 6:10]
    omega_q = torch.cat([torch.zeros_like(omega[..., :1]), omega], dim=-1)
    zc = torch.zeros_like(collective)
    for _ in range(substeps):
        # orientation: integrate by commanded body rates (perfect rate tracking), renormalize
        q = q + 0.5 * quat_mult(q, omega_q) * h
        q = q / q.norm(dim=-1, keepdim=True).clamp_min(1e-9)
        # thrust (body +Z) -> world; gravity; linear drag
        thrust_body = torch.cat([zc, zc, collective], dim=-1)
        a_world = quat_rotate(q, thrust_body) + g_vec - CD * v
        v = v + a_world * h          # semi-implicit: v before p
        p = p + v * h
    return torch.cat([p, v, q], dim=-1)


def init_state(n, device="cpu", pos=None):
    """N drones at rest, level (identity quat). pos: [3] or None (origin)."""
    s = torch.zeros(n, 10, device=device)
    s[:, 6] = 1.0  # qw = 1 (identity)
    if pos is not None:
        s[:, 0:3] = torch.as_tensor(pos, device=device, dtype=s.dtype)
    return s


if __name__ == "__main__":
    import time
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"device={dev}  TWR={TWR} TMAX={TMAX:.2f} HOVER={HOVER:.3f} CD={CD}")

    def fly(action_vec, steps=100, n=1, pos=(0, 0, 5.0)):
        s = init_state(n, dev, pos)
        a = torch.tensor(action_vec, device=dev).float().expand(n, 4)
        for _ in range(steps):
            s = step(s, a)
        return s

    # 1) hover holds altitude
    s = fly([2*HOVER-1, 0, 0, 0], steps=100)  # collective=HOVER (map: (a+1)/2*TMAX = HOVER*TMAX)
    print(f"HOVER 2s: z={s[0,2]:.3f} (start 5.0), speed={s[0,3:6].norm():.3f}  -> drift {abs(s[0,2].item()-5.0):.3f}m")

    # 2) full collective climbs; zero collective falls
    su = fly([1.0, 0, 0, 0], steps=50); print(f"FULL THRUST 1s: z={su[0,2]:.2f} vz={su[0,5]:.2f} (should climb)")
    sd = fly([-1.0, 0, 0, 0], steps=50); print(f"ZERO THRUST 1s: z={sd[0,2]:.2f} vz={sd[0,5]:.2f} (should fall ~ -g)")

    # 3) pitch body-rate produces horizontal motion (document the sign)
    sp = fly([2*HOVER-1, 0, 0.3, 0], steps=80)  # wy>0 with hover thrust
    print(f"PITCH wy>0 + hover, 1.6s: pos=({sp[0,0]:.2f},{sp[0,1]:.2f},{sp[0,2]:.2f}) vel=({sp[0,3]:.2f},{sp[0,4]:.2f},{sp[0,5]:.2f})")
    sr = fly([2*HOVER-1, 0.3, 0, 0], steps=80)  # wx>0
    print(f"ROLL  wx>0 + hover, 1.6s: pos=({sr[0,0]:.2f},{sr[0,1]:.2f},{sr[0,2]:.2f})")

    # 4) throughput: thousands of envs on GPU
    N = 4096
    s = init_state(N, dev, (0, 0, 5.0))
    a = torch.rand(N, 4, device=dev) * 0.2 + torch.tensor([2*HOVER-1, 0, 0, 0], device=dev)
    if dev == "cuda": torch.cuda.synchronize()
    t0 = time.time()
    for _ in range(1000):
        s = step(s, a)
    if dev == "cuda": torch.cuda.synchronize()
    dt = time.time() - t0
    print(f"THROUGHPUT: {N} envs x 1000 ctrl-steps in {dt:.2f}s = {N*1000/dt/1e6:.1f}M env-steps/s")
