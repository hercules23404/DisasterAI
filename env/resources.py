"""
resources.py
────────────
Rescue unit classes with capacity, passenger tracking, and hospital
depot return logistics (Gap 8).

Hospital locations are defined relative to the DEM grid.  After a
unit picks up enough victims to reach capacity, it must return to
the nearest hospital before becoming available again.
"""

import numpy as np

# Hospital / depot pixel locations within the BKC / Mithi River grid
# These approximate real facility positions:
#   - Lilavati Hospital (north-west quadrant)
#   - Holy Family Hospital (south-east quadrant)
HOSPITAL_LOCATIONS = [
    (20, 20),    # NW quadrant of the ~144×144 grid
    (120, 120),  # SE quadrant
]

# Per-type capacity (how many victims a unit can carry before depot return)
UNIT_CAPACITY = {
    "Ambulance": 2,
    "Firefighter": 1,
}


class RescueUnit:
    def __init__(self, unit_id, r, c, unit_type="Ambulance"):
        self.id = unit_id
        self.r = r
        self.c = c
        self.node_id = None
        self.type = unit_type

        self.status = "idle"  # idle, en-route, busy
        self.target_incident = None
        self.path_nodes = []  # List of OSMnx nodes to travel

        # Heuristic capacity or speed
        self.speed = 2 if unit_type == "Ambulance" else 1

        # ── Gap 8: Capacity and logistics ─────────────────────────────
        self.capacity = UNIT_CAPACITY.get(unit_type, 1)
        self.passengers = 0       # victims currently being transported
        self.returning = False    # True when heading back to depot

    def assign_task(self, incident, path_nodes):
        """Dispatches unit to a target via calculated node path."""
        self.target_incident = incident
        self.path_nodes = path_nodes
        self.status = "en-route"

    def step_move(self, node_to_rc):
        """Moves the unit along the path based on its speed."""
        if self.status != "en-route" or not self.path_nodes:
            return False  # Didn't move

        # Move up to `self.speed` steps along the path
        steps_taken = 0
        while self.path_nodes and steps_taken < self.speed:
            next_node = self.path_nodes.pop(0)
            self.node_id = next_node
            self.r, self.c = node_to_rc[next_node]
            steps_taken += 1

        # Check arrival
        if not self.path_nodes:
            self.status = "busy"  # Reached target, now resolving
            return True  # Reached destination

        return False

    def resolve_task(self):
        """Completes the assignment and reverts to idle."""
        self.status = "idle"
        self.target_incident = None

    def get_position(self):
        return self.r, self.c

    # ── Gap 8: Capacity methods ───────────────────────────────────────

    def pick_up(self, victim):
        """
        Mark a victim as picked up.
        Returns True if unit still has remaining capacity.
        """
        self.passengers += 1
        return self.passengers < self.capacity

    def drop_off(self):
        """Called when unit reaches a hospital/depot."""
        self.passengers = 0
        self.returning = False
        self.status = "idle"
        self.target_incident = None

    def needs_to_return(self):
        """True if the unit is at capacity and must go to a hospital."""
        return self.passengers >= self.capacity


class Ambulance(RescueUnit):
    def __init__(self, unit_id, r, c):
        super().__init__(unit_id, r, c, unit_type="Ambulance")


class Firefighter(RescueUnit):
    def __init__(self, unit_id, r, c):
        super().__init__(unit_id, r, c, unit_type="Firefighter")
