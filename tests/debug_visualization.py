"""
Debug script to inspect actual Plotly figure structure
"""
import numpy as np
import rasterio.transform
from components.map_renderer import build_plotly_animation, VICTIM_COLORS


class MockTerrain:
    """Mock terrain object for testing"""
    def __init__(self):
        self.min_lat = 19.0
        self.max_lat = 19.1
        self.min_lon = 72.8
        self.max_lon = 72.9
        self.transform = rasterio.transform.from_bounds(
            72.8, 19.0, 72.9, 19.1, 100, 100
        )
        self.node_to_rc = {}
        self.road_graph = None


def create_test_frame():
    """Create test frame with victims at different risk/health levels"""
    incidents = [
        [50, 50, 0.85, False, 1, 0.6, False],  # High risk, mid health
        [52, 52, 0.45, False, 2, 0.8, False],  # Mid risk, high health
        [54, 54, 0.15, False, 3, 0.9, False],  # Low risk, high health
    ]
    
    risk_scores = {1: 0.85, 2: 0.45, 3: 0.15}
    
    return {
        "incidents": incidents,
        "risk_scores": risk_scores,
        "units": [],
        "flood_depth": np.zeros((100, 100)),
        "predicted_depth": np.zeros((100, 100)),
        "event_log": [
            {"type": "rescue", "victim_id": 1, "step": 9}
        ],
        "info": {"step": 10, "active_incidents": 3, "units_busy": 0}
    }


# Create and render frame
frame = create_test_frame()
terrain = MockTerrain()
fig = build_plotly_animation(terrain, [frame], speed_ms=800)

# Inspect victim trace
print("=" * 60)
print("VICTIM TRACE INSPECTION")
print("=" * 60)

for trace in fig.data:
    if trace.name == "Victims":
        print(f"\nVictim trace found!")
        print(f"  Number of victims: {len(trace.lat)}")
        print(f"  Colors: {trace.marker.color}")
        print(f"  Sizes: {trace.marker.size}")
        print(f"\nExpected colors:")
        print(f"  High risk (0.85): {VICTIM_COLORS['high_risk']}")
        print(f"  Mid risk (0.45): {VICTIM_COLORS['mid_risk']}")
        print(f"  Low risk (0.15): {VICTIM_COLORS['low_risk']}")
        print(f"\nExpected sizes:")
        print(f"  Health 0.6: {10 + (1.0 - 0.6) * 12:.1f}px")
        print(f"  Health 0.8: {10 + (1.0 - 0.8) * 12:.1f}px")
        print(f"  Health 0.9: {10 + (1.0 - 0.9) * 12:.1f}px")

print("\n" + "=" * 60)
print("BURST TRACE INSPECTION")
print("=" * 60)

rescue_found = False
for trace in fig.data:
    if trace.name == "Rescue!":
        rescue_found = True
        print(f"\nRescue burst trace found!")
        print(f"  Number of bursts: {len(trace.lat) if trace.lat else 0}")
        print(f"  Coordinates: {list(trace.lat) if trace.lat else []}")

if not rescue_found:
    print("\nNo rescue burst trace found!")

print("\n" + "=" * 60)
