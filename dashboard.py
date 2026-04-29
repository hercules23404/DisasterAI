"""
dashboard_v2.py
───────────────
Redesigned DisasterAI Command Center with professional presentation features.

Key improvements:
  - Time translation: Steps → HH:MM:SS format
  - Human-readable metrics: Cells → km², phase labels
  - Event log with decision tracking
  - Three-view tabs: Operations | Technical | Comparison
  - Simulation mode badge
  - Technical view with baseline comparison stats

Run with:
  streamlit run dashboard_v2.py
"""

import streamlit as st
import numpy as np
import os
import rasterio
import plotly.graph_objects as go
from scipy.optimize import linear_sum_assignment
import pandas as pd

from env.terrain_loader import TerrainLoader
from env.data_loader import DataLoader
from env.hazard_injection import HazardInjector
from env.hazard_propagation import HazardPropagation
from env.environment import DisasterEnvironment
from env.population_loader import PopulationLoader
from env.building_loader import BuildingLoader
from env.disaster_alerts import DisasterAlertService
from env.baselines import get_dispatch_function

from dashboard_utils import (
    step_to_elapsed_str, get_phase_label, format_flood_extent,
    format_response_time, EventLogger, calculate_baseline_stats,
    calculate_lookahead_stats, STEP_DURATION_MINUTES
)

# ─────────────────────────── PAGE CONFIG ───────────────────────────

st.set_page_config(
    page_title="DisasterAI Command Center — v2",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with improved styling
st.markdown("""
<style>
    .main .block-container { padding-top: 1rem; }
    
    /* Simulation badge */
    .sim-badge {
        position: fixed;
        top: 10px;
        right: 20px;
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 2px solid #ff9800;
        border-radius: 8px;
        padding: 8px 16px;
        font-size: 0.85rem;
        font-weight: 700;
        color: #ff9800;
        z-index: 9999;
        box-shadow: 0 4px 15px rgba(255,152,0,0.3);
    }

    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid #0f3460;
        border-radius: 12px;
        padding: 12px 16px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    div[data-testid="stMetric"] label {
        color: #a0aec0 !important;
        font-size: 0.85rem !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #e2e8f0 !important;
        font-weight: 700 !important;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1b2a 0%, #1b2838 100%);
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #e94560 0%, #c62a40 100%) !important;
        border: none !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        padding: 0.6rem 1rem !important;
        border-radius: 8px !important;
    }

    h1 {
        background: linear-gradient(90deg, #00d2ff, #3a7bd5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.2rem !important;
    }
    
    /* Event log styling */
    .event-log {
        background: #0d1b2a;
        border: 1px solid #0f3460;
        border-radius: 8px;
        padding: 12px;
        max-height: 400px;
        overflow-y: auto;
        font-family: 'Courier New', monospace;
        font-size: 0.85rem;
    }
    .event-item {
        padding: 6px 8px;
        margin: 4px 0;
        border-left: 3px solid #0f3460;
        background: rgba(255,255,255,0.02);
    }
    .event-item.highlight {
        border-left-color: #00e676;
        background: rgba(0,230,118,0.08);
    }
    .event-time {
        color: #64b5f6;
        font-weight: 700;
    }
    .event-message {
        color: #e2e8f0;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background: #1a1a2e;
        border-radius: 8px 8px 0 0;
        padding: 12px 24px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #00e676 0%, #00c853 100%);
        color: #0d1b2a !important;
    }
</style>
""", unsafe_allow_html=True)

# Simulation badge
st.markdown("""
<div class="sim-badge">
    🔬 SIMULATION MODE — Mithi Basin Scenario
</div>
""", unsafe_allow_html=True)


# ─────────────────────────── CACHED LOADERS ───────────────────────────

@st.cache_resource
def load_terrain_and_roads():
    base_dir = os.path.dirname(__file__)
    tif_files = [
        os.path.join(base_dir, "env", "datasets", "n18_e072_1arc_v3.tif"),
        os.path.join(base_dir, "env", "datasets", "n19_e072_1arc_v3.tif")
    ]
    terrain = TerrainLoader(tif_files)
    terrain.load_and_crop_dem()
    terrain.download_road_network()
    rem = terrain.compute_rem(river_name="Ulhas River")
    return terrain, rem

@st.cache_resource
def load_flood_sources(_terrain, _rem):
    loader = DataLoader()
    flood_events = loader.load_flood_events()
    injector = HazardInjector(_terrain.transform, _rem.shape)
    source_pixels = injector.inject_from_events(flood_events)
    if not source_pixels:
        source_pixels = HazardInjector.find_coastal_sources(_rem, num_sources=4)
    return source_pixels

@st.cache_resource
def load_population(_terrain, _rem, _bl):
    pop_loader = PopulationLoader()
    pop_grid = pop_loader.load_and_crop(
        min_lon=_terrain.min_lon, min_lat=_terrain.min_lat,
        max_lon=_terrain.max_lon, max_lat=_terrain.max_lat,
        target_shape=_rem.shape,
        building_loader=_bl
    )
    return pop_grid

@st.cache_resource
def load_buildings(_terrain):
    bl = BuildingLoader()
    bl.download_buildings(
        min_lon=_terrain.min_lon, min_lat=_terrain.min_lat,
        max_lon=_terrain.max_lon, max_lat=_terrain.max_lat,
    )
    bl.extract_centroids(_terrain.transform)
    return bl

@st.cache_resource
def load_disaster_alerts():
    service = DisasterAlertService()
    service.fetch_alerts(event_type="FL", country_iso3="IND", limit=5)
    return service

# ─────────────────────────── HELPERS ───────────────────────────

def rc_to_latlon(transform, r, c):
    x, y = rasterio.transform.xy(transform, int(r), int(c))
    return float(y), float(x)

def heuristic_dispatch(env):
    """Hungarian algorithm dispatch with event logging."""
    idle_units = [u for u in env.units if u.status == "idle"]
    active_incs = env.incident_manager.get_active_incidents()
    if not idle_units or not active_incs:
        return []
    
    cost_matrix = np.zeros((len(idle_units), len(active_incs)))
    for i, u in enumerate(idle_units):
        for j, inc in enumerate(active_incs):
            dist = abs(u.r - inc.r) + abs(u.c - inc.c)
            risk_penalty = (1.0 - inc.risk_level) * 1000
            cost_matrix[i, j] = dist + risk_penalty
    
    row_ind, col_ind = linear_sum_assignment(cost_matrix)
    assignments = [(idle_units[i].id, active_incs[j].id) for i, j in zip(row_ind, col_ind)]
    
    # Log dispatches
    for i, j in zip(row_ind, col_ind):
        unit = idle_units[i]
        inc = active_incs[j]
        eta = abs(unit.r - inc.r) + abs(unit.c - inc.c)
        env.log_dispatch(unit.id, inc.id, eta)
    
    return assignments


# ─────────────────────────── PLOTLY ANIMATION BUILDER ───────────────────────────

def build_plotly_animation(terrain, frames_data, speed_ms=800):
    """Build Plotly animation with time-translated labels."""
    center_lat = (terrain.min_lat + terrain.max_lat) / 2
    center_lon = (terrain.min_lon + terrain.max_lon) / 2
    transition_ms = max(speed_ms // 3, 80)

    all_edges = [
        (u, v)
        for u, v in terrain.road_graph.edges()
        if u in terrain.node_to_rc and v in terrain.node_to_rc
    ] if terrain.road_graph else []

    plotly_frames = []
    slider_steps  = []

    for i, frame in enumerate(frames_data):
        flood_depth = frame["flood_depth"]
        info        = frame["info"]
        predicted_depth = frame.get("predicted_depth", flood_depth)
        risk_scores     = frame.get("risk_scores", {})

        # Flood density layer
        rows, cols = np.where(flood_depth > 0.05)
        f_lats = [rc_to_latlon(terrain.transform, r, c)[0] for r, c in zip(rows, cols)]
        f_lons = [rc_to_latlon(terrain.transform, r, c)[1] for r, c in zip(rows, cols)]
        f_z    = [min(float(flood_depth[r, c]), 15.0)      for r, c in zip(rows, cols)]

        if not f_lats:
            f_lats, f_lons, f_z = [center_lat], [center_lon], [0.0]

        # Predicted flood overlay
        pred_rows, pred_cols = np.where(predicted_depth > flood_depth + 0.05)
        pf_lats = [rc_to_latlon(terrain.transform, r, c)[0] for r, c in zip(pred_rows, pred_cols)]
        pf_lons = [rc_to_latlon(terrain.transform, r, c)[1] for r, c in zip(pred_rows, pred_cols)]
        pf_z    = [min(float(predicted_depth[r, c]), 15.0)   for r, c in zip(pred_rows, pred_cols)]
        if not pf_lats:
            pf_lats, pf_lons, pf_z = [center_lat], [center_lon], [0.0]

        # Road traces
        open_lats, open_lons = [], []
        blocked_lats, blocked_lons = [], []
        for u, v in all_edges:
            r1, c1 = terrain.node_to_rc[u]
            r2, c2 = terrain.node_to_rc[v]
            lat1, lon1 = rc_to_latlon(terrain.transform, r1, c1)
            lat2, lon2 = rc_to_latlon(terrain.transform, r2, c2)
            if flood_depth[r1, c1] > 0.15 or flood_depth[r2, c2] > 0.15:
                blocked_lats += [lat1, lat2, None]
                blocked_lons += [lon1, lon2, None]
            else:
                open_lats += [lat1, lat2, None]
                open_lons += [lon1, lon2, None]

        # Victim markers
        vic_lats, vic_lons, vic_colors, vic_sizes, vic_text = [], [], [], [], []
        for inc_r, inc_c, risk, resolved, inc_id, health, is_dead in frame["incidents"]:
            lat, lon = rc_to_latlon(terrain.transform, inc_r, inc_c)
            composite_risk = risk_scores.get(inc_id, risk)
            if is_dead:
                vic_lats.append(lat)
                vic_lons.append(lon)
                vic_colors.append("#78909c")
                vic_sizes.append(8)
                vic_text.append(f"<b>Victim #{inc_id}</b><br>☠️ DECEASED")
            elif resolved:
                vic_lats.append(lat)
                vic_lons.append(lon)
                vic_colors.append("rgba(0,230,118,0.35)")
                vic_sizes.append(6)
                vic_text.append(f"<b>Victim #{inc_id}</b><br>✅ RESCUED")
            else:
                vic_lats.append(lat)
                vic_lons.append(lon)
                if composite_risk > 0.9:
                    vic_colors.append("#ff1744")
                    vic_sizes.append(18)
                    vic_text.append(f"<b>Victim #{inc_id}</b><br>⚠️ CRITICAL — Risk: {composite_risk:.2f} | Health: {health:.2f}")
                elif composite_risk > 0.7:
                    vic_colors.append("#ff1744")
                    vic_sizes.append(14)
                    vic_text.append(f"<b>Victim #{inc_id}</b><br>🔴 High Risk: {composite_risk:.2f} | Health: {health:.2f}")
                elif composite_risk > 0.3:
                    vic_colors.append("#ff9800")
                    vic_sizes.append(12)
                    vic_text.append(f"<b>Victim #{inc_id}</b><br>🟠 Medium Risk: {composite_risk:.2f} | Health: {health:.2f}")
                else:
                    vic_colors.append("#4caf50")
                    vic_sizes.append(10)
                    vic_text.append(f"<b>Victim #{inc_id}</b><br>🟢 Low Risk: {composite_risk:.2f} | Health: {health:.2f}")

        # Rescue units and routes
        unit_lats, unit_lons, unit_text = [], [], []
        all_route_lats, all_route_lons = [], []
        for u_r, u_c, u_status, u_id, u_path, u_target in frame["units"]:
            lat, lon = rc_to_latlon(terrain.transform, u_r, u_c)
            unit_lats.append(lat)
            unit_lons.append(lon)
            status_icon = "🟢 IDLE" if u_status == "idle" else ("🔵 EN-ROUTE" if u_status == "en-route" else "🟠 BUSY")
            target_str  = f" → Victim #{u_target}" if u_target is not None else ""
            unit_text.append(f"<b>Unit #{u_id}</b><br>{status_icon}{target_str}")
            if u_status == "en-route" and u_path:
                r_lats = [lat]
                r_lons = [lon]
                for pr, pc in u_path:
                    plat, plon = rc_to_latlon(terrain.transform, pr, pc)
                    r_lats.append(plat)
                    r_lons.append(plon)
                all_route_lats.extend(r_lats + [None])
                all_route_lons.extend(r_lons + [None])

        # Assemble traces
        traces = [
            go.Densitymapbox(
                lat=f_lats, lon=f_lons, z=f_z, radius=18,
                colorscale=[
                    [0.0,  "rgba(13,71,161,0)"],
                    [0.2,  "rgba(13,71,161,0.3)"],
                    [0.5,  "rgba(21,101,192,0.55)"],
                    [0.8,  "rgba(30,136,229,0.7)"],
                    [1.0,  "rgba(144,202,249,0.85)"],
                ],
                showscale=False, opacity=0.85, name="🌊 Current Flood", hoverinfo="skip",
            ),
            go.Densitymapbox(
                lat=pf_lats, lon=pf_lons, z=pf_z, radius=18,
                colorscale=[
                    [0.0,  "rgba(255,87,34,0)"],
                    [0.2,  "rgba(255,87,34,0.15)"],
                    [0.5,  "rgba(255,152,0,0.3)"],
                    [0.8,  "rgba(255,87,34,0.45)"],
                    [1.0,  "rgba(244,67,54,0.6)"],
                ],
                showscale=False, opacity=0.45, name="🔮 Predicted Flood", hoverinfo="skip",
            ),
            go.Scattermapbox(
                lat=open_lats, lon=open_lons, mode="lines",
                line=dict(width=1, color="rgba(255,255,255,0.18)"),
                name="Open Roads", hoverinfo="skip",
            ),
            go.Scattermapbox(
                lat=blocked_lats, lon=blocked_lons, mode="lines",
                line=dict(width=3, color="#ff1744"),
                name="🚧 Blocked Roads", hoverinfo="skip", opacity=0.9,
            ),
            go.Scattermapbox(
                lat=all_route_lats, lon=all_route_lons, mode="lines",
                line=dict(width=3, color="#00e676"),
                name="🟢 Rescue Routes", hoverinfo="skip", opacity=0.9,
            ),
            go.Scattermapbox(
                lat=vic_lats, lon=vic_lons, mode="markers",
                marker=dict(size=vic_sizes, color=vic_colors, opacity=1.0),
                text=vic_text, hoverinfo="text", name="Victims",
            ),
            go.Scattermapbox(
                lat=unit_lats, lon=unit_lons, mode="markers",
                marker=dict(size=17, color="#00bcd4", opacity=1.0, symbol="circle"),
                text=unit_text, hoverinfo="text", name="🚑 Rescue Units",
            ),
        ]

        # Time-translated frame title
        time_str = step_to_elapsed_str(i)
        phase = get_phase_label(i)
        flood_extent = format_flood_extent(int(np.sum(flood_depth > 0.05)))
        
        frame_title = (
            f"{time_str} — {phase} | "
            f"🌊 {flood_extent} · "
            f"🆘 {info['active_incidents']} active · "
            f"🚑 {info['units_busy']} units moving"
        )

        plotly_frames.append(
            go.Frame(
                data=traces,
                name=str(i),
                layout=go.Layout(title_text=frame_title),
            )
        )
        slider_steps.append({
            "args": [[str(i)], {
                "frame": {"duration": speed_ms, "redraw": True},
                "mode": "immediate",
                "transition": {"duration": transition_ms},
            }],
            "label": step_to_elapsed_str(i),
            "method": "animate",
        })

    # Assemble figure
    fig = go.Figure(data=plotly_frames[0].data, frames=plotly_frames)

    fig.update_layout(
        mapbox={
            "style": "white-bg",
            "center": {"lat": center_lat, "lon": center_lon},
            "zoom": 13.5,
            "layers": [{
                "below": "traces",
                "sourcetype": "raster",
                "sourceattribution": "Esri World Imagery",
                "source": [
                    "https://server.arcgisonline.com/ArcGIS/rest/services/"
                    "World_Imagery/MapServer/tile/{z}/{y}/{x}"
                ],
            }],
        },
        title=dict(
            text=f"{step_to_elapsed_str(0)} — Press ▶ Play to animate",
            font=dict(color="#e2e8f0", size=14),
            x=0.01,
        ),
        height=660,
        margin={"r": 0, "t": 44, "l": 0, "b": 0},
        paper_bgcolor="#0d1b2a",
        plot_bgcolor="#0d1b2a",
        font=dict(color="#e2e8f0"),
        legend=dict(
            bgcolor="rgba(13,27,42,0.85)",
            bordercolor="#0f3460",
            borderwidth=1,
            font=dict(color="#e2e8f0", size=12),
            x=0.01, y=0.99,
            xanchor="left", yanchor="top",
        ),
        updatemenus=[{
            "type": "buttons",
            "direction": "left",
            "showactive": False,
            "x": 0.12, "y": -0.04,
            "xanchor": "right", "yanchor": "top",
            "bgcolor": "#1a1a2e",
            "bordercolor": "#0f3460",
            "font": {"color": "#e2e8f0", "size": 13},
            "buttons": [
                {
                    "label": "▶  Play",
                    "method": "animate",
                    "args": [None, {
                        "frame": {"duration": speed_ms, "redraw": True},
                        "fromcurrent": True,
                        "transition": {"duration": transition_ms, "easing": "linear"},
                    }],
                },
                {
                    "label": "⏸  Pause",
                    "method": "animate",
                    "args": [[None], {
                        "frame": {"duration": 0, "redraw": False},
                        "mode": "immediate",
                        "transition": {"duration": 0},
                    }],
                },
            ],
        }],
        sliders=[{
            "steps": slider_steps,
            "transition": {"duration": transition_ms},
            "x": 0.13, "len": 0.87, "y": -0.04,
            "currentvalue": {
                "prefix": "🕐 Time: ",
                "visible": True,
                "xanchor": "right",
                "font": {"color": "#e2e8f0", "size": 14},
            },
            "font": {"color": "#e2e8f0"},
            "bgcolor": "#1a1a2e",
            "bordercolor": "#0f3460",
            "tickcolor": "#0f3460",
        }],
    )

    return fig


# ─────────────────────────── TECHNICAL VIEW COMPONENTS ───────────────────────────

def render_technical_view():
    """Render the Technical View with baseline comparison stats."""
    st.markdown("### 📊 Performance Metrics — Hungarian Algorithm vs Baselines")
    
    baseline_stats = calculate_baseline_stats()
    lookahead_stats = calculate_lookahead_stats()
    
    # Response time comparison
    st.markdown("#### Response Time Comparison (Lower is Better)")
    
    algorithms = list(baseline_stats.keys())
    response_times = [baseline_stats[alg]["mean_response_time"] for alg in algorithms]
    colors = [baseline_stats[alg]["color"] for alg in algorithms]
    
    fig_response = go.Figure(data=[
        go.Bar(
            x=algorithms,
            y=response_times,
            marker_color=colors,
            text=[f"{rt:.1f} min" for rt in response_times],
            textposition='outside',
        )
    ])
    fig_response.update_layout(
        title="Mean Response Time (minutes)",
        yaxis_title="Response Time (min)",
        paper_bgcolor="#0d1b2a",
        plot_bgcolor="#0d1b2a",
        font=dict(color="#e2e8f0"),
        height=400,
    )
    st.plotly_chart(fig_response, use_container_width=True)
    
    # Score comparison
    st.markdown("#### Simulation Score Comparison (Higher is Better)")
    
    scores = [baseline_stats[alg]["mean_score"] for alg in algorithms]
    
    fig_score = go.Figure(data=[
        go.Bar(
            x=algorithms,
            y=scores,
            marker_color=colors,
            text=[f"{s:.0f}" for s in scores],
            textposition='outside',
        )
    ])
    fig_score.update_layout(
        title="Mean Simulation Score",
        yaxis_title="Score",
        paper_bgcolor="#0d1b2a",
        plot_bgcolor="#0d1b2a",
        font=dict(color="#e2e8f0"),
        height=400,
    )
    st.plotly_chart(fig_score, use_container_width=True)
    
    # Key findings
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "🏆 Response Time Improvement",
            "37.5% faster",
            "vs Greedy Myopic",
            delta_color="normal"
        )
    with col2:
        st.metric(
            "🏆 Score Improvement",
            "+217% better",
            "vs Greedy Myopic",
            delta_color="normal"
        )
    with col3:
        st.metric(
            "🏆 vs Random Baseline",
            "+8,550% score",
            "735.8 vs 8.5",
            delta_color="normal"
        )
    
    # Lookahead ablation
    st.markdown("---")
    st.markdown("#### Lookahead Horizon Ablation Study")
    
    lookahead_names = list(lookahead_stats.keys())
    lookahead_response = [lookahead_stats[n]["mean_response_time"] for n in lookahead_names]
    lookahead_scores = [lookahead_stats[n]["mean_score"] for n in lookahead_names]
    
    fig_ablation = go.Figure()
    fig_ablation.add_trace(go.Scatter(
        x=lookahead_names,
        y=lookahead_response,
        mode='lines+markers',
        name='Response Time (min)',
        line=dict(color='#64b5f6', width=3),
        marker=dict(size=10),
        yaxis='y1'
    ))
    fig_ablation.add_trace(go.Scatter(
        x=lookahead_names,
        y=lookahead_scores,
        mode='lines+markers',
        name='Score',
        line=dict(color='#00e676', width=3),
        marker=dict(size=10),
        yaxis='y2'
    ))
    
    fig_ablation.update_layout(
        title="Lookahead Horizon Impact (N=1 to N=7 steps)",
        xaxis=dict(title="Lookahead Steps"),
        yaxis=dict(title="Response Time (min)", side='left', color='#64b5f6'),
        yaxis2=dict(title="Score", side='right', overlaying='y', color='#00e676'),
        paper_bgcolor="#0d1b2a",
        plot_bgcolor="#0d1b2a",
        font=dict(color="#e2e8f0"),
        height=400,
        legend=dict(x=0.7, y=1.0)
    )
    st.plotly_chart(fig_ablation, use_container_width=True)
    
    st.info(
        "**Key Finding:** N=2 or N=3 lookahead provides optimal balance. "
        "Higher N increases computational cost with diminishing returns.",
        icon="💡"
    )
    
    # Raw data table
    st.markdown("---")
    st.markdown("#### Detailed Statistics (20 runs per algorithm)")
    
    df_data = []
    for alg in algorithms:
        df_data.append({
            "Algorithm": alg,
            "Mean Response Time (min)": f"{baseline_stats[alg]['mean_response_time']:.1f} ± {baseline_stats[alg]['std_response_time']:.1f}",
            "Mean Score": f"{baseline_stats[alg]['mean_score']:.1f} ± {baseline_stats[alg]['std_score']:.1f}",
        })
    
    df = pd.DataFrame(df_data)
    st.dataframe(df, use_container_width=True)


# ─────────────────────────── MAIN APPLICATION ───────────────────────────

def main():
    st.title("🛰️ DisasterAI Command Center — Decision Support System")

    terrain, rem = load_terrain_and_roads()
    source_pixels = load_flood_sources(terrain, rem)
    sources_rc = [(r, c) for r, c, _ in source_pixels]

    bl = load_buildings(terrain)
    building_pixels = bl.building_pixels
    population_grid = load_population(terrain, rem, bl)
    alert_service = load_disaster_alerts()
    gdacs_info = alert_service.get_dashboard_summary()
    severity_multiplier = alert_service.get_severity_multiplier()

    # ── Sidebar ──────────────────────────────────────────────────────────
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/flood.png", width=60)
        st.markdown("### Simulation Controls")
        st.markdown("Configure and launch the disaster scenario below.")
        st.markdown("---")

        num_steps   = st.slider("⏱ Duration (minutes)",  5,  60, 30)
        num_victims = st.slider("👥 Number of Victims", 5,  20, 12)
        num_units   = st.slider("🚑 Rescue Units",      3,  10,  5)
        
        dispatch_mode = st.selectbox(
            "🧠 Dispatch Algorithm",
            ["Hungarian (Heuristic)", "Greedy Myopic (Baseline)", "Nearest Unit (Baseline)", 
             "Priority Queue (Operational)", "Random (Baseline)"],
            index=0
        )

        st.markdown("---")
        st.markdown("### 📡 Live Data Sources")
        if population_grid is not None:
            total_pop = int(population_grid.sum())
            st.success(f"🌍 **WorldPop**: {total_pop:,} people in area", icon="✅")
        else:
            st.warning("🌍 WorldPop: Not loaded", icon="⚠️")
        
        if building_pixels:
            st.success(f"🏢 **Buildings**: {len(building_pixels):,} structures", icon="✅")
        else:
            st.warning("🏢 Buildings: Not loaded", icon="⚠️")
            
        if gdacs_info["has_alert"]:
            alert_color = {"Green": "🟢", "Orange": "🟠", "Red": "🔴"}.get(gdacs_info["alert_level"], "⚪")
            st.error(
                f"🚨 **GDACS Alert**: {alert_color} {gdacs_info['alert_level']}\n\n"
                f"**{gdacs_info['event_name']}**\n\n"
                f"{gdacs_info['date_range']}\n\n"
                f"Severity: ×{gdacs_info['severity_multiplier']:.1f}",
                icon="🚨"
            )
        else:
            st.info("🚨 **GDACS**: No active flood alerts", icon="ℹ️")

        st.markdown("---")

        anim_speed = st.select_slider(
            "🎬 Animation Speed",
            options=["Slow", "Normal", "Fast"],
            value="Normal",
        )
        speed_map = {"Slow": 1400, "Normal": 750, "Fast": 300}
        speed_ms  = speed_map[anim_speed]

        st.markdown("---")

        run_btn   = st.button("▶ LAUNCH SIMULATION", type="primary", use_container_width=True)
        reset_btn = st.button("🔄 Reset",                            use_container_width=True)

        st.markdown("---")
        st.markdown("### 🗺️ Map Legend")
        st.markdown("""
        - 🔵 **Blue heatmap** — Current flood extent
        - 🟠 **Orange/Red heatmap** — Predicted flood
        - 🔴 **Red lines** — Blocked roads
        - ⚪ **White lines** — Open roads
        - 🟢 **Green lines** — Rescue routes
        - 🟢/🟠/🔴 **Dots** — Victims (risk level)
        - 🔵 **Cyan dot** — Rescue unit
        """)

    # ── Reset ─────────────────────────────────────────────────────────────
    if reset_btn:
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    # ── Run Simulation ────────────────────────────────────────────────────
    if run_btn:
        flood_depth = np.zeros_like(rem)
        for r, c, lvl in source_pixels:
            flood_depth[r, c] += lvl

        env = DisasterEnvironment(
            rem, terrain.road_graph, terrain.node_to_rc, flood_depth,
            num_units=num_units, num_incidents=num_victims,
            population_grid=population_grid,
            building_pixels=building_pixels,
            severity_multiplier=severity_multiplier,
            flood_sources=[(r, c) for r, c, _ in source_pixels],
            transform=terrain.transform,
        )
        propagator = HazardPropagation(rem)
        frames = []
        
        # Get dispatch function
        dispatch_fn = get_dispatch_function(dispatch_mode)

        progress = st.progress(0, text="🌊 Simulating disaster scenario…")

        for step in range(num_steps):
            env.flood_depth = propagator.propagate(
                env.flood_depth, sources_rc, continuous_inflow_volume=20.0
            )
            
            # Use selected dispatch algorithm
            if dispatch_mode == "Hungarian (Heuristic)":
                actions = heuristic_dispatch(env)
            else:
                actions = dispatch_fn(env)
            
            state, reward, done, info = env.step(actions=actions)

            frames.append({
                "flood_depth": env.flood_depth.copy(),
                "predicted_depth": env.predicted_depth.copy(),
                "risk_scores": dict(env.risk_scores),
                "units": [
                    (u.r, u.c, u.status, u.id,
                     [terrain.node_to_rc[n] for n in u.path_nodes] if u.path_nodes else [],
                     u.target_incident.id if u.target_incident else None)
                    for u in env.units
                ],
                "incidents": [
                    (inc.r, inc.c, inc.risk_level, inc.is_resolved, inc.id, inc.health, inc.is_dead)
                    for inc in env.incident_manager.incidents
                ],
                "info": info.copy(),
                "event_log": list(env.event_log),  # Copy event log
                "decision_events": dict(env.decision_events),  # Copy decision counts
            })

            flooded_cells = int(np.sum(env.flood_depth > 0.05))
            flood_extent = format_flood_extent(flooded_cells)
            progress.progress(
                (step + 1) / num_steps,
                text=(
                    f"{step_to_elapsed_str(step)} — "
                    f"🌊 {flood_extent} · "
                    f"🆘 {info['active_incidents']} active"
                )
            )
            if done:
                break

        progress.empty()
        st.session_state.frames      = frames
        st.session_state.speed_ms    = speed_ms
        st.session_state.env         = env
        st.session_state.dispatch_mode = dispatch_mode
        st.rerun()

    # ── Display Results ───────────────────────────────────────────────────
    if st.session_state.get("frames"):
        frames   = st.session_state.frames
        speed_ms = st.session_state.get("speed_ms", 750)
        env      = st.session_state.get("env")
        dispatch_mode = st.session_state.get("dispatch_mode", "Hungarian (Heuristic)")

        # Summary metrics
        final_info = frames[-1]["info"]
        max_flooded = int(max(np.sum(f["flood_depth"] > 0.05) for f in frames))
        total_vic   = len(frames[0]["incidents"])
        rescued     = sum(1 for inc in frames[-1]["incidents"] if inc[3] and not inc[6])
        deaths      = sum(1 for inc in frames[-1]["incidents"] if inc[6])
        
        # Calculate average response time
        response_times = []
        for frame in frames:
            for inc in frame["incidents"]:
                if inc[3]:  # is_resolved
                    response_times.append(1)  # Placeholder - would need actual tracking
        avg_response = np.mean(response_times) if response_times else 0

        # Top metrics strip
        has_pop = 'total_population' in final_info
        if has_pop:
            c1, c2, c3, c4, c5, c6 = st.columns(6)
            c1.metric("⏱ Duration", f"{step_to_elapsed_str(len(frames)-1)}")
            c2.metric("🌊 Peak Flood", format_flood_extent(max_flooded))
            c3.metric("👥 Population", f"{final_info['total_population']:,}")
            c4.metric("🆘 Total Victims", f"{total_vic}")
            c5.metric("✅ Rescued", f"{rescued}/{total_vic}")
            c6.metric("🏆 Score", f"{round(final_info['total_reward'], 1)}")
        else:
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("⏱ Duration", f"{step_to_elapsed_str(len(frames)-1)}")
            c2.metric("🌊 Peak Flood", format_flood_extent(max_flooded))
            c3.metric("👥 Total Victims", f"{total_vic}")
            c4.metric("✅ Rescued", f"{rescued}/{total_vic}")
            c5.metric("🏆 Score", f"{round(final_info['total_reward'], 1)}")

        st.markdown("---")

        # Three-view tabs
        tab1, tab2, tab3 = st.tabs(["🎯 Operations View", "📊 Technical View", "⚖️ Comparison View"])

        with tab1:
            st.markdown("### Operations Dashboard")
            
            # Main map and event log side-by-side
            col_map, col_events = st.columns([2, 1])
            
            with col_map:
                with st.spinner("🗺️ Building animated map…"):
                    fig = build_plotly_animation(terrain, frames, speed_ms=speed_ms)
                st.plotly_chart(fig, use_container_width=True)
            
            with col_events:
                st.markdown("#### 📋 Event Log")
                
                # Get events from final frame
                final_frame = frames[-1]
                if 'event_log' in final_frame and final_frame['event_log']:
                    events = final_frame['event_log']
                    decision_summary = final_frame.get('decision_events', {})
                    
                    # Decision summary
                    st.markdown(f"""
                    **Smart Decisions Made:**
                    - 🧠 Predictive reroutes: **{decision_summary.get('reroutes', 0)}**
                    - 🎯 Preemptive dispatches: **{decision_summary.get('preemptive_dispatches', 0)}**
                    - 🔄 Cluster dispatches: **{decision_summary.get('cluster_dispatches', 0)}**
                    """)
                    
                    st.markdown("---")
                    
                    # Event feed - show last 20 events
                    event_html = '<div class="event-log">'
                    display_events = events[-20:] if len(events) > 20 else events
                    for event in reversed(display_events):
                        time_str = step_to_elapsed_str(event['step'])
                        highlight_class = " highlight" if event.get('highlight', False) else ""
                        event_html += f'''
                        <div class="event-item{highlight_class}">
                            <span class="event-time">{time_str}</span> — 
                            <span class="event-message">{event['message']}</span>
                        </div>
                        '''
                    event_html += '</div>'
                    st.markdown(event_html, unsafe_allow_html=True)
                else:
                    st.info("No events logged during this simulation.", icon="ℹ️")
            
            # Result banner
            if rescued == total_vic:
                st.success(
                    f"🎉 **ALL {total_vic} VICTIMS RESCUED!** "
                    f"Total score: {round(final_info['total_reward'], 1)}",
                    icon="🏆"
                )
            elif deaths > 0:
                st.warning(
                    f"📍 **{rescued}/{total_vic}** victims rescued · "
                    f"☠️ **{deaths}** casualties · "
                    f"Algorithm: {dispatch_mode}",
                    icon="⚠️"
                )
            else:
                st.info(
                    f"📍 **{rescued}/{total_vic}** victims rescued · "
                    f"Algorithm: {dispatch_mode}",
                    icon="ℹ️"
                )

        with tab2:
            render_technical_view()

        with tab3:
            st.markdown("### ⚖️ Algorithm Comparison")
            st.info(
                "**Coming Soon:** Side-by-side comparison of Greedy vs Hungarian on the same scenario seed. "
                "This view will show both algorithms running in parallel with synchronized playback, "
                "highlighting key decision moments where Hungarian outperforms the baseline.",
                icon="🚧"
            )
            
            st.markdown("#### How It Will Work:")
            st.markdown("""
            1. **Synchronized Playback** — Two maps side-by-side, same scenario
            2. **Decision Highlights** — Markers showing when Hungarian makes smarter choices
            3. **Live Metrics** — Real-time comparison of response times, rescues, casualties
            4. **Outcome Summary** — Final statistics showing performance delta
            """)

    else:
        # Landing state
        st.markdown("---")
        col_a, col_b = st.columns([2, 3])
        with col_a:
            st.markdown("""
            ### ✨ Decision Support Visualization

            This system provides **predictive flood modeling** and **AI-powered dispatch optimization**
            for emergency response planning and research.

            **Key Features:**
            - 🌊 **Real-time flood propagation** with lookahead prediction
            - 🧠 **Composite risk scoring** (depth + prediction + health + time)
            - 🚑 **Optimal dispatch** via Hungarian algorithm
            - 📊 **Performance analytics** vs baseline algorithms
            - 🔮 **Preemptive positioning** for high-risk zones

            ---

            ### How It Works
            1. **Flood Simulation** — Physics-based water propagation
            2. **Risk Assessment** — Multi-factor victim prioritization
            3. **AI Dispatch** — Globally optimal unit assignment
            4. **Predictive Routing** — Avoid future flooded roads

            > 👈 **Click "LAUNCH SIMULATION"** in the sidebar to begin
            """)
        with col_b:
            center_lat = (terrain.min_lat + terrain.max_lat) / 2
            center_lon = (terrain.min_lon + terrain.max_lon) / 2
            preview = go.Figure(go.Scattermapbox())
            preview.update_layout(
                mapbox={
                    "style": "white-bg",
                    "center": {"lat": center_lat, "lon": center_lon},
                    "zoom": 13,
                    "layers": [{
                        "below": "traces",
                        "sourcetype": "raster",
                        "sourceattribution": "Esri",
                        "source": [
                            "https://server.arcgisonline.com/ArcGIS/rest/services/"
                            "World_Imagery/MapServer/tile/{z}/{y}/{x}"
                        ],
                    }],
                },
                height=450,
                margin={"r": 0, "t": 0, "l": 0, "b": 0},
                paper_bgcolor="#0d1b2a",
            )
            st.plotly_chart(preview, use_container_width=True)


if __name__ == "__main__":
    main()
