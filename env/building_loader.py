"""
building_loader.py
──────────────────
Downloads real building footprints from OpenStreetMap via osmnx and
provides building-centroid coordinates for realistic victim placement.

Buildings are spatial "anchors" — instead of spawning a victim at a random
pixel, we spawn them at the centroid of an actual residential or commercial
structure.  This makes the simulation physically grounded: every victim
marker on the map sits on top of a real building.

Data source : OpenStreetMap (via osmnx)
License     : ODbL (OpenStreetMap)
"""

import numpy as np
import rasterio
import osmnx as ox
import geopandas as gpd
from typing import Optional


class BuildingLoader:
    """Downloads and processes OSM building footprints for a bounding box."""

    def __init__(self):
        self.buildings_gdf: Optional[gpd.GeoDataFrame] = None
        self.building_centroids: list[tuple[float, float]] = []  # (lat, lon)
        self.building_pixels: list[tuple[int, int]] = []          # (row, col)

    # ------------------------------------------------------------------ #
    #  Download
    # ------------------------------------------------------------------ #

    def download_buildings(
        self,
        min_lon: float,
        min_lat: float,
        max_lon: float,
        max_lat: float,
    ) -> gpd.GeoDataFrame:
        """
        Fetch all building footprints inside the bounding box from OSM.

        Parameters
        ----------
        min_lon, min_lat, max_lon, max_lat : float
            Bounding box in WGS84.

        Returns
        -------
        GeoDataFrame of building polygons.
        """
        print("Fetching OSM building footprints …")
        try:
            gdf = ox.features_from_bbox(
                bbox=(min_lon, min_lat, max_lon, max_lat),
                tags={"building": True},
            )
            # Keep only Polygon / MultiPolygon geometries (skip nodes tagged as buildings)
            gdf = gdf[gdf.geometry.type.isin(["Polygon", "MultiPolygon"])].copy()
            print(f"  Downloaded {len(gdf):,} building footprints")
        except Exception as e:
            print(f"  ⚠ Building download failed: {e}")
            gdf = gpd.GeoDataFrame()

        self.buildings_gdf = gdf
        return gdf

    # ------------------------------------------------------------------ #
    #  Centroid extraction
    # ------------------------------------------------------------------ #

    def extract_centroids(self, transform) -> list[tuple[int, int]]:
        """
        Compute the centroid of every building and map it to a DEM pixel
        (row, col) using the rasterio affine transform.

        Parameters
        ----------
        transform : rasterio.Affine
            The affine transform from the DEM / REM so centroids can be
            converted to pixel indices.

        Returns
        -------
        List of (row, col) tuples — one per building.
        """
        if self.buildings_gdf is None or self.buildings_gdf.empty:
            print("  No buildings available — centroid extraction skipped.")
            return []

        centroids = self.buildings_gdf.geometry.centroid
        self.building_centroids = []
        self.building_pixels = []

        for pt in centroids:
            lat, lon = pt.y, pt.x
            self.building_centroids.append((lat, lon))
            row, col = rasterio.transform.rowcol(transform, lon, lat)
            self.building_pixels.append((int(row), int(col)))

        print(f"  Extracted {len(self.building_pixels):,} building centroids → pixel coords")
        return self.building_pixels

    # ------------------------------------------------------------------ #
    #  Floor-area based population weighting
    # ------------------------------------------------------------------ #

    def estimate_building_population(self) -> np.ndarray:
        """
        Estimate relative population weight for each building based on
        ground-footprint area and number of floors (if available in OSM).

        Returns
        -------
        np.ndarray of float weights (one per building).  Not absolute
        population — these are relative weights used to distribute the
        WorldPop grid-cell population among the buildings in that cell.
        """
        if self.buildings_gdf is None or self.buildings_gdf.empty:
            return np.array([])

        # Project to UTM zone 43N (Mumbai) for area in m²
        try:
            projected = self.buildings_gdf.to_crs(epsg=32643)
            areas = projected.geometry.area.values  # m²
        except Exception:
            # Fallback: approximate area in degrees (rough but usable)
            areas = self.buildings_gdf.geometry.area.values * (111_320 ** 2)

        # Number of floors (OSM tag: building:levels)
        if "building:levels" in self.buildings_gdf.columns:
            floors = (
                self.buildings_gdf["building:levels"]
                .apply(lambda x: _safe_float(x, default=1.0))
                .values
            )
        else:
            floors = np.ones(len(areas))

        # Relative weight = ground_area × floors
        weights = areas * floors
        # Normalise so they sum to 1.0
        total = weights.sum()
        if total > 0:
            weights = weights / total

        return weights.astype(np.float32)

    # ------------------------------------------------------------------ #
    #  Convenience
    # ------------------------------------------------------------------ #

    def get_buildings_in_cell(self, r: int, c: int) -> list[int]:
        """Return indices of buildings whose centroid falls in pixel (r, c)."""
        return [i for i, (br, bc) in enumerate(self.building_pixels) if br == r and bc == c]

    def get_random_building_pixel(
        self, rng: np.random.Generator, exclude: set | None = None
    ) -> tuple[int, int] | None:
        """Pick a random building centroid pixel, optionally avoiding duplicates."""
        if not self.building_pixels:
            return None
        candidates = self.building_pixels
        if exclude:
            candidates = [p for p in candidates if p not in exclude]
        if not candidates:
            return None
        idx = rng.integers(0, len(candidates))
        return candidates[idx]


# ──────────────────────────────────────────────────────────────────────── #
#  Utility
# ──────────────────────────────────────────────────────────────────────── #

def _safe_float(val, default: float = 1.0) -> float:
    """Parse a potentially messy OSM tag value to float."""
    try:
        return float(val)
    except (TypeError, ValueError):
        return default
