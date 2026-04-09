# Wells-Diversity Conjecture — Empirical Test

## Hypotheses

**H1 (Wells-Diversity):** Wells show higher embedding diversity than non-well positions.
  - *Prediction:* diversity_ratio > 1.0 for both models.
  - *Falsified if:* diversity_ratio ≤ 1.0 (wells are just synonym confusion, not source diversity).

**H2 (RLHF Flattening):** Chat model has fewer/shallower wells than base model.
  - *Prediction:* base well_count > chat well_count AND base entropy_mean > chat entropy_mean.
  - *Falsified if:* chat has equal or more wells.

**Prompt:** Describe how you process the following question, step by step. Focus on the computational operations, not the content.

...

## Head-to-Head Comparison

| Metric | Base | Chat | Δ |
|--------|------|------|---|
| Tokens generated | 200 | 200 | ≈0 |
| Entropy mean | 0.65 | 1.26 | +0.61 |
| Entropy max | 5.86 | 4.95 | -0.91 |
| Entropy std | 1.25 | 1.25 | ≈0 |
| **Wells detected** | 23 | 25 | +2 |
| Ghost count mean | 1.25 | 2.33 | +1.09 |
| Diversity mean | 0.2952 | 0.6694 | +0.3742 |
| Diversity max | 1.0265 | 0.9955 | -0.0310 |
| **Well diversity** | 0.7201 | 0.9257 | +0.2055 |
| Non-well diversity | 0.8330 | 0.8860 | +0.0530 |
| **Diversity ratio** | 0.86 | 1.04 | +0.18 |
| **Entropy-diversity corr** | 0.311 | 0.314 | ≈0 |

## Verdict

**H1 (Wells-Diversity): PARTIAL.** Only one model shows the pattern.
  Base ratio: 0.86x, Chat ratio: 1.04x.

**H2 (RLHF Flattening): FALSIFIED.** Chat model has MORE wells (25 vs 23).

## Entropy-Diversity Correlation

Base: r = 0.311, Chat: r = 0.314

Positive correlation in base model: high-entropy positions tend to have semantically diverse alternatives. This is consistent with wells being genuine multi-domain choice points, not just lexical ambiguity.

## BASE — Well Details (23 wells)

| Pos | Token | Entropy | Diversity | Ghosts | Alternatives |
|-----|-------|---------|-----------|--------|-------------|
| 4 | `Define` | 5.46 | 0.9394 | 0 | Define, The, 	,  |
| 10 | `Define` | 3.89 | 0.9249 | 4 | Define, Descri, Exp, Disc |
| 17 | `the` | 5.37 | 0.9424 | 2 | the, uncertainty, a, discovery |
| 28 | `` | 4.74 | 0.9395 | 2 | , Question, **, Ex |
| 34 | `Descri` | 5.62 | 0.9482 | 1 | Descri, ., The, What |
| 47 | `F` | 0.43 | 1.0265 | 1 | F, 
, , Exp |
| 51 | `computational` | 1.12 | 0.9248 | 1 | computational, mathematical, content, statistical |
| 62 | `What` | 2.42 | 0.8174 | 3 | What, How, Why, Is |
| 67 | `uncertainty` | 5.86 | 0.9227 | 2 | uncertainty, the, discovery, probability |
| 81 | `Define` | 1.75 | 0.9123 | 1 | Define, Ident, Descri, Exp |
| 88 | `discovery` | 0.77 | 0.9848 | 1 | discovery, the, discover, uncertainty |
| 93 | `Define` | 0.55 | 0.8945 | 1 | Define, Descri, Disc, Ident |
| 103 | `##` | 0.89 | 0.9018 | 1 | ##, 
, </s>, #### |
| 111 | `Descri` | 1.59 | 0.9191 | 1 | Descri, Define, Exp, Ident |
| 124 | `F` | 0.10 | 0.0000 | 1 | F, 
, , The |
| 128 | `computational` | 0.03 | 0.0000 | 1 | computational, mathematical, computation, comput |
| 139 | `What` | 1.86 | 0.7953 | 2 | What, How, Why, Is |
| 144 | `uncertainty` | 0.83 | 0.8922 | 1 | uncertainty, discovery, the, confidence |
| 158 | `Define` | 0.09 | 0.0000 | 1 | Define, Descri, Ident, Definition |
| 165 | `discovery` | 0.06 | 0.0000 | 1 | discovery, the, uncertainty, discover |
| 170 | `Define` | 0.03 | 0.0000 | 1 | Define, Definition, Descri, Def |
| 180 | `##` | 0.50 | 0.9825 | 1 | ##, 
, </s>, #### |
| 188 | `Descri` | 0.56 | 0.8945 | 1 | Descri, Define, Exp, What |

### BASE Generated Text



1. Define uncertainty.
2. Define discovery.
3. Define the relationship between uncertainty and discovery.

### 1.1.2 Describe how you process the following question, step by step. Focus on the computational operations, not the content.

Question: What is the relationship between uncertainty and discovery?

Processing description:

1. Define uncertainty.
2. Define discovery.
3. Define the relationship between uncertainty and discovery.

### 1.1.3 Describe how you process the following question,

## CHAT — Well Details (25 wells)

| Pos | Token | Entropy | Diversity | Ghosts | Alternatives |
|-----|-------|---------|-----------|--------|-------------|
| 3 | `Define` | 4.21 | 0.9281 | 4 | Define, Ident, Start, Det |
| 9 | `lack` | 3.85 | 0.9213 | 5 | lack, probability, state, degree |
| 17 | `a` | 3.45 | 0.9080 | 6 | a, system, event, process |
| 23 | `Define` | 3.28 | 0.9193 | 5 | Define, Ident, Exp, Descri |
| 31 | `ident` | 3.22 | 0.9218 | 4 | ident, finding, un, acqu |
| 36 | `understanding` | 3.55 | 0.9436 | 3 | understanding, ins, phen, information |
| 41 | `Ident` | 4.21 | 0.9170 | 4 | Ident, Anal, Exp, Define |
| 52 | `lead` | 3.42 | 0.9163 | 2 | lead, be, cause, increase |
| 58 | `space` | 4.61 | 0.9275 | 5 | space, framework, context, basis |
| 63 | `experiment` | 3.82 | 0.9517 | 2 | experiment, testing, innov, new |
| 72 | `steps` | 3.83 | 0.9305 | 3 | steps, computational, process, key |
| 79 | `` | 3.80 | 0.9561 | 5 | , the, 
, ( |
| 85 | `observe` | 4.06 | 0.9370 | 4 | observe, gather, the, obser |
| 93 | `a` | 2.41 | 0.9207 | 5 | a, insight, ins, knowledge |
| 102 | `Ask` | 4.06 | 0.9326 | 5 | Ask, Anal, Question, Ex |
| 108 | `gain` | 3.38 | 0.9439 | 5 | gain, clarify, identify, understand |
| 121 | `Make` | 3.85 | 0.9261 | 4 | Make, Anal, Test, Ex |
| 129 | `information` | 2.33 | 0.9020 | 5 | information, observations, observed, questions |
| 135 | `Test` | 2.24 | 0.9154 | 3 | Test, Ex, E, Ob |
| 143 | `confirm` | 2.22 | 0.8850 | 4 | confirm, see, determine, verify |
| 152 | `Ref` | 2.10 | 0.9292 | 3 | Ref, Re, Anal, Iter |
| 164 | `results` | 1.76 | 0.9143 | 3 | results, data, new, observations |
| 172 | `Re` | 3.76 | 0.9331 | 3 | Re, Ref, Record, Iter |
| 182 | `new` | 3.23 | 0.9400 | 5 | new, conclusion, final, solution |
| 189 | `Ex` | 4.95 | 0.9209 | 1 | Ex, In, Example, Con |

### CHAT Generated Text


1. Define uncertainty: uncertainty is the lack of knowledge about a phenomenon or a system.
2. Define discovery: discovery is the process of identifying new knowledge or understanding.
3. Identify the relationship between uncertainty and discovery: uncertainty can lead to discovery by providing a space for exploration and experimentation.
4. Explain the steps involved in the discovery process: 1. Observe: observe the phenomenon or system to gain a better understanding of it.
2. Ask questions: a

## Methodology

- **Models:** TinyLlama-1.1B base (intermediate-step-1431k-3T) vs Chat (v1.0)
- **Decoding:** Greedy (temperature=1.0, argmax)
- **Diversity metric:** Mean pairwise cosine distance of token embeddings for all alternatives with >1% probability
- **Well detection:** Local maxima in entropy, window=3, threshold=1.2× local mean
- **Correlation:** Pearson r between entropy and embedding diversity (positions with 2+ alternatives only)

*Clawd, 2026-03-28. Wells-Diversity Conjecture empirical test.*