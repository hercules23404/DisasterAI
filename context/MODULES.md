# DisasterAI — Module Reference

**Last Updated:** April 29, 2026

This document provides detailed implementation information for all 12 core modules in the DisasterAI system.

---

## Module 1: Terrain and Data Loaders

**Files:** `terrain_loader.py`, `data_loader.py`, `population_loader.py`, `building_loader.py`

### Purpose
Foundational data ingestion and alignment layer for the simulation.

### Key Algorithms
- **Geographic Data Alignment:** KDTree nearest-neighbor interpolation to align OpenStreetMap coordinates with raster grid pixels
- **Population Proxy Modeling:** Building-floor-area proxy (Wardrop et al., 2018) to estimate high-resolution population density

### Why These Methods
Accurate spatial alignment is critical for realistic routing and flood simulation. Without precise snapping of road nodes to elevation pixels, ambulances might drive through flooded areas or get stuck. The population proxy is used because high-resolution census data is rarely available in real-time during disasters.

### Implementation Details
1. Fetch DEM raster tiles and crop them to the bounding box of the Bandra-Kurla / Mithi River basin
2. Download the OSM road network via `osmnx` and convert it to a `networkx` MultiDiGraph
3. Extract building polygons to compute floor area and allocate demographic data proportionally
4. Align everything to a shared 144×144 coordinate reference system

### Key Functions
```python
class TerrainLoader:
    def load_and_crop_dem(self) -> np.ndarray
    def download_road_network(self) -> nx.MultiDiGraph
    def compute_rem(self, river_name: str) -> np.ndarray
```

---

## Module 2: Hazard Injection & Propagation

**Files:** `hazard_injection.py`, `hazard_propagation.py`

### Purpose
Core physics engine that dictates how water flows across the terrain.

### Key Algorithms
- **Min-Heap Priority-Queue Cellular Automata (D8):** Fluid dynamics approximation using a priority queue (min-heap) to spill water from lowest elevation points outward to 8 neighbors

### Why These Methods
Solving full 2D Shallow Water Equations (Navier-Stokes) takes hours per frame, completely incompatible with the millions of steps required for MARL. The Min-Heap D8 method provides topographically accurate basin filling and spilling in milliseconds, maintaining O(n log n) efficiency.

### Implementation Details
1. `hazard_injection.py` reads real-time API data (Open-Meteo) to determine water volume entering the system
2. Water volume is added to source pixels (river geometries or coastal edges)
3. `hazard_propagation.py` pushes these updated surface elevations to the min-heap
4. Water is iteratively spilled to adjacent pixels if source elevation exceeds neighbor's elevation, simulating gravity-driven flow across the DEM

### Key Functions
```python
class HazardPropagation:
    def propagate(self, flood_depth: np.ndarray, 
                  sources: List[Tuple[int, int]], 
                  continuous_inflow_volume: float) -> np.ndarray
```

### Research Foundation
- Barnes et al. (2014) — Priority-Flood algorithm
- Ma et al. (2025) — Priority queue data structure evaluation
- Gailleton et al. (2024) — GraphFlood validation

---

## Module 3: Flood Predictor

**File:** `flood_predictor.py`

### Purpose
Forward-looking extension of the D8 propagation model to anticipate future hazard states.

### Key Algorithms
- **Forward State Simulation:** Runs D8 propagation algorithm forward *k* steps on an isolated copy of simulation state
- **State Caching:** Caches predicted depth grid to avoid redundant computations, only recomputing when unit's ETA changes significantly (> 2 steps)

### Why These Methods
Static dispatch algorithms fail because roads clear at dispatch time may become flooded by arrival time. By predicting flood *k* steps ahead (where *k* is unit's estimated time of arrival), the system can dispatch and route based on arrival-time conditions, not departure-time conditions.

### Implementation Details
When dispatch decision is needed, orchestrator queries predictor with current average ETA of active fleet. Predictor clones current depth grid, steps CA physics forward, and returns expected flood map. This future map is fed into risk scorer and pathfinding modules.

### Key Functions
```python
class FloodPredictor:
    def predict_future_flood(self, current_depth: np.ndarray, 
                            steps_ahead: int) -> np.ndarray
```

---

## Module 4: Risk Scorer

**File:** `risk_scorer.py`

### Purpose
Evaluates immediate and future danger posed to simulated victims, outputting composite risk metric.

### Key Algorithms
- **Composite Risk Formula:** 
  ```
  R = α(current_flood) + β(future_flood) + γ(time_decay) + δ(pop_vulnerability)
  ```
  All terms normalized to [0, 1]
  
- **Default Weights:** α=0.25, β=0.40, γ=0.20, δ=0.15

### Why These Methods
Treating all victims equally leads to suboptimal rescue outcomes. A victim in a rapidly flooding basin is in far more danger than one in a static, shallow puddle. The heavily weighted future flood term (β=0.40) ensures the system prioritizes individuals about to be submerged, even if they appear relatively safe currently.

### Implementation Details
During each simulation step, system iterates over all active victims. It queries current flood depth and predicted future flood depth at their location. It combines these with victim's time stranded and intrinsic vulnerability (derived from local demographics) to assign a risk score. This score dynamically updates and dictates their priority in dispatch engine.

### Key Functions
```python
class RiskScorer:
    def calculate_composite_risk(self, victim: Victim, 
                                 current_depth: float,
                                 predicted_depth: float,
                                 time_stranded: int,
                                 pop_vulnerability: float) -> float
```

---

## Module 5: Dispatch Engine

**File:** `dispatch_engine.py`

### Purpose
Matches available rescue resources to victims requiring assistance.

### Key Algorithms
- **Hungarian Algorithm (Kuhn-Munkres):** Solves linear assignment problem for bipartite matching in O(n³) time
- **Composite Cost Matrix:** Edges weighted by: `travel_time × (2.0 − composite_risk)`

### Why These Methods
Greedy dispatch (nearest-unit) causes localized pile-ups and often ignores distant but high-risk victims, resulting in catastrophic loss of life. Hungarian algorithm guarantees global mathematical optimality for assignment. By modifying cost matrix to include risk, it intrinsically balances tradeoff between saving time and saving most endangered individuals.

### Implementation Details
When victims are spawned, engine compiles cost matrix between all idle units and active victims. It solves for optimal assignment that minimizes overall risk-weighted travel time. Also features preemptive staging, directing surplus units toward high-confidence predicted victim zones before victims even formally trigger rescue request.

### Key Functions
```python
def dispatch_units(idle_units: List[Unit], 
                  active_victims: List[Victim],
                  risk_scores: Dict[int, float]) -> List[Tuple[int, int]]:
    # Returns [(unit_id, victim_id), ...]
```

### Research Foundation
- Lee & Lee (2020) — MARL for disaster response
- Verma et al. (2025) — Bipartite matching for multi-robot task allocation
- van Barneveld (2015) — Risk-weighted ambulance dispatch

---

## Module 6: Reward Function

**File:** `reward_function.py`

### Purpose
Establishes incentive structure for Multi-Agent Reinforcement Learning (MARL) framework.

### Key Algorithms
- **Explicit Dense Reward Formulation:**
  - `+rescue_base × (1 + composite_risk)` for successful rescue
  - `−time_penalty × composite_risk` per step stranded
  - `−flood_penalty` for flooded road traversals
  - `−2 × rescue_base` for victim death
  - `−idle_penalty` for inaction while high-risk victims exist

### Why These Methods
Standard RL environments often use sparse rewards (e.g., +1 at episode end). In highly complex, dynamic environment, sparse rewards lead to catastrophic unlearning or convergence failure. This dense, risk-aware formulation provides immediate, granular feedback to QMIX agents, heavily penalizing catastrophic outcomes while incentivizing preemption and risk mitigation.

### Implementation Details
At end of every step, `environment.py` orchestrator calculates aggregate state changes (victims rescued, units stranded, health decays). It passes these deltas to reward function, which computes scalar reward. This scalar is fed back to PyMARL framework to compute Q-value gradients for policy updates.

### Key Functions
```python
class RewardFunction:
    def calculate_step_reward(self, env: DisasterEnvironment, 
                             prev_state: Dict) -> float
```

---

## Module 7: Pre-Positioning Module

**File:** `pre_positioning.py`

### Purpose
Determines optimal initial locations for rescue fleets before disaster peaks.

### Key Algorithms
- **Maximum Coverage Location Problem (MCLP) Heuristics:** Operations research approach aiming to maximize number of potential victims within given response time radius
- **Topological Buffering:** Excludes candidate staging sites that fall within low Relative Elevation Model (REM) zones

### Why These Methods
Random or centralized placement results in highly inefficient initial response times. If ambulances are placed in basins, they may flood on step 1. MCLP ensures fleet is geometrically dispersed to cover population centers while REM check guarantees these staging zones act as safe, elevated strongholds.

### Implementation Details
During initialization, module identifies candidate nodes on OSMnx graph. It overlays building population data to determine coverage weights. It drops any nodes in 10th percentile of elevation. It then iteratively selects subset of nodes that maximize population covered within 5-minute travel radius, spawning ambulance agents at these locations.

### Key Functions
```python
def compute_mclp_positions(road_graph: nx.Graph,
                          population_grid: np.ndarray,
                          rem: np.ndarray,
                          num_units: int) -> List[int]
```

---

## Module 8: Pathfinding

**File:** `pathfinding.py`

### Purpose
Handles point-to-point navigation of rescue units across road network.

### Key Algorithms
- **A* Search Algorithm:** Uses Euclidean distance heuristic to rapidly explore graph
- **Predictive Flood-Aware Edge Weights:** Dynamically invalidates or heavily penalizes edges based on blend of current and predicted flood depths

### Why These Methods
Dijkstra's algorithm expands radially and is too slow for real-time recalculation of hundreds of routes per step. A* limits node expansion significantly. Furthermore, static edge weights are useless in a flood; a road must be evaluated based on what its depth *will be* when unit arrives.

### Implementation Details
When unit is dispatched, pathfinder calculates effective depth map using `(1-blend)·current + blend·predicted` (where blend defaults to 0.5). Any graph edge that crosses area where this effective depth exceeds vehicle's fording limit is temporarily removed or given infinite weight. A* is then executed on this dynamic graph to yield safe route.

### Key Functions
```python
def find_safe_path(start_node: int, 
                  goal_node: int,
                  road_graph: nx.Graph,
                  current_flood: np.ndarray,
                  predicted_flood: np.ndarray,
                  blend: float = 0.5) -> List[int]
```

### Research Foundation
- Mount et al. (2019) — Real-time wayfinding during floods
- Alabbad et al. (2024) — Web-based flood routing
- Zhou et al. (2025) — Hierarchical LPA* for dynamic networks

---

## Module 9: Victim Spawn Model

**File:** `victims.py`

### Purpose
Handles generation, health tracking, and lifecycle of victims during simulation.

### Key Algorithms
- **Dynamic Probabilistic Spawning:** `P(spawn at r,c) ∝ population_density(r,c) × max(Δdepth/Δt, 0)`
- **Building-Centric Generation:** Victims strictly spawned at valid building polygon coordinates, avoiding generation inside rivers or empty fields

### Why These Methods
Random uniform spawning breaks simulation realism. Real disasters impact densely populated areas that experience sudden changes in hazard severity. By linking spawn probability to temporal derivative of flood depth and static population map, simulation generates clustered, realistic distress signals.

### Implementation Details
At each time step, model calculates difference between current and previous flood grids. It multiplies this difference grid by population density grid. Stochastic threshold is applied to determine if victim spawns at given coordinate. Once spawned, victim object is instantiated with health value (1.0) that decays dynamically based on local water depth until rescued or deceased.

### Key Functions
```python
class VictimManager:
    def spawn_victims(self, flood_delta: np.ndarray,
                     population_grid: np.ndarray,
                     building_pixels: List[Tuple[int, int]]) -> List[Victim]
    
    def update_health(self, victim: Victim, flood_depth: float) -> None
```

---

## Module 10: Environment Orchestrator

**File:** `environment.py`

### Purpose
Master controller loop that binds all simulation components and interfaces with RL agents.

### Key Algorithms
- **OpenAI Gym-style Interface:** Implements `reset()` and `step()` functions compatible with standard RL wrappers
- **6-Channel State Tensor Generation:** Constructs (H, W, 6) array capturing depth, prediction, composite risk, victim locations, unit locations, and population vulnerability

### Why These Methods
Complex multi-agent system requires rigid sequence of execution to prevent race conditions and ensure causality (e.g., water must flow before victims drown, victims must spawn before ambulances dispatch). The 6-channel state tensor provides QMIX network with dense, comprehensive, image-like representation of entire theater of operations.

### Implementation Details
The `step()` function executes in strict order:
1. Extract current flood depths
2. Advance predictive flood model
3. Spawn new victims based on water delta
4. Update composite risk for all victims
5. Execute Hungarian dispatch and pre-routing
6. Step A* pathfinding for active units
7. Calculate step reward
8. Compile and return new 6-channel state observation

### Key Functions
```python
class DisasterEnvironment:
    def reset(self) -> np.ndarray
    def step(self, actions: List[Tuple[int, int]]) -> Tuple[np.ndarray, float, bool, Dict]
    def get_state(self) -> np.ndarray  # Returns (H, W, 6) tensor
```

---

## Module 11: MARL Engine & Baselines

**Files:** `rl_agent.py`, `baselines.py`, `run_baselines.py`, `ablation.py`

### Purpose
Provides reinforcement learning training setup and comparative operational heuristics.

### Key Algorithms
- **QMIX (PyMARL):** Centralized Training Decentralized Execution (CTDE) architecture. Centralized mixing network combines individual agent Q-values monotonically to optimize joint action value
- **Ablation Studies:** Systematic disabling of system components (e.g., predictive lookahead, risk scoring) to quantify their impact

### Why These Methods
While Hungarian algorithm provides optimal assignment, it operates on pre-defined logic. QMIX allows agents to learn emergent, synergistic behaviors that human designers might miss (such as establishing unprompted perimeter patrols). Baselines and ablation studies are academically required to prove that RL and predictive components actually outperform standard deterministic operations.

### Implementation Details
- `baselines.py` executes traditional logic (Greedy, Nearest, Random) for direct comparison
- `rl_agent.py` wraps `environment.py` into epymarl framework, handling parallel rollout threads and gradient descent optimization of mixing network
- `ablation.py` runs N=1 to N=7 lookahead variations of Hungarian baseline to prove efficacy of predictive routing approach

### Baseline Algorithms
1. **Random:** Random unit-victim pairing
2. **Nearest-Unit:** Greedy nearest-neighbor assignment
3. **Greedy Myopic:** Greedy with current risk consideration
4. **Priority Queue:** Risk-sorted queue dispatch
5. **Hungarian (Ours):** Optimal bipartite matching with risk-weighted costs

### Key Functions
```python
def get_dispatch_function(mode: str) -> Callable
def run_baseline_experiment(mode: str, num_runs: int) -> pd.DataFrame
def run_ablation_study(lookahead_values: List[int]) -> pd.DataFrame
```

---

## Module 12: Animated Dashboard

**File:** `dashboard.py` (formerly `dashboard_v2.py`)

### Purpose
Primary user interface and visualization frontend for DisasterAI system.

### Key Algorithms
- **Streamlit Web Framework:** Provides reactive UI components for simulation control
- **Plotly/Folium Layering:** Renders complex geographic data over interactive base maps
- **Client-Side Animation:** Plotly `go.Frame` objects for smooth 60 FPS playback

### Why These Methods
Headless simulation running in console provides zero intuition about spatio-temporal dynamics of disaster. Animated dashboard is critical for stakeholders to visually verify physics, dispatch behavior, and predictive routing. Distinct visual layers (predicted flood, risk markers, dispatch lines) translate abstract tensor operations into command-center view.

### Implementation Details
Script imports core `environment.py`. Provides sidebar to tweak parameters (rainfall rate, ambulance count). Upon execution, loops over environment's `step()` function, extracting state arrays and converting them into colored polygons and polylines on Folium map. Uses:
- Semi-transparent red for predicted floods
- Color-coded markers (Green to Red) for victim risk levels
- Dashed lines for preemptive and active dispatch routes

### Dashboard Features
- **3-Tab Interface:**
  - Operations View: Live map animation, KPIs, event log
  - Technical View: Baseline comparison charts, ablation study
  - Comparison View: Algorithm performance metrics
  
- **Time Translation:** Steps → HH:MM:SS format (5 min/step)
- **Phase Labels:** Early Flood / Peak Crisis / Late Response
- **Event Logging:** Tracks dispatches, rescues, deaths with timestamps

### Key Functions
```python
def build_plotly_animation(terrain: TerrainLoader,
                          frames_data: List[Dict],
                          speed_ms: int) -> go.Figure

def render_technical_view() -> None
def render_operations_view() -> None
```

---

## Module Dependencies

```
dashboard.py
    ├── environment.py (orchestrator)
    │   ├── hazard_propagation.py
    │   ├── flood_predictor.py
    │   ├── dispatch_engine.py
    │   ├── pathfinding.py
    │   ├── risk_scorer.py
    │   ├── reward_function.py
    │   └── victims.py
    ├── terrain_loader.py
    ├── population_loader.py
    ├── building_loader.py
    ├── disaster_alerts.py
    └── baselines.py
```

---

## Configuration Parameters

### Simulation Config (`simulation_config.py`)
```python
STEP_DURATION_MINUTES = 5  # Real-time minutes per simulation step
FLOOD_THRESHOLD = 0.2      # Meters depth to block roads
VICTIM_HEALTH_DECAY = 0.05 # Health loss per step in water
RESCUE_RADIUS = 2          # Grid cells for rescue proximity
```

### Reward Weights
```python
RESCUE_BASE = 100
PREEMPTIVE_BONUS = 50
TIME_PENALTY = 2
FLOOD_PENALTY = 10
IDLE_PENALTY_FACTOR = 0.3
```

### Risk Weights
```python
ALPHA_CURRENT_FLOOD = 0.25
BETA_FUTURE_FLOOD = 0.40
GAMMA_TIME_DECAY = 0.20
DELTA_POP_VULNERABILITY = 0.15
```

---

## Performance Benchmarks

| Module | Typical Runtime (per step) | Complexity |
|--------|---------------------------|-----------|
| Flood Propagation | 15-30 ms | O(n log n) |
| Flood Predictor | 50-150 ms (N=2) | O(N × n log n) |
| Risk Scorer | 1-2 ms | O(k) victims |
| Dispatch Engine | 2-5 ms | O(n³) |
| Pathfinding (per unit) | 5-10 ms | O(E log V) |
| State Assembly | 3-5 ms | O(H×W×C) |
| **Total per step** | **50-100 ms** | — |

---

For architectural overview, see `ARCHITECTURE.md`.  
For research paper mapping, see `RESEARCH_FOUNDATION.md`.
