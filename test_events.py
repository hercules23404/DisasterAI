"""Quick test to check if events are being logged"""
import numpy as np
from env.terrain_loader import TerrainLoader
from env.environment import DisasterEnvironment
from env.hazard_propagation import HazardPropagation
from env.baselines import get_dispatch_function

# Load terrain
terrain = TerrainLoader(["env/datasets/n18_e072_1arc_v3.tif", "env/datasets/n19_e072_1arc_v3.tif"])
terrain.load_and_crop_dem()
terrain.download_road_network()

# Create simple environment
rem = terrain.rem if hasattr(terrain, "rem") else np.zeros((100, 100))
flood_depth = np.zeros_like(rem)

env = DisasterEnvironment(
    rem, terrain.road_graph, terrain.node_to_rc, flood_depth,
    num_units=3, num_incidents=5,
    transform=terrain.transform,
)

propagator = HazardPropagation(rem)
dispatch_fn = get_dispatch_function("hungarian")

print("Starting simulation...")
print(f"Initial event log size: {len(env.event_log)}")

# Run for 10 steps
for step in range(10):
    env.flood_depth = propagator.propagate(env.flood_depth, [], continuous_inflow_volume=5.0)
    actions = dispatch_fn(env)
    state, reward, done, info = env.step(actions=actions)
    
    print(f"Step {step}: {len(env.event_log)} events total")
    if len(env.event_log) > 0:
        print(f"  Last event: {env.event_log[-1]}")
    
    if done:
        break

print(f"\nFinal event log size: {len(env.event_log)}")
print("\nAll events:")
for evt in env.event_log:
    print(f"  Step {evt.get('step')}: {evt.get('type')} - {evt.get('message')}")
