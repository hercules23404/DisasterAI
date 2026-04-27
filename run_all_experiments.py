"""
run_all_experiments.py
──────────────────────
Comprehensive experiment runner for the DisasterAI MARL simulation.

Sequence:
  1. Runs env/run_baselines.py logic — all 5 dispatch modes
     (Random, Nearest-Unit, Greedy Myopic, Priority Queue, Hungarian)
     for 20 independent simulation runs each.
  2. Runs env/ablation.py logic — MPC lookahead N ∈ {1, 2, 3, 5, 7}
     for 20 runs each (using Hungarian dispatch).
  3. Creates results/ directory if it doesn't exist.
  4. Outputs two CSVs:
       results/baseline_comparison.csv
       results/ablation_lookahead.csv
  5. Prints a summary table to console with mean ± std for each
     mode / N across all 20 runs.

Per-run metrics logged:
  - total_rescued       : count of victims successfully rescued
  - mean_response_time  : average timestep at which rescues occurred
  - peak_flood_cells    : max number of flooded cells at any point
  - simulation_score    : cumulative reward from the environment

Each individual run is wrapped in try/except so a single failure
does not abort the entire experiment batch.

Usage:
    python run_all_experiments.py
"""

import sys
import os
import time
import traceback
import numpy as np
import pandas as pd

# ── Ensure the project root is on the Python path ────────────────────
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

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
    hungarian_dispatch,
)

# ── Experiment configuration ─────────────────────────────────────────
N_RUNS = 20
SIM_STEPS = 100          # timesteps per episode
NUM_UNITS = 5
NUM_INCIDENTS = 10
RESULTS_DIR = os.path.join(PROJECT_ROOT, "results")

DISPATCH_MODES = {
    "Random":         random_dispatch,
    "Nearest-Unit":   nearest_unit_dispatch,
    "Greedy Myopic":  greedy_myopic_dispatch,
    "Priority Queue": priority_queue_dispatch,
    "Hungarian":      hungarian_dispatch,
}

ABLATION_N_VALUES = [1, 2, 3, 5, 7]


# =====================================================================
#  Helper: load terrain once (expensive I/O — reused across all runs)
# =====================================================================

def load_terrain():
    """Loads the DEM, road network, and flood sources once."""
    tif_files = [
        os.path.join(PROJECT_ROOT, "env", "datasets", "n18_e072_1arc_v3.tif"),
        os.path.join(PROJECT_ROOT, "env", "datasets", "n19_e072_1arc_v3.tif"),
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

    # Load buildings
    bl = BuildingLoader()
    bl.download_buildings(
        min_lon=terrain.min_lon, min_lat=terrain.min_lat,
        max_lon=terrain.max_lon, max_lat=terrain.max_lat
    )
    bl.extract_centroids(terrain.transform)

    # Load population
    pop_loader = PopulationLoader()
    pop_grid = pop_loader.load_and_crop(
        min_lon=terrain.min_lon, min_lat=terrain.min_lat,
        max_lon=terrain.max_lon, max_lat=terrain.max_lat,
        target_shape=rem.shape,
        building_loader=bl
    )

    return rem, terrain.road_graph, terrain.node_to_rc, source_pixels, pop_grid, bl.building_pixels


# =====================================================================
#  Core: run a single simulation episode
# =====================================================================

def run_single_episode(rem, road_graph, node_to_rc, source_pixels,
                       pop_grid, building_pixels,
                       dispatch_fn, lookahead_n=None):
    """
    Runs one full episode and returns a metrics dict.

    Parameters
    ----------
    dispatch_fn : callable
        Dispatch strategy function (from env.baselines).
    lookahead_n : int | None
        If provided, overrides the global LOOKAHEAD_STEPS for this run.

    Returns
    -------
    dict with keys: total_rescued, mean_response_time, peak_flood_cells,
                    simulation_score
    """
    import env.environment as env_mod
    original_lookahead = env_mod.LOOKAHEAD_STEPS
    if lookahead_n is not None:
        env_mod.LOOKAHEAD_STEPS = lookahead_n

    try:
        # Fresh flood depth per episode
        flood_depth = np.zeros_like(rem)
        for r, c, lvl in source_pixels:
            flood_depth[r, c] += lvl

        sources_rc = [(r, c) for r, c, _ in source_pixels]

        env = DisasterEnvironment(
            rem, road_graph, node_to_rc, flood_depth,
            num_units=NUM_UNITS,
            num_incidents=NUM_INCIDENTS,
            flood_sources=sources_rc,
            population_grid=pop_grid,
            building_pixels=building_pixels
        )
        propagator = HazardPropagation(rem)

        peak_flood_cells = 0
        rescue_steps = []      # timesteps at which each rescue happened
        prev_resolved = 0

        for step in range(SIM_STEPS):
            # Propagate flood
            env.flood_depth = propagator.propagate(env.flood_depth, sources_rc)

            # Track peak flood extent
            flooded_now = int(np.sum(env.flood_depth > 0.05))
            if flooded_now > peak_flood_cells:
                peak_flood_cells = flooded_now

            # Dispatch
            actions = dispatch_fn(env)
            state, reward, done, info = env.step(actions=actions)

            # Track newly rescued victims this step
            currently_resolved = sum(
                1 for inc in env.incident_manager.incidents if inc.is_resolved
            )
            new_rescues = currently_resolved - prev_resolved
            if new_rescues > 0:
                rescue_steps.extend([step] * new_rescues)
            prev_resolved = currently_resolved

            if done:
                break

        total_rescued = sum(
            1 for inc in env.incident_manager.incidents if inc.is_resolved
        )
        mean_response_time = (
            float(np.mean(rescue_steps)) if rescue_steps
            else float(env.time_step)
        )

        return {
            "total_rescued": total_rescued,
            "mean_response_time": round(mean_response_time, 2),
            "peak_flood_cells": peak_flood_cells,
            "simulation_score": round(env.total_reward, 2),
        }

    finally:
        # Always restore original lookahead so it doesn't leak
        env_mod.LOOKAHEAD_STEPS = original_lookahead


# =====================================================================
#  Experiment 1: Baseline Comparison  (mirrors env/run_baselines.py)
# =====================================================================

def run_baseline_experiment(rem, road_graph, node_to_rc, source_pixels, pop_grid, building_pixels):
    """
    Runs all 5 dispatch modes × N_RUNS and writes
    results/baseline_comparison.csv

    CSV columns: run_id, mode, total_rescued, mean_response_time,
                 peak_flood_cells, simulation_score
    """
    rows = []

    for mode_name, dispatch_fn in DISPATCH_MODES.items():
        print(f"\n{'='*60}")
        print(f"  BASELINE: {mode_name}  ({N_RUNS} runs)")
        print(f"{'='*60}")

        for run_id in range(1, N_RUNS + 1):
            try:
                metrics = run_single_episode(
                    rem, road_graph, node_to_rc, source_pixels, pop_grid, building_pixels, dispatch_fn
                )
                rows.append({
                    "run_id": run_id,
                    "mode": mode_name,
                    **metrics,
                })
                status = (
                    f"✓ rescued={metrics['total_rescued']}, "
                    f"score={metrics['simulation_score']}"
                )
            except Exception:
                tb = traceback.format_exc()
                print(f"  ✗ Run {run_id} FAILED:\n{tb}")
                rows.append({
                    "run_id": run_id,
                    "mode": mode_name,
                    "total_rescued": np.nan,
                    "mean_response_time": np.nan,
                    "peak_flood_cells": np.nan,
                    "simulation_score": np.nan,
                })
                status = "✗ FAILED"

            print(f"  Run {run_id:>2}/{N_RUNS}  {status}")

    df = pd.DataFrame(rows)
    path = os.path.join(RESULTS_DIR, "baseline_comparison.csv")
    df.to_csv(path, index=False)
    print(f"\n📄 Saved: {path}")
    return df


# =====================================================================
#  Experiment 2: MPC Lookahead Ablation  (mirrors env/ablation.py)
# =====================================================================

def run_ablation_experiment(rem, road_graph, node_to_rc, source_pixels, pop_grid, building_pixels):
    """
    Runs Hungarian dispatch with N ∈ {1,2,3,5,7} lookahead × N_RUNS
    and writes results/ablation_lookahead.csv

    CSV columns: run_id, N_value, total_rescued, mean_response_time,
                 peak_flood_cells, simulation_score
    """
    rows = []

    for n_val in ABLATION_N_VALUES:
        print(f"\n{'='*60}")
        print(f"  ABLATION: Lookahead N={n_val}  ({N_RUNS} runs)")
        print(f"{'='*60}")

        for run_id in range(1, N_RUNS + 1):
            try:
                metrics = run_single_episode(
                    rem, road_graph, node_to_rc, source_pixels,
                    pop_grid, building_pixels,
                    hungarian_dispatch,
                    lookahead_n=n_val,
                )
                rows.append({
                    "run_id": run_id,
                    "N_value": n_val,
                    **metrics,
                })
                status = (
                    f"✓ rescued={metrics['total_rescued']}, "
                    f"score={metrics['simulation_score']}"
                )
            except Exception:
                tb = traceback.format_exc()
                print(f"  ✗ Run {run_id} FAILED:\n{tb}")
                rows.append({
                    "run_id": run_id,
                    "N_value": n_val,
                    "total_rescued": np.nan,
                    "mean_response_time": np.nan,
                    "peak_flood_cells": np.nan,
                    "simulation_score": np.nan,
                })
                status = "✗ FAILED"

            print(f"  Run {run_id:>2}/{N_RUNS}  {status}")

    df = pd.DataFrame(rows)
    path = os.path.join(RESULTS_DIR, "ablation_lookahead.csv")
    df.to_csv(path, index=False)
    print(f"\n📄 Saved: {path}")
    return df


# =====================================================================
#  Console Summary — mean ± std per mode / N
# =====================================================================

METRIC_COLS = [
    "total_rescued",
    "mean_response_time",
    "peak_flood_cells",
    "simulation_score",
]

METRIC_LABELS = {
    "total_rescued":       "Total Rescued",
    "mean_response_time":  "Mean Resp. Time",
    "peak_flood_cells":    "Peak Flood Cells",
    "simulation_score":    "Sim. Score",
}


def print_summary(df, title, group_col):
    """
    Prints mean ± std per group for all 4 metrics.

    Parameters
    ----------
    df : pd.DataFrame
        Results dataframe.
    title : str
        Section title.
    group_col : str
        Column to group by ('mode' or 'N_value').
    """
    print(f"\n{'━'*78}")
    print(f"  {title}")
    print(f"{'━'*78}")

    # Header
    header = f"  {'Group':<18}"
    for m in METRIC_COLS:
        label = METRIC_LABELS[m]
        header += f" {label:>20}"
    print(header)
    print(f"  {'─'*74}")

    for group_val, grp in df.groupby(group_col, sort=False):
        line = f"  {str(group_val):<18}"
        for m in METRIC_COLS:
            vals = grp[m].dropna()
            if len(vals) > 0:
                mean = vals.mean()
                std = vals.std()
                line += f" {mean:>8.1f} ± {std:<7.1f} "
            else:
                line += f" {'N/A':>20}"
        print(line)

    # Footer: total runs and failure count
    total = len(df)
    failed = int(df[METRIC_COLS[0]].isna().sum())
    print(f"  {'─'*74}")
    print(f"  Total runs: {total}  |  Successful: {total - failed}  |  Failed: {failed}")
    print(f"{'━'*78}\n")


# =====================================================================
#  Main
# =====================================================================

def main():
    t0 = time.time()

    # Step 3: Create results/ directory
    os.makedirs(RESULTS_DIR, exist_ok=True)

    print("╔══════════════════════════════════════════════════════════════╗")
    print("║       DisasterAI — Full Experiment Suite                    ║")
    print("║  5 dispatch baselines + MPC ablation × 20 runs each        ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")

    # ── Load terrain once (shared across all experiments) ─────────────
    print("Loading terrain, road network, and flood sources...")
    try:
        rem, road_graph, node_to_rc, source_pixels, pop_grid, building_pixels = load_terrain()
    except Exception:
        print("FATAL: Could not load terrain data. Aborting.")
        traceback.print_exc()
        sys.exit(1)
    print(f"Terrain ready. REM shape: {rem.shape}, Sources: {len(source_pixels)}\n")

    # ── Step 1: Baseline comparison (env/run_baselines.py logic) ──────
    print("┌──────────────────────────────────────────────────────────────┐")
    print("│  PHASE 1 / 2 :  Baseline Comparison                        │")
    print("└──────────────────────────────────────────────────────────────┘")
    baseline_df = run_baseline_experiment(
        rem, road_graph, node_to_rc, source_pixels, pop_grid, building_pixels
    )

    # ── Step 2: Ablation study (env/ablation.py logic) ────────────────
    print("┌──────────────────────────────────────────────────────────────┐")
    print("│  PHASE 2 / 2 :  MPC Lookahead Ablation                     │")
    print("└──────────────────────────────────────────────────────────────┘")
    ablation_df = run_ablation_experiment(
        rem, road_graph, node_to_rc, source_pixels, pop_grid, building_pixels
    )

    # ── Step 5: Print summary tables ──────────────────────────────────
    print_summary(baseline_df, "BASELINE COMPARISON  (mean ± std over 20 runs)", "mode")
    print_summary(ablation_df, "MPC LOOKAHEAD ABLATION  (mean ± std over 20 runs)", "N_value")

    # ── Timing ────────────────────────────────────────────────────────
    elapsed = time.time() - t0
    print(f"Total experiment time: {elapsed:.1f}s ({elapsed/60:.1f} min)")
    print(f"Results saved to: {RESULTS_DIR}/")
    print(f"  • baseline_comparison.csv  ({len(baseline_df)} rows)")
    print(f"  • ablation_lookahead.csv   ({len(ablation_df)} rows)")


if __name__ == "__main__":
    main()
