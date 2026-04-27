# Module 7: Pre-Positioning Module

## Overview
Contained in `pre_positioning.py`, this component determines the optimal initial locations for rescue fleets before the disaster peaks.

## Methodologies
- **Maximum Coverage Location Problem (MCLP) Heuristics**: An operations research approach aiming to maximize the number of potential victims within a given response time radius.
- **Topological Buffering**: Excludes candidate staging sites that fall within low Relative Elevation Model (REM) zones.

## Why We Use Them
Random or centralized placement results in highly inefficient initial response times. If ambulances are placed in basins, they may flood on step 1. MCLP ensures the fleet is geometrically dispersed to cover the population centers while the REM check guarantees these staging zones act as safe, elevated strongholds.

## How We Use Them
During initialization, the module identifies candidate nodes on the OSMnx graph. It overlays the building population data to determine coverage weights. It drops any nodes in the 10th percentile of elevation. It then iteratively selects the subset of nodes that maximize the population covered within a 5-minute travel radius, spawning the ambulance agents at these locations.
