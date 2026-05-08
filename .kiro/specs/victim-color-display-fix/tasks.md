# Implementation Plan

## Overview

This task list implements fixes for three related visualization bugs in the disaster simulation map: victim colors (all green instead of risk-based), marker sizes (uniform instead of health-based), and burst animations (not appearing). The implementation follows the exploratory bugfix workflow: explore the bugs first with tests, preserve existing behavior, then implement the fix.

---

## Tasks

- [x] 1. Write bug condition exploration test
  - **Property 1: Bug Condition** - Victim Markers Display Incorrect Visual Properties
  - **CRITICAL**: This test MUST FAIL on unfixed code - failure confirms the bugs exist
  - **DO NOT attempt to fix the test or the code when it fails**
  - **NOTE**: This test encodes the expected behavior - it will validate the fix when it passes after implementation
  - **GOAL**: Surface counterexamples that demonstrate the three bugs exist (colors, sizes, bursts)
  - **Scoped PBT Approach**: Test concrete failing cases with known victim states and events
  - Test implementation details from Bug Condition in design:
    - Create frame with victims at different risk levels (0.85, 0.45, 0.15) and verify colors are NOT risk-based (all green)
    - Create frame with victims at different health levels (0.2, 0.9) and verify sizes are NOT health-based (uniform)
    - Create frame with rescue/casualty events within 3-frame window and verify bursts are NOT visible
  - The test assertions should match the Expected Behavior Properties from design:
    - High risk (≥0.66) should display red (#ff1744)
    - Mid risk (0.33-0.66) should display orange (#ff9800)
    - Low risk (<0.33) should display green (#4caf50)
    - Size should equal 10 + (1.0 - health) × 12 pixels
    - Rescue events should display green star bursts for 3 frames
    - Casualty events should display red X bursts for 3 frames
  - Run test on UNFIXED code
  - **EXPECTED OUTCOME**: Test FAILS (this is correct - it proves the bugs exist)
  - Document counterexamples found:
    - Which victims display incorrect colors
    - Which victims display incorrect sizes
    - Which bursts fail to appear
  - Analyze Plotly figure structure to understand root cause:
    - Inspect `marker.color` and `marker.size` in victim trace
    - Inspect burst trace coordinates (lat/lon lists)
    - Check if issue is marker configuration format, color value format, or event filtering
  - Mark task complete when test is written, run, failure is documented, and root cause is analyzed
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 1.10, 1.11, 1.12, 1.13_

- [ ] 2. Write preservation property tests (BEFORE implementing fix)
  - **Property 2: Preservation** - Rescued/Deceased Victims and Other Map Elements
  - **IMPORTANT**: Follow observation-first methodology
  - Observe behavior on UNFIXED code for non-buggy elements:
    - Rescued victims display in transparent green (rgba(0,230,118,0.35)) at size 6px
    - Deceased victims display in gray (#78909c) at size 8px
    - Victim tooltips show correct risk percentages, health percentages, and labels
    - Unit markers display in cyan (#00bcd4) at size 17px
    - Road segments display in correct colors (safe/predicted flood/currently flooded)
    - Flood density layers display with correct colorscales and opacity
  - Write property-based tests capturing observed behavior patterns from Preservation Requirements:
    - For all frames with rescued victims, verify color and size match expected values
    - For all frames with deceased victims, verify color and size match expected values
    - For all frames, verify tooltips contain correct risk/health information
    - For all frames, verify unit traces are unchanged
    - For all frames, verify road traces are unchanged
    - For all frames, verify flood traces are unchanged
  - Property-based testing generates many test cases for stronger guarantees
  - Run tests on UNFIXED code
  - **EXPECTED OUTCOME**: Tests PASS (this confirms baseline behavior to preserve)
  - Mark task complete when tests are written, run, and passing on unfixed code
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8_

- [ ] 3. Fix victim marker colors, sizes, and burst animations

  - [ ] 3.1 Implement the fix for victim colors and sizes in `_build_victim_traces()`
    - Based on root cause analysis from task 1, fix the Plotly marker configuration
    - Possible fixes (apply based on root cause):
      - Verify `marker=dict(size=sizes, color=colors, opacity=1.0)` format is correct for Plotly Scattermapbox
      - Try alternative: `marker_color=colors, marker_size=sizes` as separate parameters
      - Ensure color values are in correct format (CSS color strings like "#ff1744")
      - Test with separate traces per risk level if single trace with multiple colors doesn't work
    - Verify `_victim_marker_props()` is being called correctly and returns expected values
    - Add assertions to ensure colors and sizes lists have correct length and values
    - Test with a simple frame to verify fix works before running full test suite
    - _Bug_Condition: isBugCondition(input) where hasActiveVictims(input) AND (allVictimsDisplaySameColor(input) OR allVictimsDisplaySameSize(input))_
    - _Expected_Behavior: For all active victims, marker color matches risk level (red/orange/green) and size equals 10 + (1.0 - health) × 12_
    - _Preservation: Rescued victims remain rgba(0,230,118,0.35) at 6px, deceased remain #78909c at 8px_
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 2.10, 3.1, 3.2_

  - [ ] 3.2 Implement the fix for burst animations in `_build_burst_traces()`
    - Based on root cause analysis from task 1, fix the event filtering and burst trace creation
    - Possible fixes (apply based on root cause):
      - Debug event data structure: verify events have expected fields (type, victim_id, step)
      - Fix field name inconsistency: check if events use "event_type" instead of "type"
      - Simplify event filtering: test without 3-frame window first, then re-add with correct logic
      - Verify burst traces are added last in trace list for correct z-order
      - Confirm Scattermapbox symbol types "star" and "x" are valid
      - Test with manually constructed event to verify burst appears
    - Add logging to inspect actual event structure during debugging
    - Verify burst coordinates (lat/lon) are non-empty when events exist
    - Test with a simple frame containing a known rescue event to verify fix works
    - _Bug_Condition: isBugCondition(input) where hasRescueOrCasualtyEvents(input) AND noBurstsVisible(input)_
    - _Expected_Behavior: For all rescue/casualty events within 3-frame window, burst markers appear at victim locations_
    - _Preservation: Other map elements (units, roads, floods) remain unchanged_
    - _Requirements: 2.11, 2.12, 2.13, 2.14, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8_

  - [ ] 3.3 Verify bug condition exploration test now passes
    - **Property 1: Expected Behavior** - Victim Markers Display Correct Visual Properties
    - **IMPORTANT**: Re-run the SAME test from task 1 - do NOT write a new test
    - The test from task 1 encodes the expected behavior
    - When this test passes, it confirms the expected behavior is satisfied
    - Run bug condition exploration test from step 1
    - **EXPECTED OUTCOME**: Test PASSES (confirms bugs are fixed)
    - Verify all three bugs are resolved:
      - Victims display risk-based colors (red/orange/green)
      - Victims display health-based sizes (10-22px)
      - Rescue/casualty bursts appear for 3 frames
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 2.10, 2.11, 2.12, 2.13, 2.14_

  - [ ] 3.4 Verify preservation tests still pass
    - **Property 2: Preservation** - Rescued/Deceased Victims and Other Map Elements
    - **IMPORTANT**: Re-run the SAME tests from task 2 - do NOT write new tests
    - Run preservation property tests from step 2
    - **EXPECTED OUTCOME**: Tests PASS (confirms no regressions)
    - Confirm all preserved behaviors still work:
      - Rescued victims still display in transparent green at 6px
      - Deceased victims still display in gray at 8px
      - Tooltips still show correct information
      - Units, roads, and flood layers still render correctly
    - If any preservation test fails, investigate and fix the regression before proceeding
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8_

- [ ] 4. Checkpoint - Ensure all tests pass
  - Run complete test suite including bug condition and preservation tests
  - Verify all tests pass without failures
  - Test with real simulation data to ensure fix works with actual game frames
  - Test map animation timeline scrubbing to verify markers and bursts render correctly at all frames
  - If any issues arise, document them and ask the user for guidance
  - Mark complete when all tests pass and visual verification confirms correct behavior

---

## Notes

- **Test Framework**: Use pytest for Python tests, create test file at `tests/test_victim_visualization.py`
- **Test Data**: Create helper functions to generate test frames with known victim states and events
- **Visual Verification**: After tests pass, manually inspect the rendered map to confirm visual correctness
- **Root Cause**: The exploration test (task 1) will help identify whether the issue is Plotly marker configuration, color format, or event filtering logic
- **Debugging**: Add temporary print/logging statements during exploration to inspect Plotly figure structure and event data
- **Cleanup**: Remove debug logging after fix is confirmed working
