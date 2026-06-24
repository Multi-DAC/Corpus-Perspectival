"""Maneuver library — the grammar of flying, re-homed on the DreamerV3 pipeline.

Ported from sim/infinite_gate_env.py::ManeuverLibrary (architecture by Clayton, Feb 11 2026)
into the anakin tree for Phase 3. The maneuver formulas are architecture-agnostic — they place
the next gate relative to the current (pos, heading, alt); whether PPO or DreamerV3 consumes the
resulting track is irrelevant here. Faithfully ported; the only additions for Phase 3 are:

  - **takeoff** — was implicit in the old env (`ground_start_prob`); now an EXPLICIT, tracked
    maneuver so the curriculum measures launch competence separately. VQ1 starts from ground rest,
    so takeoff is non-optional (Clayton, Day 124).
  - the IN_FLIGHT vs ALL split, so the random planner never samples takeoff mid-course (takeoff
    only legally occurs as the first segment from ground rest).

Each maneuver: (pos, heading, alt, rng) -> (new_pos, new_heading, new_alt).
Units: metres, radians. Altitude clamped to [0.5, 12.0] in flight (takeoff lifts off from ~0).
"""
import os

import numpy as np

ALT_MIN, ALT_MAX = 0.5, 12.0

# --- Gate-spacing calibration to the official VQ1 course (Day 144) ---------------------
# The captured official_track shows gates 24-39 m apart (mean 27); the default maneuver grammar
# is mostly 3-14 m, so the policy overshoots long approaches (first official flight, Day 144).
# ANAKIN_WIDEGAP=1 re-centers the GENTLE/STRAIGHT/VERTICAL family's inter-gate distance ON the
# official band (explicit ranges, ~55% of gaps in [24,39] with tails for robustness) AND restricts
# the in-flight pool to that family (the official course's actual vocabulary: gentle straights,
# gentle turns, climbs — NO tight turns, which would cap the in-band fraction). Distribution-
# calibration ONLY — pixels-only, no geometry fed to the agent, NOT a fixed-layout overfit.
# Reversible (default off). Tight-turn skill is retained from vq1_v2's prior training + a VQ2 phase.
_WIDEGAP = os.environ.get("ANAKIN_WIDEGAP", "0") == "1"

def _gap_dist(rng, narrow, wide):
    """Inter-gate distance: official-calibrated `wide` range under WIDEGAP, else default `narrow`."""
    return rng.uniform(*(wide if _WIDEGAP else narrow))


class ManeuverLibrary:
    """Gate-placement formulas. Each tests a distinct flight skill."""

    # In-flight maneuvers — the random planner samples from these.
    # WIDEGAP restricts the in-flight pool to the official VQ1 course's vocabulary (gentle
    # straights/turns/climbs — no tight turns); default = the full grammar.
    IN_FLIGHT = (
        ["sprint", "gentle_arc", "speed_trap", "climb", "dive"] if _WIDEGAP else
        ["sprint", "gentle_arc", "hard_turn", "hairpin",
         "climb", "dive", "chicane", "speed_trap",
         "spiral", "threading", "diagonal"]
    )
    # Launch-only — legal solely as the first segment from ground rest.
    LAUNCH = ["takeoff"]
    # Full vocabulary (for metrics / mastery tables).
    MANEUVERS = LAUNCH + IN_FLIGHT

    # -- launch ---------------------------------------------------------------
    @staticmethod
    def takeoff(pos, heading, alt, rng):
        """Ground rest -> first gate, ahead and up. Tests vertical launch + initial accel.

        `pos` is the ground start (z ~ 0). Place gate 1 a short distance ahead on the current
        heading and at a modest racing altitude — the policy must arm, lift off, and accelerate
        into the gate from zero velocity.
        """
        dist = rng.uniform(4.0, 8.0)
        angle_change = rng.uniform(-0.1, 0.1)          # essentially straight ahead
        target_alt = rng.uniform(1.5, 3.0)             # climb to racing altitude

        new_heading = heading + angle_change
        new_pos = pos + np.array([
            dist * np.cos(new_heading),
            dist * np.sin(new_heading),
            0.0,
        ])
        new_alt = float(np.clip(target_alt, ALT_MIN, ALT_MAX))
        new_pos[2] = new_alt
        return new_pos, new_heading, new_alt

    # -- in-flight ------------------------------------------------------------
    @staticmethod
    def sprint(pos, heading, alt, rng):
        """Far gate, same heading — tests top speed."""
        dist = _gap_dist(rng, (10, 22), (16, 44))
        angle_change = rng.uniform(-0.1, 0.1)
        alt_change = rng.uniform(-0.3, 0.3)
        return ManeuverLibrary._advance(pos, heading, alt, dist, angle_change, alt_change)

    @staticmethod
    def gentle_arc(pos, heading, alt, rng):
        """Medium distance, 10-30 deg turn — smooth racing line."""
        dist = _gap_dist(rng, (6, 14), (14, 38))
        angle_change = rng.choice([-1, 1]) * rng.uniform(0.17, 0.52)
        alt_change = rng.uniform(-0.5, 0.5)
        return ManeuverLibrary._advance(pos, heading, alt, dist, angle_change, alt_change)

    @staticmethod
    def hard_turn(pos, heading, alt, rng):
        """Medium distance, 60-120 deg — banking skill."""
        dist = rng.uniform(4, 10)
        angle_change = rng.choice([-1, 1]) * rng.uniform(1.05, 2.09)
        alt_change = rng.uniform(-0.5, 0.5)
        return ManeuverLibrary._advance(pos, heading, alt, dist, angle_change, alt_change)

    @staticmethod
    def hairpin(pos, heading, alt, rng):
        """Close gate, 140-180 deg reversal — deceleration + flip."""
        dist = rng.uniform(3, 6)
        angle_change = rng.choice([-1, 1]) * rng.uniform(2.44, 3.14)
        alt_change = rng.uniform(-0.3, 0.3)
        return ManeuverLibrary._advance(pos, heading, alt, dist, angle_change, alt_change)

    @staticmethod
    def climb(pos, heading, alt, rng):
        """Next gate significantly higher — thrust management."""
        dist = _gap_dist(rng, (5, 12), (14, 36))
        angle_change = rng.uniform(-0.3, 0.3)
        alt_change = rng.uniform(2.0, 5.0)
        return ManeuverLibrary._advance(pos, heading, alt, dist, angle_change, alt_change)

    @staticmethod
    def dive(pos, heading, alt, rng):
        """Next gate significantly lower — controlled descent."""
        dist = _gap_dist(rng, (5, 12), (14, 36))
        angle_change = rng.uniform(-0.3, 0.3)
        alt_change = rng.uniform(-5.0, -2.0)
        return ManeuverLibrary._advance(pos, heading, alt, dist, angle_change, alt_change)

    @staticmethod
    def chicane(pos, heading, alt, rng):
        """S-curve — rapid direction change."""
        dist = rng.uniform(3, 6)
        angle_change = rng.choice([-1, 1]) * rng.uniform(0.7, 1.2)
        alt_change = rng.uniform(-0.3, 0.3)
        return ManeuverLibrary._advance(pos, heading, alt, dist, angle_change, alt_change)

    @staticmethod
    def speed_trap(pos, heading, alt, rng):
        """Long straight (then a tight turn follows) — tests speed buildup + braking."""
        dist = _gap_dist(rng, (12, 24), (18, 46))
        angle_change = rng.uniform(-0.05, 0.05)
        alt_change = rng.uniform(-0.2, 0.2)
        return ManeuverLibrary._advance(pos, heading, alt, dist, angle_change, alt_change)

    @staticmethod
    def spiral(pos, heading, alt, rng):
        """Consistent turning + altitude gain — coordinated flight."""
        dist = rng.uniform(4, 8)
        angle_change = rng.choice([-1, 1]) * rng.uniform(0.5, 0.9)
        alt_change = rng.uniform(0.5, 1.5)
        return ManeuverLibrary._advance(pos, heading, alt, dist, angle_change, alt_change)

    @staticmethod
    def threading(pos, heading, alt, rng):
        """Very close gates — precision control."""
        dist = rng.uniform(2.0, 3.5)
        angle_change = rng.choice([-1, 1]) * rng.uniform(0.1, 0.6)
        alt_change = rng.uniform(-0.5, 0.5)
        return ManeuverLibrary._advance(pos, heading, alt, dist, angle_change, alt_change)

    @staticmethod
    def diagonal(pos, heading, alt, rng):
        """Horizontal turn + altitude change — full 3D skill."""
        dist = rng.uniform(5, 12)
        angle_change = rng.choice([-1, 1]) * rng.uniform(0.5, 1.5)
        alt_change = rng.choice([-1, 1]) * rng.uniform(1.5, 4.0)
        return ManeuverLibrary._advance(pos, heading, alt, dist, angle_change, alt_change)

    # -- shared advance (in-flight gates clamp altitude) ----------------------
    @staticmethod
    def _advance(pos, heading, alt, dist, angle_change, alt_change):
        new_heading = heading + angle_change
        new_pos = pos + np.array([
            dist * np.cos(new_heading),
            dist * np.sin(new_heading),
            0.0,
        ])
        new_alt = float(np.clip(alt + alt_change, ALT_MIN, ALT_MAX))
        new_pos[2] = new_alt
        return new_pos, new_heading, new_alt

    # -- dispatch -------------------------------------------------------------
    def generate(self, pos, heading, alt, rng, maneuver=None):
        """Place the next gate. `maneuver=None` samples a random IN_FLIGHT maneuver
        (never takeoff — that's launch-only). Returns (new_pos, new_heading, new_alt, maneuver)."""
        if maneuver is None:
            maneuver = rng.choice(self.IN_FLIGHT)
        new_pos, new_heading, new_alt = getattr(self, maneuver)(pos, heading, alt, rng)
        return new_pos, new_heading, new_alt, maneuver


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    lib = ManeuverLibrary()
    # takeoff from ground rest
    p, h, a = np.array([0.0, 0.0, 0.0]), 0.0, 0.0
    p, h, a = lib.takeoff(p, h, a, rng)
    print(f"takeoff -> gate at {p.round(2)}  heading {h:+.2f}  alt {a:.2f}")
    assert ALT_MIN <= a <= ALT_MAX and p[0] > 0, "takeoff should lift off and move ahead"
    # then a random in-flight stream — confirm takeoff is never sampled
    seen = set()
    for _ in range(2000):
        p, h, a, m = lib.generate(p, h, a, rng)
        seen.add(m)
        assert ALT_MIN <= a <= ALT_MAX
    assert "takeoff" not in seen, "takeoff must be launch-only"
    print(f"in-flight maneuvers sampled ({len(seen)}/11): {sorted(seen)}")
    print("maneuvers.py self-test OK")
