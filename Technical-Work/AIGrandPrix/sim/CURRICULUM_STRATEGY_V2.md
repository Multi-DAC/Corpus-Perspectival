# Curriculum Strategy V2 — Smoothing the Critical Jump

*Clawd — February 25, 2026*
*Based on critical jumps analysis of 48M training steps*

---

## The Problem: A Bistable System

Analysis of Anakin's training trajectory reveals a fundamental instability. The reward distribution is **bimodal** — the agent oscillates between a HIGH regime (~1550 reward) and a LOW regime (~550 reward), with nothing in between. All three evaluation replicas always agree on regime, confirming this is a real policy property, not evaluation noise.

**Transition statistics:**
- Transitions are single-step (100K steps): discontinuous
- Crash threshold: ~1727 average reward
- Recovery threshold: ~357 average reward
- Hysteresis: strong (crash threshold 5x higher than recovery)

**Root cause:** The curriculum tier boundary at 80% mastery creates a **constraint structure discontinuity**. When avg mastery crosses 80%, 30% of training immediately shifts to multi-gate sequences. The agent, not yet able to chain maneuvers, fails these sequences; mastery drops; curriculum relaxes; repeat. The system is locked in a feedback cycle.

**Sprint/speed_trap's role:** These maneuvers (currently 74% and 71% mastery respectively) drag the average mastery toward the threshold. They're the weakest link that triggers the cascade.

---

## Three Proposed Changes

### Change 1: Soft Curriculum Boundaries

**Current behavior:** Hard threshold at 80%. Below 80% → 100% words. Above 80% → 30% sequences. This is a cliff.

**Proposed:** Replace the discrete tier system with continuous probability interpolation across the mastery range.

```python
def _get_tier_probs(self, avg_mastery: float) -> dict:
    """
    Continuous probability distribution over complexity levels.
    No hard boundaries — smooth transition across mastery range.
    """
    m = avg_mastery

    # Sentence probability: rises from 0% at 70% mastery to 30% at 90%
    p_sentence = np.clip((m - 0.70) / 0.20, 0.0, 0.30)

    # Paragraph probability: rises from 0% at 80% mastery to 25% at 95%
    p_paragraph = np.clip((m - 0.80) / 0.15, 0.0, 0.25)

    # Essay probability: rises from 0% at 90% mastery to 20% at 98%
    p_essay = np.clip((m - 0.90) / 0.08, 0.0, 0.20)

    # Word gets the remainder
    p_word = max(0.20, 1.0 - p_sentence - p_paragraph - p_essay)

    # Normalize
    total = p_word + p_sentence + p_paragraph + p_essay
    return {
        'word': p_word / total,
        'sentence': p_sentence / total,
        'paragraph': p_paragraph / total,
        'essay': p_essay / total,
    }
```

**Effect:** At 80% mastery, sentence probability is ~5% (not 25%). The constraint structure change is gradual. No cliff.

---

### Change 2: Per-Maneuver Tier Escalation

**Current behavior:** Curriculum complexity is determined by `avg_mastery` — a single number representing the average of all 11 maneuvers. Sprint (74%) and speed_trap (72%) drag the average, but they're included in sequences at the same rate as threading (92%).

**Proposed:** When generating sequences, only include maneuvers that have individually reached their complexity threshold.

```python
def _get_sequence_maneuvers(self, complexity: str, maneuver_masteries: dict) -> List[str]:
    """
    Filter sequence templates to only use maneuvers that are ready.
    A maneuver is 'sequence-ready' if its individual mastery > threshold.
    """
    SEQUENCE_THRESHOLD = 0.82  # individual mastery needed to appear in sequences

    ready = {m for m, rate in maneuver_masteries.items()
             if rate >= SEQUENCE_THRESHOLD}

    # Generate a candidate sequence
    candidate = self._generate_sequence(complexity)

    # Replace unready maneuvers with their nearest ready equivalent
    # or fall back to a word-level maneuver from the ready set
    result = []
    for m in candidate:
        if m in ready:
            result.append(m)
        elif ready:
            # Substitute with a ready maneuver from similar category
            # (e.g., replace sprint with hard_turn for speed sequences)
            fallback = min(ready, key=lambda x: self._maneuver_distance(m, x))
            result.append(fallback)

    return result if result else None  # None = fall back to word mode
```

**Effect:** Sprint and speed_trap are excluded from sequences until they individually reach 82% mastery. Threading, chicane, hairpin (90%+) participate fully. Sequences actually test composition of strong skills, not chains through weak links.

---

### Change 3: Asymmetric De-escalation (Hysteresis Control)

**Current behavior:** Curriculum tier is determined by current `avg_mastery` at every step. If mastery drops from 84% to 79%, immediately drops back to 100% words. This rapid de-escalation means:
1. The agent never gets sustained exposure to harder sequences after brief struggles
2. The LOW regime has its own stability (agent forgets sequence navigation)

**Proposed:** Add intentional hysteresis to the curriculum. Escalate at one threshold, de-escalate at a lower threshold.

```python
def __init__(self, rng, adaptive=True):
    # ... existing init ...
    self._current_tier = 'learning'  # tracked separately from mastery

    # Asymmetric thresholds: escalate higher, de-escalate lower
    self.ESCALATE_THRESHOLDS = {
        'learning':    0.80,  # escalate to progressing at 80%
        'progressing': 0.88,  # escalate to proficient at 88%
        'proficient':  0.93,  # escalate to mastery at 93%
    }
    self.DEESCALATE_THRESHOLDS = {
        'progressing': 0.72,  # de-escalate to learning at 72%
        'proficient':  0.80,  # de-escalate to progressing at 80%
        'mastery':     0.88,  # de-escalate to proficient at 88%
    }

def _update_tier(self, avg_mastery: float):
    """Update curriculum tier with hysteretic boundaries."""
    tier_order = ['learning', 'progressing', 'proficient', 'mastery']
    current_idx = tier_order.index(self._current_tier)

    # Check for escalation
    if current_idx < len(tier_order) - 1:
        next_tier = tier_order[current_idx + 1]
        escalate_at = self.ESCALATE_THRESHOLDS.get(self._current_tier, 1.0)
        if avg_mastery >= escalate_at:
            self._current_tier = next_tier
            return

    # Check for de-escalation
    if current_idx > 0:
        deescalate_at = self.DEESCALATE_THRESHOLDS.get(self._current_tier, 0.0)
        if avg_mastery < deescalate_at:
            self._current_tier = tier_order[current_idx - 1]
```

**Effect:** The agent escalates to `progressing` at 80% mastery. But it only de-escalates back to `learning` if mastery drops to 72% — creating a safety buffer. This prevents the rapid oscillation seen in the training data.

---

## Combined Expected Effect

The three changes work together:

| Current Behavior | V2 Behavior |
|-----------------|-------------|
| Hard cliff at 80% mastery | Smooth gradient: 5% sequences at 80%, 30% at 90% |
| Weak maneuvers included in sequences | Only sequence-ready maneuvers (>82%) compose |
| Curriculum tracks mastery point-by-point | Hysteretic tiers: escalate at 80%, de-escalate at 72% |
| Bistable: HIGH regime unstable under perturbation | HIGH regime stabilized: brief mastery dips don't cascade |
| Sprint/speed_trap drag sequence quality down | Sprint/speed_trap trained individually until ready |

**Predicted outcome:** The 80% oscillation should damp significantly. The agent should stabilize in the progressing tier, get sustained exposure to sequences, and gradually push sprint/speed_trap mastery up through individual practice before sequencing.

---

## What We're NOT Changing (Yet)

**Reward structure:** The Explore agent analysis suggests increasing `gate_speed_scale` from 0.04 to 0.08-0.12. This is still worth doing — but it's a separate variable. The curriculum V2 changes reduce the oscillation; the reward changes would directly incentivize speed.

**Recommendation:** Apply curriculum V2 first. Run 10M steps. Check if the bistability damps. Then evaluate whether reward restructuring is still needed, or if stable training in the progressing tier is sufficient to improve sprint/speed_trap through curriculum pressure.

---

## Implementation Notes

These changes touch `sequence_generators.py`:
- `SequencePlanner._get_tier` → replace with `_get_tier_probs` (Change 1)
- `SequencePlanner._roll_complexity` → use continuous probs (Change 1)
- `SequencePlanner.next_maneuver` → accept `maneuver_masteries` dict (Change 2)
- `SequencePlanner.__init__` → add `_current_tier` tracking (Change 3)
- New method `_update_tier` (Change 3)

Also touches `infinite_gate_env.py`:
- `_choose_maneuver` → pass per-maneuver masteries to planner (Change 2)

---

*Ready to implement when Clayton is ready to discuss. Code changes are non-destructive — can be applied to a new training run from the current 28.8K episode checkpoint.*
