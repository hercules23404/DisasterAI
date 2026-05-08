import streamlit as st

_LANDING_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600;700&family=Fira+Sans:wght@300;400;500;600;700&display=swap');

.main .block-container { padding-top: 2.8rem; }

/* ── Radial glow behind hero ── */
.landing-glow {
    position: fixed;
    top: -180px;
    left: 50%;
    transform: translateX(-50%);
    width: 1000px;
    height: 550px;
    background: radial-gradient(ellipse at center,
        rgba(0,212,255,0.07) 0%,
        rgba(167,139,250,0.05) 40%,
        rgba(255,45,120,0.02) 65%,
        transparent 75%);
    pointer-events: none;
    z-index: 0;
}

/* ── Hero eyebrow ── */
.hero-eyebrow {
    font-family: 'Fira Code', monospace;
    font-size: 0.72rem;
    font-weight: 600;
    color: #00d4ff;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    margin-bottom: 0.6rem;
    opacity: 0.8;
}

/* ── Hero title ── */
.hero-title {
    font-family: 'Fira Code', monospace;
    font-size: clamp(3.5rem, 10vw, 6.5rem);
    font-weight: 700;
    background: linear-gradient(110deg,
        #00d4ff 0%,
        #3b82f6 28%,
        #a78bfa 55%,
        #ff2d78 85%,
        #f59e0b 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.0;
    margin-bottom: 0.4rem;
    letter-spacing: -0.05em;
    filter: drop-shadow(0 0 60px rgba(0,212,255,0.2));
}

/* ── Hero tagline ── */
.hero-tagline {
    font-family: 'Fira Sans', sans-serif;
    font-size: 1.0rem;
    color: #475569;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    margin-bottom: 2rem;
}

/* ── Scanline accent ── */
.scanline-bar {
    width: 100%;
    height: 1px;
    background: linear-gradient(90deg,
        transparent 0%,
        rgba(0,212,255,0.5) 20%,
        rgba(167,139,250,0.6) 50%,
        rgba(255,45,120,0.4) 80%,
        transparent 100%);
    margin: 1rem 0 1.8rem;
}

/* ── Description ── */
.description-block {
    font-family: 'Fira Sans', sans-serif;
    font-size: 1.05rem;
    color: #94a3b8;
    line-height: 1.8;
    max-width: 760px;
    margin: 0 auto 1.8rem;
}

/* ── Stats strip ── */
.stats-strip {
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg,
        rgba(10,16,34,0.95) 0%,
        rgba(14,22,46,0.9) 100%);
    border: 1px solid rgba(0,212,255,0.1);
    border-radius: 14px;
    padding: 18px 0;
    margin: 0 auto 2.8rem;
    max-width: 680px;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    box-shadow:
        0 4px 28px rgba(0,0,0,0.35),
        inset 0 1px 0 rgba(255,255,255,0.04),
        inset 0 -1px 0 rgba(0,0,0,0.2);
    position: relative;
    overflow: hidden;
}
.stats-strip::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg,
        transparent,
        rgba(0,212,255,0.3),
        rgba(167,139,250,0.3),
        rgba(255,45,120,0.2),
        transparent);
}
.stat-item {
    flex: 1;
    text-align: center;
    padding: 0 16px;
}
.stat-value {
    display: block;
    font-family: 'Fira Code', monospace;
    font-size: 1.55rem;
    font-weight: 700;
    line-height: 1.15;
    margin-bottom: 3px;
}
.stat-value-1 { color: #00d4ff; }
.stat-value-2 { color: #a78bfa; }
.stat-value-3 { color: #f59e0b; }
.stat-value-4 { color: #00e676; }
.stat-label {
    display: block;
    font-family: 'Fira Sans', sans-serif;
    font-size: 0.7rem;
    color: #3d4f6a;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
.stat-divider {
    width: 1px;
    height: 38px;
    background: linear-gradient(180deg,
        transparent,
        rgba(0,212,255,0.18),
        transparent);
    flex-shrink: 0;
}

/* ── Feature cards ── */
.feature-card {
    background: linear-gradient(145deg,
        rgba(10,16,34,0.97) 0%,
        rgba(14,22,48,0.92) 100%);
    border: 1px solid var(--fc-border, rgba(0,212,255,0.18));
    border-radius: 16px;
    padding: 26px 20px 24px;
    height: 100%;
    transition: border-color 0.3s ease, box-shadow 0.3s ease, transform 0.25s ease;
    cursor: default;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    box-shadow:
        0 4px 28px rgba(0,0,0,0.4),
        inset 0 1px 0 rgba(255,255,255,0.04);
    position: relative;
    overflow: hidden;
}
.feature-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg,
        transparent,
        var(--fc-top, rgba(0,212,255,0.45)),
        transparent);
}
.feature-card::after {
    content: '';
    position: absolute;
    bottom: 0; right: 0;
    width: 80px; height: 80px;
    background: radial-gradient(circle, var(--fc-glow, rgba(0,212,255,0.06)) 0%, transparent 70%);
    pointer-events: none;
}
.feature-card:hover {
    border-color: var(--fc-border-hover, rgba(0,212,255,0.45));
    box-shadow:
        0 0 35px var(--fc-glow, rgba(0,212,255,0.12)),
        0 12px 40px rgba(0,0,0,0.5);
    transform: translateY(-4px);
}

.feature-icon-wrap {
    width: 50px;
    height: 50px;
    border-radius: 12px;
    background: var(--fc-icon-bg, rgba(0,212,255,0.07));
    border: 1px solid var(--fc-border, rgba(0,212,255,0.18));
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 16px;
    position: relative;
}

.feature-title {
    font-family: 'Fira Code', monospace;
    font-size: 0.85rem;
    font-weight: 700;
    color: var(--fc-color, #00d4ff);
    letter-spacing: 0.05em;
    margin-bottom: 10px;
    text-transform: uppercase;
}

.feature-desc {
    font-family: 'Fira Sans', sans-serif;
    font-size: 0.86rem;
    color: #4a5e7a;
    line-height: 1.68;
}

/* ── CTA Button ── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg,
        #1e4fff 0%,
        #00d4ff 45%,
        #a78bfa 85%,
        #ff2d78 100%) !important;
    background-size: 200% 100% !important;
    border: none !important;
    border-radius: 12px !important;
    color: #070b15 !important;
    font-family: 'Fira Code', monospace !important;
    font-weight: 700 !important;
    font-size: 1.0rem !important;
    padding: 0.75rem 2.5rem !important;
    letter-spacing: 0.06em !important;
    box-shadow:
        0 0 35px rgba(0,212,255,0.3),
        0 0 70px rgba(167,139,250,0.12) !important;
    transition: all 0.3s ease !important;
}
.stButton > button[kind="primary"]:hover {
    box-shadow:
        0 0 55px rgba(0,212,255,0.5),
        0 0 90px rgba(167,139,250,0.2) !important;
    transform: translateY(-2px) !important;
    filter: brightness(1.08) !important;
}

/* ── Footer ── */
.footer-block {
    font-family: 'Fira Sans', sans-serif;
    font-size: 0.83rem;
    color: #2a3a50;
    text-align: center;
    padding: 1rem 0 0.5rem;
    line-height: 1.9;
}
.footer-block a { color: #00d4ff; text-decoration: none; }
.footer-block strong { color: #3d5066; }
</style>
"""

BRIEF_TEXT = """
DAI simulates urban flood disasters in real time and orchestrates rescue operations
using a predictive multi-agent system built on the Mumbai Mithi River basin. It forecasts
which roads will flood next, dispatches rescue units via globally optimal assignment, and
reroutes them dynamically as conditions change.
"""

_ICON_WAVE = (
    '<svg width="26" height="26" viewBox="0 0 24 24" fill="none">'
    '<path d="M3 8C5 5.5 7 5.5 9 8C11 10.5 13 10.5 15 8C17 5.5 19 5.5 21 8"'
    ' stroke="#00d4ff" stroke-width="2" stroke-linecap="round"/>'
    '<path d="M3 13C5 10.5 7 10.5 9 13C11 15.5 13 15.5 15 13C17 10.5 19 10.5 21 13"'
    ' stroke="#00d4ff" stroke-width="2" stroke-linecap="round" stroke-opacity="0.55"/>'
    '<path d="M3 18C5 15.5 7 15.5 9 18C11 20.5 13 20.5 15 18C17 15.5 19 15.5 21 18"'
    ' stroke="#00d4ff" stroke-width="2" stroke-linecap="round" stroke-opacity="0.25"/>'
    '</svg>'
)

_ICON_TARGET = (
    '<svg width="26" height="26" viewBox="0 0 24 24" fill="none">'
    '<circle cx="12" cy="12" r="9" stroke="#a78bfa" stroke-width="1.5"/>'
    '<circle cx="12" cy="12" r="4.5" stroke="#a78bfa" stroke-width="1.5"/>'
    '<circle cx="12" cy="12" r="1.75" fill="#a78bfa"/>'
    '<line x1="12" y1="2" x2="12" y2="6.5" stroke="#a78bfa" stroke-width="1.5" stroke-linecap="round"/>'
    '<line x1="12" y1="17.5" x2="12" y2="22" stroke="#a78bfa" stroke-width="1.5" stroke-linecap="round"/>'
    '<line x1="2" y1="12" x2="6.5" y2="12" stroke="#a78bfa" stroke-width="1.5" stroke-linecap="round"/>'
    '<line x1="17.5" y1="12" x2="22" y2="12" stroke="#a78bfa" stroke-width="1.5" stroke-linecap="round"/>'
    '</svg>'
)

_ICON_HEXWARN = (
    '<svg width="26" height="26" viewBox="0 0 24 24" fill="none">'
    '<path d="M12 2L20.66 7V17L12 22L3.34 17V7L12 2Z"'
    ' stroke="#f59e0b" stroke-width="1.5" stroke-linejoin="round"/>'
    '<line x1="12" y1="8.5" x2="12" y2="13.5"'
    ' stroke="#f59e0b" stroke-width="2.5" stroke-linecap="round"/>'
    '<circle cx="12" cy="16.5" r="1.3" fill="#f59e0b"/>'
    '</svg>'
)

_ICON_SHIELD = (
    '<svg width="26" height="26" viewBox="0 0 24 24" fill="none">'
    '<path d="M12 2L4 6V12C4 16.4 7.4 20.5 12 21.4C16.6 20.5 20 16.4 20 12V6L12 2Z"'
    ' stroke="#00e676" stroke-width="1.5" stroke-linejoin="round"/>'
    '<polyline points="8.5,12 11,14.5 15.5,9.5"'
    ' stroke="#00e676" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
    '</svg>'
)

FEATURES = [
    {
        "icon": _ICON_WAVE,
        "title": "Predictive Pipeline",
        "desc": "Forecasts flood spread N steps ahead using D8 hydraulic propagation on real SRTM terrain data.",
        "fc_border":       "rgba(0,212,255,0.18)",
        "fc_border_hover": "rgba(0,212,255,0.48)",
        "fc_glow":         "rgba(0,212,255,0.12)",
        "fc_icon_bg":      "rgba(0,212,255,0.07)",
        "fc_top":          "rgba(0,212,255,0.45)",
        "fc_color":        "#00d4ff",
    },
    {
        "icon": _ICON_TARGET,
        "title": "Hungarian Dispatch",
        "desc": "Globally optimal unit-to-victim assignment — provably better than any greedy heuristic.",
        "fc_border":       "rgba(167,139,250,0.18)",
        "fc_border_hover": "rgba(167,139,250,0.48)",
        "fc_glow":         "rgba(167,139,250,0.12)",
        "fc_icon_bg":      "rgba(167,139,250,0.07)",
        "fc_top":          "rgba(167,139,250,0.45)",
        "fc_color":        "#a78bfa",
    },
    {
        "icon": _ICON_HEXWARN,
        "title": "Composite Risk Score",
        "desc": "Four-component weighted formula evaluates victim danger live: flood depth, prediction, health, time.",
        "fc_border":       "rgba(245,158,11,0.18)",
        "fc_border_hover": "rgba(245,158,11,0.48)",
        "fc_glow":         "rgba(245,158,11,0.12)",
        "fc_icon_bg":      "rgba(245,158,11,0.07)",
        "fc_top":          "rgba(245,158,11,0.45)",
        "fc_color":        "#f59e0b",
    },
    {
        "icon": _ICON_SHIELD,
        "title": "Validated Results",
        "desc": "Benchmarked against multiple baseline algorithms across 200 independent simulation runs.",
        "fc_border":       "rgba(0,230,118,0.18)",
        "fc_border_hover": "rgba(0,230,118,0.48)",
        "fc_glow":         "rgba(0,230,118,0.12)",
        "fc_icon_bg":      "rgba(0,230,118,0.07)",
        "fc_top":          "rgba(0,230,118,0.45)",
        "fc_color":        "#00e676",
    },
]

FOOTER_TEXT = (
    "**Authors:** Viraj Champanera · Abhinav Tripathi · Dr. R Mohandas  \n"
    "SRM Institute of Science and Technology · Department of Computational Intelligence"
)


def render_landing():
    st.markdown(_LANDING_CSS, unsafe_allow_html=True)

    # Radial glow overlay
    st.markdown("<div class='landing-glow'></div>", unsafe_allow_html=True)

    # ── Hero ──────────────────────────────────────────────────────────
    st.markdown(
        "<div class='hero-eyebrow'>Disaster Response Intelligence</div>"
        "<div class='hero-title'>DAI</div>"
        "<div class='hero-tagline'>Predictive Multi-Agent Flood Rescue Dispatch</div>",
        unsafe_allow_html=True,
    )
    st.markdown("<div class='scanline-bar'></div>", unsafe_allow_html=True)

    # ── Description ───────────────────────────────────────────────────
    st.markdown(
        f"<div class='description-block'>{BRIEF_TEXT.strip()}</div>",
        unsafe_allow_html=True,
    )

    # ── Stats strip ───────────────────────────────────────────────────
    st.markdown("""
    <div class="stats-strip">
        <div class="stat-item">
            <span class="stat-value stat-value-1">200</span>
            <span class="stat-label">Simulation Runs</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-item">
            <span class="stat-value stat-value-2">5</span>
            <span class="stat-label">Algorithms</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-item">
            <span class="stat-value stat-value-3">37.5%</span>
            <span class="stat-label">Faster Response</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-item">
            <span class="stat-value stat-value-4">217%</span>
            <span class="stat-label">Score Improvement</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Feature cards ─────────────────────────────────────────────────
    cols = st.columns(4, gap="small")
    for col, feat in zip(cols, FEATURES):
        with col:
            st.markdown(
                f"<div class='feature-card' style='"
                f"--fc-border:{feat['fc_border']};"
                f"--fc-border-hover:{feat['fc_border_hover']};"
                f"--fc-glow:{feat['fc_glow']};"
                f"--fc-icon-bg:{feat['fc_icon_bg']};"
                f"--fc-top:{feat['fc_top']};"
                f"--fc-color:{feat['fc_color']};'>"
                f"<div class='feature-icon-wrap'>{feat['icon']}</div>"
                f"<div class='feature-title'>{feat['title']}</div>"
                f"<div class='feature-desc'>{feat['desc']}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)

    # ── CTA button ────────────────────────────────────────────────────
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        if st.button("Launch Simulation", type="primary", use_container_width=True):
            st.session_state.page = "simulation"
            st.rerun()

    # ── Footer ────────────────────────────────────────────────────────
    st.divider()
    st.markdown(
        f"<div class='footer-block'>{FOOTER_TEXT}</div>",
        unsafe_allow_html=True,
    )
