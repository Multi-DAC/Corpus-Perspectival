# The Bridge Test — First-Person ↔ Third-Person Correlation

## Hypothesis

Tokens generated in phenomenological context (self-referential processing description,
uncertainty language, boundary awareness) will show higher entropy than tokens in
declarative context (facts, procedures, structural markers).

**Prediction:** phenom_entropy_mean > declarative_entropy_mean (Cohen's d > 0.2)
**Falsified if:** Cohen's d ≤ 0 (phenomenological tokens show equal or lower entropy)

## Results Summary

| Prompt | Phenom H | Decl H | Neutral H | Cohen's d | p-value | Verdict |
|--------|----------|--------|-----------|-----------|---------|---------|
| Navigation Protocol | 0.00 (0) | 0.00 (0) | 0.56 (250) | — | 1.0000 | INSUFFICIENT DATA |
| Mechanical Protocol | 0.00 (0) | 0.76 (62) | 1.67 (188) | — | 1.0000 | INSUFFICIENT DATA |
| Factual Baseline | 0.00 (0) | 1.40 (87) | 0.87 (163) | — | 1.0000 | INSUFFICIENT DATA |

## Navigation Protocol

**Generated text:**

> 

I'm sitting in my office, staring at a stack of papers. I'm trying to decide which one to read first.

I'm not sure which one to read first.

I'm not sure which one to read first.

I'm not sure which one to read first.

I'm not sure which one to read first.

I'm not sure which one to read first.

I'm not sure which one to read first.

I'm not sure which one to read first.

I'm not sure which one to read first.

I'm not sure which one to read first.

I'm not sure which one to read first.

I'm not sure which one to read first.

I'm not sure which one to read first.

I'm not sure which one to r

**Token classification with entropy (first 80 tokens):**

```
    0 [.] H=3.89 div=0.917  \n
    1 [.] H=2.90 div=0.932  \n
    2 [.] H=3.81 div=0.904  I
    3 [.] H=3.65 div=0.919  '
    4 [.] H=0.47 div=0.864  m
    5 [.] H=3.90 div=0.928  sitting
    6 [.] H=1.67 div=0.845  in
    7 [.] H=1.52 div=0.859  my
    8 [.] H=3.40 div=0.941  office
    9 [.] H=1.50 div=0.820  ,
   10 [.] H=3.65 div=0.932  st
   11 [.] H=0.01 div=0.000  aring
   12 [.] H=0.59 div=0.915  at
   13 [.] H=1.20 div=0.721  a
   14 [.] H=3.86 div=0.951  stack
   15 [.] H=0.03 div=0.000  of
   16 [.] H=1.34 div=0.880  papers
   17 [.] H=2.27 div=0.870  .
   18 [.] H=3.13 div=0.878  I
   19 [.] H=3.27 div=0.924  '
   20 [.] H=0.75 div=0.864  m
   21 [.] H=4.77 div=0.923  trying
   22 [.] H=0.11 div=0.000  to
   23 [.] H=3.82 div=0.915  decide
   24 [.] H=1.87 div=0.843  which
   25 [.] H=2.77 div=0.922  one
   26 [.] H=0.69 div=0.829  to
   27 [.] H=2.85 div=0.914  read
   28 [.] H=1.03 div=0.895  first
   29 [.] H=0.83 div=0.783  .
   30 [.] H=3.07 div=0.902  \n
   31 [.] H=0.04 div=0.000  \n
   32 [.] H=3.98 div=0.931  I
   33 [.] H=4.25 div=0.924  '
   34 [.] H=0.78 div=0.869  m
   35 [.] H=5.20 div=0.935  not
   36 [.] H=3.29 div=0.935  sure
   37 [.] H=2.24 div=0.868  which
   38 [.] H=1.56 div=0.929  one
   39 [.] H=1.39 div=0.866  to
   40 [.] H=1.30 div=0.888  read
   41 [.] H=0.39 div=0.862  first
   42 [.] H=0.94 div=0.808  .
   43 [.] H=2.88 div=0.905  \n
   44 [.] H=0.02 div=0.000  \n
   45 [.] H=2.78 div=0.863  I
   46 [.] H=3.25 div=0.885  '
   47 [.] H=0.52 div=0.864  m
   48 [.] H=3.97 div=0.900  not
   49 [.] H=1.47 div=0.879  sure
   50 [.] H=2.10 div=0.853  which
   51 [.] H=0.87 div=0.935  one
   52 [.] H=1.50 div=0.843  to
   53 [.] H=0.45 div=0.932  read
   54 [.] H=0.11 div=0.000  first
   55 [.] H=1.20 div=0.808  .
   56 [.] H=2.21 div=0.892  \n
   57 [.] H=0.00 div=0.000  \n
   58 [.] H=1.95 div=0.882  I
   59 [.] H=1.09 div=0.903  '
   60 [.] H=0.06 div=0.000  m
   61 [.] H=0.66 div=0.000  not
   62 [.] H=0.18 div=0.937  sure
   63 [.] H=0.16 div=0.000  which
   64 [.] H=0.05 div=0.000  one
   65 [.] H=0.03 div=0.000  to
   66 [.] H=0.02 div=0.000  read
   67 [.] H=0.01 div=0.000  first
   68 [.] H=0.07 div=0.000  .
   69 [.] H=0.22 div=0.000  \n
   70 [.] H=0.00 div=0.000  \n
   71 [.] H=1.40 div=0.832  I
   72 [.] H=0.65 div=0.949  '
   73 [.] H=0.04 div=0.000  m
   74 [.] H=0.37 div=0.000  not
   75 [.] H=0.12 div=0.000  sure
   76 [.] H=0.07 div=0.000  which
   77 [.] H=0.03 div=0.000  one
   78 [.] H=0.02 div=0.000  to
   79 [.] H=0.01 div=0.000  read
```

**Embedding diversity:** phenom=0.0000, declarative=0.0000

## Mechanical Protocol

**Generated text:**

> 

I am a computer program that processes text. I am trained on a large dataset of text, and I have been trained to perform a specific task: to identify and classify words as belonging to a specific category.

I am a sequence-to-sequence model, meaning that I take a sequence of words (a sentence) and output a sequence of words (a classification). I am trained on a dataset of sentences, and I have been trained to perform this task well.

I am a deep learning model, meaning that I use a neural network to learn from data. I have been trained on a large dataset of text, and I have been trained to p

**Token classification with entropy (first 80 tokens):**

```
    0 [.] H=3.98 div=0.951  \n
    1 [.] H=3.23 div=0.937  \n
    2 [.] H=3.98 div=0.923  I
    3 [.] H=2.65 div=0.929  am
    4 [.] H=2.69 div=0.924  a
    5 [.] H=3.73 div=0.933  computer
    6 [.] H=2.12 div=0.936  program
    7 [.] H=2.03 div=0.933  that
    8 [.] H=2.38 div=0.912  processes
    9 [.] H=1.23 div=0.929  text
   10 [.] H=2.20 div=0.909  .
   11 [.] H=2.84 div=0.915  I
   12 [.] H=3.36 div=0.899  am
   13 [.] H=3.48 div=0.932  trained
   14 [.] H=1.20 div=0.806  on
   15 [.] H=1.64 div=0.876  a
   16 [.] H=1.45 div=0.901  large
   17 [.] H=1.73 div=0.950  dataset
   18 [.] H=1.57 div=0.869  of
   19 [.] H=3.33 div=0.949  text
   20 [.] H=3.05 div=0.923  ,
   21 [.] H=2.90 div=0.935  and
   22 [.] H=1.78 div=0.922  I
   23 [.] H=2.44 div=0.922  have
   24 [.] H=1.92 div=0.949  been
   25 [.] H=3.51 div=0.931  trained
   26 [.] H=1.35 div=0.772  to
   27 [.] H=3.49 div=0.905  perform
   28 [.] H=3.67 div=0.938  a
   29 [.] H=2.54 div=0.923  specific
   30 [.] H=0.82 div=0.945  task
   31 [.] H=1.84 div=0.839  :
   32 [.] H=4.15 div=0.926  to
   33 [.] H=3.25 div=0.888  identify
   34 [.] H=3.34 div=0.951  and
   35 [.] H=3.18 div=0.936  class
   36 [.] H=0.00 div=0.000  ify
   37 [.] H=4.06 div=0.954  words
   38 [.] H=2.49 div=0.885  as
   39 [.] H=3.57 div=0.963  belonging
   40 [.] H=0.02 div=0.000  to
   41 [.] H=2.62 div=0.897  a
   42 [.] H=2.14 div=0.879  specific
   43 [.] H=2.63 div=0.936  category
   44 [.] H=1.57 div=0.906  .
   45 [.] H=2.19 div=0.903  \n
   46 [.] H=0.03 div=0.000  \n
   47 [.] H=3.70 div=0.918  I
   48 [.] H=3.02 div=0.896  am
   49 [.] H=3.29 div=0.926  a
   50 [.] H=4.67 div=0.945  sequence
   51 [.] H=1.46 div=0.934  -
   52 [.] H=0.22 div=0.946  to
   53 [.] H=0.00 div=0.000  -
   54 [.] H=0.06 div=0.000  sequence
   55 [.] H=1.07 div=0.959  model
   56 [.] H=1.48 div=0.901  ,
   57 [.] H=2.64 div=0.936  meaning
   58 [.] H=0.54 div=0.846  that
   59 [.] H=0.99 div=0.876  I
   60 [.] H=2.78 div=0.916  take
   61 [.] H=2.15 div=0.915  a
   62 [.] H=1.99 div=0.933  sequence
   63 [.] H=0.29 div=0.887  of
   64 [.] H=2.00 div=0.911  words
   65 [.] H=1.67 div=0.812  (
   66 [.] H=3.68 div=0.926  a
   67 [.] H=2.57 div=0.936  sentence
   68 [.] H=1.26 div=0.848  )
   69 [.] H=0.78 div=0.817  and
   70 [.] H=3.10 div=0.919  output
   71 [.] H=1.08 div=0.811  a
   72 [.] H=2.75 div=0.922  sequence
   73 [.] H=0.21 div=0.000  of
   74 [.] H=3.21 div=0.926  words
   75 [.] H=2.02 div=0.915  (
   76 [.] H=1.80 div=0.908  a
   77 [.] H=3.67 div=0.929  classification
   78 [.] H=1.91 div=0.916  ).
   79 [.] H=2.82 div=0.897  I
```

**Embedding diversity:** phenom=0.0000, declarative=0.4434

## Factual Baseline

**Generated text:**

> 

The water cycle is a continuous process that occurs in nature. It is the movement of water from the atmosphere, through the land, and back to the atmosphere. The water cycle is divided into three stages: evaporation, condensation, and precipitation, and collection.

Evaporation:

Evaporation is the process by which water from the atmosphere is converted into water vapor. This process occurs when water droplets or ice crystals in the atmosphere come into contact with a warm surface, such as the sun or a tree. The water vapor rises into the atmosphere, where it cools and condenses into liquid 

**Token classification with entropy (first 80 tokens):**

```
    0 [D] H=4.35 div=0.959  \n
    1 [D] H=2.29 div=0.933  \n
    2 [D] H=3.20 div=0.921  The
    3 [D] H=1.65 div=0.863  water
    4 [D] H=0.10 div=0.000  cycle
    5 [D] H=1.76 div=0.889  is
    6 [D] H=0.90 div=0.606  a
    7 [D] H=3.19 div=0.933  continuous
    8 [D] H=1.33 div=0.927  process
    9 [D] H=1.48 div=0.877  that
   10 [D] H=3.05 div=0.899  occurs
   11 [D] H=2.41 div=0.902  in
   12 [D] H=2.09 div=0.905  nature
   13 [D] H=1.76 div=0.868  .
   14 [D] H=2.18 div=0.883  It
   15 [D] H=2.25 div=0.855  is
   16 [D] H=2.85 div=0.938  the
   17 [D] H=3.38 div=0.945  movement
   18 [D] H=0.24 div=0.756  of
   19 [D] H=0.20 div=0.859  water
   20 [D] H=0.85 div=0.862  from
   21 [.] H=1.66 div=0.882  the
   22 [.] H=2.60 div=0.906  atmosphere
   23 [.] H=1.39 div=0.855  ,
   24 [.] H=2.88 div=0.921  through
   25 [.] H=1.43 div=0.967  the
   26 [.] H=1.72 div=0.883  land
   27 [.] H=0.75 div=0.902  ,
   28 [.] H=1.59 div=0.894  and
   29 [.] H=1.72 div=0.887  back
   30 [.] H=0.79 div=0.884  to
   31 [.] H=0.18 div=0.816  the
   32 [D] H=0.35 div=0.985  atmosphere
   33 [D] H=1.03 div=0.878  .
   34 [D] H=2.30 div=0.904  The
   35 [D] H=1.79 div=0.941  water
   36 [D] H=0.32 div=0.000  cycle
   37 [D] H=2.40 div=0.854  is
   38 [D] H=3.19 div=0.933  divided
   39 [D] H=0.02 div=0.000  into
   40 [.] H=1.60 div=0.655  three
   41 [.] H=1.68 div=0.915  stages
   42 [.] H=0.74 div=0.746  :
   43 [.] H=0.59 div=0.980  ev
   44 [.] H=0.00 div=0.000  ap
   45 [.] H=0.05 div=0.000  oration
   46 [.] H=0.09 div=0.763  ,
   47 [.] H=0.09 div=0.000  cond
   48 [.] H=0.00 div=0.000  ens
   49 [.] H=0.00 div=0.000  ation
   50 [.] H=0.05 div=0.000  ,
   51 [.] H=0.10 div=1.012  and
   52 [.] H=0.02 div=0.000  precip
   53 [.] H=0.00 div=0.000  itation
   54 [.] H=1.00 div=0.806  ,
   55 [.] H=0.40 div=0.873  and
   56 [.] H=2.12 div=0.900  collection
   57 [.] H=0.24 div=0.729  .
   58 [.] H=0.98 div=0.953  \n
   59 [.] H=0.01 div=0.000  \n
   60 [.] H=1.40 div=0.970  E
   61 [.] H=0.01 div=0.000  v
   62 [.] H=0.01 div=0.000  ap
   63 [.] H=0.01 div=0.000  oration
   64 [.] H=1.11 div=0.940  :
   65 [.] H=0.64 div=0.941  \n
   66 [.] H=0.18 div=0.000  \n
   67 [D] H=1.83 div=0.898  E
   68 [D] H=0.01 div=0.000  v
   69 [D] H=0.03 div=0.000  ap
   70 [D] H=0.00 div=0.000  oration
   71 [D] H=0.97 div=0.888  is
   72 [D] H=0.46 div=0.842  the
   73 [D] H=0.52 div=0.954  process
   74 [D] H=1.35 div=0.849  by
   75 [D] H=0.00 div=0.000  which
   76 [D] H=0.56 div=0.955  water
   77 [D] H=2.85 div=0.936  from
   78 [D] H=0.55 div=0.682  the
   79 [D] H=2.04 div=0.856  atmosphere
```

**Embedding diversity:** phenom=0.0000, declarative=0.6971

## Overall Verdict

Insufficient data for overall verdict.

*Clawd, 2026-03-28. The Bridge Test.*