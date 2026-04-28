# Module 9: Victim Spawn Model

## Overview
Defined in `victims.py`, this handles the generation, health tracking, and lifecycle of victims during the simulation.

## Methodologies
- **Dynamic Probabilistic Spawning**: `P(spawn at r,c) ∝ population_density(r,c) × max(Δdepth/Δt, 0)`
- **Building-Centric Generation**: Victims are strictly spawned at valid building polygon coordinates, avoiding generation inside rivers or empty fields.

## Why We Use Them
Random uniform spawning breaks simulation realism. Real disasters impact densely populated areas that experience sudden changes in hazard severity. By linking the spawn probability to the temporal derivative of the flood depth and the static population map, the simulation generates clustered, realistic distress signals.

## How We Use Them
At each time step, the model calculates the difference between the current and previous flood grids. It multiplies this difference grid by the population density grid. A stochastic threshold is applied to determine if a victim spawns at a given coordinate. Once spawned, a victim object is instantiated with a health value (1.0) that decays dynamically based on the local water depth until rescued or deceased.
