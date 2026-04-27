# Dataset 1: Digital Elevation Model (DEM)

## Overview
The foundational 3D topographical map of the simulation region.

## Methodologies & Properties
- **Source**: NASA SRTM (Shuttle Radar Topography Mission).
- **Resolution**: 1-arc-second (~30 meters per pixel).
- **Processing**: The raw tiles are merged, cleaned of missing data (nodata holes), and strictly cropped to the Bandra-Kurla / Mithi River basin area, resulting in an internal 144x144 grid.

## Why We Use It
Accurate elevation data is the single most important factor for simulating a flood. Without a high-resolution DEM, the D8 cellular automata would have no gravity gradients to follow, rendering the hazard propagation entirely random and unrealistic.

## How We Use It
Loaded by `terrain_loader.py` at initialization. It is passed to the REM computer to identify low-lying basins and to the `hazard_propagation.py` module to define the static flow constraints.
