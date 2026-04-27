"""
victims.py
──────────
Incident / victim management with population-aware spawning.

Previously, victims were placed randomly on the terrain.  Now they are
spawned at **real building locations**, weighted by **WorldPop population
density**, with severity calibrated from **live GDACS disaster alerts**.

Fallback: If population data or buildings are unavailable, the old
strategic-random spawning logic is preserved as a safe default.
"""

import numpy as np
from typing import Optional


class Incident:
    def __init__(self, inc_id, r, c, severity=1.0, estimated_people: int = 1):
        self.id = inc_id
        self.r = r
        self.c = c
        self.severity = severity
        self.node_id = None

        self.risk_level = 0.0
        self.is_resolved = False
        self.assigned_unit = None

        # NEW — real-world population context
        self.estimated_people = estimated_people  # people at this location

        # Predictive system attributes
        self.health = 1.0           # 1.0 = full health, 0.0 = critical
        self.steps_stranded = 0     # number of steps since spawned
        self.lat = 0.0              # populated by grid_to_latlon after spawning
        self.lon = 0.0
        self.is_dead = False        # True if victim died (health reached 0)

    def tick_risk(self, flood_depth_at_location):
        if not self.is_resolved:
            if flood_depth_at_location > 0.05:
                self.risk_level += (flood_depth_at_location * 0.1 * self.severity)
            self.risk_level = min(1.0, self.risk_level)
            # Decay health over time — faster in deeper water
            decay = 0.02 + min(flood_depth_at_location * 0.05, 0.08)
            self.health = max(0.0, self.health - decay)
            self.steps_stranded += 1

    def resolve(self):
        self.is_resolved = True
        self.risk_level = 0.0

    def mark_dead(self):
        """Mark victim as dead — distinct from rescued."""
        self.is_dead = True
        self.is_resolved = True
        self.risk_level = 0.0


class IncidentManager:
    def __init__(self, rem, population_grid=None, building_pixels=None):
        """
        Parameters
        ----------
        rem : np.ndarray
            Relative elevation model.
        population_grid : np.ndarray | None
            WorldPop population density grid, aligned to the same shape as
            the REM.  Each cell = estimated people count.
        building_pixels : list[tuple[int, int]] | None
            List of (row, col) centroids of real buildings from OSMnx.
        """
        self.incidents = []
        self.rem = rem
        self.id_counter = 0

        # Real-world data layers (may be None for fallback mode)
        self.population_grid = population_grid
        self.building_pixels = building_pixels

    # ------------------------------------------------------------------ #
    #  PRIMARY: Population-aware spawning
    # ------------------------------------------------------------------ #

    def spawn_from_population(
        self,
        count: int,
        flood_depth: np.ndarray,
        severity_multiplier: float = 1.0,
        flood_threshold: float = 0.0,
    ):
        """
        Spawn victims at real building locations, weighted by population
        density and flood exposure.

        Parameters
        ----------
        count : int
            Target number of victims to generate.
        flood_depth : np.ndarray
            Current flood depth grid (same shape as REM).
        severity_multiplier : float
            From GDACS alert level (0.5 = Green, 1.0 = Orange, 1.5 = Red).
        flood_threshold : float
            Minimum flood depth for a cell to be considered "at risk".
            Set to 0.0 to use population density across all areas.
        """
        if self.population_grid is None or self.building_pixels is None:
            print("  ⚠ No population / building data — falling back to strategic spawning")
            self.spawn_strategic_incidents(count)
            return

        H, W = self.rem.shape
        rng = np.random.default_rng()

        # ── Step 1: Score every building by (population × flood_exposure) ──
        building_scores = []
        for r, c in self.building_pixels:
            if not (0 <= r < H and 0 <= c < W):
                building_scores.append(0.0)
                continue

            pop = float(self.population_grid[r, c]) if self.population_grid is not None else 1.0
            depth = float(flood_depth[r, c]) if flood_depth is not None else 0.0

            if flood_threshold > 0 and depth < flood_threshold:
                # If we require flood exposure and this cell is dry, reduce weight
                score = pop * 0.1  # Still possible but unlikely
            else:
                # Higher flood = higher priority for victim placement
                score = pop * max(depth, 0.2)

            building_scores.append(max(score, 0.0))

        scores = np.array(building_scores, dtype=np.float64)

        if scores.sum() <= 0:
            # All scores zero — add uniform fallback
            scores = np.ones(len(scores))

        # Normalise to probability distribution
        probs = scores / scores.sum()

        # ── Step 2: Sample building indices without replacement ──
        n_available = min(count, len(self.building_pixels))
        if n_available == 0:
            print("  ⚠ No buildings available — falling back to strategic spawning")
            self.spawn_strategic_incidents(count)
            return

        chosen_indices = rng.choice(
            len(self.building_pixels),
            size=n_available,
            replace=False,
            p=probs,
        )

        # ── Step 3: Create incidents at chosen buildings ──
        for idx in chosen_indices:
            r, c = self.building_pixels[idx]
            r = max(0, min(H - 1, r))
            c = max(0, min(W - 1, c))

            # Population at this cell
            pop = int(self.population_grid[r, c]) if self.population_grid is not None else 1

            # Severity: base from flood depth + GDACS multiplier
            depth = float(flood_depth[r, c]) if flood_depth is not None else 0.0
            base_severity = 1.0 + min(depth / 2.0, 1.0)  # 1.0–2.0
            severity = base_severity * severity_multiplier

            inc = Incident(
                self.id_counter,
                r, c,
                severity=severity,
                estimated_people=max(pop, 1),
            )
            self.incidents.append(inc)
            self.id_counter += 1

        flood_zone = sum(
            1 for inc in self.incidents
            if flood_depth is not None and flood_depth[inc.r, inc.c] > 0.05
        )
        print(
            f"  ✅ Spawned {len(chosen_indices)} victims at real buildings "
            f"({flood_zone} in flood zones, severity ×{severity_multiplier:.1f})"
        )

    # ------------------------------------------------------------------ #
    #  FALLBACK: Strategic random spawning (original logic, preserved)
    # ------------------------------------------------------------------ #

    def spawn_strategic_incidents(self, count):
        """
        Spawns victims strategically:
        - 40% in the lowest-elevation areas (flood path) to show rerouting
        - 60% in medium-elevation areas (safe but nearby) to show dispatch
        """
        H, W = self.rem.shape

        # Identify flood-prone zones (lowest 20% of REM)
        flat_rem = self.rem.flatten()
        threshold_low = np.percentile(flat_rem[flat_rem > 0], 20)
        threshold_mid = np.percentile(flat_rem[flat_rem > 0], 60)

        # Flood-zone victims (40% of total)
        flood_count = max(1, int(count * 0.4))
        safe_count = count - flood_count

        spawned = 0
        attempts = 0
        while spawned < flood_count and attempts < 5000:
            r = np.random.randint(0, H)
            c = np.random.randint(0, W)
            attempts += 1
            # Low elevation = flood-prone
            if 0 < self.rem[r, c] <= threshold_low:
                inc = Incident(self.id_counter, r, c, severity=1.5)  # Higher severity
                self.incidents.append(inc)
                self.id_counter += 1
                spawned += 1

        # Nearby safe-zone victims (60% of total)
        spawned = 0
        attempts = 0
        while spawned < safe_count and attempts < 5000:
            r = np.random.randint(0, H)
            c = np.random.randint(0, W)
            attempts += 1
            if threshold_low < self.rem[r, c] <= threshold_mid:
                inc = Incident(self.id_counter, r, c, severity=1.0)
                self.incidents.append(inc)
                self.id_counter += 1
                spawned += 1

    def spawn_random_incidents(self, count):
        """Fallback: Random placement on non-zero terrain."""
        self.spawn_strategic_incidents(count)

    # ------------------------------------------------------------------ #
    #  Predictive system: formalised spawn probability
    # ------------------------------------------------------------------ #

    def spawn_probability(self, row: int, col: int,
                          current_depth: np.ndarray,
                          prev_depth: np.ndarray,
                          pop_grid: np.ndarray) -> float:
        """
        P(spawn at cell r,c) proportional to
        population_density × (Δdepth / Δt)
        Only rising flood generates new victims.
        """
        delta_depth = current_depth[row,col] - prev_depth[row,col]
        delta_depth = max(delta_depth, 0.0)
        pop = float(pop_grid[row, col])
        return float(np.clip(pop * delta_depth * 10.0, 0.0, 1.0))

    # ------------------------------------------------------------------ #
    #  Shared
    # ------------------------------------------------------------------ #

    def get_active_incidents(self):
        return [inc for inc in self.incidents if not inc.is_resolved]

    def update_risks(self, flood_depth_matrix):
        for inc in self.incidents:
            inc.tick_risk(flood_depth_matrix[inc.r, inc.c])
