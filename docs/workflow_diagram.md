# DisasterAI — System Workflow Diagram

```mermaid
flowchart TD
    %% ── DATA INGESTION ──────────────────────────────────────────
    subgraph INIT ["① Initialisation  (one-time startup)"]
        direction TB
        DEM["SRTM DEM Tiles\n30 m resolution"]
        OSM["OpenStreetMap\nroads + buildings"]
        POP["WorldPop\npopulation grid"]
        GDACS["GDACS API\nreal-time alerts"]

        DEM  --> TL["terrain_loader.py\n→ 144×144 elevation grid\n→ Relative Elevation Model\n→ NetworkX road graph"]
        OSM  --> TL
        OSM  --> BL["building_loader.py\n→ building centroids\n→ snapped to raster pixels"]
        POP  --> PL["population_loader.py\n→ population density grid"]
        GDACS --> DA["disaster_alerts.py\n→ severity multiplier\n(Green / Orange / Red)"]
    end

    INIT -->|"initial state tensors"| ENV

    %% ── SIMULATION LOOP ─────────────────────────────────────────
    subgraph ENV ["② Simulation Loop  — environment.py  (Gym step)"]
        direction TB

        FLOOD["hazard_propagation.py\nMin-Heap Priority Queue\nO(n log n)\n→ flood_depth grid"]
        PRED["flood_predictor.py\nN-step lookahead\n→ predicted_flood grid"]
        SPAWN["victims.py\nSpawn in newly flooded\nbuildings"]
        RISK["risk_scorer.py\nComposite score =\nflood depth + health decay\n+ isolation index"]
        DISPATCH["dispatch_engine.py\nHungarian Algorithm\nO(n³), n ≤ 20\ncost = dist + (1 − risk)×1000\n→ unit → victim assignments"]
        PATH["pathfinding.py\nA* Search\nFlood-aware edge weights\n(inf if depth > 0.2 m)\n→ safe road routes"]
        MOVE["Move units\nalong A* paths"]
        CHECK["Rescue / Death check\nunit @ victim → rescue\nhealth ≤ 0 → death"]
        REWARD["reward_function.py\n+ rescued × (1 + risk)\n+ preemptive arrivals\n− active victims × risk\n− deaths × 2×base\n− idle penalties"]
        STATE["State tensor  H×W×6\n[0] flood depth\n[1] predicted flood\n[2] composite risk\n[3] victim locations\n[4] unit locations\n[5] population vulnerability"]

        FLOOD --> PRED
        PRED  --> SPAWN
        SPAWN --> RISK
        RISK  --> DISPATCH
        DISPATCH --> PATH
        PATH  --> MOVE
        MOVE  --> CHECK
        CHECK --> REWARD
        REWARD --> STATE
        STATE -->|"next step"| FLOOD
    end

    %% ── PRESENTATION LAYER ──────────────────────────────────────
    subgraph DASH ["③ Dashboard  — dashboard.py  (Streamlit + Plotly + Folium)"]
        direction LR
        OPS["Operations View\nLive map animation\nKPIs + event log"]
        TECH["Technical View\nBaseline comparisons\nAblation study charts"]
        COMP["Comparison View\nAlgorithm metrics\nResponse time"]
    end

    STATE -->|"simulation history"| DASH

    %% ── BASELINES / EXPERIMENTS ─────────────────────────────────
    subgraph EXP ["④ Experiments  (offline)"]
        direction LR
        BASE["baselines.py\nGreedy Myopic / Nearest-Unit\nPriority Queue / Random"]
        ABL["ablation.py\nLookahead N = 1…7"]
        RL["rl_agent.py\nQMIX policy training\n(Stable-Baselines3)"]
    end

    ENV -.->|"controlled runs"| EXP
    EXP -.->|"results CSV → charts"| DASH

    %% ── STYLING ─────────────────────────────────────────────────
    classDef data    fill:#1e3a5f,color:#cce5ff,stroke:#4a90d9
    classDef engine  fill:#1a3a2a,color:#c3f0c8,stroke:#4caf50
    classDef dash    fill:#3a1a3a,color:#f0c3f0,stroke:#c86dd7
    classDef exp     fill:#3a2a1a,color:#f0dfc3,stroke:#d4a04a

    class DEM,OSM,POP,GDACS,TL,BL,PL,DA data
    class FLOOD,PRED,SPAWN,RISK,DISPATCH,PATH,MOVE,CHECK,REWARD,STATE engine
    class OPS,TECH,COMP dash
    class BASE,ABL,RL exp
```

## Reading the diagram

| Phase | What happens | Key files |
|---|---|---|
| **① Init** | Geospatial data is downloaded once, parsed into grids and graphs | `terrain_loader.py`, `building_loader.py`, `population_loader.py`, `disaster_alerts.py` |
| **② Sim loop** | Every Gym `step()` runs the 10-stage pipeline in strict causal order | `environment.py` orchestrates all `env/` modules |
| **③ Dashboard** | Pre-recorded simulation history replayed client-side via Plotly frames | `dashboard.py`, `views/`, `components/` |
| **④ Experiments** | Baseline and ablation runs reuse the same Gym environment | `env/baselines.py`, `env/ablation.py`, `env/rl_agent.py` |

### Causal execution order (simulation loop)

```
Flood propagates
    → future flood predicted (N-step lookahead)
        → victims spawn in newly flooded buildings
            → composite risk scores updated
                → Hungarian dispatch solves unit→victim assignment
                    → A* computes safe routes per unit
                        → units advance one step along routes
                            → rescues and deaths evaluated
                                → reward calculated
                                    → 6-channel state tensor assembled
                                        → next step begins
```
