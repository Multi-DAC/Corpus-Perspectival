"""Quick test: verify SequencePlanner activates at different mastery levels."""
from sequence_generators import SequencePlanner
import numpy as np

rng = np.random.default_rng(42)

for mastery in [0.50, 0.84, 0.92, 0.96]:
    p = SequencePlanner(rng, adaptive=True)
    for _ in range(200):
        p.next_maneuver(avg_mastery=mastery)
    stats = p.get_stats()
    dist = stats['complexity_distribution']
    comp = stats['sequence_completions']
    fail = stats['sequence_failures']
    w = dist.get('word', 0)
    s = dist.get('sentence', 0)
    pa = dist.get('paragraph', 0)
    e = dist.get('essay', 0)
    print(f"Mastery {mastery:.0%}: word={w:.0%} sent={s:.0%} para={pa:.0%} essay={e:.0%}")
    print(f"  Completions: sent={comp.get('sentence',0)} para={comp.get('paragraph',0)} essay={comp.get('essay',0)}")
    print(f"  Failures:    sent={fail.get('sentence',0)} para={fail.get('paragraph',0)} essay={fail.get('essay',0)}")
    print()
