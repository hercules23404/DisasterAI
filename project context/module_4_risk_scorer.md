# Module 4: Risk Scorer

## Overview
Defined in `risk_scorer.py`, this module evaluates the immediate and future danger posed to simulated victims, outputting a composite risk metric.

## Methodologies
- **Composite Risk Formula**: Calculates risk as a weighted sum: 
  `R = α(current_flood) + β(future_flood) + γ(time_decay) + δ(pop_vulnerability)`
- All terms are normalized to the range [0, 1].

## Why We Use Them
Treating all victims equally leads to suboptimal rescue outcomes. A victim in a rapidly flooding basin is in far more danger than one in a static, shallow puddle. The heavily weighted future flood term (β=0.40) ensures the system prioritizes individuals who are about to be submerged, even if they appear relatively safe currently.

## How We Use Them
During each simulation step, the system iterates over all active victims. It queries the current flood depth and the predicted future flood depth at their location. It combines these with the victim's time stranded and intrinsic vulnerability (derived from local demographics) to assign a risk score. This score dynamically updates and dictates their priority in the dispatch engine.
