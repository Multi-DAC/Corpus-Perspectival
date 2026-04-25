"""
MAVSDK Client — MAVLink Interface for AI Grand Prix VQ1

Wraps MAVSDK Python's async API into a synchronous interface
compatible with our competition loop.

Transport: MAVLink v2 over UDP
Commands: SET_ATTITUDE_TARGET (body rates + thrust)
Telemetry: position/velocity (ODOMETRY), attitude (ATTITUDE_QUATERNION),
           angular velocity (HIGHRES_IMU)

Frame convention:
    MAVLink uses NED (North-East-Down, z positive downward).
    Our policy was trained in z-up frame (z positive upward).
    This client converts NED → z-up on input (telemetry) and
    z-up → NED on output (commands), so the adapter/policy
    see the same frame they were trained on.

Coordinate mapping (NED → z-up):
    x_sim =  x_ned  (North → forward)
    y_sim = -y_ned  (East → left)
    z_sim = -z_ned  (Down → up)

Quaternion mapping:
    q_sim = [w, x, -y, -z] from q_ned = [w, x, y, z]
    (negating y,z components reflects the y/z axis flip)
"""

import asyncio
import math
import threading
import time
import numpy as np
from dataclasses import dataclass, field
from typing import Optional

try:
    from mavsdk import System
    from mavsdk.offboard import (
        OffboardError, AttitudeRate, Attitude, Offboard
    )
    MAVSDK_AVAILABLE = True
except ImportError:
    MAVSDK_AVAILABLE = False


@dataclass
class MAVTelemetry:
    """Telemetry snapshot in our z-up sim frame."""
    position: np.ndarray = field(
        default_factory=lambda: np.zeros(3))           # [x, y, z] meters, z-up
    velocity: np.ndarray = field(
        default_factory=lambda: np.zeros(3))           # [vx, vy, vz] m/s, z-up
    attitude_q: np.ndarray = field(
        default_factory=lambda: np.array([1., 0., 0., 0.]))  # [w, x, y, z] z-up frame
    angular_velocity: np.ndarray = field(
        default_factory=lambda: np.zeros(3))           # [p, q, r] rad/s, body frame
    timestamp: float = 0.0


def ned_to_zup_position(ned: np.ndarray) -> np.ndarray:
    """Convert NED position/velocity to z-up frame."""
    return np.array([ned[0], -ned[1], -ned[2]])


def ned_to_zup_quaternion(q_ned: np.ndarray) -> np.ndarray:
    """
    Convert quaternion from NED world frame to z-up world frame.
    Negating y and z components of the quaternion reflects the axis flip.
    """
    return np.array([q_ned[0], q_ned[1], -q_ned[2], -q_ned[3]])


def zup_to_ned_rates(rates_zup: np.ndarray) -> np.ndarray:
    """Convert body rates from z-up convention to NED convention."""
    # Body frame rates: roll (x), pitch (y), yaw (z)
    # With y/z flipped: pitch and yaw signs flip
    return np.array([rates_zup[0], -rates_zup[1], -rates_zup[2]])


# Module-level so tests can assert these match the training env without
# parsing the function body. Update both sites if you ever change either.
send_policy_action_constants = {
    "MAX_RATE_XY": 15.0,   # rad/s — must match QuadParams.omega_max_xy
    "MAX_RATE_Z": 0.3,     # rad/s — must match QuadParams.omega_max_z
    "RAD2DEG": 180.0 / math.pi,
}


class MAVSDKClient:
    """
    Synchronous wrapper around MAVSDK's async telemetry + offboard control.

    Runs an asyncio event loop in a background thread. Telemetry is updated
    via push subscriptions. Commands are dispatched to the event loop.

    Usage:
        client = MAVSDKClient()
        client.connect()
        client.arm()
        client.start_offboard()

        while running:
            telem = client.get_telemetry()
            # ... run policy ...
            client.send_body_rates(thrust_norm, wx, wy, wz)

        client.stop_offboard()
        client.disconnect()
    """

    def __init__(self,
                 system_address: str = "udp://:14540",
                 command_rate_hz: float = 50.0):
        """
        Args:
            system_address: MAVLink connection string (UDP endpoint).
                Default 14540 is PX4 SITL default.
            command_rate_hz: Target command rate. Used for timing, not enforced.
        """
        self.system_address = system_address
        self.command_rate_hz = command_rate_hz

        self._drone: Optional[object] = None  # mavsdk.System
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None

        # Latest telemetry — updated by subscription callbacks
        self._telem = MAVTelemetry()
        self._telem_lock = threading.Lock()

        # State flags
        self._connected = False
        self._armed = False
        self._in_offboard = False
        self._running = False

        # Latest body-rate setpoint pushed by the pre-stream / control loop.
        # PX4 requires a *flowing* stream of offboard setpoints (≥2 Hz, ≥10 Hz
        # recommended) to accept and hold the offboard mode change. We keep
        # the last commanded value here and let a background coroutine
        # republish it at PRESTREAM_HZ until a fresh send_body_rates()
        # arrives.
        self._last_setpoint = (0.0, 0.0, 0.0, 0.0)  # (thrust, roll, pitch, yaw) NED
        self._setpoint_lock = threading.Lock()
        self._prestream_task: Optional[object] = None  # asyncio.Task
        self._prestream_hz: float = 50.0

    # ------------------------------------------------------------------
    # Connection
    # ------------------------------------------------------------------

    def connect(self, timeout: float = 30.0):
        """Connect to the drone via MAVSDK. Blocks until connected."""
        if not MAVSDK_AVAILABLE:
            raise RuntimeError(
                "mavsdk not installed. Run: pip install mavsdk"
            )

        self._loop = asyncio.new_event_loop()
        self._running = True
        self._thread = threading.Thread(
            target=self._run_event_loop, daemon=True
        )
        self._thread.start()

        future = asyncio.run_coroutine_threadsafe(
            self._async_connect(timeout), self._loop
        )
        future.result(timeout=timeout + 5)
        print(f"MAVSDK connected to {self.system_address}")

    def _run_event_loop(self):
        """Background thread running the asyncio event loop."""
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    async def _async_connect(self, timeout: float):
        self._drone = System()
        await self._drone.connect(system_address=self.system_address)

        # Wait for connection with timeout
        t0 = time.monotonic()
        async for state in self._drone.core.connection_state():
            if state.is_connected:
                self._connected = True
                break
            if time.monotonic() - t0 > timeout:
                raise TimeoutError(
                    f"MAVSDK connection timed out after {timeout}s"
                )

        # Start telemetry subscriptions
        asyncio.ensure_future(self._sub_position_velocity())
        asyncio.ensure_future(self._sub_attitude())
        asyncio.ensure_future(self._sub_angular_velocity())

    # ------------------------------------------------------------------
    # Telemetry subscriptions (NED → z-up conversion happens here)
    # ------------------------------------------------------------------

    async def _sub_position_velocity(self):
        """Subscribe to position + velocity (NED from MAVSDK)."""
        async for pv in self._drone.telemetry.position_velocity_ned():
            pos_ned = np.array([
                pv.position.north_m,
                pv.position.east_m,
                pv.position.down_m,
            ])
            vel_ned = np.array([
                pv.velocity.north_m_s,
                pv.velocity.east_m_s,
                pv.velocity.down_m_s,
            ])
            with self._telem_lock:
                self._telem.position = ned_to_zup_position(pos_ned)
                self._telem.velocity = ned_to_zup_position(vel_ned)
                self._telem.timestamp = time.monotonic()

    async def _sub_attitude(self):
        """Subscribe to attitude quaternion."""
        async for att in self._drone.telemetry.attitude_quaternion():
            q_ned = np.array([att.w, att.x, att.y, att.z])
            with self._telem_lock:
                self._telem.attitude_q = ned_to_zup_quaternion(q_ned)

    async def _sub_angular_velocity(self):
        """Subscribe to angular velocity from IMU (body frame)."""
        async for imu in self._drone.telemetry.imu():
            # Body-frame angular velocity — no NED conversion needed
            # (body frame is the same regardless of world convention)
            omega = np.array([
                imu.angular_velocity_body.roll_rad_s,
                imu.angular_velocity_body.pitch_rad_s,
                imu.angular_velocity_body.yaw_rad_s,
            ])
            with self._telem_lock:
                self._telem.angular_velocity = omega

    # ------------------------------------------------------------------
    # Telemetry access (thread-safe read)
    # ------------------------------------------------------------------

    def get_telemetry(self) -> MAVTelemetry:
        """
        Get latest telemetry snapshot in z-up sim frame.
        Non-blocking — returns the most recently received data.
        """
        with self._telem_lock:
            return MAVTelemetry(
                position=self._telem.position.copy(),
                velocity=self._telem.velocity.copy(),
                attitude_q=self._telem.attitude_q.copy(),
                angular_velocity=self._telem.angular_velocity.copy(),
                timestamp=self._telem.timestamp,
            )

    # ------------------------------------------------------------------
    # Commands (z-up → NED conversion happens here)
    # ------------------------------------------------------------------

    def send_body_rates(self,
                        thrust_normalized: float,
                        roll_rate_deg_s: float,
                        pitch_rate_deg_s: float,
                        yaw_rate_deg_s: float):
        """
        Send body rate + thrust command.

        All values are in our z-up convention. This method converts
        to NED before sending via MAVSDK.

        Args:
            thrust_normalized: [0, 1] where 0=no thrust, 1=max thrust
            roll_rate_deg_s: Body roll rate in deg/s (our x-axis)
            pitch_rate_deg_s: Body pitch rate in deg/s (our y-axis)
            yaw_rate_deg_s: Body yaw rate in deg/s (our z-axis)
        """
        if not self._connected:
            return

        # Convert z-up body rates to NED body rates
        rates_zup = np.array([roll_rate_deg_s, pitch_rate_deg_s, yaw_rate_deg_s])
        rates_ned = zup_to_ned_rates(rates_zup)

        # Stash the latest setpoint so the pre-stream coroutine can keep
        # republishing it between policy steps. This guarantees PX4 sees
        # a continuous flow even if the policy stalls.
        with self._setpoint_lock:
            self._last_setpoint = (
                float(thrust_normalized),
                float(rates_ned[0]),
                float(rates_ned[1]),
                float(rates_ned[2]),
            )

    async def _async_send_rate(self, thrust, roll_rate, pitch_rate, yaw_rate):
        """Send attitude rate command via MAVSDK offboard."""
        try:
            await self._drone.offboard.set_attitude_rate(
                AttitudeRate(roll_rate, pitch_rate, yaw_rate, thrust)
            )
        except Exception as e:
            print(f"[MAVSDK] Rate command error: {e}")

    def send_policy_action(self, policy_action: np.ndarray):
        """
        Convenience: send raw policy output directly.

        Maps from policy's [-1,1] CTBR to MAVSDK commands:
            action[0]: collective_thrust [-1,1] → thrust [0,1]
            action[1]: ωx [-1,1] → roll rate ±15 rad/s → deg/s
            action[2]: ωy [-1,1] → pitch rate ±15 rad/s → deg/s
            action[3]: ωz [-1,1] → yaw rate ±0.3 rad/s → deg/s

        Args:
            policy_action: (4,) array in [-1, 1]
        """
        action = np.clip(policy_action, -1.0, 1.0)

        # Thrust: [-1,1] → [0,1]
        thrust = (action[0] + 1.0) * 0.5

        # Body rates: [-1,1] → rad/s → deg/s
        # Constants live at module scope (send_policy_action_constants) so
        # tests can assert they match the training env's QuadParams.
        MAX_RATE_XY = send_policy_action_constants["MAX_RATE_XY"]
        MAX_RATE_Z = send_policy_action_constants["MAX_RATE_Z"]
        RAD2DEG = send_policy_action_constants["RAD2DEG"]

        roll_rate = action[1] * MAX_RATE_XY * RAD2DEG
        pitch_rate = action[2] * MAX_RATE_XY * RAD2DEG
        yaw_rate = action[3] * MAX_RATE_Z * RAD2DEG

        self.send_body_rates(thrust, roll_rate, pitch_rate, yaw_rate)

    # ------------------------------------------------------------------
    # Offboard mode management
    # ------------------------------------------------------------------

    def arm(self):
        """Arm the drone."""
        future = asyncio.run_coroutine_threadsafe(
            self._drone.action.arm(), self._loop
        )
        future.result(timeout=10)
        self._armed = True
        print("[MAVSDK] Armed")

    def start_offboard(self):
        """
        Start offboard control mode.
        Must send an initial setpoint before starting.
        """
        future = asyncio.run_coroutine_threadsafe(
            self._async_start_offboard(), self._loop
        )
        future.result(timeout=10)

    async def _async_start_offboard(self):
        # PX4 requires a stream of setpoints flowing *before* it accepts the
        # mode change. Push ~500 ms of zero-rate setpoints, then launch the
        # background republisher, then call offboard.start().
        with self._setpoint_lock:
            self._last_setpoint = (0.0, 0.0, 0.0, 0.0)

        warmup_n = max(1, int(self._prestream_hz * 0.5))
        warmup_dt = 1.0 / self._prestream_hz
        for _ in range(warmup_n):
            await self._drone.offboard.set_attitude_rate(
                AttitudeRate(0.0, 0.0, 0.0, 0.0)
            )
            await asyncio.sleep(warmup_dt)

        # Launch the persistent republisher before requesting mode change
        self._prestream_task = asyncio.ensure_future(self._prestream_loop())

        try:
            await self._drone.offboard.start()
            self._in_offboard = True
            print("[MAVSDK] Offboard mode started")
        except OffboardError as e:
            # Tear down the pre-stream we just started
            self._prestream_task.cancel()
            self._prestream_task = None
            raise RuntimeError(f"Failed to start offboard: {e}")

    async def _prestream_loop(self):
        """Republish the latest setpoint at PRESTREAM_HZ until cancelled."""
        dt = 1.0 / self._prestream_hz
        try:
            while self._running:
                with self._setpoint_lock:
                    thrust, r, p, y = self._last_setpoint
                try:
                    await self._drone.offboard.set_attitude_rate(
                        AttitudeRate(r, p, y, thrust)
                    )
                except Exception as e:
                    # Log but keep streaming — transient failures shouldn't
                    # break the offboard contract.
                    print(f"[MAVSDK] Pre-stream send error: {e}")
                await asyncio.sleep(dt)
        except asyncio.CancelledError:
            pass

    def stop_offboard(self):
        """Stop offboard control mode."""
        if not self._in_offboard:
            return
        future = asyncio.run_coroutine_threadsafe(
            self._async_stop_offboard(), self._loop
        )
        future.result(timeout=10)

    async def _async_stop_offboard(self):
        # Cancel the pre-stream first so we stop pushing setpoints before
        # asking PX4 to leave offboard mode.
        if self._prestream_task is not None:
            self._prestream_task.cancel()
            try:
                await self._prestream_task
            except asyncio.CancelledError:
                pass
            self._prestream_task = None

        try:
            await self._drone.offboard.stop()
            self._in_offboard = False
            print("[MAVSDK] Offboard mode stopped")
        except OffboardError as e:
            print(f"[MAVSDK] Stop offboard error: {e}")

    # ------------------------------------------------------------------
    # Orchestrated bring-up
    # ------------------------------------------------------------------

    def init_flight(self,
                    connect_timeout: float = 30.0,
                    health_timeout: float = 30.0,
                    arm_timeout: float = 10.0,
                    offboard_timeout: float = 10.0):
        """
        Run the full bring-up: connect → wait_for_health → arm → start_offboard.

        Each step gets its own timeout. On any failure, raises RuntimeError
        with the failed step named so callers know where to look. Idempotent
        per-step: skips a step if it's already done.

        After this returns successfully, send_policy_action() / send_body_rates()
        will be honored by the autopilot.
        """
        try:
            if not self._connected:
                self.connect(timeout=connect_timeout)
        except Exception as e:
            raise RuntimeError(f"init_flight: connect failed — {e}") from e

        try:
            self.wait_for_health(timeout=health_timeout)
        except Exception as e:
            raise RuntimeError(f"init_flight: health check failed — {e}") from e

        try:
            if not self._armed:
                # arm() uses a hard-coded 10s timeout internally; we surface
                # the param here for symmetry but rely on arm()'s own wait.
                _ = arm_timeout
                self.arm()
        except Exception as e:
            raise RuntimeError(f"init_flight: arm failed — {e}") from e

        try:
            if not self._in_offboard:
                _ = offboard_timeout
                self.start_offboard()
        except Exception as e:
            raise RuntimeError(f"init_flight: offboard start failed — {e}") from e

        print("[MAVSDK] init_flight complete — ready for policy commands")

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def armed(self) -> bool:
        return self._armed

    @property
    def in_offboard(self) -> bool:
        return self._in_offboard

    async def _check_health(self) -> bool:
        """Check if drone is healthy enough for offboard."""
        async for health in self._drone.telemetry.health():
            return (health.is_local_position_ok and
                    health.is_armable)

    def wait_for_health(self, timeout: float = 30.0):
        """Block until drone reports healthy."""
        future = asyncio.run_coroutine_threadsafe(
            self._async_wait_health(timeout), self._loop
        )
        future.result(timeout=timeout + 5)

    async def _async_wait_health(self, timeout: float):
        t0 = time.monotonic()
        async for health in self._drone.telemetry.health():
            if health.is_local_position_ok and health.is_armable:
                print("[MAVSDK] Health OK — local position + armable")
                return
            if time.monotonic() - t0 > timeout:
                raise TimeoutError("Drone health check timed out")

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def disconnect(self):
        """Clean shutdown."""
        if self._in_offboard:
            self.stop_offboard()
        self._running = False
        if self._loop and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._thread:
            self._thread.join(timeout=5)
        self._connected = False
        print("[MAVSDK] Disconnected")


# ======================================================================
# Stub client for offline testing (no MAVSDK dependency)
# ======================================================================

class StubMAVSDKClient:
    """
    Drop-in replacement for MAVSDKClient that works without MAVSDK.
    Returns zeroed telemetry and silently accepts commands.
    Used for pipeline testing when no simulator is available.
    """

    def __init__(self, **kwargs):
        self._connected = False
        self._armed = False
        self._in_offboard = False

    def connect(self, timeout: float = 30.0):
        self._connected = True
        print("[StubMAVSDK] Connected (stub)")

    def get_telemetry(self) -> MAVTelemetry:
        return MAVTelemetry()

    def send_body_rates(self, thrust, roll_rate, pitch_rate, yaw_rate):
        pass

    def send_policy_action(self, policy_action: np.ndarray):
        pass

    def arm(self):
        self._armed = True

    def start_offboard(self):
        self._in_offboard = True

    def stop_offboard(self):
        self._in_offboard = False

    def wait_for_health(self, timeout: float = 30.0):
        pass

    def init_flight(self,
                    connect_timeout: float = 30.0,
                    health_timeout: float = 30.0,
                    arm_timeout: float = 10.0,
                    offboard_timeout: float = 10.0):
        """Stub mirror of the real init_flight; runs each step with no I/O."""
        if not self._connected:
            self.connect(timeout=connect_timeout)
        self.wait_for_health(timeout=health_timeout)
        if not self._armed:
            self.arm()
        if not self._in_offboard:
            self.start_offboard()

    def disconnect(self):
        self._connected = False

    @property
    def connected(self):
        return self._connected

    @property
    def armed(self):
        return self._armed

    @property
    def in_offboard(self):
        return self._in_offboard
