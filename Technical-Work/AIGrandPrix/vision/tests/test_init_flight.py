"""
G2 verification — init_flight() orchestration contract.

Uses StubMAVSDKClient to verify that the bring-up sequence drives the
client through the expected state transitions (connected → health-ok →
armed → in-offboard) without requiring a live SITL. The real client
inherits the same flow; only the I/O differs.
"""

import os
import sys

import numpy as np
import pytest

HERE = os.path.dirname(__file__)
VISION = os.path.dirname(HERE)
sys.path.insert(0, VISION)

from mavsdk_client import StubMAVSDKClient, MAVTelemetry  # noqa: E402


def test_init_flight_drives_state_machine():
    client = StubMAVSDKClient()
    assert not client.connected
    assert not client._armed
    assert not client._in_offboard

    client.init_flight(connect_timeout=1, health_timeout=1)

    assert client.connected
    assert client._armed
    assert client._in_offboard


def test_init_flight_idempotent():
    """Calling init_flight twice must not raise or rearm/restart."""
    client = StubMAVSDKClient()
    client.init_flight(connect_timeout=1, health_timeout=1)
    # Second call is a no-op for the stub; should not raise
    client.init_flight(connect_timeout=1, health_timeout=1)
    assert client.connected and client._armed and client._in_offboard


def test_send_policy_action_after_init_flight():
    """Stub silently accepts policy actions once init_flight has run."""
    client = StubMAVSDKClient()
    client.init_flight(connect_timeout=1, health_timeout=1)
    action = np.array([0.0, 0.1, -0.1, 0.0], dtype=np.float32)
    # Should not raise
    client.send_policy_action(action)


def test_telemetry_returns_zero_until_connected():
    client = StubMAVSDKClient()
    telem = client.get_telemetry()
    assert isinstance(telem, MAVTelemetry)
    assert np.allclose(telem.position, 0)
    assert np.allclose(telem.velocity, 0)
    assert np.allclose(telem.attitude_q, [1, 0, 0, 0])


# ----------------------------------------------------------------------
# G1 verification — pre-stream wiring on the real MAVSDKClient class.
# We don't connect to a sim here; we just check the structural invariants:
# the class exposes the pre-stream coroutine, has the lock + last-setpoint
# slot, and its default rate is 50 Hz. SITL behavior is the integration
# sprint.
# ----------------------------------------------------------------------


def test_real_client_has_prestream_attributes():
    from mavsdk_client import MAVSDKClient

    client = MAVSDKClient.__new__(MAVSDKClient)
    # Run constructor manually so we don't trigger the mavsdk import path
    MAVSDKClient.__init__(client)

    assert hasattr(client, "_prestream_task")
    assert client._prestream_task is None
    assert hasattr(client, "_setpoint_lock")
    assert hasattr(client, "_last_setpoint")
    assert client._last_setpoint == (0.0, 0.0, 0.0, 0.0)
    assert client._prestream_hz == 50.0


def test_real_client_has_prestream_coroutine_and_init_flight():
    from mavsdk_client import MAVSDKClient
    import inspect

    assert hasattr(MAVSDKClient, "_prestream_loop")
    assert inspect.iscoroutinefunction(MAVSDKClient._prestream_loop)
    assert hasattr(MAVSDKClient, "init_flight")
    assert callable(MAVSDKClient.init_flight)


def test_send_body_rates_updates_setpoint_without_offboard():
    """
    send_body_rates should *always* refresh the latest setpoint when
    connected, even before offboard is engaged — the pre-stream needs
    fresh values. Only the bypass-when-disconnected guard remains.
    """
    from mavsdk_client import MAVSDKClient, zup_to_ned_rates

    client = MAVSDKClient.__new__(MAVSDKClient)
    MAVSDKClient.__init__(client)
    client._connected = True  # simulate post-connect, pre-offboard
    client._in_offboard = False

    client.send_body_rates(0.5, 10.0, -5.0, 1.0)

    expected_ned = zup_to_ned_rates(np.array([10.0, -5.0, 1.0]))
    thrust, r, p, y = client._last_setpoint
    assert thrust == 0.5
    assert (r, p, y) == (expected_ned[0], expected_ned[1], expected_ned[2])


def test_send_body_rates_noop_when_disconnected():
    from mavsdk_client import MAVSDKClient

    client = MAVSDKClient.__new__(MAVSDKClient)
    MAVSDKClient.__init__(client)
    # Not connected
    client.send_body_rates(0.7, 99.0, 99.0, 99.0)
    assert client._last_setpoint == (0.0, 0.0, 0.0, 0.0)
