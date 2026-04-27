"""
pre_positioning.py
──────────────────
Pre-disaster resource staging using the Maximum Coverage Location Problem (MCLP)
formulation (Church & ReVelle, 1974). 

Places units at candidate road network nodes to maximize the total risk-weighted
population covered within a predefined radius. The greedy set cover approach
provides a formal (1 - 1/e) approximation guarantee for this NP-hard problem.
"""

import numpy as np
from scipy.spatial.distance import cdist


def compute_risk_map(rem, flood_sources):
    """
    Builds a pre-disaster risk raster.
    """
    H, W = rem.shape

    if not flood_sources:
        return np.ones((H, W)) * 0.5

    # Build coordinate arrays
    source_arr = np.array(flood_sources, dtype=float)
    rows, cols = np.meshgrid(np.arange(H), np.arange(W), indexing='ij')
    cell_arr = np.column_stack([rows.ravel(), cols.ravel()])

    # Distance from each cell to nearest flood source (normalized)
    dists = cdist(cell_arr, source_arr).min(axis=1)
    dists_norm = 1.0 - (dists / (dists.max() + 1e-8))

    # Low elevation = higher risk (invert and normalize REM)
    elev_flat = rem.flatten()
    elev_norm = 1.0 - (elev_flat / (elev_flat.max() + 1e-8))

    # Combine: weight proximity 60%, elevation 40%
    risk_flat = 0.6 * dists_norm + 0.4 * elev_norm
    risk_map = risk_flat.reshape(rem.shape)

    return risk_map


def mclp_greedy_placement(risk_map, candidate_locations, n_units, coverage_radius=10):
    """
    Maximum Coverage Location Problem (MCLP) greedy approximation.
    Places units at candidate locations to maximize the total risk-weighted
    coverage within a radius. Provides a (1 - 1/e) approximation guarantee.
    Based on Church & ReVelle (1974).

    Parameters
    ----------
    risk_map : np.ndarray
        2D risk raster serving as the weight matrix.
    candidate_locations : list[tuple[int, int]]
        List of (row, col) coordinates representing valid placement locations.
    n_units : int
        Number of units to place.
    coverage_radius : int
        Radius r (in pixels) defining the coverage zone of a unit.

    Returns
    -------
    list[tuple[int, int]] — (row, col) placement coordinates.
    """
    H, W = risk_map.shape
    risk_copy = risk_map.copy()
    placements = []
    
    # Convert candidates to a mutable list of unique coordinates
    candidates = list(set(candidate_locations))

    for _ in range(n_units):
        if not candidates:
            break
            
        best_loc = None
        best_coverage = -1.0
        
        # Evaluate marginal coverage for each candidate location
        for r, c in candidates:
            r_min = max(0, r - coverage_radius)
            r_max = min(H, r + coverage_radius + 1)
            c_min = max(0, c - coverage_radius)
            c_max = min(W, c + coverage_radius + 1)
            
            coverage = np.sum(risk_copy[r_min:r_max, c_min:c_max])
            if coverage > best_coverage:
                best_coverage = coverage
                best_loc = (r, c)
                
        if best_loc is not None:
            placements.append(best_loc)
            r, c = best_loc
            
            # Suppress the covered area so subsequent units cover new areas
            r_min = max(0, r - coverage_radius)
            r_max = min(H, r + coverage_radius + 1)
            c_min = max(0, c - coverage_radius)
            c_max = min(W, c + coverage_radius + 1)
            risk_copy[r_min:r_max, c_min:c_max] = 0.0
            
            candidates.remove(best_loc)
            
    return placements


def run_pre_positioning(rem, flood_sources, units, node_ids, node_to_rc):
    """
    Main entry point for MCLP pre-disaster staging.
    """
    risk_map = compute_risk_map(rem, flood_sources)
    
    if node_ids and node_to_rc:
        # Candidate locations are strictly valid road network nodes
        candidate_locations = [node_to_rc[nid] for nid in node_ids]
    else:
        # Fallback: all grid cells
        candidate_locations = [(r, c) for r in range(rem.shape[0]) for c in range(rem.shape[1])]
        
    pixel_placements = mclp_greedy_placement(
        risk_map, 
        candidate_locations, 
        n_units=len(units),
        coverage_radius=10
    )

    # Map each pixel placement back to the nearest actual road node
    from scipy.spatial import KDTree
    if node_ids and node_to_rc:
        rc_arr = np.array([node_to_rc[nid] for nid in node_ids], dtype=float)
        tree = KDTree(rc_arr)

        placement_map = {}
        for i, unit in enumerate(units):
            if i >= len(pixel_placements):
                break
            target_rc = np.array(pixel_placements[i], dtype=float)
            _, idx = tree.query(target_rc)
            best_node = node_ids[idx]
            placement_map[unit.id] = {
                "node_id": best_node,
                "r": node_to_rc[best_node][0],
                "c": node_to_rc[best_node][1],
            }
    else:
        placement_map = {}
        for i, unit in enumerate(units):
            if i >= len(pixel_placements):
                break
            r, c = pixel_placements[i]
            placement_map[unit.id] = {"node_id": None, "r": r, "c": c}

    print(f"  ✅ Pre-positioned {len(units)} units using MCLP greedy coverage")
    return risk_map, placement_map
