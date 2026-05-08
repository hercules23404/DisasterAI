import streamlit as st

_HUD_CSS = """
<style>
/* ── Base metric card ── */
div[data-testid="stMetric"] {
    background: linear-gradient(145deg, rgba(10,16,34,0.95) 0%, rgba(14,22,46,0.9) 100%);
    border: 1px solid rgba(0,212,255,0.18);
    border-radius: 12px;
    padding: 14px 16px;
    box-shadow: 0 0 20px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.04);
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
}
div[data-testid="stMetric"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,212,255,0.35), transparent);
}

div[data-testid="stMetric"] label {
    color: #3d5270 !important;
    font-size: 0.72rem !important;
    font-family: 'Fira Code', monospace !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    font-weight: 600 !important;
}
div[data-testid="stMetricValue"] {
    color: #00d4ff !important;
    font-family: 'Fira Code', monospace !important;
    font-weight: 700 !important;
    font-size: 1.5rem !important;
}
div[data-testid="stMetricDelta"] svg { display: none; }
div[data-testid="stMetricDelta"] > div {
    color: #00e676 !important;
    font-family: 'Fira Code', monospace !important;
    font-size: 0.8rem !important;
}

/* ── Per-column accent colors ── */
/* Column 1: Victims — cyan */
div[data-testid="stHorizontalBlock"] > div:nth-child(1) div[data-testid="stMetric"] {
    border-color: rgba(0,212,255,0.22) !important;
    box-shadow: 0 0 22px rgba(0,212,255,0.07), inset 0 1px 0 rgba(255,255,255,0.04) !important;
}
div[data-testid="stHorizontalBlock"] > div:nth-child(1) div[data-testid="stMetricValue"] {
    color: #00d4ff !important;
}
div[data-testid="stHorizontalBlock"] > div:nth-child(1) div[data-testid="stMetric"]::before {
    background: linear-gradient(90deg, transparent, rgba(0,212,255,0.4), transparent) !important;
}

/* Column 2: Rescue Units — purple */
div[data-testid="stHorizontalBlock"] > div:nth-child(2) div[data-testid="stMetric"] {
    border-color: rgba(167,139,250,0.22) !important;
    box-shadow: 0 0 22px rgba(167,139,250,0.07), inset 0 1px 0 rgba(255,255,255,0.04) !important;
}
div[data-testid="stHorizontalBlock"] > div:nth-child(2) div[data-testid="stMetricValue"] {
    color: #a78bfa !important;
}

/* Column 3: Rescued — green */
div[data-testid="stHorizontalBlock"] > div:nth-child(3) div[data-testid="stMetric"] {
    border-color: rgba(0,230,118,0.22) !important;
    box-shadow: 0 0 22px rgba(0,230,118,0.07), inset 0 1px 0 rgba(255,255,255,0.04) !important;
}
div[data-testid="stHorizontalBlock"] > div:nth-child(3) div[data-testid="stMetricValue"] {
    color: #00e676 !important;
}

/* Column 4: Time Steps — amber */
div[data-testid="stHorizontalBlock"] > div:nth-child(4) div[data-testid="stMetric"] {
    border-color: rgba(245,158,11,0.22) !important;
    box-shadow: 0 0 22px rgba(245,158,11,0.07), inset 0 1px 0 rgba(255,255,255,0.04) !important;
}
div[data-testid="stHorizontalBlock"] > div:nth-child(4) div[data-testid="stMetricValue"] {
    color: #f59e0b !important;
}

/* Column 5: Score — magenta */
div[data-testid="stHorizontalBlock"] > div:nth-child(5) div[data-testid="stMetric"] {
    border-color: rgba(255,45,120,0.22) !important;
    box-shadow: 0 0 22px rgba(255,45,120,0.07), inset 0 1px 0 rgba(255,255,255,0.04) !important;
}
div[data-testid="stHorizontalBlock"] > div:nth-child(5) div[data-testid="stMetricValue"] {
    color: #ff2d78 !important;
}
</style>
"""

def render_hud_strip(metrics: dict | None) -> None:
    st.markdown(_HUD_CSS, unsafe_allow_html=True)
    cols = st.columns(5)
    labels = ["Victims", "Rescue Units", "Rescued", "Time Steps", "Score"]

    if metrics is None:
        for col, label in zip(cols, labels):
            with col:
                st.metric(label, "—")
        st.caption("Run a simulation to see live metrics.")
        return

    cols[0].metric("Victims",      metrics["n_victims"])
    cols[1].metric("Rescue Units", metrics["n_units"])
    cols[2].metric("Rescued",      metrics["rescued"],
                   delta=metrics.get("rescued_delta") or None)
    cols[3].metric("Time Steps",   metrics["time_step"])
    cols[4].metric("Score",        f"{metrics['total_score']:.1f}")
