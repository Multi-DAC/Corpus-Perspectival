"""Curriculum — mastery tracking + the adaptive sequence planner, for the DreamerV3 pipeline.

Ties together:
  - `MasteryTracker` — per-maneuver competence, asymmetric EMA (fast to credit, slow to forget),
    tracking BOTH pass-rate AND speed (the speed channel is new for Phase 3 — the old PPO stack
    tracked pass-rate only; Clayton's Day-124 mandate is to optimize minimum-TIME, so we must be
    able to watch each maneuver get *faster*, not just *more reliable*).
  - `SequencePlanner` (verbatim from `sequences.py`) — WORD→SENTENCE→PARAGRAPH→ESSAY composition
    with Curriculum-V2 soft boundaries + per-maneuver sequence-readiness filtering.
  - `Curriculum` — the thin wrapper the env talks to: ask for the next maneuver, record each gate
    outcome (success + crossing speed), close the episode, print the evolution report.

Architecture-agnostic: it generates maneuver names + tracks competence. The env (Layer 2) maps a
maneuver name to gate geometry via `maneuvers.ManeuverLibrary` and feeds pixels to Dreamer.
"""
from collections import deque

import numpy as np

from maneuvers import ManeuverLibrary
from sequences import SequencePlanner


class MasteryTracker:
    """Per-maneuver competence over a rolling window, with an asymmetric global EMA.

    `record(maneuver, success, speed)` after each gate transition. `success` is whether the gate
    was passed; `speed` is the crossing speed (m/s) on a pass (ignored on failure). Tracks every
    maneuver in `ManeuverLibrary.MANEUVERS` — including `takeoff`, so launch competence is a
    first-class, separately-visible metric (VQ1 ground-start; Day 124)."""

    def __init__(self, window=200, alpha_up=0.02, alpha_down=0.005):
        self.maneuvers = list(ManeuverLibrary.MANEUVERS)
        self.window = window
        self.alpha_up = alpha_up
        self.alpha_down = alpha_down

        self.attempts = {m: 0 for m in self.maneuvers}
        self.successes = {m: 0 for m in self.maneuvers}
        self._outcomes = {m: deque(maxlen=window) for m in self.maneuvers}   # 0/1 per attempt
        self._speeds = {m: deque(maxlen=window) for m in self.maneuvers}     # crossing speed on pass
        self._recent = deque(maxlen=window)                                  # global, drives the EMA
        self._ema = 0.5                                                       # neutral start

    def record(self, maneuver, success, speed=None):
        if maneuver not in self.attempts:
            return
        s = 1 if success else 0
        self.attempts[maneuver] += 1
        self.successes[maneuver] += s
        self._outcomes[maneuver].append(s)
        if success and speed is not None:
            self._speeds[maneuver].append(float(speed))
        self._recent.append(s)
        # asymmetric EMA on the global recent success rate: rise fast, fall slow
        raw = sum(self._recent) / len(self._recent)
        alpha = self.alpha_up if raw > self._ema else self.alpha_down
        self._ema = (1 - alpha) * self._ema + alpha * raw

    @property
    def avg_mastery(self):
        return self._ema

    @property
    def maneuver_masteries(self):
        """Per-maneuver window success rate (the signal the planner filters sequences on)."""
        out = {}
        for m in self.maneuvers:
            w = self._outcomes[m]
            out[m] = (sum(w) / len(w)) if w else 0.0
        return out

    def mean_speed(self, maneuver):
        w = self._speeds[maneuver]
        return (sum(w) / len(w)) if w else 0.0

    def get_stats(self):
        masteries = self.maneuver_masteries
        per = {}
        for m in self.maneuvers:
            per[m] = {
                "attempts": self.attempts[m],
                "successes": self.successes[m],
                "rate": masteries[m],
                "mean_speed": self.mean_speed(m),
            }
        return {"avg_mastery": self.avg_mastery, "per_maneuver": per}


class Curriculum:
    """The env-facing curriculum: maneuver supply + competence tracking + reporting."""

    def __init__(self, rng, adaptive=True):
        self.rng = rng
        self.tracker = MasteryTracker()
        self.planner = SequencePlanner(rng, adaptive=adaptive)

    def next_maneuver(self):
        """Next IN_FLIGHT maneuver name (or None = let the env pick a random single maneuver).
        Uses current avg + per-maneuver mastery to drive complexity and sequence filtering.

        Only IN_FLIGHT masteries are shown to the planner: `takeoff` is launch-only, so it must
        never enter the sequence-substitution pool (its mastery is still tracked separately)."""
        masteries = self.tracker.maneuver_masteries
        in_flight = {m: masteries[m] for m in ManeuverLibrary.IN_FLIGHT}
        return self.planner.next_maneuver(
            avg_mastery=self.tracker.avg_mastery,
            maneuver_masteries=in_flight,
        )

    def record_gate(self, maneuver, success, speed=None):
        self.tracker.record(maneuver, success, speed)

    def on_episode_end(self, completed_all_gates=False):
        self.planner.on_episode_end(completed_all_gates)

    def report(self):
        """Compact evolution report: per-maneuver pass% and mean crossing speed + tier mix."""
        stats = self.tracker.get_stats()
        lines = [f"avg_mastery {stats['avg_mastery']:.2f}"]
        lines.append(f"{'maneuver':12s} {'pass':>6s} {'n':>6s} {'speed':>7s}")
        for m in self.tracker.maneuvers:
            d = stats["per_maneuver"][m]
            lines.append(f"{m:12s} {d['rate']*100:>5.0f}% {d['attempts']:>6d} {d['mean_speed']:>6.1f}m/s")
        psd = self.planner.get_stats(self.tracker.avg_mastery)["complexity_distribution"]
        lines.append("tiers: " + " ".join(f"{k}={v:.0%}" for k, v in psd.items()))
        return "\n".join(lines)


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    cur = Curriculum(rng, adaptive=True)

    # Simulate a learner that's good at easy maneuvers, weak at hard ones, and getting faster.
    EASY = {"takeoff", "sprint", "gentle_arc", "speed_trap", "threading"}
    for ep in range(400):
        cur.record_gate("takeoff", success=rng.random() < 0.9, speed=rng.uniform(3, 6))
        for _ in range(8):
            m = cur.next_maneuver() or rng.choice(ManeuverLibrary.IN_FLIGHT)
            p = 0.9 if m in EASY else 0.6
            ok = rng.random() < p
            cur.record_gate(m, success=ok, speed=rng.uniform(6, 14) if ok else None)
        cur.on_episode_end()

    print(cur.report())
    assert cur.tracker.avg_mastery > 0.5, "EMA should have risen above neutral"
    assert cur.tracker.attempts["takeoff"] == 400, "takeoff tracked every episode"
    assert all(cur.tracker.mean_speed(m) > 0 for m in ("sprint", "takeoff")), "speed channel live"
    print("\ncurriculum.py self-test OK")
