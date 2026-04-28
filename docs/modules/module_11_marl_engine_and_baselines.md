# Module 11: MARL Engine & Baselines

## Overview
Contains `rl_agent.py`, `baselines.py`, `run_baselines.py`, and `ablation.py`. It provides the reinforcement learning training setup and the comparative operational heuristics.

## Methodologies
- **QMIX (PyMARL)**: A Centralized Training Decentralized Execution (CTDE) architecture. A centralized mixing network combines individual agent Q-values monotonically to optimize a joint action value.
- **Ablation Studies**: Systematic disabling of system components (e.g., predictive lookahead, risk scoring) to quantify their impact.

## Why We Use Them
While the Hungarian algorithm provides optimal assignment, it operates on pre-defined logic. QMIX allows the agents to learn emergent, synergistic behaviors that human designers might miss (such as establishing unprompted perimeter patrols). The baselines and ablation studies are academically required to prove that the RL and predictive components actually outperform standard deterministic operations.

## How We Use Them
- `baselines.py` executes traditional logic (Greedy, Nearest, Random) for direct comparison.
- `rl_agent.py` wraps the `environment.py` into the epymarl framework, handling the parallel rollout threads and gradient descent optimization of the mixing network.
- `ablation.py` runs N=1 to N=7 lookahead variations of the Hungarian baseline to prove the efficacy of the predictive routing approach.
