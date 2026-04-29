import streamlit as st

_LANDING_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600;700&family=Fira+Sans:wght@300;400;500;600;700&display=swap');

/* ── Base ── */
.main .block-container { padding-top: 2.5rem; }
body, html { background-color: #0a0f1e; }

/* ── Hero title ── */
.hero-title {
    font-family: 'Fira Code', monospace;
    font-size: clamp(2.4rem, 6vw, 4rem);
    font-weight: 700;
    background: linear-gradient(90deg, #00d4ff 0%, #1e6fff 45%, #a78bfa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.15;
    margin-bottom: 0.25rem;
    letter-spacing: -0.02em;
}
.hero-tagline {
    font-family: 'Fira Sans', sans-serif;
    font-size: 1.1rem;
    color: #64748b;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 1.8rem;
}

/* ── Description ── */
.description-block {
    font-family: 'Fira Sans', sans-serif;
    font-size: 1.05rem;
    color: #94a3b8;
    line-height: 1.75;
    max-width: 820px;
    margin: 0 auto 2.5rem;
}

/* ── Feature cards ── */
.feature-card {
    background: linear-gradient(135deg, rgba(10,20,45,0.92) 0%,
                rgba(16,32,64,0.85) 100%);
    border: 1px solid rgba(0,212,255,0.2);
    border-radius: 14px;
    padding: 24px 20px;
    height: 100%;
    transition: border-color 0.25s ease, box-shadow 0.25s ease, transform 0.2s ease;
    cursor: default;
    box-shadow: 0 4px 24px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.04);
}
.feature-card:hover {
    border-color: rgba(0,212,255,0.55);
    box-shadow: 0 0 28px rgba(0,212,255,0.18), 0 8px 32px rgba(0,0,0,0.4);
    transform: translateY(-2px);
}
.feature-icon {
    font-size: 1.9rem;
    margin-bottom: 12px;
    display: block;
}
.feature-title {
    font-family: 'Fira Code', monospace;
    font-size: 0.92rem;
    font-weight: 700;
    color: #00d4ff;
    letter-spacing: 0.04em;
    margin-bottom: 8px;
    text-transform: uppercase;
}
.feature-desc {
    font-family: 'Fira Sans', sans-serif;
    font-size: 0.88rem;
    color: #64748b;
    line-height: 1.6;
}

/* ── CTA Button ── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1e6fff 0%, #00d4ff 100%) !important;
    border: none !important;
    border-radius: 10px !important;
    color: #0a0f1e !important;
    font-family: 'Fira Code', monospace !important;
    font-weight: 700 !important;
    font-size: 1.05rem !important;
    padding: 0.65rem 2.5rem !important;
    letter-spacing: 0.05em !important;
    box-shadow: 0 0 30px rgba(0,212,255,0.35) !important;
    transition: all 0.25s ease !important;
}
.stButton > button[kind="primary"]:hover {
    box-shadow: 0 0 50px rgba(0,212,255,0.55) !important;
    transform: translateY(-2px) !important;
}

/* ── Footer ── */
.footer-block {
    font-family: 'Fira Sans', sans-serif;
    font-size: 0.84rem;
    color: #334155;
    text-align: center;
    padding: 1rem 0 0.5rem;
    line-height: 1.8;
}
.footer-block a { color: #00d4ff; text-decoration: none; }
.footer-block a:hover { text-decoration: underline; }

/* ── Scanline accent (decoration only) ── */
.scanline-bar {
    width: 100%;
    height: 2px;
    background: linear-gradient(90deg, transparent, #00d4ff44, #1e6fff66, transparent);
    margin: 1.5rem 0;
}
</style>
"""

BRIEF_TEXT = """
DisasterAI simulates urban flood disasters in real time and orchestrates rescue operations
using a predictive multi-agent system built on the Mumbai Mithi River basin. It forecasts
which roads will flood next, dispatches rescue units via globally optimal assignment, and
reroutes them dynamically as conditions change.

The system was validated across **200 simulation runs** against five baseline algorithms,
achieving a **217% score improvement** and **37% faster response times** over greedy
approaches. Statistically significant at p < 0.001 with Cohen's d = 1.85.
"""

FEATURES = [
    {
        "icon": "🌊",
        "title": "Predictive Pipeline",
        "desc": "Forecasts flood spread N steps ahead using D8 hydraulic propagation on real SRTM terrain data.",
    },
    {
        "icon": "🎯",
        "title": "Hungarian Dispatch",
        "desc": "Globally optimal unit-to-victim assignment in O(n³) — provably better than any greedy heuristic.",
    },
    {
        "icon": "📊",
        "title": "Composite Risk Scoring",
        "desc": "4-component weighted formula evaluates victim danger live: flood depth, prediction, health, time.",
    },
    {
        "icon": "✅",
        "title": "Validated Results",
        "desc": "p < 0.001 statistical significance across 100 baseline + 100 ablation runs. No cherry-picking.",
    },
]

FOOTER_TEXT = (
    "**Authors:** Viraj Champanera · Abhinav Tripathi · Dr. R Mohandas  \n"
    "SRM Institute of Science and Technology · Department of Computational Intelligence"
)


def render_landing():
    st.markdown(_LANDING_CSS, unsafe_allow_html=True)

    # ── Hero ──────────────────────────────────────────────────────────
    st.markdown(
        "<div class='hero-title'>DisasterAI</div>"
        "<div class='hero-tagline'>Predictive Multi-Agent Flood Rescue Dispatch</div>",
        unsafe_allow_html=True,
    )
    st.markdown("<div class='scanline-bar'></div>", unsafe_allow_html=True)

    # ── Description ───────────────────────────────────────────────────
    st.markdown(
        f"<div class='description-block'>{BRIEF_TEXT.strip()}</div>",
        unsafe_allow_html=True,
    )

    # ── Feature cards ─────────────────────────────────────────────────
    cols = st.columns(4)
    for col, feat in zip(cols, FEATURES):
        with col:
            st.markdown(
                f"<div class='feature-card'>"
                f"<span class='feature-icon'>{feat['icon']}</span>"
                f"<div class='feature-title'>{feat['title']}</div>"
                f"<div class='feature-desc'>{feat['desc']}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)

    # ── CTA button (centered) ─────────────────────────────────────────
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        if st.button("▶ Launch Simulation", type="primary", use_container_width=True):
            st.session_state.page = "simulation"
            st.rerun()

    # ── Footer ────────────────────────────────────────────────────────
    st.divider()
    st.markdown(
        f"<div class='footer-block'>{FOOTER_TEXT}</div>",
        unsafe_allow_html=True,
    )
