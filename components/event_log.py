import streamlit as st

def render_event_log_popover(events: list, current_step: int) -> None:
    filtered = [e for e in events if e.get("step", 0) <= current_step]
    recent   = filtered[-10:]
    label    = f"Event Log ({len(filtered)})"

    with st.popover(label, use_container_width=False):
        st.markdown(
            "<span style='font-family:Fira Code,monospace;font-size:0.9rem;"
            "color:#00d4ff;font-weight:700;'>Last 10 events</span>",
            unsafe_allow_html=True,
        )
        if not recent:
            st.caption("No events yet.")
            return

        for e in reversed(recent):
            etype = e.get("event_type") or e.get("type", "info")
            if etype == "rescue":
                icon, color = "✅", "#00e676"
            elif etype == "casualty":
                icon, color = "☠", "#ff2d55"
            elif etype == "reroute":
                icon, color = "↩", "#00d4ff"
            elif etype == "dispatch":
                icon, color = "→", "#ffb300"
            else:
                icon, color = "ℹ", "#64748b"

            step  = e.get("step", 0)
            msg   = e.get("message", "")
            st.markdown(
                f"<div style='border-left:3px solid {color};padding:5px 10px;"
                f"margin:4px 0;background:rgba(0,0,0,0.25);border-radius:0 6px 6px 0;'>"
                f"<span style='color:{color};font-family:Fira Code,monospace;"
                f"font-size:0.78rem;font-weight:700;'>{icon} Step {step}</span>"
                f"<div style='color:#c8d6e5;font-size:0.82rem;margin-top:2px;'>{msg}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )


def render_legend_popover() -> None:
    with st.popover("Map Legend", use_container_width=False):
        entries = [
            ("#ff1744", "Currently flooded road"),
            ("#ff9800", "Predicted flood road"),
            ("rgba(255,255,255,0.45)", "Safe road"),
            ("#00e676", "Rescue route"),
            ("#ff1744", "High-risk victim"),
            ("#ff9800", "Mid-risk victim"),
            ("#4caf50", "Low-risk victim"),
            ("#00bcd4", "Rescue unit"),
            ("#00e676", "Rescue burst"),
            ("#ff2d55", "Casualty burst"),
        ]
        for color, label in entries:
            st.markdown(
                f"<div style='display:flex;align-items:center;gap:10px;"
                f"padding:4px 0;'>"
                f"<span style='display:inline-block;width:14px;height:14px;"
                f"border-radius:3px;background:{color};flex-shrink:0;'></span>"
                f"<span style='color:#c8d6e5;font-size:0.84rem;'>{label}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )
