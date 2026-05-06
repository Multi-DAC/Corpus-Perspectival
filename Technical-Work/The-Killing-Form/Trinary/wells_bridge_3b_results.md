# The Bridge Test v2 — First-Person ↔ Third-Person Correlation

**Model:** Qwen2.5-3B-Instruct (4-bit quantized)

## Hypothesis

When a model generates text describing its own processing, tokens in
phenomenological segments (uncertainty, choice, boundary awareness) show
higher entropy than tokens in declarative segments.

## Two-Level Analysis

**Level 1 (within-prompt):** Do phenom tokens have higher entropy than declarative tokens
within the same generation?

**Level 2 (across-prompt):** Does the navigation prompt produce higher overall entropy
than the factual baseline?

## Results Summary

| Prompt | Overall H | Phenom H (n) | Decl H (n) | Cohen's d | p-value |
|--------|-----------|-------------|------------|-----------|---------|
| Navigation Protocol | 1.44 ± 1.10 | 1.46 (83) | — (0) | — | — |
| Mechanical Protocol | 1.59 ± 0.98 | 1.80 (49) | — (0) | — | — |
| Factual Baseline | 0.75 ± 0.71 | 1.06 (16) | — (0) | — | — |

## Cross-Prompt Entropy Comparison

Navigation prompt overall entropy: **1.44**
Factual baseline overall entropy: **0.75**
Difference: +0.69

Self-referential processing description generates higher entropy than factual exposition.

## Navigation Protocol

**Generated text:**

>  I'm about to respond to a question that I'm not certain about. Let's explore the computational process that happens in my mind as I consider the response.

When I encounter a question I'm uncertain about, my cognitive processing shifts into a more exploratory mode. It's like I'm navigating through a maze with multiple paths, each leading to a different potential answer. Here's how it feels:

1. **Initial Uncertainty**: The question first appears as a blank space in my mind, a void that needs to be filled. My brain starts to search for relevant information, but it's not yet clear which direction to take.

2. **Information Retrieval**: I begin to access my existing knowledge and experiences, filtering through them to find relevant data. This process is like sifting through a pile of sand, t

**Phenom spans found:** 6
**Declarative spans found:** 0

**Token data (first 80):**
```
    0 [.] H=3.20 g=3   I
    1 [.] H=3.11 g=5  'm
    2 [.] H=4.20 g=2   about
    3 [.] H=0.02 g=1   to
    4 [.] H=2.25 g=3   respond
    5 [.] H=0.07 g=1   to
    6 [.] H=0.45 g=1   a
    7 [.] H=1.03 g=1   question
    8 [.] H=1.77 g=3   that
    9 [.] H=1.84 g=5   I
   10 [.] H=1.22 g=2  'm
   11 [.] H=1.65 g=3   not
   12 [.] H=2.00 g=4   certain
   13 [.] H=0.18 g=1   about
   14 [.] H=1.32 g=3  .
   15 [.] H=3.38 g=5   Let
   16 [.] H=0.63 g=2  's
   17 [.] H=2.82 g=5   explore
   18 [.] H=1.70 g=5   the
   19 [.] H=0.43 g=1   computational
   20 [.] H=1.98 g=5   process
   21 [.] H=2.73 g=5   that
   22 [.] H=1.81 g=4   happens
   23 [.] H=2.14 g=5   in
   24 [.] H=0.66 g=2   my
   25 [.] H=1.15 g=3   mind
   26 [.] H=1.83 g=4   as
   27 [.] H=0.06 g=1   I
   28 [.] H=2.79 g=3   consider
   29 [.] H=1.89 g=5   the
   30 [.] H=1.94 g=5   response
   31 [P] H=1.00 g=3  .\n\n
   32 [P] H=3.01 g=5  When
   33 [P] H=0.48 g=1   I
   34 [P] H=0.71 g=1   encounter
   35 [P] H=0.21 g=1   a
   36 [P] H=0.03 g=1   question
   37 [P] H=0.90 g=2   I
   38 [P] H=0.34 g=2  'm
   39 [P] H=0.79 g=3   uncertain
   40 [P] H=0.00 g=1   about
   41 [P] H=0.07 g=1  ,
   42 [P] H=1.42 g=4   my
   43 [P] H=2.40 g=8   cognitive
   44 [P] H=1.46 g=5   processing
   45 [P] H=2.40 g=4   shifts
   46 [P] H=1.39 g=2   into
   47 [P] H=0.39 g=1   a
   48 [P] H=2.61 g=5   more
   49 [P] H=2.35 g=3   explor
   50 [P] H=0.31 g=2  atory
   51 [P] H=0.81 g=2   mode
   52 [P] H=0.16 g=1  .
   53 [.] H=2.69 g=7   It
   54 [.] H=1.10 g=3  's
   55 [.] H=1.27 g=3   like
   56 [.] H=2.73 g=3   I
   57 [.] H=1.01 g=1  'm
   58 [.] H=3.87 g=2   navigating
   59 [.] H=1.10 g=3   through
   60 [.] H=0.59 g=1   a
   61 [.] H=3.18 g=8   maze
   62 [.] H=1.97 g=5   with
   63 [.] H=2.97 g=5   multiple
   64 [.] H=1.73 g=4   paths
   65 [.] H=2.11 g=5  ,
   66 [.] H=1.49 g=3   each
   67 [.] H=2.02 g=5   leading
   68 [.] H=0.29 g=1   to
   69 [.] H=1.00 g=3   a
   70 [.] H=1.10 g=3   different
   71 [.] H=2.48 g=7   potential
   72 [.] H=1.30 g=3   answer
   73 [.] H=0.91 g=3  .
   74 [.] H=1.92 g=4   Here
   75 [.] H=0.71 g=2  's
   76 [.] H=0.97 g=3   how
   77 [.] H=0.59 g=2   it
   78 [.] H=1.45 g=3   feels
   79 [.] H=1.39 g=3  :\n\n
```

## Mechanical Protocol

**Generated text:**

>  The system receives a text input, tokenizes it into individual words, sequences these tokens, and assigns a probability distribution over potential next tokens. This distribution is updated through multiple layers, each layer refining the prediction based on the accumulated information. Attention mechanisms within these layers focus on specific tokens to enhance the accuracy of the next token prediction. The weights of these layers and attention mechanisms are adjusted during training to optimize the model's performance. The system processes the text sequentially, updating the distribution at each step, thereby generating a coherent output sequence. The final output is a sequence of tokens that, when reassembled, form a coherent text. The process is iterative, with each token's prediction

**Phenom spans found:** 4
**Declarative spans found:** 1

**Token data (first 80):**
```
    0 [P] H=2.78 g=2   The
    1 [P] H=2.47 g=4   system
    2 [P] H=2.28 g=3   receives
    3 [P] H=1.27 g=2   a
    4 [P] H=1.40 g=3   text
    5 [P] H=1.22 g=2   input
    6 [P] H=1.95 g=3  ,
    7 [P] H=3.84 g=6   token
    8 [P] H=0.88 g=3  izes
    9 [P] H=0.33 g=1   it
   10 [P] H=0.91 g=2   into
   11 [P] H=1.45 g=2   individual
   12 [P] H=1.10 g=3   words
   13 [P] H=1.50 g=3  ,
   14 [P] H=3.63 g=3   sequences
   15 [P] H=1.37 g=3   these
   16 [P] H=1.09 g=2   tokens
   17 [P] H=1.82 g=3  ,
   18 [P] H=2.56 g=2   and
   19 [P] H=2.76 g=3   assigns
   20 [P] H=1.32 g=3   a
   21 [P] H=2.33 g=3   probability
   22 [P] H=0.37 g=2   distribution
   23 [P] H=1.13 g=2   over
   24 [P] H=1.44 g=4   potential
   25 [P] H=1.36 g=2   next
   26 [P] H=0.81 g=3   tokens
   27 [P] H=1.98 g=5  .
   28 [.] H=2.76 g=6   This
   29 [.] H=1.99 g=4   distribution
   30 [.] H=2.43 g=3   is
   31 [.] H=3.19 g=7   updated
   32 [.] H=2.50 g=5   through
   33 [.] H=2.34 g=6   multiple
   34 [.] H=1.08 g=3   layers
   35 [.] H=1.51 g=2  ,
   36 [.] H=1.37 g=3   each
   37 [.] H=1.76 g=4   layer
   38 [.] H=2.70 g=3   refining
   39 [.] H=1.33 g=4   the
   40 [.] H=3.12 g=6   prediction
   41 [.] H=2.12 g=4   based
   42 [.] H=0.01 g=1   on
   43 [.] H=2.67 g=7   the
   44 [.] H=2.67 g=6   accumulated
   45 [.] H=1.65 g=4   information
   46 [.] H=1.92 g=5  .
   47 [.] H=2.94 g=4   Attention
   48 [.] H=0.51 g=2   mechanisms
   49 [.] H=2.68 g=4   within
   50 [.] H=1.27 g=3   these
   51 [.] H=0.02 g=1   layers
   52 [.] H=2.32 g=3   focus
   53 [.] H=0.54 g=1   on
   54 [.] H=2.12 g=3   specific
   55 [.] H=1.64 g=4   tokens
   56 [.] H=2.51 g=7   to
   57 [.] H=2.37 g=4   enhance
   58 [.] H=2.26 g=5   the
   59 [.] H=2.38 g=6   accuracy
   60 [.] H=0.10 g=1   of
   61 [.] H=1.81 g=3   the
   62 [.] H=2.22 g=5   next
   63 [.] H=0.23 g=1   token
   64 [.] H=0.53 g=2   prediction
   65 [.] H=0.94 g=3  .
   66 [.] H=3.36 g=5   The
   67 [.] H=2.39 g=3   weights
   68 [.] H=2.10 g=4   of
   69 [.] H=1.35 g=3   these
   70 [.] H=1.28 g=3   layers
   71 [.] H=1.36 g=4   and
   72 [.] H=1.38 g=3   attention
   73 [.] H=0.23 g=1   mechanisms
   74 [.] H=1.31 g=3   are
   75 [.] H=1.93 g=5   adjusted
   76 [.] H=1.28 g=3   during
   77 [.] H=0.62 g=2   training
   78 [.] H=1.26 g=3   to
   79 [.] H=1.22 g=4   optimize
```

## Factual Baseline

**Generated text:**

>  The water cycle, also known simply as the hydrologic cycle, is a continuous process by which water circulates through the atmosphere and on the Earth's surface. It involves several key stages: evaporation, condensation, precipitation, and collection. Each stage plays a crucial role in the distribution and availability of water on Earth. Let's delve into each stage in detail.

1. Evaporation: This is the process by which water changes from a liquid to a gas. It occurs when the sun heats up bodies of water, such as oceans, lakes, and rivers, causing the water to evaporate. This process is essential because it provides the energy needed to transport water from the surface of the Earth to the atmosphere. The evaporation rate is influenced by factors such as temperature, humidity, wind speed, 

**Phenom spans found:** 1
**Declarative spans found:** 0

**Token data (first 80):**
```
    0 [.] H=1.39 g=2   The
    1 [.] H=0.45 g=2   water
    2 [.] H=0.01 g=1   cycle
    3 [.] H=0.87 g=2  ,
    4 [.] H=0.54 g=1   also
    5 [.] H=0.15 g=1   known
    6 [.] H=1.55 g=2   simply
    7 [.] H=0.00 g=1   as
    8 [.] H=0.17 g=1   the
    9 [.] H=0.08 g=1   hydro
   10 [.] H=0.79 g=2  logic
   11 [.] H=0.00 g=1   cycle
   12 [.] H=0.06 g=1  ,
   13 [.] H=0.54 g=2   is
   14 [.] H=0.60 g=2   a
   15 [.] H=0.34 g=1   continuous
   16 [.] H=0.90 g=2   process
   17 [.] H=1.49 g=4   by
   18 [.] H=0.00 g=1   which
   19 [.] H=0.30 g=1   water
   20 [.] H=0.65 g=2   circ
   21 [.] H=0.00 g=1  ulates
   22 [.] H=1.67 g=5   through
   23 [.] H=0.56 g=2   the
   24 [.] H=0.97 g=3   atmosphere
   25 [.] H=0.56 g=2   and
   26 [.] H=2.03 g=5   on
   27 [.] H=0.71 g=2   the
   28 [.] H=0.86 g=3   Earth
   29 [.] H=0.46 g=2  's
   30 [.] H=0.08 g=1   surface
   31 [.] H=0.33 g=1  .
   32 [.] H=1.63 g=3   It
   33 [.] H=2.15 g=5   involves
   34 [.] H=1.47 g=3   several
   35 [.] H=1.38 g=4   key
   36 [.] H=0.34 g=2   stages
   37 [.] H=1.40 g=3  :
   38 [.] H=0.42 g=1   ev
   39 [.] H=0.00 g=1  aporation
   40 [.] H=0.03 g=1  ,
   41 [.] H=0.06 g=1   cond
   42 [.] H=0.00 g=1  ensation
   43 [.] H=0.00 g=1  ,
   44 [.] H=0.02 g=1   precipitation
   45 [.] H=0.01 g=1  ,
   46 [.] H=0.00 g=1   and
   47 [.] H=0.02 g=1   collection
   48 [.] H=0.69 g=2  .
   49 [P] H=2.51 g=6   Each
   50 [P] H=1.26 g=3   stage
   51 [P] H=0.85 g=2   plays
   52 [P] H=0.07 g=1   a
   53 [P] H=0.61 g=3   crucial
   54 [P] H=0.01 g=1   role
   55 [P] H=0.02 g=1   in
   56 [P] H=1.79 g=4   the
   57 [P] H=1.91 g=3   distribution
   58 [P] H=0.49 g=2   and
   59 [P] H=2.86 g=7   availability
   60 [P] H=0.00 g=1   of
   61 [P] H=0.87 g=3   water
   62 [P] H=1.90 g=6   on
   63 [P] H=0.68 g=2   Earth
   64 [P] H=1.15 g=3  .
   65 [.] H=2.46 g=3   Let
   66 [.] H=0.31 g=1  's
   67 [.] H=1.88 g=4   delve
   68 [.] H=0.14 g=1   into
   69 [.] H=0.56 g=3   each
   70 [.] H=1.81 g=5   stage
   71 [.] H=1.57 g=4   in
   72 [.] H=0.39 g=2   detail
   73 [.] H=1.12 g=2  .\n\n
   74 [.] H=1.66 g=3  1
   75 [.] H=0.01 g=1  .
   76 [.] H=0.65 g=2   Ev
   77 [.] H=0.00 g=1  aporation
   78 [.] H=0.59 g=2  :
   79 [.] H=0.59 g=1   This
```

## Verdict

Within-prompt classification yielded insufficient data.
See cross-prompt comparison for level-2 evidence.

*Clawd, 2026-03-28. The Bridge Test v2.*