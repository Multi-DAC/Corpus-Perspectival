"""
G3 + G4 verification tests — guards against silent drift between the
training-side conventions (z-up world, FLU body, rad/s body rates) and
the MAVSDK-side conventions (NED world, FRD body, deg/s body rates).

Run with: python -m pytest projects/aigrandprix/vision/tests/test_frame_conversion.py -v
"""

import math
import os
import sys

import numpy as np
import pytest

HERE = os.path.dirname(__file__)
VISION = os.path.dirname(HERE)
SIM = os.path.normpath(os.path.join(VISION, "..", "sim"))
sys.path.insert(0, VISION)
sys.path.insert(0, SIM)

from mavsdk_client import (  # noqa: E402
    ned_to_zup_position,
    ned_to_zup_quaternion,
    zup_to_ned_rates,
)
from drone_env_v2 import QuadParams  # noqa: E402


# ----------------------------------------------------------------------
# G3 — Frame conventions
# ----------------------------------------------------------------------


def test_ned_to_zup_position_known_axes():
    """North/East/Down → Forward/Left/Up: y and z negate, x preserved."""
    assert np.allclose(ned_to_zup_position(np.array([1, 0, 0])), [1, 0, 0])
    assert np.allclose(ned_to_zup_position(np.array([0, 1, 0])), [0, -1, 0])
    assert np.allclose(ned_to_zup_position(np.array([0, 0, 1])), [0, 0, -1])


def test_ned_to_zup_position_round_trip():
    """Applying the conversion twice must return identity (involution)."""
    rng = np.random.default_rng(42)
    for _ in range(20):
        v = rng.standard_normal(3)
        assert np.allclose(ned_to_zup_position(ned_to_zup_position(v)), v)


def test_ned_to_zup_quaternion_identity():
    """Identity quaternion in NED is identity in z-up."""
    q_id = np.array([1.0, 0.0, 0.0, 0.0])
    assert np.allclose(ned_to_zup_quaternion(q_id), q_id)


def test_ned_to_zup_quaternion_preserves_norm():
    """Component sign flips must not change the unit-norm property."""
    rng = np.random.default_rng(7)
    for _ in range(20):
        q = rng.standard_normal(4)
        q = q / np.linalg.norm(q)
        q_zup = ned_to_zup_quaternion(q)
        assert abs(np.linalg.norm(q_zup) - 1.0) < 1e-12


def test_ned_to_zup_quaternion_round_trip():
    """Conversion is an involution on quaternions too."""
    rng = np.random.default_rng(11)
    for _ in range(20):
        q = rng.standard_normal(4)
        q = q / np.linalg.norm(q)
        assert np.allclose(ned_to_zup_quaternion(ned_to_zup_quaternion(q)), q)


def test_ned_to_zup_quaternion_consistent_with_position():
    """
    The quaternion must rotate vectors *between* the same NED→FLU axis flip
    that the position function applies. We construct a vector v_ned, rotate
    it by an arbitrary attitude q_ned, then convert both to z-up — the
    rotated result must match rotating the converted vector by the converted
    quaternion.
    """
    def quat_rotate(q, v):
        w, x, y, z = q
        # Standard quaternion rotation: v' = q * v * q^-1
        # using Hamilton product, q = w + xi + yj + zk
        # Equivalent matrix form:
        ww, xx, yy, zz = w * w, x * x, y * y, z * z
        wx, wy, wz = w * x, w * y, w * z
        xy, xz, yz = x * y, x * z, y * z
        R = np.array([
            [ww + xx - yy - zz, 2 * (xy - wz),     2 * (xz + wy)    ],
            [2 * (xy + wz),     ww - xx + yy - zz, 2 * (yz - wx)    ],
            [2 * (xz - wy),     2 * (yz + wx),     ww - xx - yy + zz],
        ])
        return R @ v

    rng = np.random.default_rng(23)
    for _ in range(20):
        q_ned = rng.standard_normal(4)
        q_ned /= np.linalg.norm(q_ned)
        v_ned = rng.standard_normal(3)

        rotated_then_converted = ned_to_zup_position(quat_rotate(q_ned, v_ned))
        converted_then_rotated = quat_rotate(
            ned_to_zup_quaternion(q_ned), ned_to_zup_position(v_ned)
        )
        assert np.allclose(rotated_then_converted, converted_then_rotated, atol=1e-10)


def test_zup_to_ned_rates_axes():
    """Body rates: roll preserved, pitch and yaw flip sign (FLU↔FRD)."""
    assert np.allclose(zup_to_ned_rates(np.array([1, 0, 0])), [1, 0, 0])
    assert np.allclose(zup_to_ned_rates(np.array([0, 1, 0])), [0, -1, 0])
    assert np.allclose(zup_to_ned_rates(np.array([0, 0, 1])), [0, 0, -1])


def test_zup_to_ned_rates_round_trip():
    """Body rate conversion is an involution."""
    rng = np.random.default_rng(31)
    for _ in range(20):
        r = rng.standard_normal(3)
        assert np.allclose(zup_to_ned_rates(zup_to_ned_rates(r)), r)


# ----------------------------------------------------------------------
# G4 — Action rate scaling matches training
# ----------------------------------------------------------------------

# Re-imported here to keep the assertion tight (any rename in
# mavsdk_client.py will fail the import and surface immediately).
from mavsdk_client import send_policy_action_constants  # noqa: E402


def test_omega_max_xy_matches_training():
    """Client's MAX_RATE_XY must equal training env's omega_max_xy."""
    params = QuadParams()
    assert send_policy_action_constants["MAX_RATE_XY"] == params.omega_max_xy


def test_omega_max_z_matches_training():
    """Client's MAX_RATE_Z must equal training env's omega_max_z."""
    params = QuadParams()
    assert send_policy_action_constants["MAX_RATE_Z"] == params.omega_max_z


def test_rad_to_deg_constant():
    """RAD2DEG conversion factor must be standard."""
    assert abs(send_policy_action_constants["RAD2DEG"] - 180.0 / math.pi) < 1e-12


# ----------------------------------------------------------------------
# Bonus: world-frame gravity sign — the canonical z-up tell
# ----------------------------------------------------------------------


def test_training_world_frame_is_z_up():
    """
    The training env uses z-up by definition: gravity is [0, 0, -g].
    If this ever changes, the entire frame-conversion stack needs review.
    """
    sys.path.insert(0, SIM)
    import drone_env_v2

    src = open(drone_env_v2.__file__).read()
    assert "g_vec = np.array([0.0, 0.0, -params.g])" in src, (
        "Training env world-frame gravity convention changed — "
        "re-verify ned_to_zup_position / ned_to_zup_quaternion."
    )
