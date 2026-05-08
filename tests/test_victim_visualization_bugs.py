"""
Bug Condition Exploration Test for Victim Visualization Bugs

This test demonstrates three bugs in the disaster simulation map visualization:
1. Victim colors: All victims display in green regardless of risk level
2. Marker sizes: All victims display at the same size regardless of health
3. Burst animations: Rescue and casualty bursts do not appear

EXPECTED BEHAVIOR: This test MUST FAIL on unfixed code - failure confirms the bugs exist.
The test encodes the expected behavior and will validate the fix when it passes.

**Validates: Requirements 1.1-1.13 (Bug Conditions)**
"""

import pytest
import numpy as np
import rasterio.transform
from components.map_renderer import build_plotly_animation, VICTIM_COLORS, BURST_COLORS


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


def create_test_frame_with_victims(victim_configs):
    """
    Create a test frame with victims at specified risk and health levels.
    
    Args:
        victim_configs: List of tuples (risk, health, status, victim_id)
    
    Returns:
        Dictionary representing a frame with victim data
    """
    incidents = []
    risk_scores = {}
    
    for i, (risk, health, status, vic_id) in enumerate(victim_configs):
        # Frame incidents format: [r, c, risk, resolved, inc_id, health, is_dead]
        r, c = 50 + i * 2, 50 + i * 2  # Spread victims across map
        resolved = (status == "rescued")
        is_dead = (status == "deceased")
        
        incidents.append([r, c, risk, resolved, vic_id, health, is_dead])
        risk_scores[vic_id] = risk
    
    return {
        "incidents": incidents,
        "risk_scores": risk_scores,
        "units": [],
        "flood_depth": np.zeros((100, 100)),
        "predicted_depth": np.zeros((100, 100)),
        "event_log": [],
        "info": {"step": 0, "active_incidents": len(victim_configs), "units_busy": 0}
    }


def create_test_frame_with_events(event_configs):
    """
    Create a test frame with rescue/casualty events.
    
    Args:
        event_configs: List of tuples (event_type, victim_id, step)
    
    Returns:
        Dictionary representing a frame with event data
    """
    incidents = []
    event_log = []
    
    for i, (event_type, vic_id, step) in enumerate(event_configs):
        # Add victim at location
        r, c = 50 + i * 2, 50 + i * 2
        incidents.append([r, c, 0.5, False, vic_id, 0.8, False])
        
        # Add event to log
        event_log.append({
            "type": event_type,
            "victim_id": vic_id,
            "step": step
        })
    
    return {
        "incidents": incidents,
        "risk_scores": {},
        "units": [],
        "flood_depth": np.zeros((100, 100)),
        "predicted_depth": np.zeros((100, 100)),
        "event_log": event_log,
        "info": {"step": 10, "active_incidents": len(event_configs), "units_busy": 0}
    }


def extract_victim_trace_data(fig):
    """Extract victim marker data from Plotly figure"""
    for trace in fig.data:
        if trace.name == "Victims":
            return {
                "colors": trace.marker.color if hasattr(trace.marker, 'color') else [],
                "sizes": trace.marker.size if hasattr(trace.marker, 'size') else [],
                "lats": trace.lat,
                "lons": trace.lon
            }
    return None


def extract_burst_trace_data(fig):
    """Extract burst marker data from Plotly figure"""
    rescue_bursts = []
    casualty_bursts = []
    
    for trace in fig.data:
        if trace.name == "Rescue!":
            rescue_bursts = list(trace.lat) if trace.lat else []
        elif trace.name == "Casualty":
            casualty_bursts = list(trace.lat) if trace.lat else []
    
    return {
        "rescue_count": len(rescue_bursts),
        "casualty_count": len(casualty_bursts)
    }


class TestVictimVisualizationBugs:
    """
    Bug Condition Exploration Tests
    
    These tests MUST FAIL on unfixed code to confirm the bugs exist.
    When the tests pass after implementing the fix, it confirms the expected behavior is satisfied.
    """
    
    def test_bug1_high_risk_victim_displays_wrong_color(self):
        """
        Bug 1: High risk victims (risk >= 0.66) display in green instead of red
        
        Expected behavior: High risk victims should display in red (#ff1744)
        Actual behavior (unfixed): All victims display in green
        
        **Validates: Requirements 1.1, 2.1**
        """
        # Create frame with high risk victim
        victim_configs = [
            (0.85, 0.6, "active", 1)  # High risk (0.85), moderate health
        ]
        frame = create_test_frame_with_victims(victim_configs)
        terrain = MockTerrain()
        
        # Render the visualization
        fig = build_plotly_animation(terrain, [frame], speed_ms=800)
        
        # Extract victim trace data
        victim_data = extract_victim_trace_data(fig)
        assert victim_data is not None, "Victim trace not found in figure"
        
        # Check that high risk victim displays in red
        colors = victim_data["colors"]
        assert len(colors) > 0, "No victim colors found"
        
        expected_color = VICTIM_COLORS["high_risk"]  # Should be #ff1744 (red)
        actual_color = colors[0]
        
        assert actual_color == expected_color, (
            f"High risk victim (risk=0.85) should display in red ({expected_color}), "
            f"but displays in {actual_color}"
        )
    
    def test_bug1_mid_risk_victim_displays_wrong_color(self):
        """
        Bug 1: Mid risk victims (0.33 <= risk < 0.66) display in green instead of orange
        
        Expected behavior: Mid risk victims should display in orange (#ff9800)
        Actual behavior (unfixed): All victims display in green
        
        **Validates: Requirements 1.2, 2.2**
        """
        # Create frame with mid risk victim
        victim_configs = [
            (0.45, 0.8, "active", 2)  # Mid risk (0.45), good health
        ]
        frame = create_test_frame_with_victims(victim_configs)
        terrain = MockTerrain()
        
        # Render the visualization
        fig = build_plotly_animation(terrain, [frame], speed_ms=800)
        
        # Extract victim trace data
        victim_data = extract_victim_trace_data(fig)
        assert victim_data is not None, "Victim trace not found in figure"
        
        # Check that mid risk victim displays in orange
        colors = victim_data["colors"]
        expected_color = VICTIM_COLORS["mid_risk"]  # Should be #ff9800 (orange)
        actual_color = colors[0]
        
        assert actual_color == expected_color, (
            f"Mid risk victim (risk=0.45) should display in orange ({expected_color}), "
            f"but displays in {actual_color}"
        )
    
    def test_bug1_multiple_risk_levels_display_different_colors(self):
        """
        Bug 1: Victims with different risk levels should display in different colors
        
        Expected behavior: High=red, Mid=orange, Low=green
        Actual behavior (unfixed): All display in green
        
        **Validates: Requirements 1.3, 1.4, 2.3, 2.4**
        """
        # Create frame with victims at all three risk levels
        victim_configs = [
            (0.85, 0.6, "active", 1),  # High risk -> red
            (0.45, 0.8, "active", 2),  # Mid risk -> orange
            (0.15, 0.9, "active", 3)   # Low risk -> green
        ]
        frame = create_test_frame_with_victims(victim_configs)
        terrain = MockTerrain()
        
        # Render the visualization
        fig = build_plotly_animation(terrain, [frame], speed_ms=800)
        
        # Extract victim trace data
        victim_data = extract_victim_trace_data(fig)
        assert victim_data is not None, "Victim trace not found in figure"
        
        # Check that each victim has the correct color
        colors = victim_data["colors"]
        assert len(colors) == 3, f"Expected 3 victim colors, got {len(colors)}"
        
        expected_colors = [
            VICTIM_COLORS["high_risk"],  # #ff1744 (red)
            VICTIM_COLORS["mid_risk"],   # #ff9800 (orange)
            VICTIM_COLORS["low_risk"]    # #4caf50 (green)
        ]
        
        for i, (expected, actual) in enumerate(zip(expected_colors, colors)):
            assert actual == expected, (
                f"Victim {i+1} should display in {expected}, but displays in {actual}"
            )
        
        # Verify colors are NOT all the same (the bug condition)
        unique_colors = set(colors)
        assert len(unique_colors) == 3, (
            f"All three risk levels should have different colors, "
            f"but got {len(unique_colors)} unique colors: {unique_colors}"
        )
    
    def test_bug2_low_health_victim_displays_wrong_size(self):
        """
        Bug 2: Low health victims should display larger markers
        
        Expected behavior: Size = 10 + (1.0 - health) × 12 pixels
        For health=0.2: size should be 10 + 0.8×12 = 19.6 pixels
        Actual behavior (unfixed): All victims display at uniform size
        
        **Validates: Requirements 1.6, 2.7, 2.8**
        """
        # Create frame with low health victim
        victim_configs = [
            (0.5, 0.2, "active", 1)  # Mid risk, low health (0.2)
        ]
        frame = create_test_frame_with_victims(victim_configs)
        terrain = MockTerrain()
        
        # Render the visualization
        fig = build_plotly_animation(terrain, [frame], speed_ms=800)
        
        # Extract victim trace data
        victim_data = extract_victim_trace_data(fig)
        assert victim_data is not None, "Victim trace not found in figure"
        
        # Check that low health victim displays at correct size
        sizes = victim_data["sizes"]
        assert len(sizes) > 0, "No victim sizes found"
        
        expected_size = 10 + (1.0 - 0.2) * 12  # = 19.6 pixels
        actual_size = sizes[0]
        
        assert abs(actual_size - expected_size) < 0.1, (
            f"Low health victim (health=0.2) should display at size {expected_size:.1f}px, "
            f"but displays at {actual_size}px"
        )
    
    def test_bug2_high_health_victim_displays_wrong_size(self):
        """
        Bug 2: High health victims should display smaller markers
        
        Expected behavior: Size = 10 + (1.0 - health) × 12 pixels
        For health=0.9: size should be 10 + 0.1×12 = 11.2 pixels
        Actual behavior (unfixed): All victims display at uniform size
        
        **Validates: Requirements 1.7, 2.6, 2.8**
        """
        # Create frame with high health victim
        victim_configs = [
            (0.5, 0.9, "active", 2)  # Mid risk, high health (0.9)
        ]
        frame = create_test_frame_with_victims(victim_configs)
        terrain = MockTerrain()
        
        # Render the visualization
        fig = build_plotly_animation(terrain, [frame], speed_ms=800)
        
        # Extract victim trace data
        victim_data = extract_victim_trace_data(fig)
        assert victim_data is not None, "Victim trace not found in figure"
        
        # Check that high health victim displays at correct size
        sizes = victim_data["sizes"]
        expected_size = 10 + (1.0 - 0.9) * 12  # = 11.2 pixels
        actual_size = sizes[0]
        
        assert abs(actual_size - expected_size) < 0.1, (
            f"High health victim (health=0.9) should display at size {expected_size:.1f}px, "
            f"but displays at {actual_size}px"
        )
    
    def test_bug2_different_health_levels_display_different_sizes(self):
        """
        Bug 2: Victims with different health levels should display at different sizes
        
        Expected behavior: Lower health = larger size
        Actual behavior (unfixed): All display at uniform size
        
        **Validates: Requirements 1.8, 1.9, 2.9, 2.10**
        """
        # Create frame with victims at different health levels
        victim_configs = [
            (0.5, 0.2, "active", 1),  # Low health -> large size (19.6px)
            (0.5, 0.9, "active", 2)   # High health -> small size (11.2px)
        ]
        frame = create_test_frame_with_victims(victim_configs)
        terrain = MockTerrain()
        
        # Render the visualization
        fig = build_plotly_animation(terrain, [frame], speed_ms=800)
        
        # Extract victim trace data
        victim_data = extract_victim_trace_data(fig)
        assert victim_data is not None, "Victim trace not found in figure"
        
        # Check that each victim has the correct size
        sizes = victim_data["sizes"]
        assert len(sizes) == 2, f"Expected 2 victim sizes, got {len(sizes)}"
        
        expected_sizes = [
            10 + (1.0 - 0.2) * 12,  # 19.6 pixels
            10 + (1.0 - 0.9) * 12   # 11.2 pixels
        ]
        
        for i, (expected, actual) in enumerate(zip(expected_sizes, sizes)):
            assert abs(actual - expected) < 0.1, (
                f"Victim {i+1} should display at size {expected:.1f}px, "
                f"but displays at {actual}px"
            )
        
        # Verify sizes are different (not uniform)
        size_difference = abs(sizes[0] - sizes[1])
        assert size_difference > 2, (
            f"Victims with different health (0.2 vs 0.9) should have significantly "
            f"different sizes, but difference is only {size_difference:.1f}px"
        )
    
    def test_bug3_rescue_burst_not_appearing(self):
        """
        Bug 3: Rescue events should display green star bursts for 3 frames
        
        Expected behavior: Green star burst at victim location when rescue occurs
        Actual behavior (unfixed): No burst markers visible
        
        **Validates: Requirements 1.10, 2.11**
        """
        # Create frame with rescue event within 3-frame window
        event_configs = [
            ("rescue", 1, 9)  # Rescue at step 9, current step is 10
        ]
        frame = create_test_frame_with_events(event_configs)
        terrain = MockTerrain()
        
        # Render the visualization
        fig = build_plotly_animation(terrain, [frame], speed_ms=800)
        
        # Extract burst trace data
        burst_data = extract_burst_trace_data(fig)
        
        # Check that rescue burst appears
        assert burst_data["rescue_count"] > 0, (
            f"Rescue event at step 9 (current step 10) should display a burst marker, "
            f"but {burst_data['rescue_count']} rescue bursts found"
        )
    
    def test_bug3_casualty_burst_not_appearing(self):
        """
        Bug 3: Casualty events should display red X bursts for 3 frames
        
        Expected behavior: Red X burst at victim location when casualty occurs
        Actual behavior (unfixed): No burst markers visible
        
        **Validates: Requirements 1.11, 2.12**
        """
        # Create frame with casualty event within 3-frame window
        event_configs = [
            ("casualty", 2, 8)  # Casualty at step 8, current step is 10
        ]
        frame = create_test_frame_with_events(event_configs)
        terrain = MockTerrain()
        
        # Render the visualization
        fig = build_plotly_animation(terrain, [frame], speed_ms=800)
        
        # Extract burst trace data
        burst_data = extract_burst_trace_data(fig)
        
        # Check that casualty burst appears
        assert burst_data["casualty_count"] > 0, (
            f"Casualty event at step 8 (current step 10) should display a burst marker, "
            f"but {burst_data['casualty_count']} casualty bursts found"
        )
    
    def test_bug3_multiple_events_display_bursts(self):
        """
        Bug 3: Multiple rescue/casualty events should each display their bursts
        
        Expected behavior: Each event within 3-frame window displays a burst
        Actual behavior (unfixed): No burst markers visible
        
        **Validates: Requirements 1.12, 1.13, 2.13, 2.14**
        """
        # Create frame with multiple events within 3-frame window
        event_configs = [
            ("rescue", 1, 9),    # Rescue at step 9
            ("casualty", 2, 8),  # Casualty at step 8
            ("rescue", 3, 10)    # Rescue at step 10 (current step)
        ]
        frame = create_test_frame_with_events(event_configs)
        terrain = MockTerrain()
        
        # Render the visualization
        fig = build_plotly_animation(terrain, [frame], speed_ms=800)
        
        # Extract burst trace data
        burst_data = extract_burst_trace_data(fig)
        
        # Check that all bursts appear
        assert burst_data["rescue_count"] == 2, (
            f"Expected 2 rescue bursts (steps 9 and 10), "
            f"but found {burst_data['rescue_count']}"
        )
        assert burst_data["casualty_count"] == 1, (
            f"Expected 1 casualty burst (step 8), "
            f"but found {burst_data['casualty_count']}"
        )
    
    def test_preservation_rescued_victim_styling(self):
        """
        Preservation: Rescued victims should display in transparent green at size 6px
        
        This test verifies that rescued victim styling is working correctly
        and should be preserved when fixing the bugs.
        
        **Validates: Requirements 3.1**
        """
        # Create frame with rescued victim
        victim_configs = [
            (0.9, 0.3, "rescued", 1)  # High risk, low health, but rescued
        ]
        frame = create_test_frame_with_victims(victim_configs)
        terrain = MockTerrain()
        
        # Render the visualization
        fig = build_plotly_animation(terrain, [frame], speed_ms=800)
        
        # Extract victim trace data
        victim_data = extract_victim_trace_data(fig)
        assert victim_data is not None, "Victim trace not found in figure"
        
        # Check rescued victim styling
        colors = victim_data["colors"]
        sizes = victim_data["sizes"]
        
        expected_color = VICTIM_COLORS["rescued"]  # rgba(0,230,118,0.35)
        expected_size = 6
        
        assert colors[0] == expected_color, (
            f"Rescued victim should display in {expected_color}, "
            f"but displays in {colors[0]}"
        )
        assert sizes[0] == expected_size, (
            f"Rescued victim should display at size {expected_size}px, "
            f"but displays at {sizes[0]}px"
        )
    
    def test_preservation_deceased_victim_styling(self):
        """
        Preservation: Deceased victims should display in gray at size 8px
        
        This test verifies that deceased victim styling is working correctly
        and should be preserved when fixing the bugs.
        
        **Validates: Requirements 3.2**
        """
        # Create frame with deceased victim
        victim_configs = [
            (0.9, 0.0, "deceased", 1)  # High risk, no health, deceased
        ]
        frame = create_test_frame_with_victims(victim_configs)
        terrain = MockTerrain()
        
        # Render the visualization
        fig = build_plotly_animation(terrain, [frame], speed_ms=800)
        
        # Extract victim trace data
        victim_data = extract_victim_trace_data(fig)
        assert victim_data is not None, "Victim trace not found in figure"
        
        # Check deceased victim styling
        colors = victim_data["colors"]
        sizes = victim_data["sizes"]
        
        expected_color = VICTIM_COLORS["deceased"]  # #78909c (gray)
        expected_size = 8
        
        assert colors[0] == expected_color, (
            f"Deceased victim should display in {expected_color}, "
            f"but displays in {colors[0]}"
        )
        assert sizes[0] == expected_size, (
            f"Deceased victim should display at size {expected_size}px, "
            f"but displays at {sizes[0]}px"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
