import streamlit as st

_HUD_CSS = """
<style>
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, rgba(10,20,45,0.92) 0%, rgba(16,32,64,0.88) 100%);
    border: 1px solid rgba(0,212,255,0.22);
    border-radius: 10px;
    padding: 14px 16px;
    box-shadow: 0 0 18px rgba(0,212,255,0.08), inset 0 1px 0 rgba(255,255,255,0.05);
}
div[data-testid="stMetric"] label {
    color: #64748b !important;
    font-size: 0.78rem !important;
    font-family: 'Fira Sans', sans-serif !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
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
    font-size: 0.82rem !important;
}
</style>
"""

def render_hud_strip(metrics: dict | None) -> None:
    st.markdown(_HUD_CSS, unsafe_allow_html=True)
    cols = st.columns(5)
    labels = ["Time Step", "Rescued", "Remaining", "Active Units", "Score"]

    if metrics is None:
        for col, label in zip(cols, labels):
            with col:
                st.metric(label, "—")
        st.caption("Run a simulation to see live metrics.")
        return

    cols[0].metric("Time Step",    metrics["time_step"])
    cols[1].metric("Rescued",      metrics["rescued"],
                   delta=metrics.get("rescued_delta") or None)
    cols[2].metric("Remaining",    metrics["remaining"])
    cols[3].metric("Active Units", metrics["active_units"])
    cols[4].metric("Score",        f"{metrics['total_score']:.1f}")
