"""
dashboard.py — DisasterAI entry point.
Single-page routing via st.session_state.page.
"""

import streamlit as st

# ── Page config (must be first Streamlit call) ────────────────────────
st.set_page_config(
    page_title="DisasterAI — Flood Rescue Command Center",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="auto",
)

# ── Global base CSS ───────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600;700&family=Fira+Sans:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Fira Sans', sans-serif;
    background-color: #0a0f1e;
    color: #e2e8f0;
}
.main .block-container {
    padding-top: 1.5rem;
    padding-bottom: 1.5rem;
}
h1, h2, h3 {
    font-family: 'Fira Code', monospace;
    color: #e2e8f0;
}
a { color: #00d4ff; }
hr {
    border: none;
    border-top: 1px solid rgba(0,212,255,0.12);
    margin: 1.5rem 0;
}
#MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── State initialisation ──────────────────────────────────────────────
DEFAULTS = {
    "page": "landing",
    "sim_params": {
        "duration_min":    30,
        "n_victims":       10,
        "n_units":         6,
        "algorithm":       "Hungarian",
        "scenario_preset": "Moderate",
    },
    "sim_cache":      None,
    "playback_speed": 1,
    "current_frame":  0,
    "run_status":     "idle",
}

for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Router ────────────────────────────────────────────────────────────
page = st.session_state.page

if page == "landing":
    from views.landing import render_landing
    render_landing()

elif page == "simulation":
    from views.simulation import render_simulation
    render_simulation()

elif page == "results":
    from views.results import render_results
    render_results()

else:
    st.error(f"Unknown page: {page!r}")
    if st.button("Go Home"):
        st.session_state.page = "landing"
        st.rerun()
