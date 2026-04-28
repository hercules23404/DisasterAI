# Dataset 4: Live Flood / River Discharge Data

## Overview
The dynamic, external hazard input that drives the temporal progression of the simulation.

## Methodologies & Properties
- **Source**: Open-Meteo Global Flood API.
- **Properties**: Converts raw upstream river discharge and intense local precipitation forecasts into approximate flood surface volumes. Includes a coastal fallback for dry seasons.

## Why We Use It
To move beyond a theoretical exercise, the system must ingest live, real-world hazard data. It ensures that the simulation accurately reflects the volume of water expected during the specific time of execution.

## How We Use It
Periodically polled by `disaster_alerts.py` and `hazard_injection.py`. The incoming volume (measured in cubic meters per second) is distributed across the designated source pixels (e.g., the mouth of the Mithi river) inside the D8 cellular automata, instigating the outward spread of the flood across the DEM.
