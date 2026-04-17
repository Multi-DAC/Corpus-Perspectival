"""
Sequence Generators — Teaching Composition

Vocabulary school teaches individual maneuvers (words).
Sequence generators teach how maneuvers compose (sentences, paragraphs, essays).

Architecture:
    The InfiniteGateEnv calls _choose_maneuver() each time it needs a new gate.
    With sequences enabled, it instead consults a SequencePlanner which may
    return a pre-planned sequence of maneuvers to execute in order.

    When the planner has an active sequence, gates come from that plan.
    When the sequence completes, the planner rolls again: word? sentence? paragraph?

Complexity Levels:
    WORD      — Single random maneuver (current behavior)
    SENTENCE  — 3-5 related maneuvers forming a coherent phrase
    PARAGRAPH — 8-15 mixed maneuvers forming a mini-track
    ESSAY     — 20-45 gates, a full procedural racecourse

The adaptive curriculum controls the probability distribution over
complexity levels based on overall mastery.

By Clayton & Clawd, Feb 12, 2026.
"""

import numpy as np
from typing import List, Tuple, Optional


# ============================================================
# Sentence Templates — Coherent short sequences
# ============================================================

class SentenceTemplates:
    """
    Each sentence is a function that returns a list of maneuver names.
    Parameters are randomized so no two sentences are identical,
    but the structure is coherent — moves that belong together.
    """
    
    @staticmethod
    def spiral_staircase(rng, length=None) -> List[str]:
        """Sustained spiral — climbing in circles."""
        n = length or rng.integers(3, 6)
        return ['spiral'] * n
    
    @staticmethod
    def vertical_ladder(rng, length=None) -> List[str]:
        """Alternating climb and threading — ascending through tight gates."""
        n = length or rng.integers(2, 4)
        seq = []
        for _ in range(n):
            seq.extend(['climb', 'threading'])
        return seq
    
    @staticmethod
    def slalom(rng, length=None) -> List[str]:
        """Alternating hard turns — like skiing gates."""
        n = length or rng.integers(3, 6)
        return ['hard_turn'] * n  # The env randomizes L/R each time
    
    @staticmethod
    def speed_chicane(rng, length=None) -> List[str]:
        """Sprint into chicane — build speed then swerve."""
        n_chicanes = length or rng.integers(2, 4)
        return ['sprint'] + ['chicane'] * n_chicanes
    
    @staticmethod
    def dive_bomb(rng, length=None) -> List[str]:
        """Climb high, then dive through threading gates."""
        n_threads = length or rng.integers(2, 4)
        return ['climb', 'climb'] + ['dive'] + ['threading'] * n_threads
    
    @staticmethod
    def precision_run(rng, length=None) -> List[str]:
        """All threading — sustained close-quarters flying."""
        n = length or rng.integers(4, 7)
        return ['threading'] * n
    
    @staticmethod
    def roller_coaster(rng, length=None) -> List[str]:
        """Alternating climb and dive — vertical oscillation."""
        n = length or rng.integers(2, 4)
        seq = []
        for _ in range(n):
            seq.extend(['climb', 'dive'])
        return seq
    
    @staticmethod
    def hairpin_alley(rng, length=None) -> List[str]:
        """Repeated hairpins — constant reversal."""
        n = length or rng.integers(3, 5)
        return ['hairpin'] * n
    
    @staticmethod
    def sprint_brake(rng, length=None) -> List[str]:
        """Speed trap into hairpin — build speed, emergency stop."""
        return ['speed_trap', 'hairpin']
    
    @staticmethod
    def corkscrew(rng, length=None) -> List[str]:
        """Spiral with threading — tight ascending helix."""
        n = length or rng.integers(3, 6)
        seq = []
        for _ in range(n):
            # Alternate spiral and threading for tight corkscrew feel
            seq.append(rng.choice(['spiral', 'threading']))
        return seq
    
    @staticmethod
    def diagonal_cross(rng, length=None) -> List[str]:
        """Sustained 3D movement — diagonal after diagonal."""
        n = length or rng.integers(3, 5)
        return ['diagonal'] * n
    
    @staticmethod
    def approach_and_thread(rng, length=None) -> List[str]:
        """Gentle arcs into precision section."""
        n_arcs = rng.integers(2, 4)
        n_threads = rng.integers(2, 4)
        return ['gentle_arc'] * n_arcs + ['threading'] * n_threads
    
    @staticmethod
    def full_send(rng, length=None) -> List[str]:
        """Sprint, sprint, hard turn — max speed into banking."""
        return ['sprint', 'sprint', 'hard_turn']
    
    @staticmethod
    def elevator_shaft(rng, length=None) -> List[str]:
        """Sustained climbing through tight gates — vertical gauntlet."""
        n = length or rng.integers(4, 7)
        seq = []
        for _ in range(n):
            seq.append(rng.choice(['climb', 'threading']))
        return seq
    
    @staticmethod
    def descending_spiral(rng, length=None) -> List[str]:
        """Spiral but descending — the mirror of spiral_staircase.
        Uses diagonal with downward bias (will need special handling in env)."""
        n = length or rng.integers(3, 6)
        # Mix of dive and gentle_arc to create descending spiral feel
        seq = []
        for _ in range(n):
            seq.append(rng.choice(['dive', 'gentle_arc']))
        return seq
    
    ALL = [
        spiral_staircase, vertical_ladder, slalom, speed_chicane,
        dive_bomb, precision_run, roller_coaster, hairpin_alley,
        sprint_brake, corkscrew, diagonal_cross, approach_and_thread,
        full_send, elevator_shaft, descending_spiral,
    ]


# ============================================================
# Paragraph Generator — Coherent mini-tracks
# ============================================================

class ParagraphGenerator:
    """
    Generates 8-15 gate sequences that form coherent mini-tracks.
    
    Strategy: Chain 2-4 sentences together with transition maneuvers
    between them. This teaches the agent to handle mode changes —
    going from a speed section to a technical section, etc.
    """
    
    # Track section archetypes
    SECTION_TYPES = {
        'speed':     ['sprint', 'speed_trap', 'gentle_arc'],
        'technical': ['hard_turn', 'chicane', 'hairpin', 'threading'],
        'vertical':  ['climb', 'dive', 'diagonal', 'spiral'],
        'precision': ['threading', 'gentle_arc'],
    }
    
    # Natural transitions between section types
    TRANSITIONS = {
        'speed':     {'technical': 0.4, 'vertical': 0.3, 'precision': 0.3},
        'technical': {'speed': 0.4, 'vertical': 0.3, 'precision': 0.3},
        'vertical':  {'speed': 0.3, 'technical': 0.4, 'precision': 0.3},
        'precision': {'speed': 0.4, 'technical': 0.4, 'vertical': 0.2},
    }
    
    @staticmethod
    def generate(rng, target_length=None) -> List[str]:
        """Generate a paragraph-length sequence of maneuvers."""
        target = target_length or rng.integers(8, 16)
        
        # Pick starting section type
        section_type = rng.choice(list(ParagraphGenerator.SECTION_TYPES.keys()))
        
        sequence = []
        while len(sequence) < target:
            # Generate 2-5 moves from current section
            section_moves = ParagraphGenerator.SECTION_TYPES[section_type]
            section_len = min(rng.integers(2, 6), target - len(sequence))
            
            for _ in range(section_len):
                sequence.append(rng.choice(section_moves))
            
            if len(sequence) >= target:
                break
            
            # Transition to next section
            trans = ParagraphGenerator.TRANSITIONS[section_type]
            next_types = list(trans.keys())
            next_probs = np.array(list(trans.values()))
            next_probs = next_probs / next_probs.sum()
            section_type = rng.choice(next_types, p=next_probs)
            
            # Add a transition maneuver (gentle move between sections)
            if len(sequence) < target:
                sequence.append('gentle_arc')
        
        return sequence[:target]


# ============================================================
# Essay Generator — Full procedural tracks
# ============================================================

class EssayGenerator:
    """
    Generates 20-45 gate sequences — full procedural racecourses.
    
    Strategy: 
    1. Pick an overall track "character" (speed-focused, technical, mixed, vertical)
    2. Generate 4-8 paragraphs with character-appropriate weights
    3. Add an opening sprint and a closing technical section
    
    These are the final exam: can you fly a complete, novel racecourse?
    """
    
    TRACK_CHARACTERS = {
        'speedway': {
            'speed': 0.45, 'technical': 0.2, 'vertical': 0.15, 'precision': 0.2
        },
        'technical_gauntlet': {
            'speed': 0.15, 'technical': 0.45, 'vertical': 0.2, 'precision': 0.2
        },
        'mountain': {
            'speed': 0.15, 'technical': 0.2, 'vertical': 0.45, 'precision': 0.2
        },
        'precision_maze': {
            'speed': 0.15, 'technical': 0.25, 'vertical': 0.15, 'precision': 0.45
        },
        'mixed_championship': {
            'speed': 0.25, 'technical': 0.25, 'vertical': 0.25, 'precision': 0.25
        },
    }
    
    @staticmethod
    def generate(rng, target_length=None) -> Tuple[List[str], str]:
        """
        Generate an essay-length sequence.
        Returns (maneuver_list, track_character_name).
        """
        target = target_length or rng.integers(20, 46)
        
        # Pick track character
        character_name = rng.choice(list(EssayGenerator.TRACK_CHARACTERS.keys()))
        weights = EssayGenerator.TRACK_CHARACTERS[character_name]
        
        # Opening: always start with a sprint to build speed
        sequence = ['sprint', 'gentle_arc']
        
        # Generate body using weighted section selection
        section_types = list(weights.keys())
        section_probs = np.array(list(weights.values()))
        section_probs = section_probs / section_probs.sum()
        
        while len(sequence) < target - 2:  # Leave room for closing
            # Pick section type based on track character
            section_type = rng.choice(section_types, p=section_probs)
            section_moves = ParagraphGenerator.SECTION_TYPES[section_type]
            
            # Section length: 3-7 moves
            section_len = min(rng.integers(3, 8), target - len(sequence) - 2)
            
            for _ in range(section_len):
                sequence.append(rng.choice(section_moves))
            
            # Transition
            if len(sequence) < target - 2:
                sequence.append(rng.choice(['gentle_arc', 'sprint']))
        
        # Closing: technical finish
        while len(sequence) < target:
            sequence.append(rng.choice(['chicane', 'threading', 'hard_turn']))
        
        return sequence[:target], character_name


# ============================================================
# Sequence Planner — Orchestrates complexity levels
# ============================================================

class SequencePlanner:
    """
    Sits between the env and the maneuver library.

    Each time the env needs a maneuver, it asks the planner.
    The planner either:
    a) Returns a single random maneuver (word mode)
    b) Feeds the next maneuver from an active sequence

    When a sequence completes, the planner rolls for the next
    complexity level based on adaptive weights.

    V2 Curriculum (Feb 25, 2026):
    - Continuous probability interpolation (no hard tier boundaries)
    - Sentences ramp 0% -> 30% over mastery 70%-90%
    - Paragraphs ramp 0% -> 25% over mastery 80%-95%
    - Essays ramp 0% -> 20% over mastery 90%-98%
    - Per-maneuver sequence filtering: only maneuvers with >82%
      individual mastery appear in multi-gate sequences
    """
    
    # V1 tiers (kept for non-adaptive fallback)
    COMPLEXITY_TIERS = {
        'learning':    {'word': 1.00, 'sentence': 0.00, 'paragraph': 0.00, 'essay': 0.00},
        'progressing': {'word': 0.70, 'sentence': 0.25, 'paragraph': 0.05, 'essay': 0.00},
        'proficient':  {'word': 0.40, 'sentence': 0.35, 'paragraph': 0.20, 'essay': 0.05},
        'mastery':     {'word': 0.20, 'sentence': 0.30, 'paragraph': 0.30, 'essay': 0.20},
    }

    # Maneuver categories for sequence substitution
    MANEUVER_CATEGORIES = {
        'sprint': 'speed', 'speed_trap': 'speed', 'gentle_arc': 'speed',
        'hard_turn': 'technical', 'chicane': 'technical', 'hairpin': 'technical', 'threading': 'technical',
        'climb': 'vertical', 'dive': 'vertical', 'diagonal': 'vertical', 'spiral': 'vertical',
    }

    SEQUENCE_READY_THRESHOLD = 0.82
    
    def __init__(self, rng, adaptive=True):
        self.rng = rng
        self.adaptive = adaptive
        
        # Active sequence state
        self._active_sequence: List[str] = []
        self._sequence_idx: int = 0
        self._current_complexity: str = 'word'
        
        # Tracking
        self.complexity_counts = {'word': 0, 'sentence': 0, 'paragraph': 0, 'essay': 0}
        self.sequence_completions = {'sentence': 0, 'paragraph': 0, 'essay': 0}
        self.sequence_failures = {'sentence': 0, 'paragraph': 0, 'essay': 0}
    
    def _get_tier_probs(self, avg_mastery: float) -> dict:
        """Continuous probability distribution over complexity levels.

        No hard boundaries — smooth interpolation across mastery range.
        Eliminates the 80% cliff that caused bistable training dynamics.
        """
        m = avg_mastery

        # Sentence: ramps 0% -> 30% over mastery 70%-90%
        p_sentence = np.clip((m - 0.70) / 0.20, 0.0, 0.30)

        # Paragraph: ramps 0% -> 25% over mastery 80%-95%
        p_paragraph = np.clip((m - 0.80) / 0.15, 0.0, 0.25)

        # Essay: ramps 0% -> 20% over mastery 90%-98%
        p_essay = np.clip((m - 0.90) / 0.08, 0.0, 0.20)

        # Word gets the remainder, minimum 20%
        p_word = max(0.20, 1.0 - p_sentence - p_paragraph - p_essay)

        # Normalize
        total = p_word + p_sentence + p_paragraph + p_essay
        return {
            'word': p_word / total,
            'sentence': p_sentence / total,
            'paragraph': p_paragraph / total,
            'essay': p_essay / total,
        }

    def _roll_complexity(self, avg_mastery: float) -> str:
        """Roll for next complexity level using continuous probabilities."""
        if not self.adaptive:
            # Fixed distribution for non-adaptive mode
            dist = self.COMPLEXITY_TIERS['proficient']
        else:
            dist = self._get_tier_probs(avg_mastery)

        levels = list(dist.keys())
        probs = np.array(list(dist.values()))

        return self.rng.choice(levels, p=probs)
    
    def _generate_sequence(self, complexity: str) -> List[str]:
        """Generate a maneuver sequence for the given complexity."""
        if complexity == 'word':
            return []  # Empty = use single random maneuver
        
        elif complexity == 'sentence':
            template = self.rng.choice(SentenceTemplates.ALL)
            return template.__func__(self.rng)
        
        elif complexity == 'paragraph':
            return ParagraphGenerator.generate(self.rng)
        
        elif complexity == 'essay':
            seq, _ = EssayGenerator.generate(self.rng)
            return seq
        
        return []
    
    def _filter_sequence(self, sequence: List[str], maneuver_masteries: dict) -> Optional[List[str]]:
        """Filter sequence to only include sequence-ready maneuvers.

        Maneuvers below SEQUENCE_READY_THRESHOLD are substituted with
        ready maneuvers from the same category. Falls back to word mode
        if no substitution is possible.
        """
        ready = {m for m, rate in maneuver_masteries.items()
                 if rate >= self.SEQUENCE_READY_THRESHOLD}

        if not ready:
            return None

        result = []
        for m in sequence:
            if m in ready:
                result.append(m)
            else:
                # Substitute with a ready maneuver from the same category
                category = self.MANEUVER_CATEGORIES.get(m, 'speed')
                same_cat = [r for r in ready
                            if self.MANEUVER_CATEGORIES.get(r) == category]
                if same_cat:
                    result.append(self.rng.choice(same_cat))
                else:
                    # Any ready maneuver
                    result.append(self.rng.choice(list(ready)))

        return result

    def next_maneuver(self, avg_mastery: float = 0.5,
                      maneuver_masteries: dict = None) -> Optional[str]:
        """
        Get the next maneuver to generate.

        Args:
            avg_mastery: Average mastery across all maneuvers (for complexity roll).
            maneuver_masteries: Per-maneuver mastery rates (for sequence filtering).

        Returns:
            str or None — maneuver name, or None for random single maneuver
        """
        # If we have an active sequence, return next from it
        if self._active_sequence and self._sequence_idx < len(self._active_sequence):
            maneuver = self._active_sequence[self._sequence_idx]
            self._sequence_idx += 1

            # Check if sequence just completed
            if self._sequence_idx >= len(self._active_sequence):
                self.sequence_completions[self._current_complexity] = (
                    self.sequence_completions.get(self._current_complexity, 0) + 1
                )
                self._active_sequence = []
                self._sequence_idx = 0

            return maneuver

        # No active sequence — roll for next complexity
        complexity = self._roll_complexity(avg_mastery)
        self._current_complexity = complexity
        self.complexity_counts[complexity] += 1

        if complexity == 'word':
            return None  # Let the env pick randomly

        # Generate and start a new sequence
        self._active_sequence = self._generate_sequence(complexity)

        # Filter through per-maneuver masteries if provided
        if maneuver_masteries is not None and self._active_sequence:
            filtered = self._filter_sequence(self._active_sequence, maneuver_masteries)
            if filtered is None:
                # No ready maneuvers — fall back to word mode
                self._active_sequence = []
                self.complexity_counts[complexity] -= 1
                self.complexity_counts['word'] += 1
                return None
            self._active_sequence = filtered

        self._sequence_idx = 0

        if self._active_sequence:
            maneuver = self._active_sequence[self._sequence_idx]
            self._sequence_idx += 1
            return maneuver

        return None  # Fallback
    
    def on_episode_end(self, completed_all_gates: bool = False):
        """Called when episode ends — track sequence failures."""
        if self._active_sequence and self._sequence_idx < len(self._active_sequence):
            # Sequence was interrupted (crash/timeout before completing it)
            if self._current_complexity in self.sequence_failures:
                self.sequence_failures[self._current_complexity] += 1
        
        # Reset sequence state for new episode
        self._active_sequence = []
        self._sequence_idx = 0
    
    def get_stats(self, avg_mastery: float = 0.5) -> dict:
        """Get planner statistics."""
        total = sum(self.complexity_counts.values())
        return {
            'complexity_distribution': {
                k: v / max(total, 1) for k, v in self.complexity_counts.items()
            },
            'target_distribution': self._get_tier_probs(avg_mastery),
            'raw_counts': dict(self.complexity_counts),
            'sequence_completions': dict(self.sequence_completions),
            'sequence_failures': dict(self.sequence_failures),
            'total_decisions': total,
        }


# ============================================================
# Test
# ============================================================

if __name__ == '__main__':
    rng = np.random.default_rng(42)
    
    print("=" * 60)
    print("Sequence Generator Tests")
    print("=" * 60)
    
    # Test sentences
    print("\n--- Sentence Examples ---")
    for template in SentenceTemplates.ALL[:5]:
        name = template.__name__
        seq = template.__func__(rng)
        print(f"  {name:25s}: {' -> '.join(seq)}")
    
    # Test paragraphs
    print("\n--- Paragraph Examples ---")
    for i in range(3):
        seq = ParagraphGenerator.generate(rng)
        print(f"  Paragraph {i+1} ({len(seq)} gates): {' -> '.join(seq)}")
    
    # Test essays
    print("\n--- Essay Examples ---")
    for i in range(2):
        seq, character = EssayGenerator.generate(rng)
        print(f"  Essay {i+1} [{character}] ({len(seq)} gates):")
        # Print in chunks of 8
        for j in range(0, len(seq), 8):
            chunk = seq[j:j+8]
            print(f"    {' -> '.join(chunk)}")
    
    # Test planner at different mastery levels (V2 continuous probs)
    print("\n--- Planner Distribution Test (V2 Continuous) ---")
    for mastery in [0.5, 0.75, 0.80, 0.85, 0.90, 0.95]:
        planner = SequencePlanner(rng, adaptive=True)
        probs = planner._get_tier_probs(mastery)
        print(f"  Mastery {mastery:.0%}: "
              f"word={probs['word']:.0%} "
              f"sent={probs['sentence']:.0%} "
              f"para={probs['paragraph']:.0%} "
              f"essay={probs['essay']:.0%}")

    # Test with per-maneuver filtering
    print("\n--- Per-Maneuver Filtering Test ---")
    planner = SequencePlanner(rng, adaptive=True)
    fake_masteries = {
        'sprint': 0.74, 'speed_trap': 0.71, 'gentle_arc': 0.85,
        'hard_turn': 0.88, 'chicane': 0.90, 'hairpin': 0.89,
        'climb': 0.87, 'dive': 0.82, 'threading': 0.92,
        'spiral': 0.90, 'diagonal': 0.85,
    }
    word_count = 0
    seq_count = 0
    for _ in range(200):
        m = planner.next_maneuver(avg_mastery=0.85, maneuver_masteries=fake_masteries)
        if m is None:
            word_count += 1
        else:
            seq_count += 1
            # Verify no unready maneuvers appear in sequences
            assert m not in ('sprint', 'speed_trap'), f"Unready maneuver {m} in sequence!"
    print(f"  Word rolls: {word_count}, Sequence maneuvers: {seq_count}")
    print(f"  Sprint/speed_trap correctly excluded from sequences")
    
    print("\nAll tests passed!")
