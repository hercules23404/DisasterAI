# Module 3: Flood Predictor

## Overview
Located in `flood_predictor.py`, this is a forward-looking extension of the D8 propagation model designed to anticipate future hazard states.

## Methodologies
- **Forward State Simulation**: Runs the D8 propagation algorithm forward *k* steps on an isolated copy of the simulation state.
- **State Caching**: Caches the predicted depth grid to avoid redundant computations, only recomputing when a unit's ETA changes significantly (> 2 steps).

## Why We Use Them
Static dispatch algorithms fail because roads that are clear at the time of dispatch may become flooded by the time the ambulance arrives. By predicting the flood *k* steps ahead (where *k* is the unit's estimated time of arrival), the system can dispatch and route units based on arrival-time conditions, not departure-time conditions.

## How We Use Them
When a dispatch decision is needed, the orchestrator queries the predictor with the current average ETA of the active fleet. The predictor clones the current depth grid, steps the CA physics forward, and returns the expected flood map. This future map is then fed into the risk scorer and pathfinding modules.
