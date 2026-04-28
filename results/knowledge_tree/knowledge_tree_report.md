# Graph Report - /Users/hercules/DisasterAI  (2026-04-28)

## Corpus Check
- 33 files · ~23,990 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 392 nodes · 928 edges · 20 communities detected
- Extraction: 48% EXTRACTED · 52% INFERRED · 0% AMBIGUOUS · INFERRED: 482 edges (avg confidence: 0.6)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Module-0 (82 nodes)|Module-0 (82 nodes)]]
- [[_COMMUNITY_Module-1 (66 nodes)|Module-1 (66 nodes)]]
- [[_COMMUNITY_Module-2 (51 nodes)|Module-2 (51 nodes)]]
- [[_COMMUNITY_Module-3 (50 nodes)|Module-3 (50 nodes)]]
- [[_COMMUNITY_Module-4 (28 nodes)|Module-4 (28 nodes)]]
- [[_COMMUNITY_Module-5 (25 nodes)|Module-5 (25 nodes)]]
- [[_COMMUNITY_Module-6 (20 nodes)|Module-6 (20 nodes)]]
- [[_COMMUNITY_Module-7 (13 nodes)|Module-7 (13 nodes)]]
- [[_COMMUNITY_Module-8 (11 nodes)|Module-8 (11 nodes)]]
- [[_COMMUNITY_Module-9 (8 nodes)|Module-9 (8 nodes)]]
- [[_COMMUNITY_Module-10 (7 nodes)|Module-10 (7 nodes)]]
- [[_COMMUNITY_Module-11 (6 nodes)|Module-11 (6 nodes)]]
- [[_COMMUNITY_Module-12 (6 nodes)|Module-12 (6 nodes)]]
- [[_COMMUNITY_Module-13 (4 nodes)|Module-13 (4 nodes)]]
- [[_COMMUNITY_Module-14 (4 nodes)|Module-14 (4 nodes)]]
- [[_COMMUNITY_Module-15 (3 nodes)|Module-15 (3 nodes)]]
- [[_COMMUNITY_Module-16 (2 nodes)|Module-16 (2 nodes)]]
- [[_COMMUNITY_Module-17 (2 nodes)|Module-17 (2 nodes)]]
- [[_COMMUNITY_Module-19 (1 nodes)|Module-19 (1 nodes)]]
- [[_COMMUNITY_Module-20 (1 nodes)|Module-20 (1 nodes)]]

## God Nodes (most connected - your core abstractions)
1. `DisasterEnvironment` - 56 edges
2. `HazardPropagation` - 47 edges
3. `BuildingLoader` - 30 edges
4. `IncidentManager` - 30 edges
5. `Incident` - 29 edges
6. `PopulationLoader` - 28 edges
7. `DataLoader` - 27 edges
8. `DispatchEngine` - 27 edges
9. `FloodPredictor` - 27 edges
10. `RiskScorer` - 27 edges
11. `TerrainLoader` - 27 edges
12. `RewardFunction` - 26 edges
13. `HazardInjector` - 25 edges
14. `Ambulance` - 25 edges
15. `Firefighter` - 24 edges

## Surprising Connections (you probably didn't know these)
- `load_population()` --calls--> `PopulationLoader`  [INFERRED]
  dashboard_animated.py → env/population_loader.py
- `load_buildings()` --calls--> `BuildingLoader`  [INFERRED]
  dashboard_animated.py → env/building_loader.py
- `main()` --calls--> `DisasterEnvironment`  [INFERRED]
  dashboard_animated.py → env/environment.py
- `main()` --calls--> `HazardPropagation`  [INFERRED]
  dashboard_animated.py → env/hazard_propagation.py
- `dashboard_animated.py ───────────────────── Smooth-animation version of the Disa` --uses--> `HazardPropagation`  [INFERRED]
  dashboard_animated.py → env/hazard_propagation.py
- `dashboard_animated.py ───────────────────── Smooth-animation version of the Disa` --uses--> `DisasterEnvironment`  [INFERRED]
  dashboard_animated.py → env/environment.py
- `dashboard_animated.py ───────────────────── Smooth-animation version of the Disa` --uses--> `DisasterAlertService`  [INFERRED]
  dashboard_animated.py → env/disaster_alerts.py
- `Load building-density population raster, sized to our bbox.` --uses--> `HazardPropagation`  [INFERRED]
  dashboard_animated.py → env/hazard_propagation.py
- `Load building-density population raster, sized to our bbox.` --uses--> `DisasterEnvironment`  [INFERRED]
  dashboard_animated.py → env/environment.py
- `Load building-density population raster, sized to our bbox.` --uses--> `DisasterAlertService`  [INFERRED]
  dashboard_animated.py → env/disaster_alerts.py

## Communities

### Community 0 - "Module-0 (82 nodes)"
Cohesion: 0.07
Nodes (55): load_flood_sources(), load_terrain_and_roads(), dashboard_animated.py ───────────────────── Smooth-animation version of the Disa, Load building-density population raster, sized to our bbox., Download OSMnx building footprints and extract centroid pixels., Fetch live flood alerts from GDACS., Converts all simulation frames into a Plotly figure with go.Frame objects., load_flood_sources() (+47 more)

### Community 1 - "Module-1 (66 nodes)"
Cohesion: 0.11
Nodes (41): DispatchEngine, Hungarian dispatch on composite risk scores + preemptive staging     for predict, Assigns idle units to active victims using Hungarian algorithm         on a risk, environment.py ────────────── Central MARL environment orchestrator defining the, Map hospital pixel positions to nearest road nodes., Convert grid (row, col) to (lat, lon) using rasterio transform., Convert (lat, lon) back to (row, col) — inverse of grid_to_latlon.         For I, Returns set of (row, col) for all active victims. (+33 more)

### Community 2 - "Module-2 (51 nodes)"
Cohesion: 0.06
Nodes (38): calculate_baseline_stats(), calculate_lookahead_stats(), cells_to_basin_percent(), cells_to_km2(), EventLogger, format_eta_minutes(), format_flood_extent(), format_response_time() (+30 more)

### Community 3 - "Module-3 (50 nodes)"
Cohesion: 0.07
Nodes (13): Identifies predicted future victim zones for preemptive staging.          Scores, DisasterEnvironment, Optimized A* pathfinding precisely matching physical OSMnx road networks.     Dy, route_on_road_network(), True if the unit is at capacity and must go to a hospital., Dispatches unit to a target via calculated node path., Moves the unit along the path based on its speed., Completes the assignment and reverts to idle. (+5 more)

### Community 4 - "Module-4 (28 nodes)"
Cohesion: 0.09
Nodes (14): DisasterPyMARLEnv, Returns the partial observation for a single agent.         Includes local flood, Returns the shape of the observation., Returns the global state for Centralized Training with Decentralized Execution (, Returns the shape of the global state., Returns the available actions for all agents., Returns a list of length n_actions with 1s and 0s indicating available actions., Returns the total number of actions an agent could ever take. (+6 more)

### Community 5 - "Module-5 (25 nodes)"
Cohesion: 0.12
Nodes (16): build_plotly_animation(), heuristic_dispatch(), load_buildings(), load_disaster_alerts(), load_population(), main(), rc_to_latlon(), DisasterAlert (+8 more)

### Community 6 - "Module-6 (20 nodes)"
Cohesion: 0.1
Nodes (18): get_dispatch_function(), greedy_myopic_dispatch(), hungarian_dispatch(), log_episode_metrics(), nearest_unit_dispatch(), priority_queue_dispatch(), random_dispatch(), baselines.py ──────────── Baseline dispatch strategies for comparison / ablation (+10 more)

### Community 7 - "Module-7 (13 nodes)"
Cohesion: 0.15
Nodes (4): DisasterAI — Figure Generation Script (Revised) Generates Figs 1–7 per paper han, save(), plot_baseline_comparison(), plot_lookahead_ablation()

### Community 8 - "Module-8 (11 nodes)"
Cohesion: 0.22
Nodes (5): data_sources.py ─────────────── Unified data ingestion module for the DisasterAI, Loads static historical validation data for model calibration.         Reads the, Attempts to load live operational data.         Primary: IMD 0.25° Gridded Rainf, Stub for IMD API integration. In production, this requires an API key         an, UnifiedDataSourceLoader

### Community 9 - "Module-9 (8 nodes)"
Cohesion: 0.32
Nodes (7): compute_risk_map(), mclp_greedy_placement(), pre_positioning.py ────────────────── Pre-disaster resource staging using the Ma, Main entry point for MCLP pre-disaster staging., Builds a pre-disaster risk raster., Maximum Coverage Location Problem (MCLP) greedy approximation.     Places units, run_pre_positioning()

### Community 10 - "Module-10 (7 nodes)"
Cohesion: 0.33
Nodes (6): edge_weight(), midpoint(), Predictive edge weight for A* routing.      Effective depth = (1-blend)*current, Compute the midpoint between two nodes (for grid lookup)., A* pathfinding with blended current + predicted flood depth.      A road that wi, route_predictive()

### Community 11 - "Module-11 (6 nodes)"
Cohesion: 0.33
Nodes (4): building_loader.py ────────────────── Downloads real building footprints from Op, Estimate relative population weight for each building based on         ground-fo, Parse a potentially messy OSM tag value to float., _safe_float()

### Community 12 - "Module-12 (6 nodes)"
Cohesion: 0.4
Nodes (4): _cache_path(), _fetch_single_with_fallback(), data_loader.py ────────────── Ingests live river discharge data from the Open-Me, Fetches river discharge for one coordinate.     Order of operations:       1. Tr

### Community 13 - "Module-13 (4 nodes)"
Cohesion: 0.5
Nodes (2): Returns predicted flood depth grid after k steps.         Does NOT mutate curren, Convenience wrapper — predict at unit arrival time.

### Community 14 - "Module-14 (4 nodes)"
Cohesion: 0.5
Nodes (3): hazard_propagation.py ───────────────────── Min-Heap based topographic flow accu, Runs the propagation model forward n_steps WITHOUT modifying the     actual simu, simulate_lookahead()

### Community 15 - "Module-15 (3 nodes)"
Cohesion: 0.67
Nodes (1): plot_ieee.py ──────────── Generates IEEE-standard figures for the DisasterAI res

### Community 16 - "Module-16 (2 nodes)"
Cohesion: 1.0
Nodes (1): DisasterAI — Knowledge Tree via graphify Extracts code graph, clusters communiti

### Community 17 - "Module-17 (2 nodes)"
Cohesion: 1.0
Nodes (1): Flood physics configuration for the Mithi River / BKC basin, Mumbai.  Constants

### Community 19 - "Module-19 (1 nodes)"
Cohesion: 1.0
Nodes (1): Map GDACS alert level to a victim severity multiplier.

### Community 20 - "Module-20 (1 nodes)"
Cohesion: 1.0
Nodes (1): Finds the lowest-elevation pixels as natural flood injection points.         The

## Knowledge Gaps
- **116 isolated node(s):** `DisasterAI — Knowledge Tree via graphify Extracts code graph, clusters communiti`, `dashboard_utils.py ────────────────── Utility functions for the DisasterAI dashb`, `Convert step number to HH:MM:SS format.`, `Convert step to elapsed time string like 'T+00:47:00'.`, `Return disaster phase based on elapsed time.` (+111 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Module-13 (4 nodes)`** (4 nodes): `.predict()`, `.predict_at_eta()`, `Returns predicted flood depth grid after k steps.         Does NOT mutate curren`, `Convenience wrapper — predict at unit arrival time.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Module-15 (3 nodes)`** (3 nodes): `plot_ieee.py ──────────── Generates IEEE-standard figures for the DisasterAI res`, `set_ieee_style()`, `plot_ieee.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Module-16 (2 nodes)`** (2 nodes): `build_knowledge_tree.py`, `DisasterAI — Knowledge Tree via graphify Extracts code graph, clusters communiti`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Module-17 (2 nodes)`** (2 nodes): `simulation_config.py`, `Flood physics configuration for the Mithi River / BKC basin, Mumbai.  Constants`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Module-19 (1 nodes)`** (1 nodes): `Map GDACS alert level to a victim severity multiplier.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Module-20 (1 nodes)`** (1 nodes): `Finds the lowest-elevation pixels as natural flood injection points.         The`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.