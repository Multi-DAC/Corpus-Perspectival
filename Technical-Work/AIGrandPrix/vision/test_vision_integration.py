"""
Vision integration smoke test — sim-independent, no model/SB3/MAVSDK needed.

Verifies the two things wired up 2026-05-31 before the VQ1 sim drop:
  (A) UDP receiver -> JPEG decode -> GateDetector.detect runs end-to-end on synthetic frames.
  (B) VisionPolicyBridge blind-flight fallback: detected -> stored; brief miss -> HELD
      (last-known gate reused in the observation); sustained miss -> LOST (no-gate default).

Run:  python vision/test_vision_integration.py   (from the AIGrandPrix dir)
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np

from adapter import CompetitionAdapter, VisionPolicyBridge, Telemetry
from udp_vision_receiver import UdpVisionReceiver, chunk_frame


# ---- stubs (let us control detection + capture the observation) -----------------------
class StubDetection:
    def __init__(self, found, position_3d=None, distance=None, bearing_body=None, area=0.0):
        self.found = found
        self.position_3d = position_3d
        self.distance = distance
        self.bearing_body = bearing_body
        self.area = area


class StubDetector:
    """Returns whatever detection we set. detect() ignores the frame."""
    def __init__(self):
        self.next = [StubDetection(False)]
    def set_found(self, pos_cam, dist):
        self.next = [StubDetection(True, position_3d=np.array(pos_cam, float),
                                   distance=dist, bearing_body=np.array(pos_cam, float),
                                   area=100.0)]
    def set_missed(self):
        self.next = [StubDetection(False)]
    def detect(self, frame):
        return self.next


class StubPolicy:
    """Records the last observation it was asked to predict on."""
    def __init__(self):
        self.last_obs = None
    def predict(self, obs, deterministic=True):
        self.last_obs = np.asarray(obs, float)
        return np.array([0.0, 0.0, 0.0, 0.0], dtype=np.float32), None


def _telem():
    return Telemetry(
        position=np.array([0.0, 0.0, 2.0]),
        velocity=np.array([1.0, 0.0, 0.0]),
        orientation=np.array([1.0, 0.0, 0.0, 0.0]),  # identity quat
        angular_velocity=np.zeros(3),
    )


# obs layout (see adapter.build_observation assembly): rel_gate_body = obs[9:12], dist = obs[12]
REL_GATE = slice(9, 12)
DIST_IDX = 12


def test_fallback():
    pol, det = StubPolicy(), StubDetector()
    bridge = VisionPolicyBridge(pol, det, CompetitionAdapter(command_rate_hz=50.0),
                                camera_tilt_deg=20.0, gate_hold_frames=8)
    bridge.reset()
    frame = np.zeros((360, 640, 3), np.uint8)

    # 1. gate detected at 5 m ahead (camera frame z=forward)
    det.set_found(pos_cam=[0.0, 0.0, 5.0], dist=5.0)
    bridge.step(_telem(), frame)
    held_gate = pol.last_obs[REL_GATE].copy()
    assert bridge._last_gate is not None and not bridge.lost, "detection should store + not be lost"
    assert np.linalg.norm(held_gate) > 0.1, "detected gate should give nonzero rel_gate_body"
    print(f"[1] detected  : rel_gate_body={held_gate.round(3)} stored; lost={bridge.lost}")

    # 2. eight consecutive misses (within hold window) -> HELD: obs reuses last-known gate
    det.set_missed()
    for i in range(8):
        bridge.step(_telem(), frame)
        assert not bridge.lost, f"miss {i+1}/8 should still be HELD, not lost"
        assert np.allclose(pol.last_obs[REL_GATE], held_gate), \
            f"held frame {i+1} must reuse last-known gate, got {pol.last_obs[REL_GATE]}"
    print(f"[2] hold 8x   : rel_gate_body held at {pol.last_obs[REL_GATE].round(3)}; "
          f"frames_held={bridge.frames_held}; lost={bridge.lost}")

    # 3. ninth miss -> beyond hold window -> LOST: no-gate default (zeros, dist=10)
    bridge.step(_telem(), frame)
    assert bridge.lost, "9th consecutive miss should be LOST"
    assert np.allclose(pol.last_obs[REL_GATE], 0.0), "lost frame must use zero rel_gate_body"
    assert abs(pol.last_obs[DIST_IDX] - 10.0) < 1e-3, "lost frame must use default dist=10"
    print(f"[3] lost (9th): rel_gate_body={pol.last_obs[REL_GATE].round(3)}, "
          f"dist={pol.last_obs[DIST_IDX]:.1f}; lost={bridge.lost}")

    # 4. re-acquire -> resets cleanly
    det.set_found(pos_cam=[0.5, 0.0, 4.0], dist=4.0)
    bridge.step(_telem(), frame)
    assert not bridge.lost and bridge._consecutive_misses == 0, "re-acquire should reset"
    print(f"[4] reacquire : lost={bridge.lost}, misses={bridge._consecutive_misses} (reset OK)")
    print("FALLBACK: PASS\n")


def test_udp_to_detector():
    try:
        import cv2
    except Exception as e:
        print(f"[udp->detector] SKIPPED — cv2 not importable ({e.__class__.__name__}); "
              f"reassembly itself is covered in udp_vision_receiver.py self-test.")
        return
    from gate_detector import GateDetector, GateDetectorConfig

    # synthetic 640x360 frame (a bright rectangle on dark bg — not a calibrated gate, just
    # enough to prove decode + detect run end-to-end without crashing)
    img = np.zeros((360, 640, 3), np.uint8)
    cv2.rectangle(img, (270, 130), (370, 230), (255, 255, 255), 8)
    ok, enc = cv2.imencode(".jpg", img)
    assert ok, "jpeg encode failed"
    jpeg = enc.tobytes()

    rx = UdpVisionReceiver()
    for pkt in chunk_frame(jpeg, frame_id=1, sim_time_ns=1, payload_max=1400):
        rx.handle_packet(pkt)
    frame = rx.get_latest_frame()
    assert frame is not None and frame.shape == (360, 640, 3), \
        f"decoded frame shape wrong: {None if frame is None else frame.shape}"
    print(f"[udp->detector] decoded frame {frame.shape} from {len(jpeg)}B JPEG over "
          f"{(len(jpeg)+1399)//1400} UDP chunks")

    det = GateDetector(GateDetectorConfig())
    det.set_camera_from_fov(640, 360, 90.0)
    detections = det.detect(frame)
    assert isinstance(detections, (list, tuple)) and len(detections) >= 1, "detector returned nothing"
    print(f"[udp->detector] GateDetector.detect ran -> {len(detections)} detection(s), "
          f"primary.found={detections[0].found} (chain runs end-to-end)")
    print("UDP->DECODE->DETECT: PASS\n")


if __name__ == "__main__":
    print("=== Vision integration smoke test (sim-independent) ===\n")
    test_fallback()
    test_udp_to_detector()
    print("ALL INTEGRATION TESTS PASSED.")
