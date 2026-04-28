# Dataset 5: Relative Elevation Model (REM)

## Overview
A derivative geographic dataset representing height above the nearest drainage point, rather than absolute height above sea level.

## Methodologies & Properties
- **Generation**: Computed dynamically from the DEM and OSM river geometries.
- **Technique**: KDTree nearest-neighbor interpolation maps every terrestrial pixel to the elevation of its closest river/drainage pixel, subtracting the latter from the former.

## Why We Use It
Absolute elevation is misleading for flood vulnerability. A city block at 1000m above sea level is highly vulnerable if the adjacent river is at 1002m. REM standardizes the terrain, making it instantly apparent which areas are localized basins, regardless of their absolute altitude.

## How We Use It
The REM is primarily utilized by the `pre_positioning.py` module. When solving the MCLP to place ambulance staging zones, any candidate nodes falling in the lowest percentile of the REM are automatically discarded. This guarantees that initial staging areas are geographically safe from initial spillover.
