"""
baselines.py
────────────
Baseline dispatch strategies for comparison / ablation studies.

Three dispatch modes are available:
  1. Random Dispatch     — weakest baseline
  2. Nearest Unit        — greedy, locally optimal
  3. Hungarian Algorithm — globally optimal (existing heuristic_dispatch)

Two operational baselines added for rigorous academic benchmarking:
  4. Greedy Myopic      — assigns nearest unit to highest-risk victim
  5. Priority Queue     — ranks unit-victim pairs by (risk/distance) ratio

A metrics logger is included for recording per-episode statistics
to results/metrics.csv for paper-quality comparison tables.
"""

import numpy as np
import random
import os
import csv
from scipy.optimize import linear_sum_assignment


def random_dispatch(env):
    """
    Baseline 1: Random assignment.
    Each idle unit is assigned to a uniformly random active victim.
    This is the weakest possible baseline — your system should beat it easily.
    """
    idle_units = [u for u in env.units if u.status == "idle"]
    active_incs = env.incident_manager.get_active_incidents()

    if not idle_units or not active_incs:
        return []

    random.shuffle(idle_units)
    random.shuffle(active_incs)

    assignments = []
    for i, unit in enumerate(idle_units):
        if i < len(active_incs):
            assignments.append((unit.id, active_incs[i].id))

    return assignments


def nearest_unit_dispatch(env):
    """
    Baseline 2: Greedy nearest-unit assignment.
    Each victim is assigned to the closest available unit (by Manhattan distance).
    No global optimality — units can cluster around nearby victims
    while distant victims wait. Stronger than random, weaker than Hungarian.
    """
    idle_units = [u for u in env.units if u.status == "idle"]
    active_incs = env.incident_manager.get_active_incidents()

    if not idle_units or not active_incs:
        return []

    assignments = []
    assigned_units = set()

    # Prioritize high-risk victims
    for inc in sorted(active_incs, key=lambda v: v.risk_level, reverse=True):
        best_unit = None
        best_dist = float('inf')
        for unit in idle_units:
            if unit.id in assigned_units:
                continue
            dist = abs(unit.r - inc.r) + abs(unit.c - inc.c)
            if dist < best_dist:
                best_dist = dist
                best_unit = unit
        if best_unit:
            assignments.append((best_unit.id, inc.id))
            assigned_units.add(best_unit.id)

    return assignments

def greedy_myopic_dispatch(env):
    """
    Baseline 4: Greedy Myopic.
    Assigns the nearest available unit to the highest-risk current victim,
    ignoring road conditions, capacity, and future victims. Proper greedy benchmark.
    """
    idle_units = [u for u in env.units if u.status == "idle"]
    active_incs = env.incident_manager.get_active_incidents()
    
    if not idle_units or not active_incs:
        return []
        
    # Sort victims by risk (highest first)
    sorted_victims = sorted(active_incs, key=lambda inc: inc.risk_level, reverse=True)
    assignments = []
    assigned_units = set()
    
    for victim in sorted_victims:
        best_unit = None
        best_dist = float('inf')
        for unit in idle_units:
            if unit.id in assigned_units:
                continue
            dist = abs(unit.r - victim.r) + abs(unit.c - victim.c)
            if dist < best_dist:
                best_dist = dist
                best_unit = unit
        
        if best_unit:
            assignments.append((best_unit.id, victim.id))
            assigned_units.add(best_unit.id)
            
    return assignments

def priority_queue_dispatch(env):
    """
    Baseline 5: Priority Queue.
    Ranks all victim-unit pairs by (risk_score / distance) and assigns greedily 
    until all units are dispatched. Approximates operational real-world logic.
    """
    idle_units = [u for u in env.units if u.status == "idle"]
    active_incs = env.incident_manager.get_active_incidents()
    
    if not idle_units or not active_incs:
        return []
        
    pairs = []
    for u in idle_units:
        for inc in active_incs:
            dist = max(1, abs(u.r - inc.r) + abs(u.c - inc.c))
            score = inc.risk_level / dist
            pairs.append((score, u.id, inc.id))
            
    # Sort pairs by score (highest first)
    pairs.sort(key=lambda x: x[0], reverse=True)
    
    assignments = []
    assigned_units = set()
    assigned_victims = set()
    
    for score, u_id, inc_id in pairs:
        if u_id not in assigned_units and inc_id not in assigned_victims:
            assignments.append((u_id, inc_id))
            assigned_units.add(u_id)
            assigned_victims.add(inc_id)
            
    return assignments

def hungarian_dispatch(env):
    """
    Baseline 3 / Primary heuristic: Hungarian Algorithm.
    Globally optimal 1-to-1 assignment minimizing total fleet cost.
    Cost = manhattan_distance + (1.0 - risk_level) × 1000.
    """
    idle_units = [u for u in env.units if u.status == "idle"]
    active_incs = env.incident_manager.get_active_incidents()

    if not idle_units or not active_incs:
        return []

    cost_matrix = np.zeros((len(idle_units), len(active_incs)))
    for i, u in enumerate(idle_units):
        for j, inc in enumerate(active_incs):
            dist = abs(u.r - inc.r) + abs(u.c - inc.c)
            risk_penalty = (1.0 - inc.risk_level) * 1000
            cost_matrix[i, j] = dist + risk_penalty

    row_ind, col_ind = linear_sum_assignment(cost_matrix)
    return [(idle_units[i].id, active_incs[j].id) for i, j in zip(row_ind, col_ind)]


# ─────────────────────────── Metrics Logger ─────────────────────────── #

def log_episode_metrics(episode_id, dispatch_mode, rescued, total_victims,
                        total_steps, total_reward, peak_flood,
                        output_path="results/metrics.csv"):
    """
    Appends one row of episode metrics to a CSV for comparison across baselines.
    Run each baseline for at least 20 episodes and report mean ± std.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    write_header = not os.path.exists(output_path)
    with open(output_path, "a", newline="") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow([
                "episode_id", "dispatch_mode", "rescued", "total_victims",
                "rescue_rate", "total_steps", "total_reward", "peak_flood"
            ])
        rescue_rate = rescued / max(total_victims, 1)
        writer.writerow([
            episode_id, dispatch_mode, rescued, total_victims,
            round(rescue_rate, 4), total_steps,
            round(total_reward, 2), round(peak_flood, 4)
        ])


# ─────────────────────────── Dispatch Router ─────────────────────────── #

def get_dispatch_function(mode_name):
    """
    Returns the dispatch function for the given mode name.
    Used by the dashboard to switch between modes.
    """
    dispatch_map = {
        "Random (Baseline)": random_dispatch,
        "Nearest Unit (Baseline)": nearest_unit_dispatch,
        "Greedy Myopic (Baseline)": greedy_myopic_dispatch,
        "Priority Queue (Operational)": priority_queue_dispatch,
        "Hungarian (Heuristic)": hungarian_dispatch,
    }
    return dispatch_map.get(mode_name, hungarian_dispatch)
