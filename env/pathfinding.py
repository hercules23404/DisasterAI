import networkx as nx
import numpy as np


def route_on_road_network(graph, source_node, target_node, flood_depth, node_to_rc, depth_threshold=0.2):
    """
    Optimized A* pathfinding precisely matching physical OSMnx road networks.
    Dynamically adjusts edge weights to infinity if the pixel underneath the road is flooded.
    """
    # OSMnx drive graphs are MultiDiGraphs. The weight function signature: weight(u, v, edge_dict)
    def dynamic_weight(u, v, edge_data):
        # Extract base physical length of the road
        if 0 in edge_data:
            base_length = edge_data[0].get('length', 10.0)
        else:
            base_length = edge_data.get('length', 10.0)
        
        # Check flood constraint mapping to pixel
        if v in node_to_rc:
            r, c = node_to_rc[v]
            if flood_depth[r, c] > depth_threshold:
                return float('inf') # Impassable road segment!
                
        return base_length
        
    try:
        path = nx.astar_path(graph, source_node, target_node, weight=dynamic_weight)
        return path
    except Exception:
        # No path available (completely blocked or isolated)
        return []


def edge_weight(u, v, data,
                current_depth, predicted_depth,
                unit_eta_steps, grid_transform,
                blend=0.5):
    """
    Predictive edge weight for A* routing.

    Effective depth = (1-blend)*current + blend*predicted.
    blend=0.5 gives equal weight to now vs arrival-time.
    Increase blend for more conservative (safe) routing.

    Parameters
    ----------
    u, v : graph node IDs
    data : edge data dict
    current_depth : np.ndarray
        Current flood depth grid.
    predicted_depth : np.ndarray
        Predicted flood depth at t+k.
    unit_eta_steps : int
        Estimated time of arrival in simulation steps.
    grid_transform : callable
        (lat, lon) or midpoint -> (row, col) converter.
    blend : float
        Weight between current (0.0) and predicted (1.0) depth.
    """
    row, col    = grid_transform(midpoint(u, v))
    cur_depth   = current_depth[row, col]
    pred_depth  = predicted_depth[row, col]
    eff_depth   = (1 - blend)*cur_depth + blend*pred_depth

    if eff_depth > 0.3:   # 30cm = impassable threshold
        return float('inf')
    return data.get('length', 1.0) * (1.0 + eff_depth * 5.0)


def midpoint(u, v):
    """Compute the midpoint between two nodes (for grid lookup)."""
    return ((u[0] + v[0]) / 2, (u[1] + v[1]) / 2)


def route_predictive(graph, source_node, target_node,
                     current_depth, predicted_depth,
                     node_to_rc, depth_threshold=0.3, blend=0.5):
    """
    A* pathfinding with blended current + predicted flood depth.

    A road that will be flooded when the rescue unit arrives should be
    treated as impassable now — not after the unit is already on it.

    Parameters
    ----------
    graph : networkx.MultiDiGraph
        OSMnx road network.
    source_node, target_node : int
        Graph node IDs.
    current_depth : np.ndarray
        Current flood depth grid.
    predicted_depth : np.ndarray
        Predicted flood depth at t+k steps.
    node_to_rc : dict
        Map from node ID -> (row, col).
    depth_threshold : float
        Effective depth above which road is impassable (default 0.3m).
    blend : float
        Weight between current (0.0) and predicted (1.0) depth.

    Returns
    -------
    list of node IDs forming the path, or [] if no path exists.
    """
    def predictive_weight(u, v, edge_data):
        if 0 in edge_data:
            base_length = edge_data[0].get('length', 10.0)
        else:
            base_length = edge_data.get('length', 10.0)

        if v in node_to_rc:
            r, c = node_to_rc[v]
            cur_d = current_depth[r, c]
            pred_d = predicted_depth[r, c]
            eff_depth = (1 - blend) * cur_d + blend * pred_d

            if eff_depth > depth_threshold:
                return float('inf')
            return base_length * (1.0 + eff_depth * 5.0)

        return base_length

    try:
        path = nx.astar_path(graph, source_node, target_node, weight=predictive_weight)
        return path
    except Exception:
        return []
