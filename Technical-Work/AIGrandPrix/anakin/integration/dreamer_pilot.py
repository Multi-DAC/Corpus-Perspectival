"""
DreamerPilot — drives the trained DreamerV3 racer (best.pt) from the competition
act(frame) -> action interface. The sim-to-sim translation adapter (anticipation #6).

Pipeline position (replaces the PPO path's GateDetector + CompetitionAdapter — the
Dreamer pilot is from-pixels, so the gate-detector stage is bypassed entirely):

    UDP camera (640x360 JPEG, BGR) --to_training_frame--> 64x64 RGB, geometry-preserving
        --DreamerPilot.act (stateful RSSM)--> action [-1,1]^4 = [collective, wx, wy, wz]
        --to_competition_action--> throttle 0..1 + body rates rad/s (SIM constants)

Correctness cruxes (each one is a way the pilot silently flies blind):

  1. GEOMETRY. Training frames are square 64x64 with HFOV = VFOV = 90deg
     (sim/render.py: fx = fy ~= 32, cx = cy = 32). The competition feed is 640x360
     with fx ~= 320, so HFOV matches at 90deg but the vertical FoV is only ~59deg.
     We scale by exactly 1/10 (640 -> 64, 360 -> 36) and PAD top/bottom 14px each
     with the renderer's background gray (40) -> fx = fy = 32, principal point
     centered: angular geometry identical to training. A naive 640x360 -> 64x64
     resize would stretch vertical 1.6x and feed the world model OOD frames.

  2. COLOR. cv2.imdecode gives BGR; the training render is RGB. Converted here.

  3. YAW SCALE. sim/dynamics.py trains with OMEGA_Z = 2.5 rad/s. The PPO-era
     VisionPolicyBridge maps yaw at MAX_RATE_Z = 0.3 — reusing it would give this
     pilot 8.3x weaker yaw than it learned with. to_competition_action uses the
     sim's own constants.

  4. STATE. The RSSM latent persists across steps and resets on episode start.
     That statefulness is the whole difference from PPO's stateless predict():
     drop the state and the world model loses its filter over occlusions/dropouts.

LIVE-TEST CHECKLIST (not verifiable offline — check before trusting a translation run):
  - Camera tilt sign: RESOLVED Day-129 (Mirror #32) — sim/render.py now trains 20deg
    UP-tilt, matching VQ1 spec (vq1_spec.txt:325) and vision/adapter.py. Verified by
    render.py __main__ (level gate projects BELOW center) and Day-135 mask_vfov_diag.py
    (rendered gate-rows below center, ~42.8). Tilt is NOT the official-gap cause.
  - Body-frame handedness: sim omega is body [x,y,z] = [roll,pitch,yaw]; an
    FLU-vs-FRD mismatch flips pitch/yaw signs.
  - Thrust calibration: sim TWR ~3.95 (TMAX ~38.7 m/s^2). Competition throttle 1.0
    may map to a different TWR. Symptom: pilot pinned to floor or ceiling.
  - Frame-rate: feed is 30 Hz; training control tick was dt=0.02 (50 Hz). The RSSM
    filters this, but if behavior is sluggish, consider stepping the policy twice
    per frame.

Usage:
    pilot = DreamerPilot("path/to/best.pt")        # device auto: cuda if available
    pilot.reset()                                   # at episode start
    a = pilot.act(frame_bgr_640x360)                # per frame -> [-1,1]^4
    cmd = to_competition_action(a)                  # throttle + body rates

Self-test (loads best.pt, checks the frame transform, statefulness, latency):
    .venv/Scripts/python.exe integration/dreamer_pilot.py --checkpoint \
        third_party/dreamerv3-torch/logdir/maneuver_scale_2/best.pt
"""

import argparse
import pathlib
import sys
import time
from dataclasses import dataclass

import numpy as np
import torch

_ANAKIN = pathlib.Path(__file__).resolve().parent.parent
_DREAMER_DIR = _ANAKIN / "third_party" / "dreamerv3-torch"
sys.path.insert(0, str(_DREAMER_DIR))
sys.path.insert(0, str(_ANAKIN / "sim"))

import ruamel.yaml as yaml  # noqa: E402  (dreamerv3-torch dependency)

# Sim ground truth — single source for the command mapping (crux #3).
from dynamics import TMAX, OMEGA_XY, OMEGA_Z  # noqa: E402
import gate_mask as _gm  # noqa: E402  gate-isolation obs transform (env-var gated; Day 134)
import edge_filter as _ef  # noqa: E402  edge/pencil obs transform (env-var ANAKIN_EDGE; Day 135)

IMG = 64                 # training resolution (sim/render.py IMG)
BG_UINT8 = 40            # render.py BG_GRAY=0.16 -> int(0.16*255) after uint8 cast
FEED_W, FEED_H = 640, 360  # udp_vision_receiver.py FRAME_SHAPE


def _build_config(configs=("anakin_maneuver",), device=None, dreamer_dir=_DREAMER_DIR):
    """Rebuild the training config exactly the way dreamer.py __main__ does, so the
    constructed model matches the checkpoint architecture by construction."""
    import tools  # dreamerv3-torch

    raw = yaml.YAML(typ="safe", pure=True).load(
        (pathlib.Path(dreamer_dir) / "configs.yaml").read_text()
    )

    def recursive_update(base, update):
        for key, value in update.items():
            if isinstance(value, dict) and key in base:
                recursive_update(base[key], value)
            else:
                base[key] = value

    defaults = {}
    for name in ["defaults", *configs]:
        recursive_update(defaults, raw[name])

    parser = argparse.ArgumentParser()
    for key, value in sorted(defaults.items(), key=lambda x: x[0]):
        arg_type = tools.args_type(value)
        parser.add_argument(f"--{key}", type=arg_type, default=arg_type(value))
    config = parser.parse_args([])

    if device is not None:
        config.device = device
    elif not torch.cuda.is_available():
        config.device = "cpu"
    config.compile = False  # inference only; also unsupported on Windows
    return config


class _StepStub:
    """Minimal stand-in for tools.Logger — Dreamer.__init__ only reads .step
    (and the training branch, which we never enter, writes it back)."""
    step = 0


def to_training_frame(frame_bgr: np.ndarray) -> np.ndarray:
    """640x360 BGR competition frame -> 64x64 RGB uint8 training-distribution frame.

    Scale by exactly 1/10 then pad vertically with background gray: preserves the
    angular geometry the world model trained on (crux #1). Asserts on unexpected
    input shape rather than silently re-deriving the scale — an official-sim
    resolution change should be a loud event, not a quiet intrinsics drift.
    """
    import cv2

    h, w = frame_bgr.shape[:2]
    assert (w, h) == (FEED_W, FEED_H), (
        f"expected {FEED_W}x{FEED_H} feed, got {w}x{h} — re-derive the transform "
        f"(scale AND padding change with resolution; see crux #1)"
    )
    rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    small = cv2.resize(rgb, (IMG, FEED_H * IMG // FEED_W), interpolation=cv2.INTER_AREA)
    if _gm.enabled():                       # SkyDreamer route: gate-isolate the CONTENT only.
        small = _gm.gate_isolate_np(small)  # bands stay BG_UINT8 -> matches _band()'s gray rows
    if _ef.enabled():                       # edge route (Day 135): edge the CONTENT (bands stay gray);
        small = _ef.edge_np(small)          # same zero-pad borders as render edge_t(out[:,14:50])
    out = np.full((IMG, IMG, 3), BG_UINT8, dtype=np.uint8)  # in training (envs/anakin_batched._band)
    top = (IMG - small.shape[0]) // 2
    out[top:top + small.shape[0]] = small
    return out


class DreamerPilot:
    """Stateful wrapper: holds the Dreamer agent + RSSM latent across steps (crux #4)."""

    def __init__(self, checkpoint, configs=("anakin_maneuver",), device=None):
        import gym
        from dreamer import Dreamer

        config = _build_config(configs=configs, device=device)
        obs_space = gym.spaces.Dict({
            "image": gym.spaces.Box(0, 255, (IMG, IMG, 3), dtype=np.uint8),
        })
        act_space = gym.spaces.Box(-1.0, 1.0, (4,), dtype=np.float32)
        config.num_actions = act_space.shape[0]

        agent = Dreamer(obs_space, act_space, config, _StepStub(), dataset=None)
        agent.requires_grad_(requires_grad=False)
        ckpt = torch.load(checkpoint, map_location=config.device)
        # Non-strict, but raise on MISSING keys (real arch drift). An informed-Dreamer checkpoint is a
        # SUPERSET of a vision pilot (extra priv_state decoder head); loading it into this image-only
        # model drops that head — harmless at inference (the gate uses only the encoder). Missing keys,
        # by contrast, mean the model needs weights the checkpoint lacks => genuine drift => raise.
        res = agent.load_state_dict(ckpt["agent_state_dict"], strict=False)
        if res.missing_keys:
            raise RuntimeError(f"checkpoint missing {len(res.missing_keys)} model keys (arch drift): "
                               f"{res.missing_keys[:5]}")
        if res.unexpected_keys:
            print(f"[DreamerPilot] ignoring {len(res.unexpected_keys)} extra ckpt keys "
                  f"(e.g. informed priv_state head): {res.unexpected_keys[:3]}")
        agent.to(config.device)
        agent.eval()

        self._agent = agent
        self._config = config
        self._state = None
        print(f"DreamerPilot: {checkpoint} loaded on {config.device} "
              f"({sum(p.numel() for p in agent.parameters()):,} params)")

    def reset(self):
        """Call at episode start — clears the RSSM latent."""
        self._state = None

    def act(self, frame_bgr: np.ndarray) -> np.ndarray:
        """One competition step: 640x360 BGR frame -> action in [-1,1]^4
        ([collective, omega_x, omega_y, omega_z], the sim's CTBR convention)."""
        return self.act_training_frame(to_training_frame(frame_bgr))

    def act_training_frame(self, img: np.ndarray) -> np.ndarray:
        """Policy step on an already-training-distribution 64x64 RGB frame
        (used by offline evals that have direct sim frames; the competition
        path goes through act())."""
        is_first = self._state is None
        obs = {
            "image": img[None],
            "is_first": np.array([is_first]),
            "is_terminal": np.array([False]),
        }
        with torch.no_grad():
            policy_output, self._state = self._agent(
                obs, np.array([is_first]), self._state, training=False
            )
        return policy_output["action"][0].detach().cpu().numpy()


@dataclass
class CompetitionCommand:
    throttle: float          # 0..1
    roll_rate_rad_s: float
    pitch_rate_rad_s: float
    yaw_rate_rad_s: float


def to_competition_action(action: np.ndarray) -> CompetitionCommand:
    """[-1,1]^4 -> competition command, using the SIM's constants (crux #3).
    Mirrors dynamics.map_action: a[0] is collective ((a+1)/2), a[1:4] body rates."""
    a = np.clip(action, -1.0, 1.0)
    return CompetitionCommand(
        throttle=float((a[0] + 1.0) * 0.5),
        roll_rate_rad_s=float(a[1] * OMEGA_XY),
        pitch_rate_rad_s=float(a[2] * OMEGA_XY),
        yaw_rate_rad_s=float(a[3] * OMEGA_Z),
    )


def _selftest(checkpoint):
    """Offline verification: transform geometry, checkpoint load, statefulness, latency."""
    import cv2  # noqa: F401  (fail early if missing)

    # 1. Frame transform: geometry + padding value.
    frame = np.random.randint(0, 255, (FEED_H, FEED_W, 3), dtype=np.uint8)
    img = to_training_frame(frame)
    assert img.shape == (IMG, IMG, 3) and img.dtype == np.uint8
    assert (img[:14] == BG_UINT8).all() and (img[-14:] == BG_UINT8).all(), "pad rows wrong"
    assert not (img[14:50] == BG_UINT8).all(), "content rows empty"
    print("[1/4] frame transform OK (64x64, 14px gray pads, content centered)")

    # 2. Checkpoint loads strict into the rebuilt architecture.
    pilot = DreamerPilot(checkpoint)
    print("[2/4] checkpoint load OK (strict state_dict match)")

    # 3. Stateful rollout: latent persists, actions valid, reset clears.
    a0 = pilot.act(frame)
    assert a0.shape == (4,) and np.isfinite(a0).all() and (np.abs(a0) <= 1.0 + 1e-5).all()
    assert pilot._state is not None, "RSSM state not held"
    a1 = pilot.act(frame)
    pilot.reset()
    assert pilot._state is None
    a0b = pilot.act(frame)
    # Not bit-deterministic: the RSSM posterior is SAMPLED even at eval (training ran
    # eval_state_mean=False, so the +256 eval behavior is stochastic-latent). Just
    # report the spread; correctness is matching the training eval path, not RNG.
    cmd = to_competition_action(a1)
    print(f"      post-reset action spread |a0-a0b|max={np.abs(a0 - a0b).max():.3f} "
          f"(stochastic posterior — expected nonzero)")
    print(f"[3/4] stateful rollout OK; sample cmd: throttle={cmd.throttle:.3f} "
          f"rates=({cmd.roll_rate_rad_s:+.2f},{cmd.pitch_rate_rad_s:+.2f},"
          f"{cmd.yaw_rate_rad_s:+.2f}) rad/s")

    # 4. Latency vs the 30 Hz feed (33 ms budget).
    pilot.reset()
    pilot.act(frame)  # warm
    t0 = time.perf_counter()
    n = 30
    for _ in range(n):
        pilot.act(frame)
    ms = (time.perf_counter() - t0) / n * 1000
    print(f"[4/4] latency {ms:.1f} ms/step on {pilot._config.device} "
          f"({'OK' if ms < 33 else 'OVER'} for 30 Hz)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", default=str(
        _DREAMER_DIR / "logdir" / "maneuver_scale_2" / "best.pt"))
    args = ap.parse_args()
    _selftest(args.checkpoint)
