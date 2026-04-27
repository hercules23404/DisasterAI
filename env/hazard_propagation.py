"""
hazard_propagation.py
─────────────────────
Min-Heap based topographic flow accumulation (Priority-Flood).

Constants are loaded from simulation_config.py and are calibrated
against IMD/CWC data for the Mithi River basin.  See that file for
sourcing and justification of every numeric value.

Includes a simulate_lookahead() function used by the predictive
rerouting system in environment.py (Gap 4).
"""

import heapq
import numpy as np
from env.simulation_config import PHYSICS


class HazardPropagation:
    def __init__(self, rem):
        self.rem = rem
        self.H, self.W = rem.shape

    def propagate(self, flood_depth, source_pixels, continuous_inflow_volume=None):
        """
        Min-Heap based topographic flow accumulation (D8).
        Constants loaded from simulation_config.py — no magic numbers.

        Parameters
        ----------
        flood_depth : np.ndarray
            Current flood depth grid (modified in-place).
        source_pixels : list[tuple[int, int]]
            (row, col) flood injection points.
        continuous_inflow_volume : float | None
            Override injection volume (defaults to PHYSICS config).
        """
        if continuous_inflow_volume is None:
            continuous_inflow_volume = PHYSICS["injection_volume"]

        flow_rate = PHYSICS["flow_transfer_rate"]
        dampening = PHYSICS["source_dampening"]
        min_flow = PHYSICS["min_flow_threshold"]
        cleanup = PHYSICS["cleanup_threshold"]
        prop_mult = PHYSICS["propagation_multiplier"]

        visited = np.zeros((self.H, self.W), dtype=bool)
        heap = []

        # Inject continuous surging water per frame
        for r, c in source_pixels:
            flood_depth[r, c] += continuous_inflow_volume
            ws = self.rem[r, c] + flood_depth[r, c]
            heapq.heappush(heap, (ws, r, c))
            visited[r, c] = True

        max_spread_iterations = len(heap) * prop_mult
        iters = 0

        while heap and iters < max_spread_iterations:
            current_ws, r, c = heapq.heappop(heap)
            iters += 1

            # Flood downhill neighbors (8-directional)
            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1), (-1,-1),(-1,1),(1,-1),(1,1)]:
                nr, nc = r+dr, c+dc

                if 0 <= nr < self.H and 0 <= nc < self.W and not visited[nr, nc]:
                    visited[nr, nc] = True
                    neighbor_ws = self.rem[nr, nc] + flood_depth[nr, nc]

                    if neighbor_ws < current_ws:
                        # Calibrated flow transfer (was hardcoded 0.95)
                        flow_amount = (current_ws - neighbor_ws) * flow_rate
                        actual_flow = min(flow_amount, flood_depth[r, c])

                        if actual_flow > min_flow:
                            # Calibrated source dampening (was hardcoded 0.50)
                            flood_depth[r, c] -= (actual_flow * dampening)
                            flood_depth[nr, nc] += actual_flow

                            new_ws = self.rem[nr, nc] + flood_depth[nr, nc]
                            heapq.heappush(heap, (new_ws, nr, nc))

        # Zero out numerical noise
        flood_depth[flood_depth < cleanup] = 0

        return flood_depth


def simulate_lookahead(propagator, flood_depth, source_pixels, n_steps=3):
    """
    Runs the propagation model forward n_steps WITHOUT modifying the
    actual simulation state.  Returns the predicted flood grid.

    Used by the predictive rerouting system in environment.py
    so that rescue units avoid roads that WILL BE flooded, not
    just roads that ARE flooded.

    Parameters
    ----------
    propagator : HazardPropagation
        The propagation engine instance (carries the REM).
    flood_depth : np.ndarray
        Current flood depth grid (NOT modified — a copy is used).
    source_pixels : list[tuple[int, int]]
        Flood injection source coordinates.
    n_steps : int
        How many frames to simulate ahead (default 3).

    Returns
    -------
    np.ndarray — predicted flood depth grid n_steps into the future.
    """
    predicted = flood_depth.copy()

    for _ in range(n_steps):
        predicted = propagator.propagate(
            predicted,
            source_pixels,
        )

    return predicted