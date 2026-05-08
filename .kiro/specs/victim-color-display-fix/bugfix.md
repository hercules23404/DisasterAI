# Bugfix Requirements Document

## Introduction

This document specifies the requirements for fixing three related visualization bugs in the disaster simulation map that prevent proper victim marker rendering. The bugs affect victim colors, marker sizes, and burst animations - all critical visual indicators for emergency response decision-making.

**Bugs identified:**
1. **Victim colors**: All victims display in green regardless of risk level (should be red/orange/green)
2. **Marker sizes**: All victims display at the same size regardless of health (should scale 10-22px based on health)
3. **Burst animations**: Rescue and casualty bursts do not appear at all (should display as stars/X marks for 3 frames)

**Impact:** The visualization fails to communicate critical risk and health information to users, making it impossible to visually identify high-risk victims, critically injured victims, or recent rescue/casualty events. This undermines the primary purpose of the risk-based visualization system.

**Context:** The event log fix (showing all events from last frame) is working correctly. The victim marker logic exists in `_victim_marker_props()`, `_build_victim_traces()`, and `_build_burst_traces()` functions in `components/map_renderer.py`, but the visual properties are not being applied correctly to the Plotly visualization.

## Bug Analysis

### Current Behavior (Defect)

**Bug 1: Victim Colors**

1.1 WHEN victims with high risk (composite_risk >= 0.66) are displayed on the map THEN the system shows them in green color instead of red (#ff1744)

1.2 WHEN victims with mid risk (0.33 <= composite_risk < 0.66) are displayed on the map THEN the system shows them in green color instead of orange (#ff9800)

1.3 WHEN victims with low risk (composite_risk < 0.33) are displayed on the map THEN the system shows them in green color (correct color but possibly by accident)

1.4 WHEN the map animation plays through multiple frames THEN all active victims consistently appear in green regardless of their changing risk scores

1.5 WHEN hovering over victim markers THEN the tooltip shows correct risk percentages and labels (CRITICAL/HIGH/MED/LOW) but the marker color does not match

**Bug 2: Marker Sizes**

1.6 WHEN victims with low health (health < 0.5) are displayed on the map THEN the system shows them at the same size as healthy victims instead of larger size

1.7 WHEN victims with high health (health > 0.8) are displayed on the map THEN the system shows them at the same size as injured victims instead of smaller size

1.8 WHEN victim health changes between frames THEN the marker size does not change to reflect the health deterioration

1.9 WHEN all active victims are displayed THEN they all appear at the same uniform size regardless of their individual health values

**Bug 3: Burst Animations**

1.10 WHEN a rescue event occurs THEN the system does not display a green star burst at the victim location

1.11 WHEN a casualty event occurs THEN the system does not display a red X burst at the victim location

1.12 WHEN the event log shows rescue/casualty events THEN no corresponding visual burst animations appear on the map

1.13 WHEN the map animation plays through frames with logged rescue/casualty events THEN no burst markers are visible at any time

### Expected Behavior (Correct)

**Bug 1: Victim Colors**

2.1 WHEN victims with high risk (composite_risk >= 0.66) are displayed on the map THEN the system SHALL render them in red color (#ff1744)

2.2 WHEN victims with mid risk (0.33 <= composite_risk < 0.66) are displayed on the map THEN the system SHALL render them in orange color (#ff9800)

2.3 WHEN victims with low risk (composite_risk < 0.33) are displayed on the map THEN the system SHALL render them in green color (#4caf50)

2.4 WHEN a victim's risk level changes between frames THEN the system SHALL update the marker color to reflect the new risk level

2.5 WHEN hovering over victim markers THEN the tooltip risk information SHALL match the visual marker color

**Bug 2: Marker Sizes**

2.6 WHEN victims with health = 1.0 (full health) are displayed THEN the system SHALL render markers at size 10 pixels

2.7 WHEN victims with health = 0.0 (critical) are displayed THEN the system SHALL render markers at size 22 pixels

2.8 WHEN victims with health between 0.0 and 1.0 are displayed THEN the system SHALL render markers at size = 10 + (1.0 - health) × 12 pixels

2.9 WHEN victim health deteriorates between frames THEN the system SHALL increase the marker size proportionally

2.10 WHEN multiple victims with different health values are displayed THEN each SHALL have a distinct size reflecting their individual health

**Bug 3: Burst Animations**

2.11 WHEN a rescue event occurs at step N THEN the system SHALL display a green star burst at the victim location for frames N through N+3

2.12 WHEN a casualty event occurs at step N THEN the system SHALL display a red X burst at the victim location for frames N through N+3

2.13 WHEN multiple rescue/casualty events occur at different steps THEN each SHALL display its burst independently according to the 3-frame visibility window

2.14 WHEN the event log shows rescue/casualty events THEN corresponding burst animations SHALL be visible on the map at the victim locations

### Unchanged Behavior (Regression Prevention)

3.1 WHEN victims are rescued THEN the system SHALL CONTINUE TO display them in transparent green (rgba(0,230,118,0.35)) with size 6 pixels regardless of their previous risk level or health

3.2 WHEN victims are deceased THEN the system SHALL CONTINUE TO display them in gray (#78909c) with size 8 pixels regardless of their previous risk level or health

3.3 WHEN the event log displays events THEN the system SHALL CONTINUE TO show all events from the last frame correctly

3.4 WHEN the map animation timeline is scrubbed THEN the system SHALL CONTINUE TO update all other elements (flood depth, units, routes) correctly

3.5 WHEN victim tooltips are displayed THEN the system SHALL CONTINUE TO show correct risk percentages, health percentages, and risk labels

3.6 WHEN unit markers are displayed THEN the system SHALL CONTINUE TO render at size 17 pixels in cyan color (#00bcd4)

3.7 WHEN road segments are classified THEN the system SHALL CONTINUE TO display in correct colors (safe/predicted flood/currently flooded)

3.8 WHEN flood density layers are rendered THEN the system SHALL CONTINUE TO display with correct colorscales and opacity
