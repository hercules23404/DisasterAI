import streamlit as st
import numpy as np
import os

from env.terrain_loader import TerrainLoader
from env.data_loader import DataLoader
from env.hazard_injection import HazardInjector
from env.hazard_propagation import HazardPropagation
from env.environment import DisasterEnvironment
from env.population_loader import PopulationLoader
from env.building_loader import BuildingLoader
from env.disaster_alerts import DisasterAlertService
from env.baselines import get_dispatch_function

from dashboard_utils import step_to_elapsed_str, format_flood_extent

from components.hud import render_hud_strip
from components.controls import render_control_panel, ALGO_CODES
from components.event_log import render_event_log_popover, render_legend_popover
from components.map_renderer import build_plotly_animation
from components.status_pill import render_status_pill

SPEED_TO_MS = {1: 500, 2: 250, 5: 100}

_SIM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600;700&family=Fira+Sans:wght@300;400;500;600;700&display=swap');
.main .block-container { padding-top: 1.2rem; }

.map-container {
    background: rgba(10,20,45,0.6);
    border: 1px solid rgba(0,212,255,0.18);
    border-radius: 14px;
    overflow: hidden;
    box-shadow: 0 0 40px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.04);
}
.map-title-bar {
    font-family: 'Fira Code', monospace;
    font-size: 0.82rem;
    font-weight: 600;
    color: #64748b;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 10px 16px 6px;
    border-bottom: 1px solid rgba(0,212,255,0.1);
    display: flex;
    align-items: center;
    gap: 8px;
}
.map-title-bar-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #00d4ff;
    box-shadow: 0 0 6px #00d4ff;
    display: inline-block;
}

.stSegmentedControl > div {
    background: rgba(10,20,45,0.85) !important;
    border: 1px solid rgba(0,212,255,0.25) !important;
    border-radius: 8px !important;
}

.stButton > button {
    border-radius: 8px !important;
    font-family: 'Fira Code', monospace !important;
    font-size: 0.84rem !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}

.results-link-btn .stButton > button {
    background: rgba(10,20,45,0.85) !important;
    border: 1px solid rgba(0,212,255,0.3) !important;
    color: #00d4ff !important;
}
.results-link-btn .stButton > button:hover {
    background: rgba(0,212,255,0.1) !important;
    box-shadow: 0 0 12px rgba(0,212,255,0.25) !important;
}

div[data-testid="stInfo"] {
    background: rgba(30,111,255,0.08) !important;
    border: 1px solid rgba(30,111,255,0.25) !important;
    border-radius: 10px !important;
    color: #94a3b8 !important;
    font-family: 'Fira Sans', sans-serif !important;
}
</style>
"""


# ── Cached resource loaders (reuse across reruns) ──────────────────────

@st.cache_resource
def _load_terrain():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    tif_files = [
        os.path.join(base_dir, "env", "datasets", "n18_e072_1arc_v3.tif"),
        os.path.join(base_dir, "env", "datasets", "n19_e072_1arc_v3.tif"),
    ]
    terrain = TerrainLoader(tif_files)
    terrain.load_and_crop_dem()
    terrain.download_road_network()
    terrain.compute_rem(river_name="Ulhas River")
    return terrain


@st.cache_resource
def _load_rem(_terrain):
    return _terrain.rem if hasattr(_terrain, "rem") else np.zeros((100, 100))


@st.cache_resource
def _load_flood_sources(_terrain, _rem):
    loader = DataLoader()
    flood_events = loader.load_flood_events()
    injector = HazardInjector(_terrain.transform, _rem.shape)
    source_pixels = injector.inject_from_events(flood_events)
    if not source_pixels:
        source_pixels = HazardInjector.find_coastal_sources(_rem, num_sources=4)
    return source_pixels


@st.cache_resource
def _load_buildings(_terrain):
    bl = BuildingLoader()
    bl.download_buildings(
        min_lon=_terrain.min_lon, min_lat=_terrain.min_lat,
        max_lon=_terrain.max_lon, max_lat=_terrain.max_lat,
    )
    bl.extract_centroids(_terrain.transform)
    return bl


@st.cache_resource
def _load_population(_terrain, _rem, _bl):
    pop = PopulationLoader()
    return pop.load_and_crop(
        min_lon=_terrain.min_lon, min_lat=_terrain.min_lat,
        max_lon=_terrain.max_lon, max_lat=_terrain.max_lat,
        target_shape=_rem.shape,
        building_loader=_bl,
    )


@st.cache_resource
def _load_alerts():
    svc = DisasterAlertService()
    svc.fetch_alerts(event_type="FL", country_iso3="IND", limit=5)
    return svc


# ── Simulation runner ──────────────────────────────────────────────────

def _run_environment(duration_min, n_victims, n_units, algorithm_key):
    terrain       = _load_terrain()
    rem           = terrain.rem if hasattr(terrain, "rem") else np.zeros((100, 100))
    source_pixels = _load_flood_sources(terrain, rem)
    bl            = _load_buildings(terrain)
    pop_grid      = _load_population(terrain, rem, bl)
    alerts        = _load_alerts()

    severity_multiplier = alerts.get_severity_multiplier()
    sources_rc          = [(r, c) for r, c, _ in source_pixels]

    flood_depth = np.zeros_like(rem)
    for r, c, lvl in source_pixels:
        flood_depth[r, c] += lvl

    env = DisasterEnvironment(
        rem, terrain.road_graph, terrain.node_to_rc, flood_depth,
        num_units=n_units, num_incidents=n_victims,
        population_grid=pop_grid,
        building_pixels=bl.building_pixels,
        severity_multiplier=severity_multiplier,
        flood_sources=sources_rc,
        transform=terrain.transform,
    )
    propagator   = HazardPropagation(rem)
    dispatch_fn  = get_dispatch_function(algorithm_key)
    frames       = []

    for step in range(duration_min):
        env.flood_depth = propagator.propagate(
            env.flood_depth, sources_rc, continuous_inflow_volume=20.0
        )
        actions = dispatch_fn(env)
        state, reward, done, info = env.step(actions=actions)
        info["step"] = step

        frames.append({
            "step":           step,
            "flood_depth":    env.flood_depth.copy(),
            "predicted_depth": env.predicted_depth.copy(),
            "risk_scores":    dict(env.risk_scores),
            "units": [
                (u.r, u.c, u.status, u.id,
                 [terrain.node_to_rc[n] for n in u.path_nodes] if u.path_nodes else [],
                 u.target_incident.id if u.target_incident else None)
                for u in env.units
            ],
            "incidents": [
                (inc.r, inc.c, inc.risk_level, inc.is_resolved,
                 inc.id, inc.health, inc.is_dead)
                for inc in env.incident_manager.incidents
            ],
            "info":           info.copy(),
            "event_log":      list(env.event_log),
            "decision_events": dict(env.decision_events),
        })

        if done:
            break

    last_info  = frames[-1]["info"] if frames else {}
    last_frame = frames[-1]          if frames else {}
    total_vic  = len(last_frame.get("incidents", []))
    rescued    = sum(1 for i in last_frame.get("incidents", []) if i[3] and not i[6])
    deaths     = sum(1 for i in last_frame.get("incidents", []) if i[6])
    kpi_summary = {
        "total_rescued":        rescued,
        "total_casualties":     deaths,
        "mean_response_time_min": last_info.get("mean_response_time", 0.0),
        "total_score":          last_info.get("total_reward", 0.0),
        "peak_flood_extent_pct": 0.0,
    }

    event_log = frames[-1].get("event_log", []) if frames else []
    return terrain, frames, event_log, kpi_summary


def _run_simulation():
    st.session_state.run_status = "computing"
    params    = st.session_state.sim_params
    algo_key  = ALGO_CODES[params["algorithm"]]

    with st.status("Pre-computing flood propagation frames...", expanded=True) as status:
        try:
            terrain, frames, event_log, kpi = _run_environment(
                duration_min=params["duration_min"],
                n_victims=params["n_victims"],
                n_units=params["n_units"],
                algorithm_key=algo_key,
            )
            st.session_state.sim_cache = {
                "frames":      frames,
                "event_log":   event_log,
                "terrain":     terrain,
                "kpi_summary": kpi,
                "n_steps":     len(frames),
            }
            st.session_state.current_frame = 0
            st.session_state.run_status    = "ready"
            status.update(label="Simulation ready", state="complete")
        except Exception as e:
            st.session_state.run_status = "error"
            status.update(label=f"Error: {e}", state="error")
            return

    st.rerun()


# ── HUD metric builder ─────────────────────────────────────────────────

def _build_hud_metrics():
    cache = st.session_state.sim_cache
    if cache is None:
        return None

    frames = cache["frames"]
    n      = len(frames)
    frame  = frames[-1]
    kpi    = cache["kpi_summary"]

    active_units = sum(
        1 for row in frame["units"] if row[2] != "idle"
    )
    return {
        "time_step":    f"{n}/{cache['n_steps']}",
        "rescued":      kpi["total_rescued"],
        "rescued_delta": None,
        "remaining":    (
            sum(1 for i in frame["incidents"] if not i[3] and not i[6])
        ),
        "active_units": active_units,
        "total_score":  kpi["total_score"],
    }


# ── Main view ──────────────────────────────────────────────────────────

def render_simulation():
    st.markdown(_SIM_CSS, unsafe_allow_html=True)

    terrain       = _load_terrain()
    bl            = _load_buildings(terrain)
    rem           = terrain.rem if hasattr(terrain, "rem") else None
    pop_grid      = _load_population(terrain, rem, bl) if rem is not None else None
    alert_service = _load_alerts()

    # ── Sidebar ──────────────────────────────────────────────────────
    with st.sidebar:
        render_control_panel(
            on_run=_run_simulation,
            alert_service=alert_service,
            population_grid=pop_grid,
            building_pixels=bl.building_pixels if bl else None,
        )

    # ── Main area ─────────────────────────────────────────────────────
    col_title, col_results_btn = st.columns([5, 1])
    with col_title:
        st.markdown(
            "<div style='font-family:Fira Code,monospace;font-size:0.85rem;"
            "color:#64748b;letter-spacing:0.1em;text-transform:uppercase;"
            "margin-bottom:4px;'>"
            "<span style='color:#00d4ff;'>◉</span> Mumbai Mithi River Basin</div>",
            unsafe_allow_html=True,
        )
    with col_results_btn:
        st.markdown("<div class='results-link-btn'>", unsafe_allow_html=True)
        if st.button("View Results →", use_container_width=True):
            st.session_state.page = "results"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # HUD strip
    render_hud_strip(_build_hud_metrics())

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    # Map area
    st.markdown("<div class='map-container'>", unsafe_allow_html=True)
    st.markdown(
        "<div class='map-title-bar'>"
        "<span class='map-title-bar-dot'></span>"
        "LIVE SIMULATION MAP"
        "</div>",
        unsafe_allow_html=True,
    )

    cache = st.session_state.sim_cache
    if cache is not None:
        speed_ms = SPEED_TO_MS.get(st.session_state.playback_speed, 500)
        with st.spinner("Building animated map..."):
            fig = build_plotly_animation(
                terrain=cache["terrain"],
                frames_data=cache["frames"],
                speed_ms=speed_ms,
            )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(
            "Configure parameters in the sidebar and click **▶ Run Simulation** to begin."
        )

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Below-map control row ─────────────────────────────────────────
    col_speed, col_events, col_legend, _spacer, col_status = st.columns([1, 1, 1, 2, 1])

    with col_speed:
        try:
            speed = st.segmented_control(
                "Speed",
                options=[1, 2, 5],
                format_func=lambda x: f"{x}×",
                default=st.session_state.playback_speed,
                label_visibility="collapsed",
            )
        except AttributeError:
            speed = st.radio(
                "Speed", options=[1, 2, 5],
                format_func=lambda x: f"{x}×",
                index=[1, 2, 5].index(st.session_state.playback_speed),
                horizontal=True,
                label_visibility="collapsed",
            )
        if speed is not None and speed != st.session_state.playback_speed:
            st.session_state.playback_speed = speed
            st.rerun()

    with col_events:
        events = cache["event_log"] if cache else []
        render_event_log_popover(events, st.session_state.current_frame)

    with col_legend:
        render_legend_popover()

    with col_status:
        render_status_pill(st.session_state.run_status)
