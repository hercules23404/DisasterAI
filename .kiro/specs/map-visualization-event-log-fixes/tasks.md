# Implementation Plan: Map Visualization and Event Log Fixes

## Overview

This plan implements three surgical fixes to the DisasterAI dashboard visualization: (1) correct event log data flow to show current frame's events, (2) extend burst visibility duration from 1 to 3 frames, and (3) verify victim color application. All changes are minimal modifications to existing rendering logic without architectural changes.

## Tasks

- [x] 1. Fix event log data flow in simulation view
  - Modify `views/simulation.py` to pass current frame's event log instead of cached final frame
  - Extract events from `cache["frames"][current_idx]` instead of `cache["event_log"]`
  - Extract current step from frame data: `current_frame_data.get("step", current_idx)`
  - Add bounds checking for `current_frame` index to prevent out-of-range errors
  - Update event log rendering call to use frame-specific events and step
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 5.2, 5.3, 5.5_

- [x] 2. Extend burst visibility duration in map renderer
  - Modify `components/map_renderer.py` in `_build_burst_traces()` function
  - Add constant `BURST_DURATION_FRAMES = 3` at module or function level
  - Replace exact step match condition `if evt.get("step") != current_step` with range check
  - Implement visibility window: `if not (evt_step <= current_step <= evt_step + BURST_DURATION_FRAMES)`
  - Ensure bursts appear for rescue and casualty events within 3-frame window
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 3. Verify and document victim color application
  - Review `components/map_renderer.py` in `_build_victim_traces()` function
  - Verify that `colors` list is correctly populated from `_victim_marker_props()`
  - Verify Plotly Scattermapbox trace uses `marker=dict(color=colors)` correctly
  - Confirm VICTIM_COLORS dictionary contains valid CSS color strings
  - Add inline comment documenting that colors list must contain valid CSS strings
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6_

- [ ]* 4. Write property test for event log data flow accuracy
  - **Property 2: Event Log Data Flow Accuracy**
  - **Validates: Requirements 2.1, 2.3, 2.4**
  - Create test file `tests/test_event_log_properties.py`
  - Use hypothesis library to generate random frame data with varying event counts
  - Test that filtered events count equals events where `event.step <= current_step`
  - Test that events list comes from correct frame index
  - Verify bounds checking prevents index errors

- [ ]* 5. Write property test for burst visibility window
  - **Property 3: Burst Visibility Window**
  - **Validates: Requirements 3.1, 3.2, 3.5**
  - Create test file `tests/test_burst_visibility_properties.py`
  - Use hypothesis to generate random event steps and current steps
  - Assert burst visible if and only if `event_step <= current_step <= event_step + 3`
  - Test multiple events at different steps have independent visibility windows
  - Verify burst count matches events in visibility window

- [ ]* 6. Write unit tests for victim color mapping
  - Create test file `tests/test_victim_colors.py`
  - Test high-risk victim (risk >= 0.66) returns red color (#ff1744)
  - Test mid-risk victim (0.33 <= risk < 0.66) returns orange color (#ff9800)
  - Test low-risk victim (risk < 0.33) returns green color (#4caf50)
  - Test rescued status returns transparent green regardless of risk
  - Test deceased status returns gray color regardless of risk
  - Test edge cases: risk=0.0, risk=1.0, health=0.0, health=1.0
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [ ]* 7. Write unit tests for marker size calculation
  - Create test file `tests/test_marker_size.py`
  - Test active victim size formula: `10 + (1.0 - health) × 12`
  - Test health=1.0 returns size 10 pixels
  - Test health=0.0 returns size 22 pixels
  - Test rescued status returns size 6 pixels regardless of health
  - Test deceased status returns size 8 pixels regardless of health
  - Test inverse relationship: lower health produces larger size
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_

- [x] 8. Checkpoint - Verify fixes and run tests
  - Run the dashboard and verify event log shows correct event count
  - Scrub timeline and verify event log updates with each frame
  - Verify rescue bursts appear for 3 frames after rescue events
  - Verify victim markers show correct colors (red/orange/green based on risk)
  - Run all tests if created: `pytest tests/`
  - Ensure all tests pass, ask the user if questions arise

- [ ]* 9. Write integration test for end-to-end event flow
  - Create test file `tests/test_integration_event_flow.py`
  - Run simulation for 10 steps
  - Verify each frame's event_log contains all events up to that step
  - Verify event log popover shows correct count for each frame
  - Test scrubbing timeline updates event log correctly
  - Test that frame index clamping works at boundaries (0 and max)
  - _Requirements: 2.1, 2.2, 2.3, 5.2, 5.3_

- [x] 10. Final checkpoint - Complete verification
  - Ensure all implementation tasks are complete
  - Verify all three fixes are working correctly in the dashboard
  - Confirm no regressions in existing functionality
  - Document any edge cases discovered during testing
  - Ensure all tests pass, ask the user if questions arise

## Notes

- Tasks marked with `*` are optional and can be skipped for faster delivery
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at reasonable breaks
- Property tests validate universal correctness properties from the design
- Unit tests validate specific examples and edge cases
- All changes are surgical fixes to existing code without architectural modifications
- The design document provides detailed pseudocode and specifications for each fix
