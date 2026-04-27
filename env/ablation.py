"""
ablation.py
───────────
Ablation study module for Model Predictive Control (MPC) N-step lookahead.
Runs the simulation environment across various lookahead horizons (N) to
quantify the impact of predictive routing on mean rescue rate and response time.
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
from env.baselines import hungarian_dispatch

def run_lookahead_ablation(n_runs=20, output_path="results/mpc_ablation.csv"):
    """
    Runs the MPC lookahead ablation experiment for N in {1, 2, 3, 5, 7}.
    Records mean rescue rate and mean response time over `n_runs` per N.
    """
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
    
    lookahead_values = [1, 2, 3, 5, 7]
    results = []
    
    for n in lookahead_values:
        print(f"\\n[MPC Ablation] Running N={n} over {n_runs} episodes...")
        rescued_list = []
        response_time_list = []
        
        for run in range(n_runs):
            # We override the global LOOKAHEAD_STEPS dynamically for the test
            import env.environment as env_module
            env_module.LOOKAHEAD_STEPS = n
            
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
            
            episode_rescued = 0
            # Track steps taken for rescued victims
            
            for step in range(100):
                env.flood_depth = propagator.propagate(env.flood_depth, sources_rc)
                actions = hungarian_dispatch(env)
                state, reward, done, info = env.step(actions=actions)
                
                if done:
                    break
                    
            rescued_rate = info.get("people_rescued", 0) / max(1, info.get("people_in_danger", 10))
            # Approximate response time as time_step (could be refined)
            response_time = env.time_step
            
            rescued_list.append(rescued_rate)
            response_time_list.append(response_time)
            
        mean_rescue = np.mean(rescued_list)
        std_rescue = np.std(rescued_list)
        mean_time = np.mean(response_time_list)
        std_time = np.std(response_time_list)
        
        results.append({
            "Lookahead_N": n,
            "Mean_Rescue_Rate": mean_rescue,
            "Std_Rescue_Rate": std_rescue,
            "Mean_Response_Time": mean_time,
            "Std_Response_Time": std_time
        })
        
    df = pd.DataFrame(results)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"\\n✅ Ablation results saved to {output_path}")
    return df

if __name__ == "__main__":
    run_lookahead_ablation()
