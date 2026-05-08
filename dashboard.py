"""
dashboard.py — DAI entry point.
Single-page routing via st.session_state.page.
"""

import streamlit as st

# ── Page config (must be first Streamlit call) ────────────────────────
st.set_page_config(
    page_title="DAI — Flood Rescue Command Center",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="auto",
)

# ── Global base CSS ───────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600;700&family=Fira+Sans:wght@300;400;500;600;700&display=swap');

:root {
    --c-cyan:    #00d4ff;
    --c-purple:  #a78bfa;
    --c-amber:   #f59e0b;
    --c-magenta: #ff2d78;
    --c-green:   #00e676;
    --c-blue:    #3b82f6;
    --bg-base:   #070b15;
    --bg-card:   rgba(12,18,35,0.92);
}

html, body {
    background-color: #070b15 !important;
    background-image: radial-gradient(circle, rgba(0,212,255,0.045) 1px, transparent 1px);
    background-size: 28px 28px;
    background-attachment: fixed;
}

[data-testid="stAppViewContainer"] {
    background: transparent !important;
}

[class*="css"] {
    font-family: 'Fira Sans', sans-serif;
    color: #e2e8f0;
}

.main {
    background: transparent !important;
}
.main .block-container {
    padding-top: 1.5rem;
    padding-bottom: 1.5rem;
    background: transparent !important;
}

h1, h2, h3 {
    font-family: 'Fira Code', monospace;
    color: #e2e8f0;
}
h1 {
    background: linear-gradient(110deg, #00d4ff 0%, #a78bfa 60%, #ff2d78 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

a { color: #00d4ff; }

hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent, rgba(0,212,255,0.18), rgba(167,139,250,0.12), transparent) !important;
    margin: 1.5rem 0 !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #070b15; }
::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #00d4ff44, #a78bfa44);
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover { background: linear-gradient(180deg, #00d4ff88, #a78bfa88); }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(7,11,21,0.85) !important;
    border-bottom: 1px solid rgba(0,212,255,0.12) !important;
    gap: 2px !important;
    padding: 0 4px !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Fira Code', monospace !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    color: #475569 !important;
    border-radius: 6px 6px 0 0 !important;
    padding: 8px 18px !important;
    letter-spacing: 0.04em !important;
    transition: color 0.2s ease, background 0.2s ease !important;
    background: transparent !important;
    border: none !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #94a3b8 !important;
    background: rgba(0,212,255,0.05) !important;
}
.stTabs [aria-selected="true"] {
    color: #00d4ff !important;
    background: rgba(0,212,255,0.08) !important;
    border-bottom: 2px solid #00d4ff !important;
}
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }

/* Info/warning/error boxes */
div[data-testid="stInfo"] {
    background: rgba(30,111,255,0.07) !important;
    border: 1px solid rgba(30,111,255,0.22) !important;
    border-radius: 10px !important;
}
div[data-testid="stSuccess"] {
    background: rgba(0,230,118,0.07) !important;
    border: 1px solid rgba(0,230,118,0.22) !important;
    border-radius: 10px !important;
}
div[data-testid="stWarning"] {
    background: rgba(245,158,11,0.07) !important;
    border: 1px solid rgba(245,158,11,0.22) !important;
    border-radius: 10px !important;
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
