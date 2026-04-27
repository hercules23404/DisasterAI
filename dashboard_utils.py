"""
dashboard_utils.py
──────────────────
Utility functions for the DisasterAI dashboard redesign.
Handles time conversion, metric formatting, and event log generation.
"""

import numpy as np
from datetime import timedelta

# ─────────────────────────── CONSTANTS ───────────────────────────

STEP_DURATION_MINUTES = 1  # 1 step = 1 minute of disaster time
CELL_AREA_M2 = 900  # 30m × 30m SRTM resolution
CELLS_PER_KM2 = 1111  # Approximately 1,111 cells = 1 km²
BASIN_TOTAL_AREA_KM2 = 42.0  # Mithi Basin total area

# ─────────────────────────── TIME CONVERSION ───────────────────────────

def step_to_time_str(step):
    """Convert step number to HH:MM:SS format."""
    total_minutes = step * STEP_DURATION_MINUTES
    hours = total_minutes // 60
    minutes = total_minutes % 60
    return f"{int(hours):02d}:{int(minutes):02d}:00"

def step_to_elapsed_str(step):
    """Convert step to elapsed time string like 'T+00:47:00'."""
    return f"T+{step_to_time_str(step)}"

def get_phase_label(step):
    """Return disaster phase based on elapsed time."""
    minutes = step * STEP_DURATION_MINUTES
    if minutes < 20:
        return "Initial Response"
    elif minutes < 60:
        return "Peak Inundation"
    else:
        return "Recovery Phase"

# ─────────────────────────── METRIC FORMATTING ───────────────────────────

def cells_to_km2(num_cells):
    """Convert flood cells to km²."""
    return num_cells / CELLS_PER_KM2

def cells_to_basin_percent(num_cells):
    """Convert flood cells to percentage of basin area."""
    km2 = cells_to_km2(num_cells)
    return (km2 / BASIN_TOTAL_AREA_KM2) * 100

def format_flood_extent(num_cells):
    """Format flood extent as 'X.X km² (Y% of basin)'."""
    km2 = cells_to_km2(num_cells)
    pct = cells_to_basin_percent(num_cells)
    return f"{km2:.1f} km² ({pct:.1f}% of basin)"

def format_eta_minutes(steps):
    """Convert ETA in steps to minutes."""
    return steps * STEP_DURATION_MINUTES

def format_response_time(steps):
    """Format response time as 'X.X min'."""
    minutes = steps * STEP_DURATION_MINUTES
    return f"{minutes:.1f} min"

# ─────────────────────────── EVENT LOG GENERATION ───────────────────────────

class EventLogger:
    """Tracks and formats events for the dashboard event log."""
    
    def __init__(self):
        self.events = []
        self.decision_counts = {
            "reroutes": 0,
            "preemptive_dispatches": 0,
            "cluster_dispatches": 0,
        }
    
    def add_distress_signal(self, step, location, risk_level, victim_id):
        """Log a new distress signal."""
        time_str = step_to_elapsed_str(step)
        risk_emoji = "🔴" if risk_level > 0.7 else ("🟠" if risk_level > 0.3 else "🟢")
        risk_label = "CRITICAL" if risk_level > 0.9 else ("HIGH" if risk_level > 0.7 else ("MEDIUM" if risk_level > 0.3 else "LOW"))
        
        self.events.append({
            "time": time_str,
            "step": step,
            "type": "distress",
            "message": f"{risk_emoji} Distress signal #{victim_id}, {location}. Risk: {risk_label}",
            "icon": "🆘"
        })
    
    def add_dispatch(self, step, unit_id, victim_id, eta_steps, route_type="standard"):
        """Log a unit dispatch."""
        time_str = step_to_elapsed_str(step)
        eta_min = format_eta_minutes(eta_steps)
        
        route_info = ""
        if route_type == "preemptive":
            route_info = " (Preemptive positioning)"
            self.decision_counts["preemptive_dispatches"] += 1
        
        self.events.append({
            "time": time_str,
            "step": step,
            "type": "dispatch",
            "message": f"Unit {unit_id} dispatched to Victim #{victim_id}. ETA {eta_min:.0f} min{route_info}",
            "icon": "🚑"
        })
    
    def add_reroute(self, step, unit_id, reason="predicted flooding"):
        """Log a smart reroute decision."""
        time_str = step_to_elapsed_str(step)
        self.decision_counts["reroutes"] += 1
        
        self.events.append({
            "time": time_str,
            "step": step,
            "type": "reroute",
            "message": f"🧠 SMART REROUTE: Unit {unit_id} diverted — {reason}",
            "icon": "🔄",
            "highlight": True
        })
    
    def add_rescue_complete(self, step, unit_id, victim_id, response_time_steps):
        """Log a successful rescue."""
        time_str = step_to_elapsed_str(step)
        response_min = format_eta_minutes(response_time_steps)
        
        self.events.append({
            "time": time_str,
            "step": step,
            "type": "rescue",
            "message": f"✅ Rescue complete: Unit {unit_id} saved Victim #{victim_id} (Response: {response_min:.0f} min)",
            "icon": "🎯"
        })
    
    def add_casualty(self, step, victim_id, reason="health depleted"):
        """Log a casualty."""
        time_str = step_to_elapsed_str(step)
        
        self.events.append({
            "time": time_str,
            "step": step,
            "type": "casualty",
            "message": f"☠️ Casualty: Victim #{victim_id} — {reason}",
            "icon": "⚠️"
        })
    
    def add_cluster_dispatch(self, step, unit_ids, victim_ids):
        """Log a cluster dispatch decision."""
        time_str = step_to_elapsed_str(step)
        self.decision_counts["cluster_dispatches"] += 1
        
        self.events.append({
            "time": time_str,
            "step": step,
            "type": "cluster",
            "message": f"🧠 CLUSTER DISPATCH: {len(unit_ids)} units to {len(victim_ids)} nearby victims",
            "icon": "🎯",
            "highlight": True
        })
    
    def add_flood_warning(self, step, location, predicted_depth):
        """Log a flood prediction warning."""
        time_str = step_to_elapsed_str(step)
        
        self.events.append({
            "time": time_str,
            "step": step,
            "type": "warning",
            "message": f"⚠️ Flood prediction: {location} — {predicted_depth:.1f}m in next 5 min",
            "icon": "🌊"
        })
    
    def get_recent_events(self, limit=20):
        """Get the most recent events."""
        return self.events[-limit:]
    
    def get_all_events(self):
        """Get all events."""
        return self.events
    
    def get_decision_summary(self):
        """Get summary of smart decisions made."""
        return self.decision_counts

# ─────────────────────────── STATISTICS HELPERS ───────────────────────────

def calculate_baseline_stats():
    """Return pre-calculated baseline comparison statistics."""
    return {
        "Hungarian": {
            "mean_response_time": 18.9,
            "std_response_time": 4.2,
            "mean_score": 735.8,
            "std_score": 312.5,
            "color": "#00e676"
        },
        "Greedy Myopic": {
            "mean_response_time": 29.6,
            "std_response_time": 3.8,
            "mean_score": 231.6,
            "std_score": 285.4,
            "color": "#ff9800"
        },
        "Nearest-Unit": {
            "mean_response_time": 30.1,
            "std_response_time": 3.4,
            "mean_score": 173.5,
            "std_score": 312.8,
            "color": "#ff5722"
        },
        "Priority Queue": {
            "mean_response_time": 31.0,
            "std_response_time": 3.5,
            "mean_score": -26.3,
            "std_score": 245.7,
            "color": "#f44336"
        },
        "Random": {
            "mean_response_time": 30.3,
            "std_response_time": 3.2,
            "mean_score": 8.5,
            "std_score": 287.3,
            "color": "#9e9e9e"
        }
    }

def calculate_lookahead_stats():
    """Return pre-calculated lookahead ablation statistics."""
    return {
        "N=1": {"mean_response_time": 19.1, "mean_score": 685.4, "color": "#64b5f6"},
        "N=2": {"mean_response_time": 18.8, "mean_score": 821.4, "color": "#42a5f5"},
        "N=3": {"mean_response_time": 18.5, "mean_score": 788.0, "color": "#00e676"},
        "N=5": {"mean_response_time": 18.3, "mean_score": 770.4, "color": "#1e88e5"},
        "N=7": {"mean_response_time": 18.7, "mean_score": 798.8, "color": "#1565c0"},
    }
