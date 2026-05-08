# Requirements Document

## Introduction

This document specifies the requirements for fixing three critical visualization issues in the DisasterAI dashboard: victim marker colors not reflecting risk levels, event log displaying zero events, and lack of visual feedback for rescue operations. These fixes restore correct visual representation of simulation state without architectural changes.

## Glossary

- **Victim_Marker**: Visual representation of a victim on the map, displayed as a colored dot with size indicating health status
- **Risk_Level**: Composite score (0.0-1.0) indicating urgency of victim situation, categorized as low (<0.33), mid (0.33-0.66), or high (≥0.66)
- **Event_Log**: Chronological list of simulation events (rescues, casualties, discoveries) displayed in the dashboard
- **Burst_Animation**: Visual effect (star-shaped marker) shown at victim location when rescue or casualty event occurs
- **Frame**: Single timestep snapshot of simulation state, including terrain, victims, agents, and events
- **Current_Step**: The simulation timestep currently being displayed to the user
- **Map_Renderer**: Component responsible for building Plotly map visualization with victim markers and burst animations
- **Event_Log_Component**: UI component that displays filtered list of events for current timestep

## Requirements

### Requirement 1: Victim Marker Color Accuracy

**User Story:** As a disaster response coordinator, I want victim markers to display colors matching their risk levels, so that I can quickly identify which victims need immediate attention.

#### Acceptance Criteria

1. WHEN a victim has high risk (≥0.66) and status is "active", THE Map_Renderer SHALL display the marker in red color (#ff1744)
2. WHEN a victim has mid risk (0.33-0.66) and status is "active", THE Map_Renderer SHALL display the marker in orange color (#ff9800)
3. WHEN a victim has low risk (<0.33) and status is "active", THE Map_Renderer SHALL display the marker in green color (#4caf50)
4. WHEN a victim has status "rescued", THE Map_Renderer SHALL display the marker in transparent green color (rgba(0,230,118,0.35)) regardless of risk level
5. WHEN a victim has status "deceased", THE Map_Renderer SHALL display the marker in gray color regardless of risk level
6. FOR ALL victims in any frame, THE Map_Renderer SHALL apply the color list correctly to Plotly Scattermapbox markers

### Requirement 2: Event Log Data Accuracy

**User Story:** As a disaster response coordinator, I want the event log to show all events that have occurred up to the current timestep, so that I can review the simulation history accurately.

#### Acceptance Criteria

1. WHEN the user views any frame in the simulation, THE Event_Log_Component SHALL display events from that specific frame's event log
2. WHEN the user scrubs the timeline to a different frame, THE Event_Log_Component SHALL update to show events from the newly selected frame
3. WHEN filtering events by current step, THE Event_Log_Component SHALL use the step number from the current frame being displayed
4. WHEN a frame contains N events, THE Event_Log_Component SHALL display "N events" in the popover label
5. IF the current frame has no events, THEN THE Event_Log_Component SHALL display "No events yet"
6. WHEN the simulation cache is empty or invalid, THE Event_Log_Component SHALL handle gracefully by displaying zero events

### Requirement 3: Rescue Visual Feedback

**User Story:** As a disaster response coordinator, I want to see visual feedback when victims are rescued, so that I can confirm rescue operations are being executed successfully.

#### Acceptance Criteria

1. WHEN a rescue event occurs at step S, THE Map_Renderer SHALL display a burst animation at the victim's location for frames S through S+3
2. WHEN a casualty event occurs at step S, THE Map_Renderer SHALL display a burst animation at the victim's location for frames S through S+3
3. WHEN the user scrubs to a frame within the burst visibility window, THE Map_Renderer SHALL display the burst animation
4. WHEN the user scrubs to a frame outside the burst visibility window, THE Map_Renderer SHALL hide the burst animation
5. WHEN multiple rescue events occur at different steps, THE Map_Renderer SHALL display bursts for all events within their respective visibility windows
6. IF an event references a victim_id that does not exist in the incidents list, THEN THE Map_Renderer SHALL skip that burst without affecting other bursts

### Requirement 4: Victim Marker Size Scaling

**User Story:** As a disaster response coordinator, I want victim marker sizes to reflect their health status, so that I can visually identify victims in critical condition.

#### Acceptance Criteria

1. WHEN a victim has status "active", THE Map_Renderer SHALL calculate marker size as 10 + (1.0 - health) × 12 pixels
2. WHEN a victim has health 1.0 (full health), THE Map_Renderer SHALL display marker size of 10 pixels
3. WHEN a victim has health 0.0 (critical), THE Map_Renderer SHALL display marker size of 22 pixels
4. WHEN a victim has status "rescued", THE Map_Renderer SHALL display marker size of 6 pixels regardless of health
5. WHEN a victim has status "deceased", THE Map_Renderer SHALL display marker size of 8 pixels regardless of health
6. FOR ALL active victims, THE Map_Renderer SHALL ensure lower health results in larger marker size

### Requirement 5: Error Handling and Robustness

**User Story:** As a system operator, I want the visualization to handle missing or invalid data gracefully, so that the dashboard remains functional even with incomplete data.

#### Acceptance Criteria

1. IF a frame does not contain an "event_log" key, THEN THE Map_Renderer SHALL use an empty list as default
2. IF the current_frame index is greater than the number of frames, THEN THE system SHALL clamp it to the last valid frame index
3. IF the current_frame index is negative, THEN THE system SHALL clamp it to zero
4. IF an event references a victim_id not found in the incidents list, THEN THE Map_Renderer SHALL skip that event and continue processing other events
5. WHEN the simulation cache is None or empty, THE Event_Log_Component SHALL display zero events without throwing errors
6. FOR ALL error conditions, THE system SHALL maintain partial functionality and not crash the dashboard
