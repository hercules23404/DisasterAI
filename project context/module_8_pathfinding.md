# Module 8: Pathfinding

## Overview
Implemented in `pathfinding.py`, this module handles the point-to-point navigation of rescue units across the road network.

## Methodologies
- **A* Search Algorithm**: Uses a Euclidean distance heuristic to rapidly explore the graph.
- **Predictive Flood-Aware Edge Weights**: Dynamically invalidates or heavily penalizes edges based on a blend of current and predicted flood depths.

## Why We Use Them
Dijkstra's algorithm expands radially and is too slow for real-time recalculation of hundreds of routes per step. A* limits node expansion significantly. Furthermore, static edge weights are useless in a flood; a road must be evaluated based on what its depth *will be* when the unit arrives. 

## How We Use Them
When a unit is dispatched, the pathfinder calculates an effective depth map using `(1-blend)·current + blend·predicted` (where blend defaults to 0.5). Any graph edge that crosses an area where this effective depth exceeds the vehicle's fording limit is temporarily removed or given an infinite weight. A* is then executed on this dynamic graph to yield a safe route.
