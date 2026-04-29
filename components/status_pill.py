import streamlit as st

_STATUS_CONFIG = {
    "idle":      {"label": "● Idle",        "color": "#64748b", "pulse": False},
    "computing": {"label": "● Computing...", "color": "#ffb300", "pulse": True},
    "ready":     {"label": "● Ready",        "color": "#00e676", "pulse": False},
    "error":     {"label": "● Error",        "color": "#ff2d55", "pulse": False},
}

_PULSE_KEYFRAMES = """
<style>
@keyframes status-pulse {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.4; }
}
.status-pill-pulse { animation: status-pulse 1.2s ease-in-out infinite; }
</style>
"""

def render_status_pill(status: str) -> None:
    cfg = _STATUS_CONFIG.get(status, _STATUS_CONFIG["idle"])
    pulse_class = "status-pill-pulse" if cfg["pulse"] else ""
    st.markdown(_PULSE_KEYFRAMES, unsafe_allow_html=True)
    st.markdown(
        f"""<span class="{pulse_class}" style="
            display: inline-block;
            background: rgba(10,20,45,0.85);
            border: 1px solid {cfg['color']}44;
            border-radius: 20px;
            padding: 4px 14px;
            font-size: 0.82rem;
            font-family: 'Fira Code', monospace;
            font-weight: 600;
            color: {cfg['color']};
            letter-spacing: 0.03em;
            box-shadow: 0 0 8px {cfg['color']}33;
        ">{cfg['label']}</span>""",
        unsafe_allow_html=True,
    )
