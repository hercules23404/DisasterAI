# DisasterAI

DisasterAI is a data-driven disaster simulation and Multi-Agent Reinforcement Learning (MARL) environment that visualizes real-time emergency rescue operations during catastrophic urban flooding in Mumbai.

> **Note:** For full technical documentation, algorithm comparisons, architecture breakdowns, and research sources, please see the [Project Detail Overview](project_detail_overview.md).

## Quick Start Guide

**Prerequisites:** Python 3.9+

### 1. Installation

Install all required Python dependencies:

```bash
pip install -r requirements.txt
```

### 2. Launch the Command Center

Start the Streamlit dashboard to run and visualize the disaster simulation:

```bash
python3 -m streamlit run dashboard.py
```

The interactive dashboard will automatically open in your default browser at `http://localhost:8501`.

### 3. Usage

1. **Configure Simulation:** Use the left sidebar to adjust the number of victims, rescue units, and the simulation duration. The system incorporates real-time GDACS alerts and a building-floor-area population proxy.
2. **Launch:** Click the red **LAUNCH SIMULATION** button to process the flood propagation, predictive preemptive staging, and A* dispatch routes.
3. **Playback:** Use the **Animation** controls to auto-play the simulation frame-by-frame, or the **Timeline** slider to manually scrub through the disaster events. Observe the composite risk scores and idle penalty metrics.

---
*For a deeper dive into the QMIX, MCLP, and A* Pathfinding implementations, see [project_detail_overview.md](project_detail_overview.md).*
