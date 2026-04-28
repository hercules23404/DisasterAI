# Module 10: Environment Orchestrator

## Overview
Located in `environment.py`, this is the master controller loop that binds all simulation components and interfaces with the RL agents.

## Methodologies
- **OpenAI Gym-style Interface**: Implements `reset()` and `step()` functions compatible with standard RL wrappers.
- **6-Channel State Tensor Generation**: Constructs a `(H, W, 6)` array capturing depth, prediction, composite risk, victim locations, unit locations, and population vulnerability.

## Why We Use Them
A complex multi-agent system requires a rigid sequence of execution to prevent race conditions and ensure causality (e.g., water must flow before victims drown, victims must spawn before ambulances dispatch). The 6-channel state tensor provides the QMIX network with a dense, comprehensive, image-like representation of the entire theater of operations.

## How We Use Them
The `step()` function executes in strict order:
1. Extract current flood depths.
2. Advance the predictive flood model.
3. Spawn new victims based on water delta.
4. Update composite risk for all victims.
5. Execute the Hungarian dispatch and pre-routing.
6. Step the A* pathfinding for active units.
7. Calculate the step reward.
8. Compile and return the new 6-channel state observation.
