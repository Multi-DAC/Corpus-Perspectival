#
# Synthetic command-frame unit test for AI-GP VQ1 (Phase-0 regimen item 4).
#
# Locks the body-rate sign convention so the send path can never silently invert
# again. Pure/offline — no sim, no policy, runs in milliseconds. This is the GATE:
# the convention fix is correct iff this passes.
#
# Ground truth (measured, calib_log_2026-05-31.csv, see CALIB_FIT_2026-06-01.md):
#   ODOMETRY body rate = -(set_attitude_target sent rate), per axis, all three.
#   (Sign is clean at the step onset; magnitude is divergence-contaminated and
#    is NOT asserted here — sign-only, which is what governs fly-vs-tumble.)
#
# The obs path is validated (findings §1.8, 10/13 training terms reproduce), so
# ned_to_zup_omega is held FIXED; only the send path (zup_to_ned_rates) is fitted.
#
import numpy as np

# ---- obs path: VALIDATED, held fixed (verbatim from state_pilot) ----
def ned_to_zup_omega(o):        # ODOMETRY (FRD) -> policy FLU body rates
    return np.array([o[0], -o[1], -o[2]])

# ---- send path: the thing under test ----
def zup_to_ned_rates_OLD(r):    # what we flew tonight -> tumbled
    return np.array([r[0], -r[1], -r[2]])

def zup_to_ned_rates_FIXED(r):  # derived: negation of OLD == [-r, +p, +y]
    return np.array([-r[0], r[1], r[2]])

# ---- competition sim, modeled as the measured sign map ODOMETRY = -sent ----
def competition_sim_response(sent_cmd):
    """Given set_attitude_target rates we send, return the ODOMETRY rates the sim
    reports. Sign-exact per the calib measurement (gain abstracted away)."""
    return -np.asarray(sent_cmd, dtype=float)

def closed_loop_obs(desired_flu, send_fn):
    """policy desired FLU rate -> send_fn -> sim -> ODOMETRY -> obs FLU rate.
    Honest control requires this returns desired_flu (up to positive gain)."""
    sent = send_fn(np.asarray(desired_flu, dtype=float))
    odo  = competition_sim_response(sent)
    return ned_to_zup_omega(odo)


def test_rest_sends_zero():
    for fn in (zup_to_ned_rates_OLD, zup_to_ned_rates_FIXED):
        assert np.allclose(fn(np.zeros(3)), 0.0), "rest must command zero rate"

def test_old_path_inverts_all_axes():
    # Documents the bug we flew: closed loop is sign-inverted on every axis.
    for axis in range(3):
        d = np.zeros(3); d[axis] = 1.0
        obs = closed_loop_obs(d, zup_to_ned_rates_OLD)
        assert obs[axis] < 0, f"OLD path: axis {axis} should invert (bug), got {obs[axis]:+.1f}"

def test_fixed_path_is_honest_all_axes():
    # The fix: closed loop preserves sign on every axis (negative feedback).
    for axis in range(3):
        d = np.zeros(3); d[axis] = 1.0
        obs = closed_loop_obs(d, zup_to_ned_rates_FIXED)
        assert np.allclose(obs, d), f"FIXED path: axis {axis} must be honest, got {obs}"

def test_fixed_is_negation_of_old():
    rng = np.random.default_rng(0)
    for _ in range(100):
        r = rng.uniform(-1, 1, 3)
        assert np.allclose(zup_to_ned_rates_FIXED(r), -zup_to_ned_rates_OLD(r))


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = 0
    for t in fns:
        try:
            t(); passed += 1; print(f"  PASS  {t.__name__}")
        except AssertionError as e:
            print(f"  FAIL  {t.__name__}: {e}")
    print(f"\n{passed}/{len(fns)} passed")
    if passed != len(fns):
        raise SystemExit(1)
    print("Command-frame convention LOCKED: send path = [-r, +p, +y] (negation of tonight's).")
