# Victim Color Display Fix - Bugfix Design

## Overview

This bugfix addresses three related visualization defects in the disaster simulation map that prevent proper victim marker rendering. The bugs affect victim colors (all green instead of risk-based red/orange/green), marker sizes (uniform instead of health-based scaling), and burst animations (not appearing at all). These defects undermine the primary purpose of the risk-based visualization system by failing to communicate critical risk and health information to emergency response decision-makers.

The root cause analysis suggests that while the `_victim_marker_props()` function correctly calculates color and size values, the Plotly `Scattermapbox` marker configuration may not be properly applying these values. For burst animations, the event filtering logic may be preventing bursts from displaying, or the event data structure may not match the expected format.

## Glossary

- **Bug_Condition (C)**: The condition that triggers the bug - when victim markers are rendered with incorrect visual properties (color, size) or when burst animations fail to appear despite events being logged
- **Property (P)**: The desired behavior - victim markers should display with risk-based colors (red/orange/green), health-based sizes (10-22px), and rescue/casualty events should display burst animations for 3 frames
- **Preservation**: Existing behaviors that must remain unchanged - rescued/deceased victim styling, tooltips, event log display, other map elements (units, roads, flood layers)
- **composite_risk**: The risk score from `frame["risk_scores"]` dictionary, falling back to the base risk value from the incidents array
- **_victim_marker_props()**: The function in `components/map_renderer.py` that calculates color and size based on risk, health, and status
- **_build_victim_traces()**: The function that constructs the Plotly Scattermapbox trace for victim markers
- **_build_burst_traces()**: The function that constructs burst animation traces for rescue/casualty events
- **Scattermapbox**: Plotly's mapbox scatter plot type that renders markers on a map

## Bug Details

### Bug Condition

The bugs manifest when victim markers are rendered on the map visualization. The `_build_victim_traces()` function correctly calls `_victim_marker_props()` to calculate color and size values, but these values are not being applied correctly to the Plotly visualization. Similarly, `_build_burst_traces()` constructs burst traces but they do not appear on the map.

**Formal Specification:**
```
FUNCTION isBugCondition(input)
  INPUT: input of type VisualizationFrame
  OUTPUT: boolean
  
  RETURN (hasActiveVictims(input) AND allVictimsDisplaySameColor(input))
         OR (hasVictimsWithDifferentHealth(input) AND allVictimsDisplaySameSize(input))
         OR (hasRescueOrCasualtyEvents(input) AND noBurstsVisible(input))
END FUNCTION
```

**Sub-conditions:**
```
FUNCTION hasActiveVictims(frame)
  RETURN EXISTS incident IN frame.incidents WHERE incident.status == "active"
END FUNCTION

FUNCTION allVictimsDisplaySameColor(frame)
  colors := [getDisplayedColor(incident) FOR incident IN frame.incidents WHERE incident.status == "active"]
  RETURN ALL colors are identical (all green)
END FUNCTION

FUNCTION hasVictimsWithDifferentHealth(frame)
  health_values := [incident.health FOR incident IN frame.incidents WHERE incident.status == "active"]
  RETURN MAX(health_values) - MIN(health_values) > 0.2
END FUNCTION

FUNCTION allVictimsDisplaySameSize(frame)
  sizes := [getDisplayedSize(incident) FOR incident IN frame.incidents WHERE incident.status == "active"]
  RETURN MAX(sizes) - MIN(sizes) < 2  // Less than 2 pixels difference
END FUNCTION

FUNCTION hasRescueOrCasualtyEvents(frame)
  current_step := frame.info.step
  RETURN EXISTS event IN frame.event_log WHERE 
    (event.type IN ["rescue", "casualty"]) 
    AND (event.step <= current_step <= event.step + 3)
END FUNCTION

FUNCTION noBurstsVisible(frame)
  RETURN COUNT(visible_burst_markers) == 0
END FUNCTION
```

### Examples

**Bug 1: Victim Colors**
- **Input**: Frame with 3 victims: V1 (risk=0.85, health=0.6), V2 (risk=0.45, health=0.8), V3 (risk=0.15, health=0.9)
- **Expected**: V1 displays red (#ff1744), V2 displays orange (#ff9800), V3 displays green (#4caf50)
- **Actual**: All three victims display green

**Bug 2: Marker Sizes**
- **Input**: Frame with 2 victims: V1 (health=0.2), V2 (health=0.9)
- **Expected**: V1 displays at size 19.6px (10 + 0.8×12), V2 displays at size 11.2px (10 + 0.1×12)
- **Actual**: Both victims display at the same size (likely 10px or a default size)

**Bug 3: Burst Animations**
- **Input**: Frame at step 10 with event_log containing {type: "rescue", victim_id: 5, step: 9}
- **Expected**: Green star burst visible at victim #5's location (event within 3-frame window: 9 ≤ 10 ≤ 12)
- **Actual**: No burst marker visible at any location

**Edge Case: Mixed Status Victims**
- **Input**: Frame with V1 (active, risk=0.9, health=0.3), V2 (rescued), V3 (deceased)
- **Expected**: V1 displays red at size 18.4px, V2 displays transparent green at size 6px, V3 displays gray at size 8px
- **Actual**: V1 displays green at uniform size, V2 and V3 display correctly (preserved behavior)

## Expected Behavior

### Preservation Requirements

**Unchanged Behaviors:**
- Rescued victims must continue to display in transparent green (rgba(0,230,118,0.35)) with size 6 pixels
- Deceased victims must continue to display in gray (#78909c) with size 8 pixels
- Victim tooltips must continue to show correct risk percentages, health percentages, and risk labels (CRITICAL/HIGH/MED/LOW)
- Event log display must continue to show all events from the last frame correctly
- Other map elements (units, roads, flood layers, routes) must continue to render correctly
- Map animation timeline scrubbing must continue to work correctly

**Scope:**
All visualization elements that do NOT involve active victim marker colors, active victim marker sizes, or burst animations should be completely unaffected by this fix. This includes:
- Unit markers (cyan, size 17px)
- Road segment colors (safe/predicted flood/currently flooded)
- Flood density layers and colorscales
- Route traces
- Rescued and deceased victim styling
- Tooltip content and formatting

## Hypothesized Root Cause

Based on the bug description and code analysis, the most likely issues are:

1. **Plotly Marker Color Format Issue**: The `marker=dict(color=colors, ...)` configuration may not be correctly interpreting the color list. Plotly Scattermapbox may require a different format (e.g., a single color string when all markers should have different colors, or may not support per-marker color lists in the same way as regular scatter plots).

2. **Marker Dictionary Structure**: The `marker=dict(size=sizes, color=colors, opacity=1.0)` may need to specify colors and sizes differently. Plotly may require `marker_color` and `marker_size` as separate parameters rather than nested in the `marker` dict.

3. **Color Value Format**: The color strings from `VICTIM_COLORS` dictionary may not be in a format Plotly recognizes. While CSS color strings like "#ff1744" should work, the rgba() format for rescued victims might be causing issues that cascade to other markers.

4. **Burst Event Filtering Logic**: The condition `evt_step <= current_step <= evt_step + BURST_DURATION_FRAMES` may be too restrictive or the event data structure may not have the expected `step` field. Events may be stored with different field names or the step comparison may be failing.

5. **Event Type Field Inconsistency**: The code checks both `evt.get("type")` and `evt.get("event_type", "")`, suggesting inconsistent event data structure. If events use a different field name, bursts won't be created.

6. **Burst Trace Ordering**: The burst traces may be created correctly but rendered behind other layers (z-order issue), making them invisible even though they exist.

## Correctness Properties

Property 1: Bug Condition - Victim Markers Display Risk-Based Colors and Health-Based Sizes

_For any_ visualization frame where active victims exist with different risk levels or health values, the fixed rendering function SHALL display each victim marker with a color corresponding to its risk level (red for high ≥0.66, orange for mid 0.33-0.66, green for low <0.33) and a size corresponding to its health (10 + (1.0 - health) × 12 pixels).

**Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 2.10**

Property 2: Bug Condition - Burst Animations Display for Rescue and Casualty Events

_For any_ visualization frame where rescue or casualty events occurred within the last 3 frames (event.step ≤ current_step ≤ event.step + 3), the fixed rendering function SHALL display burst markers (green star for rescue, red X for casualty) at the corresponding victim locations.

**Validates: Requirements 2.11, 2.12, 2.13, 2.14**

Property 3: Preservation - Rescued and Deceased Victim Styling

_For any_ visualization frame containing rescued or deceased victims, the fixed rendering function SHALL produce exactly the same visual styling as the original function, preserving transparent green (rgba(0,230,118,0.35)) at size 6px for rescued victims and gray (#78909c) at size 8px for deceased victims.

**Validates: Requirements 3.1, 3.2**

Property 4: Preservation - Non-Victim Map Elements

_For any_ visualization frame, the fixed rendering function SHALL produce exactly the same rendering as the original function for all non-victim elements including units, roads, flood layers, routes, and tooltips.

**Validates: Requirements 3.3, 3.4, 3.5, 3.6, 3.7, 3.8**

## Fix Implementation

### Changes Required

Assuming our root cause analysis is correct, the fix will focus on the Plotly marker configuration in `_build_victim_traces()` and event filtering logic in `_build_burst_traces()`.

**File**: `components/map_renderer.py`

**Function**: `_build_victim_traces()`

**Specific Changes**:

1. **Verify Plotly Marker Color/Size Format**: Research Plotly Scattermapbox documentation to confirm the correct way to specify per-marker colors and sizes. The current approach uses `marker=dict(size=sizes, color=colors, opacity=1.0)` which should work, but may need adjustment.

2. **Test Color Value Format**: Ensure all color values in `VICTIM_COLORS` dictionary are in a format Plotly recognizes. Convert rgba() strings to a consistent format if needed.

3. **Add Debugging Output**: Temporarily add print statements to verify that:
   - `_victim_marker_props()` is returning correct color and size values
   - The `colors` and `sizes` lists contain the expected values before being passed to Plotly
   - The Plotly trace is being constructed with the correct parameters

4. **Alternative Marker Configuration**: If the current approach doesn't work, try alternative Plotly configurations:
   - Use `marker_color=colors` and `marker_size=sizes` as separate parameters instead of nested dict
   - Create separate traces for each risk level (high/mid/low) instead of one trace with multiple colors
   - Use `marker=go.scattermapbox.Marker(color=colors, size=sizes, opacity=1.0)` instead of dict

**Function**: `_build_burst_traces()`

**Specific Changes**:

1. **Debug Event Data Structure**: Add logging to inspect the actual structure of events in `frame.get("event_log", [])`:
   - Verify events have the expected fields (`type`, `victim_id`, `step`)
   - Check if field names are different (e.g., `event_type` vs `type`)
   - Confirm the step values are integers and the comparison logic works

2. **Simplify Event Filtering**: Test with a simpler condition first to isolate the issue:
   - Remove the 3-frame window check temporarily and show all events
   - Verify bursts appear when filtering is removed
   - Then re-add the window logic with corrected field names

3. **Check Trace Z-Order**: Ensure burst traces are added to the figure after other traces so they render on top:
   - Verify the order in which traces are added in `build_plotly_animation()`
   - Burst traces should be last in the traces list

4. **Verify Burst Trace Configuration**: Confirm the Scattermapbox configuration for bursts is correct:
   - Symbol types "star" and "x" are valid for Plotly Scattermapbox
   - Size 30 is appropriate and visible
   - Opacity 0.7 is sufficient for visibility

5. **Test with Known Events**: Create a test frame with a known rescue event and verify the burst appears:
   - Manually construct a frame with `event_log=[{"type": "rescue", "victim_id": 1, "step": 0}]`
   - Verify the burst trace is created with non-empty lat/lon lists
   - Confirm the burst is visible in the rendered visualization

## Testing Strategy

### Validation Approach

The testing strategy follows a two-phase approach: first, surface counterexamples that demonstrate the bugs on unfixed code, then verify the fix works correctly and preserves existing behavior.

### Exploratory Bug Condition Checking

**Goal**: Surface counterexamples that demonstrate the bugs BEFORE implementing the fix. Confirm or refute the root cause analysis. If we refute, we will need to re-hypothesize.

**Test Plan**: Write tests that create visualization frames with known victim states and event logs, render them using the UNFIXED code, and inspect the resulting Plotly figure to verify that colors, sizes, and bursts are incorrect. This will confirm the bug and help identify the root cause.

**Test Cases**:

1. **High Risk Victim Color Test**: Create frame with victim (risk=0.85, health=0.6, status="active"), render, inspect marker color
   - **Expected on unfixed code**: Marker color is green (incorrect)
   - **Confirms**: Bug 1 - victim colors not risk-based

2. **Low Health Victim Size Test**: Create frame with victim (risk=0.5, health=0.2, status="active"), render, inspect marker size
   - **Expected on unfixed code**: Marker size is uniform/default (incorrect)
   - **Confirms**: Bug 2 - marker sizes not health-based

3. **Rescue Burst Test**: Create frame at step 10 with event_log containing {type: "rescue", victim_id: 1, step: 9}, render, inspect burst traces
   - **Expected on unfixed code**: No burst markers visible (incorrect)
   - **Confirms**: Bug 3 - burst animations not appearing

4. **Multiple Risk Levels Test**: Create frame with 3 victims (risk=0.9, 0.5, 0.1), render, inspect all marker colors
   - **Expected on unfixed code**: All markers same color (incorrect)
   - **Confirms**: Bug 1 affects all risk levels

5. **Rescued Victim Preservation Test**: Create frame with rescued victim, render, inspect marker color and size
   - **Expected on unfixed code**: Transparent green, size 6px (correct - preserved behavior)
   - **Confirms**: Rescued victim styling is working correctly

**Expected Counterexamples**:
- Plotly figure's victim trace will have `marker.color` as a single value or incorrect list
- Plotly figure's victim trace will have `marker.size` as a single value or incorrect list
- Plotly figure's burst traces will have empty `lat` and `lon` lists
- Possible causes: Plotly marker configuration format, color value format, event filtering logic, event data structure mismatch

### Fix Checking

**Goal**: Verify that for all inputs where the bug condition holds, the fixed function produces the expected behavior.

**Pseudocode:**
```
FOR ALL frame WHERE isBugCondition(frame) DO
  result := build_plotly_animation_fixed(frame)
  ASSERT expectedBehavior(result)
END FOR
```

**Expected Behavior Verification:**
```
FUNCTION expectedBehavior(plotly_figure)
  victim_trace := findTraceByName(plotly_figure, "Victims")
  
  // Verify colors are risk-based
  FOR EACH victim IN frame.incidents WHERE victim.status == "active" DO
    expected_color := getExpectedColor(victim.risk)
    actual_color := victim_trace.marker.color[victim.index]
    ASSERT actual_color == expected_color
  END FOR
  
  // Verify sizes are health-based
  FOR EACH victim IN frame.incidents WHERE victim.status == "active" DO
    expected_size := 10 + (1.0 - victim.health) * 12
    actual_size := victim_trace.marker.size[victim.index]
    ASSERT abs(actual_size - expected_size) < 0.1
  END FOR
  
  // Verify bursts appear for recent events
  FOR EACH event IN frame.event_log WHERE isWithinBurstWindow(event, frame.step) DO
    burst_trace := findBurstTrace(plotly_figure, event.type)
    ASSERT event.victim_location IN burst_trace.coordinates
  END FOR
  
  RETURN true
END FUNCTION
```

### Preservation Checking

**Goal**: Verify that for all inputs where the bug condition does NOT hold (rescued/deceased victims, other map elements), the fixed function produces the same result as the original function.

**Pseudocode:**
```
FOR ALL frame WHERE NOT isBugCondition(frame) DO
  ASSERT build_plotly_animation_original(frame) = build_plotly_animation_fixed(frame)
END FOR

// Also check preserved elements within frames that DO have the bug
FOR ALL frame WHERE isBugCondition(frame) DO
  original_fig := build_plotly_animation_original(frame)
  fixed_fig := build_plotly_animation_fixed(frame)
  
  // Verify rescued/deceased victims unchanged
  ASSERT getRescuedVictimStyling(original_fig) = getRescuedVictimStyling(fixed_fig)
  ASSERT getDeceasedVictimStyling(original_fig) = getDeceasedVictimStyling(fixed_fig)
  
  // Verify other map elements unchanged
  ASSERT getUnitTraces(original_fig) = getUnitTraces(fixed_fig)
  ASSERT getRoadTraces(original_fig) = getRoadTraces(fixed_fig)
  ASSERT getFloodTraces(original_fig) = getFloodTraces(fixed_fig)
  ASSERT getTooltips(original_fig) = getTooltips(fixed_fig)
END FOR
```

**Testing Approach**: Property-based testing is recommended for preservation checking because:
- It generates many test cases automatically across the input domain
- It catches edge cases that manual unit tests might miss
- It provides strong guarantees that behavior is unchanged for all non-buggy inputs

**Test Plan**: Observe behavior on UNFIXED code first for rescued/deceased victims and other map elements, then write property-based tests capturing that behavior.

**Test Cases**:

1. **Rescued Victim Preservation**: Generate random frames with rescued victims, verify color is rgba(0,230,118,0.35) and size is 6px in both original and fixed code

2. **Deceased Victim Preservation**: Generate random frames with deceased victims, verify color is #78909c and size is 8px in both original and fixed code

3. **Tooltip Preservation**: Generate random frames with various victim states, verify tooltip text (risk %, health %, labels) is identical in both original and fixed code

4. **Unit Marker Preservation**: Generate random frames with units, verify unit traces (color, size, position) are identical in both original and fixed code

5. **Road Classification Preservation**: Generate random frames with various flood states, verify road traces (safe/predicted/flooded colors) are identical in both original and fixed code

6. **Flood Layer Preservation**: Generate random frames with various flood depths, verify flood density layers are identical in both original and fixed code

### Unit Tests

- Test `_victim_marker_props()` with various risk/health/status combinations to verify correct color and size calculation
- Test `_build_victim_traces()` with frames containing victims at different risk levels to verify Plotly trace has correct marker colors
- Test `_build_victim_traces()` with frames containing victims at different health levels to verify Plotly trace has correct marker sizes
- Test `_build_burst_traces()` with frames containing rescue events to verify burst traces have non-empty coordinates
- Test `_build_burst_traces()` with frames containing casualty events to verify burst traces have non-empty coordinates
- Test `_build_burst_traces()` with events outside the 3-frame window to verify bursts are not created
- Test edge cases: empty frames, frames with only rescued victims, frames with only deceased victims

### Property-Based Tests

- Generate random frames with N victims (1 ≤ N ≤ 20) with random risk values (0.0 to 1.0) and verify each marker has the correct risk-based color
- Generate random frames with N victims with random health values (0.0 to 1.0) and verify each marker has the correct health-based size
- Generate random event logs with rescue/casualty events at various steps and verify bursts appear in the correct frames
- Generate random frames with mixed victim statuses (active/rescued/deceased) and verify rescued/deceased styling is preserved
- Generate random frames and verify all non-victim map elements (units, roads, floods) are identical between original and fixed code

### Integration Tests

- Test full animation sequence with victims transitioning through different risk levels and verify colors update correctly
- Test full animation sequence with victims losing health over time and verify sizes increase correctly
- Test full animation sequence with rescue events occurring and verify bursts appear for 3 frames then disappear
- Test full animation sequence with casualty events occurring and verify bursts appear for 3 frames then disappear
- Test map timeline scrubbing (jumping to different frames) and verify victim markers and bursts render correctly at each frame
- Test with real simulation data to verify the fix works with actual game frames
