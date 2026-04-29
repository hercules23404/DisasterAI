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
    background: linear-gradient(180deg, #060c1a 0%, #0a1628 100%);
    border-right: 1px solid rgba(0,212,255,0.12);
}
section[data-testid="stSidebar"] .stSlider > div > div > div {
    background: rgba(0,212,255,0.15) !important;
}
section[data-testid="stSidebar"] .stSlider > div > div > div > div {
    background: #00d4ff !important;
}
section[data-testid="stSidebar"] label {
    color: #94a3b8 !important;
    font-size: 0.82rem !important;
    font-family: 'Fira Sans', sans-serif !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
}
section[data-testid="stSidebar"] .stSelectbox > div > div {
    background: rgba(10,20,45,0.9) !important;
    border: 1px solid rgba(0,212,255,0.25) !important;
    border-radius: 8px !important;
    color: #e2e8f0 !important;
}
section[data-testid="stSidebar"] .stButton > button {
    border-radius: 8px !important;
    font-family: 'Fira Code', monospace !important;
    font-weight: 600 !important;
    letter-spacing: 0.04em !important;
    transition: all 0.2s ease !important;
}
section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1e6fff 0%, #00d4ff 100%) !important;
    border: none !important;
    color: #0a0f1e !important;
    box-shadow: 0 0 20px rgba(0,212,255,0.3) !important;
}
section[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
    box-shadow: 0 0 30px rgba(0,212,255,0.5) !important;
    transform: translateY(-1px) !important;
}
section[data-testid="stSidebar"] .stButton > button:not([kind="primary"]) {
    background: rgba(10,20,45,0.85) !important;
    border: 1px solid rgba(0,212,255,0.25) !important;
    color: #94a3b8 !important;
}
section[data-testid="stSidebar"] .stButton > button:not([kind="primary"]):hover {
    border-color: rgba(0,212,255,0.6) !important;
    color: #00d4ff !important;
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

    st.markdown(
        "<h3 style='color:#00d4ff;font-family:Fira Code,monospace;"
        "font-size:1rem;letter-spacing:0.05em;margin-bottom:4px;'>"
        "⚙ SIMULATION CONTROLS</h3>",
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

    # ── Sliders ──────────────────────────────────────────────────────────
    duration = st.slider("Duration (minutes)", 5, 60,
                         params["duration_min"], step=5)
    victims  = st.slider("Victims",            5, 20, params["n_victims"])
    units    = st.slider("Rescue Units",        3, 10, params["n_units"])

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
    if st.button("▶ Run Simulation", type="primary",
                 use_container_width=True, disabled=run_disabled):
        on_run()

    if st.button("↻ Reset", use_container_width=True):
        st.session_state.sim_cache  = None
        st.session_state.run_status = "idle"
        st.rerun()

    st.divider()

    # ── Live Data Sources expander ────────────────────────────────────────
    with st.expander("📡 Live Data Sources", expanded=False):
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
    if st.button("← Home", use_container_width=True):
        st.session_state.page = "landing"
        st.rerun()
