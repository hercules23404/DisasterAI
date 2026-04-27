# env/dispatch_engine.py
"""
dispatch_engine.py
──────────────────
Separates dispatch into its own clean module and adds preemptive
dispatch — sending units toward predicted future victim zones before
victims formally spawn.

The Hungarian algorithm operates on composite risk scores, not just
distance, so high-risk victims receive lower cost assignments and are
prioritised globally.

Cost matrix formula:
    C[i, j] = travel_time(unit_i, victim_j) × (2.0 − composite_risk(victim_j))

This means high-risk victims (composite_risk close to 1.0) get a cost
multiplier near 1.0 (cheap to assign), while low-risk victims get a
multiplier near 2.0 (expensive). Combined with travel time, this
creates a globally optimal assignment that balances urgency and
proximity.
"""

import numpy as np
from scipy.optimize import linear_sum_assignment


class DispatchEngine:
    """
    Hungarian dispatch on composite risk scores + preemptive staging
    for predicted future victims.
    """

    def __init__(self, preemptive_threshold: float = 0.3):
        self.preemptive_threshold = preemptive_threshold

    def dispatch(self, idle_units, victims,
                 risk_scores: dict,
                 travel_time_fn) -> list:
        """
        Assigns idle units to active victims using Hungarian algorithm
        on a risk-adjusted cost matrix.

        Parameters
        ----------
        idle_units : list
            Rescue units with status == "idle".
        victims : list
            Active (unresolved) victims.
        risk_scores : dict
            {victim_id: composite_risk_score} from RiskScorer.
        travel_time_fn : callable
            (unit, victim) -> estimated travel time in steps.

        Returns
        -------
        list of (unit, victim) assignment pairs.
        """
        if not idle_units or not victims:
            return []

        n_units = len(idle_units)
        n_victims = len(victims)
        cost_matrix = np.zeros((n_units, n_victims))

        for i, unit in enumerate(idle_units):
            for j, victim in enumerate(victims):
                tt = travel_time_fn(unit, victim)
                risk = risk_scores.get(victim.id, 0.5)
                # High risk → low cost multiplier → prioritised
                cost_matrix[i, j] = tt * (2.0 - risk)

        row_ind, col_ind = linear_sum_assignment(cost_matrix)
        assignments = []
        for i, j in zip(row_ind, col_ind):
            assignments.append((idle_units[i], victims[j]))

        return assignments

    def preemptive_targets(self, predicted_depth: np.ndarray,
                           pop_grid: np.ndarray,
                           current_victim_cells: set,
                           grid_to_latlon_fn) -> list:
        """
        Identifies predicted future victim zones for preemptive staging.

        Scores each non-victim cell by combining predicted flood risk
        with population density. Returns top-10 locations sorted by
        combined score.

        Parameters
        ----------
        predicted_depth : np.ndarray
            Predicted flood depth grid at t+k.
        pop_grid : np.ndarray
            Population density grid (normalised 0–1).
        current_victim_cells : set
            Set of (row, col) tuples where victims already exist.
        grid_to_latlon_fn : callable
            (row, col) -> (lat, lon) converter.

        Returns
        -------
        list of (lat, lon, combined_score) tuples, sorted descending.
        """
        H, W = predicted_depth.shape
        targets = []
        for r in range(H):
            for c in range(W):
                if (r, c) in current_victim_cells:
                    continue
                flood_risk = min(predicted_depth[r,c]/2.0, 1.0)
                pop_risk   = float(np.clip(pop_grid[r,c], 0, 1))
                combined   = 0.6*flood_risk + 0.4*pop_risk
                if combined >= self.preemptive_threshold:
                    lat, lon = grid_to_latlon_fn(r, c)
                    targets.append((lat, lon, combined))
        targets.sort(key=lambda x: -x[2])
        return targets[:10]
