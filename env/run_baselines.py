"""
run_baselines.py
────────────────
Executes the simulation across all 5 dispatch baselines
(Random, Nearest Unit, Greedy Myopic, Priority Queue, Hungarian)
plus the DQN/QMIX RL Agent over 20 independent runs.

Logs mean ± standard deviation of:
- Total Rescued (%)
- Mean Response Time (steps)
- Peak Flood Coverage (cells)
- Simulation Score

Outputs to results/baseline_comparison.csv
"""

import numpy as np
import pandas as pd
import os
from env.terrain_loader import TerrainLoader
from env.data_loader import DataLoader
from env.hazard_injection import HazardInjector
from env.environment import DisasterEnvironment
from env.hazard_propagation import HazardPropagation
from env.building_loader import BuildingLoader
from env.population_loader import PopulationLoader
from env.baselines import (
    random_dispatch,
    nearest_unit_dispatch,
    greedy_myopic_dispatch,
    priority_queue_dispatch,
    hungarian_dispatch
)
from env.rl_agent import rl_dispatch

def run_all_baselines(n_runs=20, output_path="results/baseline_comparison.csv"):
    base_dir = os.path.dirname(os.path.dirname(__file__))
    tif_files = [
        os.path.join(base_dir, "env", "datasets", "n18_e072_1arc_v3.tif"),
        os.path.join(base_dir, "env", "datasets", "n19_e072_1arc_v3.tif")
    ]
    terrain = TerrainLoader(tif_files)
    terrain.load_and_crop_dem()
    terrain.download_road_network()
    rem = terrain.compute_rem()
    
    loader = DataLoader()
    flood_events = loader.load_flood_events()
    injector = HazardInjector(terrain.transform, rem.shape)
    source_pixels = injector.inject_from_events(flood_events)
    if not source_pixels:
        source_pixels = HazardInjector.find_coastal_sources(rem, num_sources=4)
    sources_rc = [(r, c) for r, c, _ in source_pixels]
    
    bl = BuildingLoader()
    bl.download_buildings(
        min_lon=terrain.min_lon, min_lat=terrain.min_lat,
        max_lon=terrain.max_lon, max_lat=terrain.max_lat
    )
    bl.extract_centroids(terrain.transform)
    
    pop_loader = PopulationLoader()
    pop_grid = pop_loader.load_and_crop(
        min_lon=terrain.min_lon, min_lat=terrain.min_lat,
        max_lon=terrain.max_lon, max_lat=terrain.max_lat,
        target_shape=rem.shape,
        building_loader=bl
    )
    
    modes = {
        "Random": random_dispatch,
        "Nearest Unit": nearest_unit_dispatch,
        "Greedy Myopic": greedy_myopic_dispatch,
        "Priority Queue": priority_queue_dispatch,
        "Hungarian": hungarian_dispatch,
        "DQN/QMIX": rl_dispatch
    }
    
    results = []
    
    for mode_name, dispatch_fn in modes.items():
        print(f"\\n[Baseline Evaluation] Running {mode_name} over {n_runs} episodes...")
        
        rescued_rates = []
        response_times = []
        peak_floods = []
        scores = []
        
        for run in range(n_runs):
            flood_depth = np.zeros_like(rem)
            for r, c, lvl in source_pixels:
                flood_depth[r, c] += lvl
                
            env = DisasterEnvironment(
                rem, terrain.road_graph, terrain.node_to_rc, flood_depth,
                num_units=5, num_incidents=10,
                flood_sources=sources_rc,
                population_grid=pop_grid,
                building_pixels=bl.building_pixels
            )
            propagator = HazardPropagation(rem)
            
            peak_flood = 0
            
            for step in range(100):
                env.flood_depth = propagator.propagate(env.flood_depth, sources_rc)
                current_flood = np.sum(env.flood_depth > 0.05)
                if current_flood > peak_flood:
                    peak_flood = current_flood
                    
                actions = dispatch_fn(env)
                state, reward, done, info = env.step(actions=actions)
                
                if done:
                    break
                    
            rescued_rate = info.get("people_rescued", 0) / max(1, info.get("people_in_danger", 10))
            
            rescued_rates.append(rescued_rate * 100) # Percentage
            response_times.append(env.time_step)
            peak_floods.append(peak_flood)
            scores.append(env.total_reward)
            
        results.append({
            "Dispatch Mode": mode_name,
            "Total Rescued (%)": f"{np.mean(rescued_rates):.1f} ± {np.std(rescued_rates):.1f}",
            "Mean Response Time (steps)": f"{np.mean(response_times):.1f} ± {np.std(response_times):.1f}",
            "Peak Flood Coverage (cells)": f"{np.mean(peak_floods):.1f} ± {np.std(peak_floods):.1f}",
            "Simulation Score": f"{np.mean(scores):.1f} ± {np.std(scores):.1f}"
        })
        
    df = pd.DataFrame(results)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"\\n✅ Baseline comparison results saved to {output_path}")
    return df

if __name__ == "__main__":
    run_all_baselines()
