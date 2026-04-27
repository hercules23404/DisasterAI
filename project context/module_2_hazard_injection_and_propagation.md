# Module 2: Hazard Injection & Propagation

## Overview
Contains `hazard_injection.py` and `hazard_propagation.py`. This is the core physics engine that dictates how water flows across the terrain.

## Methodologies
- **Min-Heap Priority-Queue Cellular Automata (D8)**: A fluid dynamics approximation that uses a priority queue (min-heap) to spill water from the lowest elevation points outward to 8 neighbors.

## Why We Use Them
Solving full 2D Shallow Water Equations (Navier-Stokes) takes hours per frame, which is completely incompatible with the millions of steps required for Multi-Agent Reinforcement Learning (MARL). The Min-Heap D8 method provides topographically accurate basin filling and spilling in milliseconds, maintaining O(n log n) efficiency.

## How We Use Them
1. `hazard_injection.py` reads real-time API data (Open-Meteo) to determine the volume of water entering the system.
2. Water volume is added to source pixels (river geometries or coastal edges).
3. `hazard_propagation.py` pushes these updated surface elevations to the min-heap.
4. Water is iteratively spilled to adjacent pixels if the source elevation exceeds the neighbor's elevation, simulating gravity-driven flow across the DEM.
