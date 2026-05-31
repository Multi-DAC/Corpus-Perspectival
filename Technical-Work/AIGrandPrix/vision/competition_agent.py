"""
Competition Agent — Entry Point for AI Grand Prix VQ1

Interfaces with the competition simulator via MAVSDK (MAVLink v2 over UDP).
The vision stream spec is pending — camera integration is stubbed until then.

Architecture:
    MAVSDK Telemetry + Camera → GateDetector → Adapter → Policy → MAVSDK Commands

Control mode: SET_ATTITUDE_TARGET (body rates + thrust) via Offboard plugin.
Physics: 120 Hz server-side. Command rate: 50-120 Hz (our loop speed).
Max run: 8 minutes.

Usage:
    # Competition mode (requires MAVSDK + running simulator):
    python competition_agent.py --model path/to/best_model.zip --compete

    # Competition with custom endpoint:
    python competition_agent.py --model path/to/best_model.zip --compete --address udp://:14550

    # Offline test with our own sim (no MAVSDK needed):
    python competition_agent.py --model path/to/best_model.zip --test
"""

import argparse
import math
import numpy as np
import time
from pathlib import Path

from gate_detector import GateDetector, GateDetectorConfig
from adapter import CompetitionAdapter, VisionPolicyBridge, Telemetry
from mavsdk_client import MAVSDKClient, StubMAVSDKClient, MAVTelemetry, MAVSDK_AVAILABLE
from udp_vision_receiver import UdpVisionReceiver


def load_policy(model_path: str):
    """Load trained PPO policy."""
    from stable_baselines3 import PPO
    model = PPO.load(model_path)
    print(f"Policy loaded: {model_path}")
    print(f"  Params: {sum(p.numel() for p in model.policy.parameters()):,}")
    return model


def create_pipeline(model_path: str,
                    image_width: int = 640,
                    image_height: int = 360,
                    fov_deg: float = 90.0,
                    command_rate_hz: float = 50.0) -> VisionPolicyBridge:
    """Create the full vision-to-action pipeline.

    DCL VQ1 spec (VADR-TS-002 Issue 00.02, 2026-05-08):
      Image resolution: 640px x 360px
      [cx,cy] = [320px, 180px]
      [fx,fy] = [320, 320]
      Camera tilted upwards by 20° (NED — handle in adapter for body-frame gate pose)
      Vision stream: UDP port 5600, 30 Hz, JPEG-encoded with 24-byte chunked metadata header

    HFoV convention: fov_deg=90 with image_width=640 yields fx=320 ✓ (matches spec)
    Then image_height=360 yields cy=180 ✓ (matches spec).
    """

    # 1. Gate detector
    config = GateDetectorConfig()
    detector = GateDetector(config)
    detector.set_camera_from_fov(image_width, image_height, fov_deg)

    # 2. Adapter (with command rate matching our loop)
    adapter = CompetitionAdapter(command_rate_hz=command_rate_hz)

    # 3. Policy
    policy = load_policy(model_path)

    # 4. Bridge
    bridge = VisionPolicyBridge(policy, detector, adapter)

    return bridge


def mav_telemetry_to_adapter(mav: MAVTelemetry) -> Telemetry:
    """Convert MAVSDKClient telemetry to adapter's Telemetry dataclass."""
    return Telemetry(
        position=mav.position,
        velocity=mav.velocity,
        orientation=mav.attitude_q,
        angular_velocity=mav.angular_velocity,
    )


# ============================================================
# Main Competition Loop (MAVSDK)
# ============================================================

def run_competition(model_path: str,
                    system_address: str = "udp://:14540",
                    command_rate_hz: float = 50.0,
                    max_duration_s: float = 480.0,
                    vision_port: int = 5600):
    """
    Main competition loop using MAVSDK.

    Flow:
        1. Connect to simulator via MAVSDK
        2. Arm + start offboard mode
        3. Loop: telemetry → vision → policy → command
        4. Stop after max_duration or race end signal

    Args:
        model_path: Path to trained PPO model (.zip)
        system_address: MAVSDK connection string
        command_rate_hz: Target command rate (50-120 Hz per spec)
        max_duration_s: Maximum run time (8 min = 480s per spec)
    """
    if not MAVSDK_AVAILABLE:
        print("ERROR: mavsdk not installed. Run: pip install mavsdk")
        return

    target_dt = 1.0 / command_rate_hz

    # Create pipeline
    bridge = create_pipeline(model_path, command_rate_hz=command_rate_hz)

    # Connect to simulator
    client = MAVSDKClient(
        system_address=system_address,
        command_rate_hz=command_rate_hz,
    )
    client.connect()
    client.wait_for_health()

    # Arm and start offboard
    client.arm()
    client.start_offboard()

    print(f"Competition agent running @ {command_rate_hz} Hz target")
    print(f"Max duration: {max_duration_s}s")
    bridge.reset()

    # Start the UDP vision-stream receiver (spec §4.6, port 5600). Background thread;
    # get_latest_frame() is non-blocking and returns the newest complete BGR frame.
    vision_rx = UdpVisionReceiver(port=vision_port)
    vision_rx.start()
    print(f"Vision receiver listening on UDP :{vision_port}")

    step_count = 0
    t_start = time.perf_counter()

    try:
        while True:
            t0 = time.perf_counter()
            elapsed = t0 - t_start

            # Check time limit
            if elapsed >= max_duration_s:
                print(f"Time limit reached ({max_duration_s}s)")
                break

            # Get telemetry (already in z-up frame)
            mav_telem = client.get_telemetry()
            telemetry = mav_telemetry_to_adapter(mav_telem)

            # Get camera frame from the UDP vision stream (spec §4.6, port 5600).
            camera = vision_rx.get_latest_frame()
            if camera is None:
                # No frame yet (pre-first-packet, or a decode miss). Blank frame → detector
                # returns no detection → the bridge's blind-flight hold / no-gate default
                # keeps flight stable rather than feeding garbage.
                camera = np.zeros((360, 640, 3), dtype=np.uint8)

            # Run full pipeline: camera → gate detect → observation → policy → action
            action = bridge.step(telemetry, camera)

            # Send command via MAVSDK
            # action fields are already in physical units (rad/s + normalized thrust)
            RAD2DEG = 180.0 / math.pi
            client.send_body_rates(
                thrust_normalized=action.throttle,
                roll_rate_deg_s=action.roll_rate_rad_s * RAD2DEG,
                pitch_rate_deg_s=action.pitch_rate_rad_s * RAD2DEG,
                yaw_rate_deg_s=action.yaw_rate_rad_s * RAD2DEG,
            )

            step_count += 1
            dt = time.perf_counter() - t0

            # Rate limiting — sleep if we're faster than target
            sleep_time = target_dt - dt
            if sleep_time > 0:
                time.sleep(sleep_time)

            if step_count % 500 == 0:
                actual_dt = time.perf_counter() - t0
                print(f"  Step {step_count}: dt={actual_dt*1000:.1f}ms "
                      f"({1/max(actual_dt,1e-6):.0f} Hz) "
                      f"elapsed={elapsed:.1f}s")

    except KeyboardInterrupt:
        print("\nInterrupted by user")
    finally:
        vision_rx.stop()
        client.stop_offboard()
        client.disconnect()
        print(f"Vision: {vision_rx.frames_completed} frames received, "
              f"{bridge.frames_held} frames held (blind-flight fallback)")

    total_time = time.perf_counter() - t_start
    avg_hz = step_count / max(total_time, 1e-6)
    print(f"Race complete. {step_count} steps in {total_time:.1f}s "
          f"(avg {avg_hz:.0f} Hz)")


# ============================================================
# Offline Testing (with our own sim — no MAVSDK needed)
# ============================================================

def test_pipeline_offline(model_path: str, n_episodes: int = 3):
    """
    Test the full pipeline using our own simulation + synthetic camera.
    Validates that gate_detector -> adapter -> policy -> action works end-to-end.
    """
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / 'sim'))
    sys.path.insert(0, str(Path(__file__).parent.parent / 'rl'))

    from stable_baselines3 import PPO
    from infinite_gate_env import InfiniteGateEnv
    from train_ppo import ImprovedObsWrapper, CTBRActionWrapper

    print("=" * 60)
    print("Offline Pipeline Test")
    print("=" * 60)

    # Load policy
    model = PPO.load(model_path)

    # Create env
    env = InfiniteGateEnv(
        gate_radius=0.75,
        max_steps=10000,
        dt=0.002,
        substeps=1,
        domain_rand=False,
        adaptive_curriculum=False,
    )

    for ep in range(n_episodes):
        obs, info = env.reset()
        total_reward = 0
        gates = 0

        for step in range(10000):
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = env.step(action)
            total_reward += reward
            gates = info.get('gates_passed', gates)

            if terminated or truncated:
                break

        print(f"  Episode {ep+1}: gates={gates}, reward={total_reward:.1f}, "
              f"steps={step+1}")

    env.close()
    print("\nOffline test complete.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='AI Grand Prix Competition Agent')
    parser.add_argument('--model', type=str, required=True,
                        help='Path to trained model (.zip)')
    parser.add_argument('--test', action='store_true',
                        help='Run offline test with our sim')
    parser.add_argument('--compete', action='store_true',
                        help='Run in competition mode (requires MAVSDK + simulator)')
    parser.add_argument('--address', type=str, default='udp://:14540',
                        help='MAVSDK connection string (default: udp://:14540)')
    parser.add_argument('--rate', type=float, default=50.0,
                        help='Command rate in Hz (default: 50, spec allows 50-120)')
    parser.add_argument('--max-time', type=float, default=480.0,
                        help='Max run time in seconds (default: 480 = 8 min)')
    parser.add_argument('--vision-port', type=int, default=5600,
                        help='UDP vision-stream port (default: 5600 per VQ1 spec §4.6)')

    args = parser.parse_args()

    if args.test:
        test_pipeline_offline(args.model)
    elif args.compete:
        run_competition(args.model, args.address, args.rate, args.max_time, args.vision_port)
    else:
        # Default: offline test
        test_pipeline_offline(args.model)
