# Dataset 3: Demographic & Real-time Alerts

## Overview
Data that defines the human population distribution and the macro-level severity of the current natural disaster.

## Methodologies & Properties
- **Population Source**: Building-floor-area proxy methodology (Wardrop et al., 2018).
- **Alert Source**: GDACS (Global Disaster Alert and Coordination System).

## Why We Use It
Precise census microdata is rarely available at the 30m scale required for dynamic simulation. The floor-area proxy provides a mathematically sound estimation of population density. GDACS data provides live contextual multipliers, informing the system if it is dealing with a severe, fast-moving catastrophe or a slower, mild inundation.

## How We Use It
The `population_loader.py` distributes total local population estimates based on the computed internal area of the OSM building footprints. This generates a static population density matrix. This matrix is directly multiplied by the derivative of the flood volume to calculate the spawn probabilities in `victims.py`.
