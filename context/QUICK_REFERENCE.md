# DisasterAI — Quick Reference Guide

**Last Updated:** April 29, 2026

---

## Installation & Setup

### Prerequisites
```bash
# Check Python version (requires 3.9+)
python3 --version

# Install dependencies
pip install -r requirements.txt
```

### Required Datasets
All datasets are automatically downloaded on first run:
- **DEM Tiles:** SRTM 1-arc-second (n18_e072, n19_e072)
- **Road Network:** OpenStreetMap via OSMnx
- **Buildings:** OpenStreetMap building footprints
- **Population:** WorldPop (optional, uses building proxy if unavailable)

---

## Running the Simulation

### Launch Dashboard
```bash
python3 -m streamlit run dashboard.py
```

Dashboard opens at `http://localhost:8501`

### Command-Line Simulation
```python
from env.environment import DisasterEnvironment
from env.terrain_loader import TerrainLoader

# Load terrain
terrain = TerrainLoader(["env/datasets/n18_e072_1arc_v3.tif"])
terrain.load_and_crop_dem()
terrain.download_road_network()
rem = terrain.compute_rem(river_name="Ulhas River")

# Initialize environment
env = DisasterEnvironment(
    rem=rem,
    road_graph=terrain.road_graph,
    node_to_rc=terrain.node_to_rc,
    flood_depth=np.zeros_like(rem),
    num_units=5,
    num_incidents=10
)

# Run simulation
for step in range(30):
    actions = []  # Your dispatch logic here
    state, reward, done, info = env.step(actions)
    if done:
        break
```

---

## Key Configuration Parameters

### Simulation Config (`env/simulation_config.py`)
```python
STEP_DURATION_MINUTES = 5      # Real-time minutes per step
FLOOD_THRESHOLD = 0.2          # Meters depth to block roads
VICTIM_HEALTH_DECAY = 0.05     # Health loss per step in water
RESCUE_RADIUS = 2              # Grid cells for rescue proximity
```

### Reward Weights (`env/reward_function.py`)
```python
RESCUE_BASE = 100              # Base reward for rescue
PREEMPTIVE_BONUS = 50          # Bonus for preemptive staging
TIME_PENALTY = 2               # Penalty per step victim waits
FLOOD_PENALTY = 10             # Penalty for driving through flood
IDLE_PENALTY_FACTOR = 0.3      # Penalty for idle units
```

### Risk Weights (`env/risk_scorer.py`)
```python
ALPHA_CURRENT_FLOOD = 0.25     # Weight for current flood depth
BETA_FUTURE_FLOOD = 0.40       # Weight for predicted flood depth
GAMMA_TIME_DECAY = 0.20        # Weight for time stranded
DELTA_POP_VULNERABILITY = 0.15 # Weight for population vulnerability
```

---

## Common Tasks

### Run Baseline Comparison
```bash
python3 env/run_baselines.py
```

Output: `results/baseline_comparison.csv`

### Run Ablation Study
```bash
python3 env/ablation.py
```

Output: `results/ablation_lookahead.csv`

### Generate Figures
```bash
python3 generate_figures.py
```

Output: `results/ieee_figures/*.png`

### Run All Experiments
```bash
python3 run_all_experiments.py
```

Runs both baseline and ablation studies sequentially.

---

## Dashboard Controls

### Sidebar Parameters
- **Duration:** 5-60 minutes (simulation length)
- **Number of Victims:** 5-20 (spawned dynamically)
- **Rescue Units:** 3-10 (initial fleet size)
- **Dispatch Algorithm:** Hungarian / Greedy / Nearest / Priority Queue / Random
- **Animation Speed:** Slow / Normal / Fast

### Tab Views
1. **Operations View:** Live map animation, KPIs, event log
2. **Technical View:** Baseline comparison charts, ablation study
3. **Comparison View:** Algorithm performance metrics

### Map Layers
- 🔵 Blue heatmap: Current flood extent
- 🟠 Orange/Red heatmap: Predicted flood (t+N)
- 🔴 Red lines: Blocked roads (depth > 0.2m)
- ⚪ White lines: Open roads
- 🟢 Green lines: Rescue routes (risk-colored)
- 🟢🟠🔴 Dots: Victims (color = risk level)
- 🔵 Cyan dots: Rescue units
- 🟠 Orange circles: Preemptive staging zones

---

## File Structure

```
DisasterAI/
├── env/                          # Core simulation modules
│   ├── environment.py            # Main orchestrator (Gym interface)
│   ├── hazard_propagation.py    # Flood engine (Priority-Queue D8)
│   ├── dispatch_engine.py       # Hungarian algorithm dispatch
│   ├── pathfinding.py           # A* with flood-aware weights
│   ├── flood_predictor.py       # N-step lookahead prediction
│   ├── risk_scorer.py           # Composite risk calculation
│   ├── reward_function.py       # MARL reward shaping
│   ├── victims.py               # Victim spawn and health model
│   ├── terrain_loader.py        # DEM and road network loading
│   ├── population_loader.py     # Building-based population proxy
│   ├── building_loader.py       # OSM building extraction
│   ├── disaster_alerts.py       # GDACS API integration
│   ├── baselines.py             # Baseline dispatch algorithms
│   ├── run_baselines.py         # Baseline experiment runner
│   ├── ablation.py              # Lookahead ablation study
│   ├── rl_agent.py              # QMIX RL agent (WIP)
│   └── datasets/                # DEM tiles, cached data
├── dashboard.py                  # Streamlit visualization
├── dashboard_utils.py            # UI helper functions
├── results/                      # Experimental data
│   ├── baseline_comparison.csv  # 100 baseline runs
│   ├── ablation_lookahead.csv   # 100 ablation runs
│   └── ieee_figures/            # Publication-ready plots
├── papers/                       # 29 research papers (PDFs)
├── context/                      # Human-readable documentation
│   ├── PROJECT_OVERVIEW.md      # High-level what/why/how
│   ├── ARCHITECTURE.md          # System design & components
│   ├── MODULES.md               # Detailed module reference
│   ├── RESEARCH_FOUNDATION.md   # 29 papers mapped to components
│   ├── RESULTS_SUMMARY.md       # Experimental results
│   └── QUICK_REFERENCE.md       # This file
├── ai_context/                   # AI-optimized documentation
│   └── (structured JSON/YAML for AI tools)
└── docs/                         # Legacy detailed docs
    ├── modules/                  # Original module docs
    ├── datasets/                 # Dataset descriptions
    └── dev/                      # Development logs
```

---

## Troubleshooting

### Issue: Dashboard won't start
```bash
# Check Streamlit installation
pip install --upgrade streamlit

# Check port availability
lsof -i :8501

# Try different port
streamlit run dashboard.py --server.port 8502
```

### Issue: DEM tiles not found
```bash
# Manually download SRTM tiles
# Place in: env/datasets/n18_e072_1arc_v3.tif
# Download from: https://earthexplorer.usgs.gov/
```

### Issue: OSMnx download fails
```bash
# Check internet connection
# OSMnx requires active connection to OpenStreetMap API
# Retry after a few minutes if rate-limited
```

### Issue: Slow simulation
```bash
# Reduce grid size in terrain_loader.py
# Reduce number of units/victims in dashboard sidebar
# Disable flood prediction (set N=1)
```

### Issue: Memory error
```bash
# Reduce simulation duration
# Reduce grid resolution
# Close other applications
```

---

## Performance Optimization

### Speed Up Simulation
1. **Reduce lookahead:** N=1 instead of N=2 (30% faster)
2. **Smaller grid:** 100×100 instead of 144×144 (40% faster)
3. **Fewer units:** 5 instead of 10 (25% faster)
4. **Disable visualization:** Run headless experiments

### Reduce Memory Usage
1. **Clear cache:** Delete `cache/` folder
2. **Reduce history:** Limit stored frames in dashboard
3. **Disable event logging:** Comment out event log in environment.py

---

## API Reference

### Environment Interface
```python
class DisasterEnvironment:
    def reset(self) -> np.ndarray:
        """Reset environment, return initial state (H, W, 6)"""
    
    def step(self, actions: List[Tuple[int, int]]) -> Tuple:
        """Execute actions, return (state, reward, done, info)"""
    
    def get_state(self) -> np.ndarray:
        """Return current 6-channel state tensor"""
```

### Dispatch Functions
```python
def heuristic_dispatch(env: DisasterEnvironment) -> List[Tuple[int, int]]:
    """Hungarian algorithm with risk-weighted costs"""

def greedy_dispatch(env: DisasterEnvironment) -> List[Tuple[int, int]]:
    """Greedy myopic dispatch"""

def nearest_dispatch(env: DisasterEnvironment) -> List[Tuple[int, int]]:
    """Nearest-unit dispatch"""
```

### Pathfinding
```python
def find_safe_path(
    start_node: int,
    goal_node: int,
    road_graph: nx.Graph,
    current_flood: np.ndarray,
    predicted_flood: np.ndarray,
    blend: float = 0.5
) -> List[int]:
    """A* with flood-aware edge weights"""
```

---

## Data Sources

### Terrain Data
- **Source:** SRTM 1-arc-second DEM
- **Resolution:** 30m per pixel
- **Coverage:** Mumbai (18-20°N, 72-73°E)
- **Format:** GeoTIFF

### Road Network
- **Source:** OpenStreetMap via OSMnx
- **Type:** Drivable roads (motorway, trunk, primary, secondary, tertiary)
- **Format:** NetworkX MultiDiGraph

### Population
- **Source:** WorldPop / Building-floor-area proxy
- **Resolution:** Aligned to DEM (30m)
- **Method:** Wardrop et al. (2018) building proxy

### Disaster Alerts
- **Source:** GDACS API
- **Type:** Flood alerts for India
- **Update:** Real-time (fetched on dashboard launch)

---

## Citation

If you use DisasterAI in your research, please cite:

```bibtex
@misc{disasterai2026,
  title={DisasterAI: Multi-Agent Reinforcement Learning for Emergency Response Optimization},
  author={[Your Name]},
  year={2026},
  note={College Project Submission}
}
```

---

## Support & Contact

- **Documentation:** See `context/` folder
- **Issues:** Check `docs/dev/` for known issues
- **Research Papers:** See `papers/` folder and `context/RESEARCH_FOUNDATION.md`

---

## Quick Commands Cheat Sheet

```bash
# Launch dashboard
streamlit run dashboard.py

# Run baseline comparison
python3 env/run_baselines.py

# Run ablation study
python3 env/ablation.py

# Generate figures
python3 generate_figures.py

# Run all experiments
python3 run_all_experiments.py

# Check dependencies
pip list | grep -E "streamlit|numpy|scipy|networkx|osmnx"

# Clear cache
rm -rf cache/

# View results
cat results/baseline_comparison.csv
cat results/ablation_lookahead.csv
```

---

For detailed architecture, see `ARCHITECTURE.md`.  
For module reference, see `MODULES.md`.  
For research foundation, see `RESEARCH_FOUNDATION.md`.
