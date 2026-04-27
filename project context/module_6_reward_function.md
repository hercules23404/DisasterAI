# Module 6: Reward Function

## Overview
Found in `reward_function.py`, this establishes the incentive structure for the Multi-Agent Reinforcement Learning (MARL) framework.

## Methodologies
- **Explicit Dense Reward Formulation**: 
  - + `rescue_base × (1 + composite_risk)` for successful rescue
  - - `time_penalty × composite_risk` per step stranded
  - - `flood_penalty` for flooded road traversals
  - - `2 × rescue_base` for victim death
  - - `idle_penalty` for inaction while high-risk victims exist

## Why We Use Them
Standard RL environments often use sparse rewards (e.g., +1 at the end of the episode). In a highly complex, dynamic environment, sparse rewards lead to catastrophic unlearning or convergence failure. This dense, risk-aware formulation provides immediate, granular feedback to the QMIX agents, heavily penalizing catastrophic outcomes while incentivizing preemption and risk mitigation.

## How We Use Them
At the end of every step, the `environment.py` orchestrator calculates the aggregate state changes (victims rescued, units stranded, health decays). It passes these deltas to the reward function, which computes a scalar reward. This scalar is fed back to the PyMARL framework to compute the Q-value gradients for policy updates.
