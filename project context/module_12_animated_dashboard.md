# Module 12: Animated Dashboard

## Overview
Implemented in `dashboard_animated.py`, this is the primary user interface and visualization frontend for the DisasterAI system.

## Methodologies
- **Streamlit Web Framework**: Provides reactive UI components for simulation control.
- **Plotly/Folium Layering**: Renders complex geographic data over interactive base maps.

## Why We Use Them
A headless simulation running in the console provides zero intuition about the spatio-temporal dynamics of the disaster. The animated dashboard is critical for stakeholders to visually verify the physics, dispatch behavior, and predictive routing. The distinct visual layers (predicted flood, risk markers, dispatch lines) translate abstract tensor operations into a command-center view.

## How We Use Them
The script imports the core `environment.py`. It provides a sidebar to tweak parameters (rainfall rate, ambulance count). Upon execution, it loops over the environment's `step()` function, extracting state arrays and converting them into colored polygons and polylines on a Folium map. It uses:
- Semi-transparent red for predicted floods.
- Color-coded markers (Green to Red) for victim risk levels.
- Dashed lines for preemptive and active dispatch routes.
