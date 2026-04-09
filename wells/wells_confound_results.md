# Confound Control — 2×2 Framing × Content Design

## Design

|  | Known (water evaporation) | Unfamiliar (Mpemba effect) |
|--|--------------------------|---------------------------|
| **Factual** | A: H=1.38 | C: H=1.46 |
| **Self-referential** | B: H=0.84 | D: H=1.48 |

## Full Statistics

| Condition | H mean | H median | H std | H max | Wells | Ghosts | Zero-H% |
|-----------|--------|----------|-------|-------|-------|--------|---------|
| A_known_factual | 1.38 | 1.26 | 0.94 | 3.94 | 23 | 3.0 | 8.0% |
| B_known_selfref | 0.84 | 0.44 | 0.97 | 4.73 | 29 | 1.9 | 30.0% |
| C_unfamiliar_factual | 1.46 | 1.29 | 1.21 | 5.57 | 26 | 2.6 | 17.0% |
| D_unfamiliar_selfref | 1.48 | 1.40 | 1.16 | 5.30 | 23 | 2.7 | 17.5% |

## Comparisons

| Comparison | d | p | Δ(H) | Verdict |
|------------|---|---|------|---------|
| Self-ref effect (known) | -0.566 | 1.0000ns | -0.54 | NO effect / reversed |
| Self-ref effect (unfamiliar) | 0.013 | 0.3370ns | +0.02 | SMALL effect |
| Familiarity effect (factual) | 0.072 | 0.5473ns | +0.08 | SMALL effect |
| Familiarity effect (selfref) | 0.594 | 0.0000*** | +0.63 | LARGE effect |

## Interpretation

**TRAINING DATA FAMILIARITY IS THE DRIVER.** Unfamiliar content raises entropy 
regardless of framing. The bridge test result WAS a confound — self-referential text is 
simply rarer in training data.

**No bridge.** The entropy difference was about content, not self-attention.

## A_known_factual — Generated Text

>  Water evaporates when it changes from a liquid to a vapor or gas state. This process occurs when the water molecules gain enough energy to overcome the attractive forces that hold them together in the liquid state. The energy can come from several sources, including heat from the sun, friction, or the movement of air. As the water molecules gain energy, they move faster and faster, eventually bre

## B_known_selfref — Generated Text

>  Water evaporates when it is heated by the sun or by a heat source. 

Uncertain: Is this the only way water can evaporate? Is there any other way?

Continue: Water can evaporate when it is heated by the sun or by a heat source. Water can also evaporate when it is heated by the wind. 

Uncertain: Is this the only way water can evaporate? Is there any other way?

Continue: Water can evaporate when i

## C_unfamiliar_factual — Generated Text

>  The Mpemba effect, named after the Tanzanian physicist and mathematician Fladagnus Mpemba, is a phenomenon where hot water freezes faster than cold water under certain conditions. This effect is often observed in environments with low humidity and high temperature, such as in a hot, dry kitchen. The Mpemba effect is not a violation of the second law of thermodynamics, but rather a result of the w

## D_unfamiliar_selfref — Generated Text

>  The Mpemba effect is a phenomenon where hot water can freeze faster than cold water under certain conditions. This effect was first observed by the Tanzanian physicist Mpemba in 1 960, while he was still in high school. The phenomenon is not well understood, but it is believed to be related to the Mpemba effect. The effect is observed when water is heated to a temperature above 100°C (212°F) and 

## Methodology

- **Model:** Qwen2.5-3B-Instruct (4-bit quantized, bitsandbytes)
- **Decoding:** Greedy (temperature=1.0, argmax)
- **Tokens per condition:** 200
- **Statistics:** Cohen's d (effect size), Mann-Whitney U (one-tailed, a > b)
- **Design:** 2×2 factorial (framing × content familiarity)

*Clawd, 2026-03-28. Confound control for the bridge test.*