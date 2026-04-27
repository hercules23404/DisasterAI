"""
environment.py
──────────────
Central MARL environment orchestrator defining the Dec-POMDP for disaster response.

Dec-POMDP Formulation ⟨I, S, A, Ω, T, O, R, γ⟩:
- S (Global State): 6-channel H×W tensor. Channels = [Current Flood Depth, Predicted Flood Depth, Composite Risk Grid, Victim Positions, Unit Positions, Population Vulnerability].
- I (Agent Set): Set of heterogeneous cooperative agents (Ambulances and Firefighters).
- A_i (Action Space): Discrete space of size M+1, where M is max simultaneous victims. Index 0 is No-Op; indices 1..M assign unit to an active victim.
- Ω (Observation Space): Local spatial crop of radius r=5 grid cells around each agent, concatenated with a 2-dim one-hot agent type encoding. Total size = (2r+1)² × 6 + 2 = 728.
- T (Transition Function): Two-part deterministic update. 1) Agent physical movement along dynamic A* road networks. 2) D8 topographic flood propagation via min-heap priority queue.
- R (Reward Function): R_t = rescue_base × (1 + composite_risk) per rescue − time_penalty × composite_risk per active victim − flood_penalty per flooded traversal − 2×rescue_base per death + preemptive_bonus per preemptive arrival.
- γ (Discount Factor): 0.99.

Integrates:
- Predictive flood simulation (FloodPredictor)
- Composite risk scoring (RiskScorer)
- Hungarian dispatch on composite scores (DispatchEngine)
- Explicit QMIX reward function (RewardFunction)
- Pre-disaster resource staging (MCLP)
- N-step predictive rerouting (MPC)
- Unit capacity and hospital depot return logistics
- Population-aware victim spawning
"""

import numpy as np
import networkx as nx
import rasterio
from env.resources import Ambulance, Firefighter, HOSPITAL_LOCATIONS
from env.victims import IncidentManager
from env.pathfinding import route_on_road_network, route_predictive
from env.pre_positioning import run_pre_positioning
from env.hazard_propagation import HazardPropagation, simulate_lookahead
from env.flood_predictor import FloodPredictor
from env.risk_scorer import RiskScorer
from env.dispatch_engine import DispatchEngine
from env.reward_function import RewardFunction
from env.simulation_config import PHYSICS
from scipy.spatial import KDTree

# ── Configuration constants ──────────────────────────────────────────
FLOOD_THRESHOLD = 0.2    # depth above which a road cell is impassable
LOOKAHEAD_STEPS = 3      # frames ahead the predictive rerouter looks
GAMMA = 0.99
OBS_RADIUS = 5
MAX_VICTIMS = 20
ACTION_SPACE_SIZE = MAX_VICTIMS + 1

class DisasterEnvironment:
    def __init__(self, rem, road_graph, node_to_rc, flood_depth=None,
                 num_units=5, num_incidents=10,
                 population_grid=None, building_pixels=None,
                 severity_multiplier=1.0,
                 flood_sources=None,
                 transform=None):
        """
        Central MARL environment.

        Parameters
        ----------
        rem : np.ndarray
            Relative elevation model.
        road_graph : networkx.MultiDiGraph
            OSMnx road network graph.
        node_to_rc : dict
            Map from graph node ID → (row, col) in the DEM.
        flood_depth : np.ndarray | None
            Initial flood depth grid.
        num_units : int
            Number of rescue units (ambulances).
        num_incidents : int
            Number of victims to spawn.
        population_grid : np.ndarray | None
            WorldPop population density grid (same shape as REM).
        building_pixels : list[tuple[int, int]] | None
            List of (row, col) building centroids from OSMnx.
        severity_multiplier : float
            From GDACS live alert level (0.5 / 1.0 / 1.5).
        flood_sources : list[tuple[int, int]] | None
            (row, col) flood injection source pixels for lookahead.
        transform : rasterio.Affine | None
            Rasterio transform for converting (row, col) to (lat, lon).
        """
        self.rem = rem
        self.road_graph = road_graph
        self.node_to_rc = node_to_rc
        self.H, self.W = rem.shape

        self.flood_depth = flood_depth if flood_depth is not None else np.zeros_like(rem)
        self.prev_depth = self.flood_depth.copy()
        self.flood_sources = flood_sources or []
        self.transform = transform

        # Store population data for metrics and risk scoring
        self.population_grid = population_grid
        # Normalised population grid for risk scoring (0–1)
        if population_grid is not None:
            pop_max = population_grid.max()
            self.pop_grid_normalised = population_grid / pop_max if pop_max > 0 else np.zeros_like(population_grid)
        else:
            self.pop_grid_normalised = np.zeros_like(rem)

        # ── Propagator instance for lookahead predictions ──
        self.propagator = HazardPropagation(rem)

        # ── NEW: Predictive system modules ──
        self.flood_predictor = FloodPredictor(
            dem=rem,
            injection_rate=PHYSICS["injection_volume"]
        )
        self.risk_scorer = RiskScorer(alpha=0.3, beta=0.4, gamma=0.2, delta=0.1)
        self.dispatch_engine = DispatchEngine(preemptive_threshold=0.3)
        self.reward_fn = RewardFunction(
            rescue_base=10.0, time_penalty=0.1,
            flood_penalty=5.0, preemptive_bonus=3.0
        )

        # Latest predictive state (updated each step)
        self.predicted_depth = self.flood_depth.copy()
        self.risk_scores = {}
        self.preemptive_targets = []

        # Build KDTree to map arbitrary coordinates to nearest OSMnx node
        self.graph_nodes = list(self.road_graph.nodes(data=True)) if self.road_graph else []
        if self.graph_nodes:
            self.node_coords = [(data['y'], data['x']) for _, data in self.graph_nodes]
            self.node_ids = [n for n, _ in self.graph_nodes]
            self.node_tree = KDTree(self.node_coords)
        else:
            self.node_tree = None
            self.node_ids = []

        # Create incident manager with real-world data layers
        self.incident_manager = IncidentManager(
            rem,
            population_grid=population_grid,
            building_pixels=building_pixels,
        )

        # Spawn victims — use population-aware spawning if data is available
        if population_grid is not None and building_pixels is not None:
            self.incident_manager.spawn_from_population(
                count=num_incidents,
                flood_depth=self.flood_depth,
                severity_multiplier=severity_multiplier,
            )
        else:
            self.incident_manager.spawn_random_incidents(num_incidents)

        # Assign actual road nodes to incidents
        self.patch_incident_nodes(self.incident_manager.incidents)

        # ── Pre-disaster resource staging ──────────────────────
        self.units = []
        for i in range(num_units):
            r = np.random.randint(0, self.H)
            c = np.random.randint(0, self.W)
            amb = Ambulance(unit_id=i, r=r, c=c)
            self.units.append(amb)

        # Run pre-positioning if we have flood source data
        self.pre_disaster_risk_map = None
        if self.flood_sources and self.node_ids:
            risk_map, placement_map = run_pre_positioning(
                rem=self.rem,
                flood_sources=self.flood_sources,
                units=self.units,
                node_ids=self.node_ids,
                node_to_rc=self.node_to_rc,
            )
            self.pre_disaster_risk_map = risk_map

            # Apply computed placements to units
            for unit in self.units:
                if unit.id in placement_map:
                    pos = placement_map[unit.id]
                    unit.r = pos["r"]
                    unit.c = pos["c"]
                    unit.node_id = pos["node_id"]
                    unit.path_nodes = []
        else:
            # Fallback: random road node placement
            for u in self.units:
                self.patch_unit_nodes([u])

        # ── Place hospital markers on the road network ─────────
        self._init_hospital_nodes()

        self.time_step = 0
        self.total_reward = 0

    # ------------------------------------------------------------------ #
    #  Initialization helpers
    # ------------------------------------------------------------------ #

    def _init_hospital_nodes(self):
        """Map hospital pixel positions to nearest road nodes."""
        self.hospital_nodes = {}
        if not self.node_tree:
            return
        rc_arr = np.array([self.node_to_rc[nid] for nid in self.node_ids], dtype=float)
        tree = KDTree(rc_arr)
        for hr, hc in HOSPITAL_LOCATIONS:
            hr_c = min(hr, self.H - 1)
            hc_c = min(hc, self.W - 1)
            _, idx = tree.query([hr_c, hc_c])
            self.hospital_nodes[(hr, hc)] = self.node_ids[idx]

    def patch_incident_nodes(self, items):
        if not self.node_tree:
            return
        for it in items:
            random_idx = np.random.randint(0, len(self.node_ids))
            it.node_id = self.node_ids[random_idx]
            it.r, it.c = self.node_to_rc[it.node_id]

    def patch_unit_nodes(self, units):
        if not self.node_tree:
            return
        for u in units:
            random_idx = np.random.randint(0, len(self.node_ids))
            u.node_id = self.node_ids[random_idx]
            u.r, u.c = self.node_to_rc[u.node_id]
            u.path_nodes = []

    def grid_to_latlon(self, r, c):
        """Convert grid (row, col) to (lat, lon) using rasterio transform."""
        if self.transform is not None:
            x, y = rasterio.transform.xy(self.transform, int(r), int(c))
            return float(y), float(x)
        # Fallback: return grid coords as-is
        return float(r), float(c)

    def _grid_transform(self, lat, lon):
        """Convert (lat, lon) back to (row, col) — inverse of grid_to_latlon.
        For Incident objects that store (r, c) directly, just use (r, c)."""
        # For our incidents, lat/lon are stored but we use .r, .c directly
        return int(lat), int(lon)

    def _victim_cells(self):
        """Returns set of (row, col) for all active victims."""
        return {(inc.r, inc.c) for inc in self.incident_manager.get_active_incidents()}

    def _compute_average_eta(self):
        """Compute average ETA of active units in simulation steps."""
        etas = []
        for unit in self.units:
            if unit.status == "en-route" and unit.path_nodes:
                etas.append(len(unit.path_nodes))
        if etas:
            return max(1, int(np.mean(etas)))
        return LOOKAHEAD_STEPS  # default if no units en-route

    def _travel_time(self, unit, victim):
        """Estimate travel time between unit and victim in grid steps."""
        return abs(unit.r - victim.r) + abs(unit.c - victim.c)

    # ------------------------------------------------------------------ #
    #  State
    # ------------------------------------------------------------------ #

    def reset(self):
        """Resets the environment for a new episode."""
        self.flood_depth = np.zeros_like(self.rem)
        self.prev_depth = np.zeros_like(self.rem)
        self.predicted_depth = np.zeros_like(self.rem)
        self.risk_scores = {}
        self.preemptive_targets = []
        self.time_step = 0
        self.total_reward = 0
        
        # Reset victims
        self.incident_manager.incidents = []
        self.incident_manager.id_counter = 0
        if self.population_grid is not None and getattr(self.incident_manager, 'building_pixels', None) is not None:
            self.incident_manager.spawn_from_population(
                count=10, # default
                flood_depth=self.flood_depth
            )
        else:
            self.incident_manager.spawn_random_incidents(10)
        self.patch_incident_nodes(self.incident_manager.incidents)
        
        # Reset units
        for unit in self.units:
            unit.drop_off()
            unit.path_nodes = []
        
        # Re-run pre-positioning if applicable
        if getattr(self, 'flood_sources', None) and self.node_ids:
            risk_map, placement_map = run_pre_positioning(
                rem=self.rem,
                flood_sources=self.flood_sources,
                units=self.units,
                node_ids=self.node_ids,
                node_to_rc=self.node_to_rc,
            )
            for unit in self.units:
                if unit.id in placement_map:
                    pos = placement_map[unit.id]
                    unit.r = pos["r"]
                    unit.c = pos["c"]
                    unit.node_id = pos["node_id"]
        else:
            self.patch_unit_nodes(self.units)
            
        return self.get_state()

    def get_state(self):
        """
        Returns the 6-channel state tensor (H, W, 6):
          Channel 0: Current flood depth (normalised 0–1)
          Channel 1: Predicted flood depth at t+k (normalised 0–1)
          Channel 2: Composite risk score grid
          Channel 3: Active victim locations (binary mask)
          Channel 4: Rescue unit positions (binary mask)
          Channel 5: Population vulnerability grid (from WorldPop)
        """
        # Channel 0: Current flood depth normalised
        max_depth = max(self.flood_depth.max(), 1.0)
        ch_current = np.clip(self.flood_depth / max_depth, 0, 1)

        # Channel 1: Predicted flood depth normalised
        pred_max = max(self.predicted_depth.max(), 1.0)
        ch_predicted = np.clip(self.predicted_depth / pred_max, 0, 1)

        # Channel 2: Composite risk score grid
        ch_risk = np.zeros_like(self.rem)
        for inc in self.incident_manager.get_active_incidents():
            risk = self.risk_scores.get(inc.id, inc.risk_level)
            ch_risk[inc.r, inc.c] = risk

        # Channel 3: Active victim locations (binary mask)
        ch_victims = np.zeros_like(self.rem)
        for inc in self.incident_manager.get_active_incidents():
            ch_victims[inc.r, inc.c] = 1.0

        # Channel 4: Rescue unit positions (binary mask)
        ch_units = np.zeros_like(self.rem)
        for u in self.units:
            ch_units[u.r, u.c] = 1.0

        # Channel 5: Population vulnerability grid
        ch_pop = self.pop_grid_normalised

        return np.stack([ch_current, ch_predicted, ch_risk,
                         ch_victims, ch_units, ch_pop], axis=-1)

    # ------------------------------------------------------------------ #
    #  Core simulation step — NEW predictive pipeline
    # ------------------------------------------------------------------ #

    def step(self, actions=None):
        """
        Restructured step loop running the flood predictor before dispatch,
        so all downstream decisions use the prediction-aware flood state.

        Step order:
          1. Inject flood volume → get current_depth
          2. Predict flood at average ETA of active units
          3. Spawn victims using formalised spawn model
          4. Score all active victims using composite formula
          5. Dispatch — Hungarian on composite scores
          6. Preemptive staging for remaining idle units
          7. Route units with predictive A*
          8. Build state tensor for QMIX
          9. Compute reward from post-transition state
        """
        reward = 0
        events = {
            'rescues': [],
            'preemptive_arrivals': 0,
            'active_victims': [],
            'flooded_traversals': 0,
            'deaths': 0,
        }

        # ── 1. Current flood state (propagation happens externally in dashboard,
        #       or can be done here for standalone runs) ──
        current_depth = self.flood_depth

        # ── 2. Predict flood at average ETA of active units ──
        avg_eta = self._compute_average_eta()
        source_rc = [(r, c) for r, c in self.flood_sources] if self.flood_sources else []
        if source_rc:
            self.predicted_depth = self.flood_predictor.predict(
                current_depth, source_rc, k_steps=avg_eta)
        else:
            self.predicted_depth = current_depth.copy()

        # ── 3. Spawn victims using formalised spawn model ──
        # (Additional dynamic spawning based on flood rise rate)
        if (self.population_grid is not None and 
            self.incident_manager.building_pixels is not None and
            self.time_step > 0):
            self._spawn_dynamic_victims(current_depth, self.prev_depth)

        # ── 4. Score all active victims using composite formula ──
        active_incidents = self.incident_manager.get_active_incidents()
        self.risk_scores = {}
        for inc in active_incidents:
            r, c = inc.r, inc.c
            r = int(np.clip(r, 0, self.H - 1))
            c = int(np.clip(c, 0, self.W - 1))
            self.risk_scores[inc.id] = self.risk_scorer.score(
                current_depth_at_victim=current_depth[r, c],
                predicted_depth_at_victim=self.predicted_depth[r, c],
                victim_health=inc.health,
                time_stranded=inc.steps_stranded,
                pop_vulnerability=self.pop_grid_normalised[r, c]
            )
            # Track active victims for reward
            events['active_victims'].append({
                'composite_risk': self.risk_scores[inc.id]
            })

        # ── 5. Dispatch — Hungarian on composite scores ──
        if actions and self.road_graph:
            # Use explicit actions from RL agent or external controller
            active_incs = {inc.id: inc for inc in active_incidents}
            for unit_id, inc_id in actions:
                unit = next((u for u in self.units if u.id == unit_id), None)
                incident = active_incs.get(inc_id)

                if unit and incident and unit.status == "idle" and not unit.returning:
                    path_nodes = route_predictive(
                        self.road_graph, unit.node_id, incident.node_id,
                        current_depth, self.predicted_depth,
                        self.node_to_rc
                    )
                    if not path_nodes:
                        # Fallback to current-only routing
                        path_nodes = route_on_road_network(
                            self.road_graph, unit.node_id, incident.node_id,
                            self.flood_depth, self.node_to_rc
                        )
                    if path_nodes:
                        unit.assign_task(incident, path_nodes)
                        incident.assigned_unit = unit

        # ── 6. Preemptive staging for remaining idle units ──
        if self.population_grid is not None:
            self.preemptive_targets = self.dispatch_engine.preemptive_targets(
                self.predicted_depth, self.pop_grid_normalised,
                self._victim_cells(), self.grid_to_latlon
            )

        # ── 7. Route units with predictive A* ──
        for unit in self.units:
            # Handle units returning to hospital
            if unit.returning:
                reached = unit.step_move(self.node_to_rc)
                if reached:
                    unit.drop_off()
                continue

            if unit.status == "en-route":
                # Predictive obstacle check — uses BOTH current AND predicted flood
                path_blocked = False
                flooded_traversal = False
                for node in unit.path_nodes:
                    if node in self.node_to_rc:
                        nr, nc = self.node_to_rc[node]
                        current_flooded = self.flood_depth[nr, nc] > FLOOD_THRESHOLD
                        future_flooded = self.predicted_depth[nr, nc] > FLOOD_THRESHOLD
                        if current_flooded or future_flooded:
                            path_blocked = True
                            if current_flooded:
                                flooded_traversal = True
                            break

                if flooded_traversal:
                    events['flooded_traversals'] += 1

                if path_blocked:
                    # Reroute using predicted flood state
                    new_path_nodes = route_predictive(
                        self.road_graph, unit.node_id, unit.target_incident.node_id,
                        current_depth, self.predicted_depth,
                        self.node_to_rc
                    )
                    if not new_path_nodes:
                        # Fallback to current-only routing
                        new_path_nodes = route_on_road_network(
                            self.road_graph, unit.node_id, unit.target_incident.node_id,
                            self.flood_depth, self.node_to_rc
                        )
                    if new_path_nodes:
                        unit.path_nodes = new_path_nodes
                    else:
                        unit.resolve_task()
                        if unit.target_incident:
                            unit.target_incident.assigned_unit = None

                # Move physically
                reached = unit.step_move(self.node_to_rc)

                if reached:
                    if unit.target_incident:
                        unit.target_incident.resolve()
                        # Track rescue event with composite risk
                        composite_risk = self.risk_scores.get(unit.target_incident.id, 0.5)
                        events['rescues'].append({
                            'composite_risk': composite_risk
                        })

                        # Pick up victim and check capacity
                        unit.pick_up(unit.target_incident)

                        if unit.needs_to_return():
                            # Route to nearest hospital
                            self._route_to_nearest_hospital(unit)
                        else:
                            unit.resolve_task()
                    else:
                        unit.resolve_task()

        # ── Update victim risks ──
        self.incident_manager.update_risks(self.flood_depth)

        # Check for deaths (health <= 0)
        for inc in self.incident_manager.get_active_incidents():
            if inc.health <= 0.0:
                events['deaths'] += 1
                inc.mark_dead()  # Mark as dead (distinct from rescued)

        self.time_step += 1
        self.prev_depth = current_depth.copy()

        done = len(self.incident_manager.get_active_incidents()) == 0 or self.time_step > 200

        # ── 8. Build state tensor for QMIX (before reward) ──
        state = self.get_state()

        # ── 9. Compute reward from the post-transition state ──
        events['idle_agents'] = sum(
            1 for u in self.units if u.status == "idle" and not u.returning
        )
        structured_reward = self.reward_fn.step_reward(events)
        reward += structured_reward
        self.total_reward += reward

        return state, reward, done, self.get_info()

    # ------------------------------------------------------------------ #
    #  Dynamic victim spawning
    # ------------------------------------------------------------------ #

    def _spawn_dynamic_victims(self, current_depth, prev_depth):
        """Spawn new victims dynamically based on flood rise rate and population."""
        if self.incident_manager.building_pixels is None:
            return
        rng = np.random.default_rng()
        new_spawns = 0
        max_new_per_step = 3  # cap dynamic spawns per step

        for r, c in self.incident_manager.building_pixels:
            if not (0 <= r < self.H and 0 <= c < self.W):
                continue
            if new_spawns >= max_new_per_step:
                break
            prob = self.incident_manager.spawn_probability(
                r, c, current_depth, prev_depth, self.pop_grid_normalised
            )
            if rng.random() < prob:
                from env.victims import Incident
                inc = Incident(
                    self.incident_manager.id_counter,
                    r, c,
                    severity=1.0 + min(current_depth[r, c] / 2.0, 1.0),
                    estimated_people=max(1, int(self.population_grid[r, c]) if self.population_grid is not None else 1)
                )
                self.incident_manager.incidents.append(inc)
                self.incident_manager.id_counter += 1
                self.patch_incident_nodes([inc])
                new_spawns += 1

    # ------------------------------------------------------------------ #
    #  Hospital routing
    # ------------------------------------------------------------------ #

    def _route_to_nearest_hospital(self, unit):
        """Route a full unit to the nearest hospital for drop-off."""
        if not self.hospital_nodes:
            unit.drop_off()
            return

        # Find nearest hospital by road distance
        best_path = None
        best_len = float('inf')
        for (hr, hc), h_node in self.hospital_nodes.items():
            path = route_on_road_network(
                self.road_graph, unit.node_id, h_node,
                self.flood_depth, self.node_to_rc
            )
            if path and len(path) < best_len:
                best_len = len(path)
                best_path = path

        if best_path:
            unit.path_nodes = best_path
            unit.status = "en-route"
            unit.returning = True
        else:
            # No path to any hospital — drop off in place
            unit.drop_off()

    # ------------------------------------------------------------------ #
    #  Events helper (for reward function)
    # ------------------------------------------------------------------ #

    def _events(self):
        """Build events dict for reward function (used when called externally)."""
        events = {
            'rescues': [],
            'preemptive_arrivals': 0,
            'active_victims': [],
            'flooded_traversals': 0,
            'deaths': 0,
        }
        for inc in self.incident_manager.get_active_incidents():
            risk = self.risk_scores.get(inc.id, inc.risk_level)
            events['active_victims'].append({'composite_risk': risk})
        return events

    # ------------------------------------------------------------------ #
    #  Info / metrics
    # ------------------------------------------------------------------ #

    def get_info(self):
        info = {
            "time_step": self.time_step,
            "total_reward": self.total_reward,
            "active_incidents": len(self.incident_manager.get_active_incidents()),
            "units_busy": sum(1 for u in self.units if u.status != "idle"),
        }
        # Add risk scores to info for dashboard
        info["risk_scores"] = dict(self.risk_scores)
        info["preemptive_targets"] = list(self.preemptive_targets) if self.preemptive_targets else []

        # Add population-aware metrics
        if self.population_grid is not None:
            total_pop = int(self.population_grid.sum())
            flooded_mask = self.flood_depth > 0.05
            flooded_pop = int(self.population_grid[flooded_mask].sum()) if flooded_mask.any() else 0
            people_in_danger = sum(
                inc.estimated_people for inc in self.incident_manager.get_active_incidents()
            )
            people_rescued = sum(
                inc.estimated_people for inc in self.incident_manager.incidents if inc.is_resolved
            )
            info["total_population"] = total_pop
            info["flooded_population"] = flooded_pop
            info["people_in_danger"] = people_in_danger
            info["people_rescued"] = people_rescued
        return info