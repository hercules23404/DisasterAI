import streamlit as st

SCENARIO_PRESETS: dict[str, dict] = {
    "Light Flood":   {"duration_min": 15, "n_victims": 5,  "n_units": 4,  "algorithm": "Hungarian"},
    "Moderate":      {"duration_min": 30, "n_victims": 10, "n_units": 6,  "algorithm": "Hungarian"},
    "Severe":        {"duration_min": 45, "n_victims": 15, "n_units": 8,  "algorithm": "Hungarian"},
    "Catastrophic":  {"duration_min": 60, "n_victims": 20, "n_units": 10, "algorithm": "Hungarian"},
}

ALGO_CODES: dict[str, str] = {
    "Hungarian":    "Hungarian (Heuristic)",
    "Greedy Myopic": "Greedy Myopic (Baseline)",
    "Nearest Unit": "Nearest Unit (Baseline)",
    "Priority Queue": "Priority Queue (Operational)",
    "Random":       "Random (Baseline)",
}

_SIDEBAR_CSS = """
<style>
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg,
        #050912 0%,
        #070d1c 40%,
        #0a1020 100%);
    border-right: 1px solid rgba(0,212,255,0.1);
    box-shadow: 4px 0 24px rgba(0,0,0,0.4);
}

/* Sidebar top accent line */
section[data-testid="stSidebar"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg,
        #00d4ff, #3b82f6, #a78bfa, #ff2d78, #f59e0b);
    z-index: 10;
}

section[data-testid="stSidebar"] label {
    color: #3d5270 !important;
    font-size: 0.72rem !important;
    font-family: 'Fira Code', monospace !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    font-weight: 600 !important;
}

section[data-testid="stSidebar"] .stSelectbox > div > div {
    background: rgba(7,13,30,0.95) !important;
    border: 1px solid rgba(0,212,255,0.18) !important;
    border-radius: 8px !important;
    color: #94a3b8 !important;
    font-family: 'Fira Code', monospace !important;
    font-size: 0.85rem !important;
}
section[data-testid="stSidebar"] .stSelectbox > div > div:hover {
    border-color: rgba(0,212,255,0.38) !important;
}

section[data-testid="stSidebar"] .stButton > button {
    border-radius: 9px !important;
    font-family: 'Fira Code', monospace !important;
    font-weight: 600 !important;
    font-size: 0.84rem !important;
    letter-spacing: 0.05em !important;
    transition: all 0.22s ease !important;
}
section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: linear-gradient(135deg,
        #1e4fff 0%,
        #00d4ff 50%,
        #a78bfa 100%) !important;
    border: none !important;
    color: #070b15 !important;
    box-shadow: 0 0 24px rgba(0,212,255,0.28), 0 0 48px rgba(167,139,250,0.1) !important;
}
section[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
    box-shadow: 0 0 36px rgba(0,212,255,0.48), 0 0 60px rgba(167,139,250,0.18) !important;
    transform: translateY(-1px) !important;
    filter: brightness(1.06) !important;
}
section[data-testid="stSidebar"] .stButton > button:not([kind="primary"]) {
    background: rgba(7,13,30,0.9) !important;
    border: 1px solid rgba(0,212,255,0.18) !important;
    color: #475569 !important;
}
section[data-testid="stSidebar"] .stButton > button:not([kind="primary"]):hover {
    border-color: rgba(0,212,255,0.45) !important;
    color: #00d4ff !important;
    background: rgba(0,212,255,0.06) !important;
}

section[data-testid="stSidebar"] hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg,
        transparent,
        rgba(0,212,255,0.12),
        rgba(167,139,250,0.08),
        transparent) !important;
    margin: 0.6rem 0 !important;
}
</style>
"""


def render_control_panel(
    on_run,
    alert_service=None,
    population_grid=None,
    building_pixels=None,
) -> None:
    st.markdown(_SIDEBAR_CSS, unsafe_allow_html=True)

    _GEAR = (
        '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" style="vertical-align:-2px">'
        '<circle cx="12" cy="12" r="3" stroke="#00d4ff" stroke-width="2"/>'
        '<path d="M12 2v3M12 19v3M4.22 4.22l2.12 2.12M17.66 17.66l2.12 2.12'
        'M2 12h3M19 12h3M4.22 19.78l2.12-2.12M17.66 6.34l2.12-2.12"'
        ' stroke="#00d4ff" stroke-width="2" stroke-linecap="round"/>'
        '</svg>'
    )
    st.markdown(
        f"<div style='font-family:Fira Code,monospace;font-size:0.82rem;"
        f"font-weight:700;color:#00d4ff;letter-spacing:0.12em;"
        f"text-transform:uppercase;margin-bottom:4px;'>"
        f"{_GEAR}&nbsp; Simulation Controls</div>",
        unsafe_allow_html=True,
    )
    st.divider()

    params = st.session_state.sim_params

    # ── Scenario preset ──────────────────────────────────────────────────
    preset_options = ["Custom"] + list(SCENARIO_PRESETS.keys())
    current_preset = params.get("scenario_preset", "Moderate")
    preset_idx = preset_options.index(current_preset) if current_preset in preset_options else 2

    preset = st.selectbox("Scenario", options=preset_options, index=preset_idx)

    if preset != "Custom" and preset != current_preset:
        p = SCENARIO_PRESETS[preset]
        st.session_state.sim_params.update({
            "duration_min":    p["duration_min"],
            "n_victims":       p["n_victims"],
            "n_units":         p["n_units"],
            "algorithm":       p["algorithm"],
            "scenario_preset": preset,
        })
        st.rerun()

    st.session_state.sim_params["scenario_preset"] = preset

    # ── Dropdowns ────────────────────────────────────────────────────────
    duration = st.selectbox("Duration (minutes)", options=list(range(5, 65, 5)),
                            index=list(range(5, 65, 5)).index(params["duration_min"]))
    victims  = st.selectbox("Victims", options=list(range(5, 21)),
                            index=list(range(5, 21)).index(params["n_victims"]))
    units    = st.selectbox("Rescue Units", options=list(range(3, 11)),
                            index=list(range(3, 11)).index(params["n_units"]))

    st.session_state.sim_params["duration_min"] = duration
    st.session_state.sim_params["n_victims"]    = victims
    st.session_state.sim_params["n_units"]      = units

    # ── Algorithm selectbox ──────────────────────────────────────────────
    algo_labels  = list(ALGO_CODES.keys())
    current_algo = params.get("algorithm", "Hungarian")
    algo_idx     = algo_labels.index(current_algo) if current_algo in algo_labels else 0

    algo = st.selectbox(
        "Dispatch Algorithm",
        options=algo_labels,
        index=algo_idx,
        help="Hungarian is the optimal baseline (this paper). Others are comparison baselines.",
    )
    st.session_state.sim_params["algorithm"] = algo

    st.divider()

    # ── Run / Reset ──────────────────────────────────────────────────────
    run_disabled = st.session_state.run_status == "computing"
    if st.button("Run Simulation", type="primary",
                 use_container_width=True, disabled=run_disabled):
        on_run()

    if st.button("Reset", use_container_width=True):
        st.session_state.sim_cache  = None
        st.session_state.run_status = "idle"
        st.rerun()

    st.divider()

    # ── Live Data Sources expander ────────────────────────────────────────
    with st.expander("Live Data Sources", expanded=False):
        if population_grid is not None:
            total_pop = int(population_grid.sum())
            st.success(f"WorldPop — {total_pop:,} people in area")
        else:
            st.warning("WorldPop — not loaded")

        if building_pixels:
            st.success(f"Buildings — {len(building_pixels):,} structures")
        else:
            st.warning("Buildings — not loaded")

        if alert_service:
            gdacs = alert_service.get_dashboard_summary()
            if gdacs.get("has_alert"):
                lvl = gdacs.get("alert_level", "")
                color_map = {"Green": "🟢", "Orange": "🟠", "Red": "🔴"}
                icon = color_map.get(lvl, "⚪")
                st.error(
                    f"GDACS {icon} {lvl} — {gdacs.get('event_name', '')}\n\n"
                    f"Severity ×{gdacs.get('severity_multiplier', 1.0):.1f}"
                )
            else:
                st.info("GDACS — no active flood alerts")

    st.divider()

    # ── Back to Landing ──────────────────────────────────────────────────
    if st.button("Home", use_container_width=True):
        st.session_state.page = "landing"
        st.rerun()
