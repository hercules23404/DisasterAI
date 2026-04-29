# DisasterAI — Project Overview

**Last Updated:** April 29, 2026  
**Status:** Production-Ready Research Prototype  
**Location:** Mumbai, India (Bandra-Kurla / Mithi River Basin)

---

## What is DisasterAI?

DisasterAI is a **data-driven disaster simulation and Multi-Agent Reinforcement Learning (MARL) environment** that visualizes real-time emergency rescue operations during catastrophic urban flooding in Mumbai.

### Core Mission
Enable emergency response agencies to:
- **Simulate** realistic flood propagation over real terrain
- **Optimize** rescue unit dispatch using globally optimal algorithms
- **Predict** flood evolution and preemptively stage resources
- **Evaluate** different dispatch strategies through controlled experiments

---

## System Architecture

DisasterAI consists of **4 core components** working in concert:

### 1. Flood Propagation Engine
- **Algorithm:** Min-Heap Priority Queue over Digital Elevation Model (DEM)
- **Purpose:** Physically realistic water flow simulation
- **Performance:** Milliseconds per frame (vs hours for Navier-Stokes)
- **Key Feature:** Topographically accurate basin filling and spillover

### 2. Rescue Unit Dispatch Engine
- **Algorithm:** Hungarian Algorithm (Bipartite Matching via `scipy.optimize.linear_sum_assignment`)
- **Purpose:** Globally optimal unit-to-victim assignment
- **Cost Function:** `distance + (1.0 - composite_risk) × 1000`
- **Key Feature:** Balances travel time with victim mortality risk

### 3. Dynamic Pathfinding System
- **Algorithm:** A* Search with flood-aware edge weights
- **Purpose:** Real-time safe-route computation on road networks
- **Key Feature:** Dynamically sets edge weights to ∞ when roads flood (depth > 0.2m)
- **Data Source:** OpenStreetMap via OSMnx

### 4. Multi-Agent RL Environment
- **Framework:** OpenAI Gym-compatible interface
- **State Space:** 6-channel spatial tensor (H×W×6)
- **Reward Function:** Shaped to incentivize fast rescue, penalize deaths and idle time
- **Key Feature:** Supports both heuristic dispatch and RL policy training

---

## Technology Stack

| Layer | Technologies |
|-------|-------------|
| **Core Simulation** | Python 3.9+, NumPy, SciPy |
| **Geospatial** | Rasterio, GeoPandas, OSMnx, NetworkX |
| **Visualization** | Streamlit, Plotly, Folium |
| **Data Sources** | SRTM DEM, OpenStreetMap, WorldPop, GDACS API, Open-Meteo |
| **RL Framework** | Gymnasium, Stable-Baselines3 |

---

## Key Results

### Dispatch Algorithm Comparison (20 runs each)
| Algorithm | Mean Response Time | Mean Score | vs Greedy Myopic |
|-----------|-------------------|------------|------------------|
| **Hungarian (Ours)** | **19.3 min** | **735.8** | **37.5% faster, +217% score** |
| Greedy Myopic | 30.9 min | 232.0 | Baseline |
| Nearest-Unit | 30.1 min | 193.8 | -16.5% score |
| Priority Queue | 31.5 min | 23.9 | -89.7% score |
| Random | 30.5 min | 8.5 | -96.3% score |

### Lookahead Horizon Ablation
- **N=1:** 19.5 min response, 719.4 score
- **N=2:** 18.9 min response, 835.8 score ⭐ **Optimal**
- **N=3:** 18.8 min response, 789.9 score
- **N=5:** 18.3 min response, 740.3 score
- **N=7:** 19.3 min response, 800.8 score

**Finding:** N=2 or N=3 provides optimal balance between prediction accuracy and computational cost.

---

## Research Foundation

DisasterAI is grounded in **29 peer-reviewed research papers** spanning:
- Hydrological modeling and DEM-based flood simulation
- Multi-agent task allocation and bipartite matching
- Emergency vehicle routing and pathfinding
- Multi-agent reinforcement learning

**Key Papers:**
- Barnes et al. (2014) — Priority-Flood algorithm foundation
- Lee & Lee (2020) — MARL for disaster response
- Sivagnanam et al. (2024, ICML) — Hierarchical MARL for emergency responder stationing

See `RESEARCH_FOUNDATION.md` for complete paper mapping.

---

## Use Cases

1. **Emergency Response Training:** Simulate disaster scenarios for responder training
2. **Policy Evaluation:** Compare dispatch strategies under controlled conditions
3. **Resource Planning:** Determine optimal ambulance fleet size and staging locations
4. **Predictive Staging:** Test preemptive resource positioning based on flood forecasts
5. **Research Platform:** Benchmark new MARL algorithms for disaster response

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Launch interactive dashboard
python3 -m streamlit run dashboard.py
```

Dashboard opens at `http://localhost:8501`

---

## Project Structure

```
DisasterAI/
├── env/                    # Core simulation modules
│   ├── environment.py      # Main orchestrator
│   ├── hazard_propagation.py
│   ├── dispatch_engine.py
│   ├── pathfinding.py
│   └── datasets/           # DEM tiles, cached data
├── dashboard.py            # Streamlit visualization
├── dashboard_utils.py      # UI helper functions
├── results/                # Experimental data
│   ├── baseline_comparison.csv
│   ├── ablation_lookahead.csv
│   └── ieee_figures/       # Publication-ready plots
├── papers/                 # 29 research papers (PDFs)
├── context/                # This documentation
└── docs/                   # Legacy detailed docs
```

---

## Current Status

✅ **Complete:**
- All 4 core components implemented and tested
- Baseline comparison experiments (100 runs)
- Lookahead ablation study (100 runs)
- Interactive dashboard with 3-view tabs
- Research paper mapping (29 papers)

🚧 **In Progress:**
- QMIX policy training (RL agent)
- IEEE paper submission

🔮 **Future Work:**
- Multi-city generalization
- Real-time API integration for live disasters
- Mobile app for field responders

---

## Contact & Attribution

**Project:** DisasterAI — Advanced Multi-Agent Autonomous Rescue Simulation  
**Submission Date:** April 2026  
**License:** Research Prototype

For questions or collaboration inquiries, see project repository.
