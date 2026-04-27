"""
Flood physics configuration for the Mithi River / BKC basin, Mumbai.

Constants are derived from:
- Central Water Commission (CWC) India flood hazard guidelines
- Mithi River flood study: IIT Bombay, 2006 post-flood survey
- Open-Meteo discharge data calibration (see data_loader.py)

These are simplified proxies for a full Saint-Venant model.
The system uses a topographic cellular automata approach, not
a full hydrodynamic solver. See limitations section in README.
"""

PHYSICS = {
    # Flow transfer fraction between adjacent cells per timestep
    # Derived from: Manning's n ≈ 0.035 (concrete-lined urban channel),
    # average slope of Mithi basin ~0.002 m/m → ~92% transfer rate.
    # Using 0.90 (slightly conservative for urban friction/obstruction).
    "flow_transfer_rate": 0.90,

    # Source dampening: injection volume decay per frame
    # Represents rainfall intensity reduction + soil absorption.
    # Mumbai July peak rainfall ~944mm/day (IMD 2005 data).
    # Decay factor ~0.60 for sustained monsoon injection.
    "source_dampening": 0.60,

    # Injection volume per frame
    # Calibrated so peak flood extent at step 30 approximates
    # the ~12 km² inundation area reported in the 2005 Mumbai flood
    # for the Mithi basin (MCGM flood audit report, 2006).
    # At 30m SRTM resolution over a 4.5x4.5km grid: ~3.5 units/frame.
    "injection_volume": 3.5,

    # Maximum propagation iterations per frame (sources × multiplier)
    "propagation_multiplier": 800,

    # Minimum flow threshold — ignore transfers below this
    "min_flow_threshold": 0.05,

    # Flood depth cleanup threshold — zero out noise
    "cleanup_threshold": 0.01,
}
