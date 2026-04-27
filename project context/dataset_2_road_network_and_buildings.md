# Dataset 2: Road Network & Buildings

## Overview
The geometric constraint layer that defines human infrastructure, enabling routing and determining where victims can logically exist.

## Methodologies & Properties
- **Source**: OpenStreetMap (OSM) accessed via `osmnx` and building footprint shapefiles.
- **Properties**: A directed multi-graph comprising ~1,750 intersection nodes and connecting edge geometries.

## Why We Use It
Ambulances cannot drive through buildings or in straight lines over terrain; they are confined to the road network. Furthermore, victims do not randomly spawn in the middle of a river or empty fields during a flood—they are trapped in buildings.

## How We Use It
The graph is built and its nodes are aligned to the DEM coordinate grid. The pathfinding module uses this graph to calculate A* routes, heavily penalizing edges that intersect deeply flooded DEM pixels. The building polygons are used by the `building_loader.py` to anchor the victim generation algorithms.
