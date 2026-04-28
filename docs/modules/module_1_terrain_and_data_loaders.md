# Module 1: Terrain and Data Loaders

## Overview
This module consists of `terrain_loader.py`, `data_loader.py`, `population_loader.py`, and `building_loader.py`. It serves as the foundational data ingestion and alignment layer for the DisasterAI simulation.

## Methodologies
- **Geographic Data Alignment**: Uses KDTree for nearest-neighbor interpolation to align OpenStreetMap coordinates with raster grid pixels.
- **Population Proxy Modeling**: Implements the building-floor-area proxy (Wardrop et al., 2018) to estimate high-resolution population density without requiring precise census microdata.

## Why We Use Them
Accurate spatial alignment is critical for realistic routing and flood simulation. Without precise snapping of road nodes to elevation pixels, ambulances might drive through flooded areas or get stuck. The population proxy is used because high-resolution census data is rarely available in real-time during disasters.

## How We Use Them
1. Fetch DEM raster tiles and crop them to the bounding box of the Bandra-Kurla / Mithi River basin.
2. Download the OSM road network via `osmnx` and convert it to a `networkx` MultiDiGraph.
3. Extract building polygons to compute floor area and allocate demographic data proportionally.
4. Align everything to a shared 144x144 coordinate reference system.
