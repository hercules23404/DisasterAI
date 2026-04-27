# env/flood_predictor.py
"""
flood_predictor.py
──────────────────
Runs D8 min-heap propagation forward k timesteps on a lightweight copy
of the current flood state — no side effects on the live simulation.

Called once per dispatch cycle with k equal to the estimated travel time
of the rescue unit in simulation steps. This gives a flood map that is
time-locked to when the unit actually arrives.

Why this design:
    Running D8 on a copy is O(n log n) per prediction call — identical
    cost to the live simulation. For a 144×144 grid this is trivially
    fast. The key insight is that the prediction horizon k is not fixed:
    it equals the ETA of the rescue unit being dispatched, so every
    assignment uses a flood map that is calibrated to that specific
    unit's travel time. Cache the predicted depth grid and only recompute
    when a unit's ETA changes by more than 2 steps to avoid redundant calls.
"""

import numpy as np
import heapq


class FloodPredictor:
    """
    Runs D8 min-heap propagation forward k timesteps on a copy
    of the current flood state to produce predicted depth at t+k.
    """

    def __init__(self, dem: np.ndarray, injection_rate: float):
        self.dem = dem          # (H, W) elevation array
        self.injection_rate = injection_rate
        self._neighbors = [(-1,0),(1,0),(0,-1),(0,1),
                           (-1,-1),(-1,1),(1,-1),(1,1)]

    def predict(self, current_depth: np.ndarray,
                source_pixels: list,
                k_steps: int) -> np.ndarray:
        """
        Returns predicted flood depth grid after k steps.
        Does NOT mutate current_depth — operates on a copy.
        """
        depth = current_depth.copy()
        H, W = depth.shape
        heap = []
        for r in range(H):
            for c in range(W):
                if depth[r, c] > 0:
                    surface = self.dem[r, c] + depth[r, c]
                    heapq.heappush(heap, (surface, r, c))

        for _ in range(k_steps):
            for (r, c) in source_pixels:
                depth[r, c] += self.injection_rate
                heapq.heappush(heap,
                    (self.dem[r,c] + depth[r,c], r, c))
            if not heap:
                break
            surf, r, c = heapq.heappop(heap)
            for dr, dc in self._neighbors:
                nr, nc = r+dr, c+dc
                if 0 <= nr < H and 0 <= nc < W:
                    neighbor_surface = self.dem[nr,nc] + depth[nr,nc]
                    if surf > neighbor_surface + 1e-4:
                        spill = (surf - neighbor_surface) / 2
                        depth[nr, nc] += spill
                        heapq.heappush(heap,
                            (self.dem[nr,nc]+depth[nr,nc], nr, nc))

        return depth   # (H, W) predicted depths

    def predict_at_eta(self, current_depth, source_pixels,
                       eta_steps: int) -> np.ndarray:
        """Convenience wrapper — predict at unit arrival time."""
        return self.predict(current_depth, source_pixels, eta_steps)
