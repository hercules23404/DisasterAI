"""
population_loader.py
────────────────────
Generates a building-floor-area population proxy to replace the synthetic
dataset, matching the DEM grid shape and providing estimated people count per pixel.
Academic justification for this method: Wardrop et al. (2018) 'Spatially disaggregated
population estimates in the absence of national population and housing census data'.
"""

import numpy as np

class PopulationLoader:
    """Generates building-floor-area population proxy grids."""

    def __init__(self, tif_path: str = None):
        """
        Parameters
        ----------
        tif_path : str, optional
            Ignored. Kept for backwards compatibility.
        """
        self.population_grid = None

    def load_and_crop(
        self,
        min_lon: float,
        min_lat: float,
        max_lon: float,
        max_lat: float,
        target_shape: tuple[int, int] | None = None,
        building_loader = None,
    ) -> np.ndarray:
        """
        Generate a building-density-based population estimate.

        Parameters
        ----------
        min_lon, min_lat, max_lon, max_lat : float
            Bounding box in WGS84 degrees.
        target_shape : tuple[int, int] | None
            The target (rows, cols) of the simulation. Required.
        building_loader : BuildingLoader | None
            Building footprint data already downloaded.

        Returns
        -------
        np.ndarray  — 2-D float32 array.  Each cell = estimated people count.
        """
        if target_shape is None:
            target_shape = (500, 500)

        print("Generating building-density-based population proxy ...")
        
        pop_data = np.zeros(target_shape, dtype=np.float32)
        
        if building_loader and building_loader.buildings_gdf is not None and not building_loader.buildings_gdf.empty:
            # Project to UTM zone 43N (Mumbai) for ground area in m²
            try:
                projected = building_loader.buildings_gdf.to_crs(epsg=32643)
                areas = projected.geometry.area.values
            except Exception:
                # Fallback approximation
                areas = building_loader.buildings_gdf.geometry.area.values * (111_320 ** 2)
            
            gdf = building_loader.buildings_gdf
            if "building:levels" in gdf.columns:
                def _safe_float(val, default=2.0):
                    try: return float(val)
                    except (TypeError, ValueError): return default
                floors = gdf["building:levels"].apply(lambda x: _safe_float(x, default=2.0)).values
            else:
                floors = np.full(len(areas), 2.0)
            
            # Floor area = ground_area × number of floors
            floor_areas = areas * floors
            
            for (r, c), floor_area in zip(building_loader.building_pixels, floor_areas):
                if 0 <= r < target_shape[0] and 0 <= c < target_shape[1]:
                    pop_data[r, c] += floor_area
        else:
            print("  ⚠ No building data provided. Using uniform population.")
            pop_data += 1.0

        desired_total = 250000.0
        
        total_area = pop_data.sum()
        if total_area > 0:
            pop_data = pop_data * (desired_total / total_area)
        
        # Replace NaN values with 0
        pop_data = np.nan_to_num(pop_data, nan=0.0)
            
        self.population_grid = pop_data
        print(f"  Crop shape : {pop_data.shape}")
        total_pop = pop_data.sum()
        if np.isnan(total_pop):
            total_pop = 0
        print(f"  Total population in bbox : {int(total_pop):,}")
        
        return self.population_grid

    def get_population_at(self, r: int, c: int) -> float:
        """Return the population count at grid cell (r, c)."""
        if self.population_grid is None:
            return 0.0
        if 0 <= r < self.population_grid.shape[0] and 0 <= c < self.population_grid.shape[1]:
            return float(self.population_grid[r, c])
        return 0.0

    def get_population_summary(self, flood_depth: np.ndarray, threshold: float = 0.05) -> dict:
        """
        Given a flood-depth grid (same shape as population_grid), compute
        headline statistics for the dashboard.
        """
        if self.population_grid is None:
            return {
                "total_population": 0,
                "flooded_population": 0,
                "pct_affected": 0.0,
                "high_risk_population": 0,
            }

        total = float(self.population_grid.sum())
        flooded_mask = flood_depth > threshold
        flooded_pop = float(self.population_grid[flooded_mask].sum()) if flooded_mask.any() else 0.0
        high_risk_mask = flood_depth > 0.5
        high_risk_pop = float(self.population_grid[high_risk_mask].sum()) if high_risk_mask.any() else 0.0

        return {
            "total_population": int(total),
            "flooded_population": int(flooded_pop),
            "pct_affected": round(flooded_pop / total * 100, 1) if total > 0 else 0.0,
            "high_risk_population": int(high_risk_pop),
        }
