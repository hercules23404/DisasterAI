import numpy as np
import rasterio.transform
import plotly.graph_objects as go

from dashboard_utils import step_to_elapsed_str, get_phase_label, format_flood_extent

# ── Color constants (all visual tweaks live here) ─────────────────────
ROAD_COLORS = {
    "safe":              "rgba(255,255,255,0.18)",
    "predicted_flood":   "rgba(255,152,0,0.75)",
    "currently_flooded": "#ff1744",
    "unit_traversal":    "rgba(0,212,255,0.9)",
}

VICTIM_COLORS = {
    "low_risk":  "#4caf50",
    "mid_risk":  "#ff9800",
    "high_risk": "#ff1744",
    "rescued":   "rgba(0,230,118,0.35)",
    "deceased":  "#78909c",
}

BURST_COLORS = {
    "rescue":   "#00e676",
    "casualty": "#ff2d55",
}

UNIT_COLOR     = "#00bcd4"
ROUTE_COLOR    = "#00e676"

FLOOD_COLORSCALE = [
    [0.0, "rgba(13,71,161,0)"],
    [0.2, "rgba(13,71,161,0.30)"],
    [0.5, "rgba(30,111,255,0.55)"],
    [0.8, "rgba(30,136,229,0.70)"],
    [1.0, "rgba(144,202,249,0.85)"],
]

PRED_COLORSCALE = [
    [0.0, "rgba(255,87,34,0)"],
    [0.2, "rgba(255,87,34,0.12)"],
    [0.5, "rgba(255,152,0,0.28)"],
    [0.8, "rgba(255,87,34,0.42)"],
    [1.0, "rgba(244,67,54,0.55)"],
]


# ── Helpers ───────────────────────────────────────────────────────────

def _rc_to_latlon(transform, r, c):
    x, y = rasterio.transform.xy(transform, int(r), int(c))
    return float(y), float(x)


def _classify_road(u, v, node_to_rc, flood_depth, predicted_depth, threshold=0.15):
    r1, c1 = node_to_rc[u]
    r2, c2 = node_to_rc[v]
    cur_max  = max(float(flood_depth[r1, c1]),  float(flood_depth[r2, c2]))
    pred_max = max(float(predicted_depth[r1, c1]), float(predicted_depth[r2, c2]))

    if cur_max >= threshold:
        return "currently_flooded"
    if pred_max >= threshold:
        return "predicted_flood"
    return "safe"


def _victim_marker_props(risk, health, status):
    if status == "rescued":
        return VICTIM_COLORS["rescued"], 6
    if status == "deceased":
        return VICTIM_COLORS["deceased"], 8

    if risk >= 0.66:
        color = VICTIM_COLORS["high_risk"]
    elif risk >= 0.33:
        color = VICTIM_COLORS["mid_risk"]
    else:
        color = VICTIM_COLORS["low_risk"]

    size = 10 + (1.0 - health) * 12   # 10–22 px
    return color, size


def _build_road_traces(all_edges, node_to_rc, transform, flood_depth, predicted_depth,
                       traversed_edges: set):
    buckets = {"safe": ([], []), "predicted_flood": ([], []), "currently_flooded": ([], [])}
    traversal_lats, traversal_lons = [], []

    for u, v in all_edges:
        state = _classify_road(u, v, node_to_rc, flood_depth, predicted_depth)
        r1, c1 = node_to_rc[u]
        r2, c2 = node_to_rc[v]
        lat1, lon1 = _rc_to_latlon(transform, r1, c1)
        lat2, lon2 = _rc_to_latlon(transform, r2, c2)
        lats, lons = buckets[state]
        lats += [lat1, lat2, None]
        lons += [lon1, lon2, None]

        if (u, v) in traversed_edges or (v, u) in traversed_edges:
            traversal_lats += [lat1, lat2, None]
            traversal_lons += [lon1, lon2, None]

    traces = [
        go.Scattermapbox(
            lat=buckets["safe"][0], lon=buckets["safe"][1], mode="lines",
            line=dict(width=1, color=ROAD_COLORS["safe"]),
            name="Safe Roads", hoverinfo="skip",
        ),
        go.Scattermapbox(
            lat=buckets["predicted_flood"][0], lon=buckets["predicted_flood"][1],
            mode="lines",
            line=dict(width=2.5, color=ROAD_COLORS["predicted_flood"]),
            name="Predicted Flood Road", hoverinfo="skip", opacity=0.85,
        ),
        go.Scattermapbox(
            lat=buckets["currently_flooded"][0], lon=buckets["currently_flooded"][1],
            mode="lines",
            line=dict(width=3, color=ROAD_COLORS["currently_flooded"]),
            name="Flooded Road", hoverinfo="skip", opacity=0.95,
        ),
        go.Scattermapbox(
            lat=traversal_lats, lon=traversal_lons, mode="lines",
            line=dict(width=4, color=ROAD_COLORS["unit_traversal"]),
            name="Unit Path", hoverinfo="skip", opacity=0.95,
        ),
    ]
    return traces


def _build_victim_traces(frame, transform):
    lats, lons, colors, sizes, texts = [], [], [], [], []

    for row in frame["incidents"]:
        r, c, risk, resolved, inc_id, health, is_dead = row
        lat, lon = _rc_to_latlon(transform, r, c)
        risk_scores = frame.get("risk_scores", {})
        composite_risk = risk_scores.get(inc_id, risk)

        if is_dead:
            status = "deceased"
        elif resolved:
            status = "rescued"
        else:
            status = "active"

        color, size = _victim_marker_props(composite_risk, health, status)
        lats.append(lat);  lons.append(lon)
        colors.append(color); sizes.append(size)

        risk_pct = f"{composite_risk:.0%}"
        hp_pct   = f"{health:.0%}"
        if status == "deceased":
            texts.append(f"<b>Victim #{inc_id}</b><br>☠ DECEASED")
        elif status == "rescued":
            texts.append(f"<b>Victim #{inc_id}</b><br>✅ RESCUED")
        else:
            label = "CRITICAL" if composite_risk >= 0.9 else (
                    "HIGH"     if composite_risk >= 0.66 else (
                    "MED"      if composite_risk >= 0.33 else "LOW"))
            texts.append(
                f"<b>Victim #{inc_id}</b><br>Risk: {risk_pct} [{label}]<br>Health: {hp_pct}"
            )

    return go.Scattermapbox(
        lat=lats, lon=lons, mode="markers",
        marker=dict(size=sizes, color=colors, opacity=1.0),
        text=texts, hoverinfo="text", name="Victims",
    )


def _build_unit_traces(frame, transform, node_to_rc):
    unit_lats, unit_lons, unit_texts = [], [], []
    route_lats, route_lons = [], []
    traversed_edges: set = set()

    for row in frame["units"]:
        u_r, u_c, u_status, u_id, u_path, u_target = row
        lat, lon = _rc_to_latlon(transform, u_r, u_c)
        unit_lats.append(lat); unit_lons.append(lon)

        status_label = ("IDLE" if u_status == "idle" else
                        "EN-ROUTE" if u_status == "en-route" else "BUSY")
        tgt_str = f" → V#{u_target}" if u_target is not None else ""
        unit_texts.append(f"<b>Unit #{u_id}</b><br>{status_label}{tgt_str}")

        if u_status == "en-route" and u_path:
            r_lats = [lat]; r_lons = [lon]
            for pr, pc in u_path:
                plat, plon = _rc_to_latlon(transform, pr, pc)
                r_lats.append(plat); r_lons.append(plon)
            route_lats.extend(r_lats + [None])
            route_lons.extend(r_lons + [None])

    units_trace = go.Scattermapbox(
        lat=unit_lats, lon=unit_lons, mode="markers",
        marker=dict(size=17, color=UNIT_COLOR, opacity=1.0, symbol="circle"),
        text=unit_texts, hoverinfo="text", name="Rescue Units",
    )
    route_trace = go.Scattermapbox(
        lat=route_lats, lon=route_lons, mode="lines",
        line=dict(width=2.5, color=ROUTE_COLOR),
        name="Rescue Routes", hoverinfo="skip", opacity=0.9,
    )
    return units_trace, route_trace, traversed_edges


def _build_burst_traces(frame, transform):
    rescue_lats, rescue_lons = [], []
    casualty_lats, casualty_lons = [], []

    events_this_step = frame.get("event_log", [])
    current_step     = frame.get("info", {}).get("step", 0)

    incidents_by_id = {
        row[4]: (row[0], row[1]) for row in frame["incidents"]
    }

    for evt in events_this_step:
        if evt.get("step") != current_step:
            continue
        etype = evt.get("type") or evt.get("event_type", "")
        vic_id = evt.get("victim_id") or evt.get("incident_id")

        if vic_id is None:
            continue
        if vic_id not in incidents_by_id:
            continue

        r, c = incidents_by_id[vic_id]
        lat, lon = _rc_to_latlon(transform, r, c)

        if etype == "rescue":
            rescue_lats.append(lat); rescue_lons.append(lon)
        elif etype == "casualty":
            casualty_lats.append(lat); casualty_lons.append(lon)

    rescue_burst = go.Scattermapbox(
        lat=rescue_lats, lon=rescue_lons, mode="markers",
        marker=dict(size=30, color=BURST_COLORS["rescue"],
                    opacity=0.7, symbol="star"),
        name="Rescue!", hoverinfo="skip",
    )
    casualty_burst = go.Scattermapbox(
        lat=casualty_lats, lon=casualty_lons, mode="markers",
        marker=dict(size=30, color=BURST_COLORS["casualty"],
                    opacity=0.7, symbol="x"),
        name="Casualty", hoverinfo="skip",
    )
    return rescue_burst, casualty_burst


# ── Main public function ──────────────────────────────────────────────

def build_plotly_animation(terrain, frames_data, speed_ms=800):
    center_lat    = (terrain.min_lat + terrain.max_lat) / 2
    center_lon    = (terrain.min_lon + terrain.max_lon) / 2
    transition_ms = max(speed_ms // 3, 80)

    all_edges = [
        (u, v)
        for u, v in terrain.road_graph.edges()
        if u in terrain.node_to_rc and v in terrain.node_to_rc
    ] if terrain.road_graph else []

    plotly_frames = []
    slider_steps  = []

    for i, frame in enumerate(frames_data):
        flood_depth     = frame["flood_depth"]
        predicted_depth = frame.get("predicted_depth", flood_depth)
        info            = frame["info"]

        # ── Flood density layers ─────────────────────────────────────────
        rows, cols = np.where(flood_depth > 0.05)
        f_lats = [_rc_to_latlon(terrain.transform, r, c)[0] for r, c in zip(rows, cols)]
        f_lons = [_rc_to_latlon(terrain.transform, r, c)[1] for r, c in zip(rows, cols)]
        f_z    = [min(float(flood_depth[r, c]), 15.0)       for r, c in zip(rows, cols)]
        if not f_lats:
            f_lats, f_lons, f_z = [center_lat], [center_lon], [0.0]

        pred_rows, pred_cols = np.where(predicted_depth > flood_depth + 0.05)
        pf_lats = [_rc_to_latlon(terrain.transform, r, c)[0] for r, c in zip(pred_rows, pred_cols)]
        pf_lons = [_rc_to_latlon(terrain.transform, r, c)[1] for r, c in zip(pred_rows, pred_cols)]
        pf_z    = [min(float(predicted_depth[r, c]), 15.0)    for r, c in zip(pred_rows, pred_cols)]
        if not pf_lats:
            pf_lats, pf_lons, pf_z = [center_lat], [center_lon], [0.0]

        flood_trace = go.Densitymapbox(
            lat=f_lats, lon=f_lons, z=f_z, radius=18,
            colorscale=FLOOD_COLORSCALE,
            showscale=False, opacity=0.85,
            name="Current Flood", hoverinfo="skip",
        )
        pred_trace = go.Densitymapbox(
            lat=pf_lats, lon=pf_lons, z=pf_z, radius=18,
            colorscale=PRED_COLORSCALE,
            showscale=False, opacity=0.45,
            name="Predicted Flood", hoverinfo="skip",
        )

        # ── Units (extract traversed edges for road highlight) ────────────
        unit_trace, route_trace, traversed_edges = _build_unit_traces(
            frame, terrain.transform, terrain.node_to_rc
        )

        # ── Road classification (3-state) ─────────────────────────────────
        road_traces = _build_road_traces(
            all_edges, terrain.node_to_rc, terrain.transform,
            flood_depth, predicted_depth, traversed_edges,
        )

        # ── Victims ───────────────────────────────────────────────────────
        victim_trace = _build_victim_traces(frame, terrain.transform)

        # ── Burst overlays ────────────────────────────────────────────────
        rescue_burst, casualty_burst = _build_burst_traces(frame, terrain.transform)

        traces = (
            [flood_trace, pred_trace]
            + road_traces
            + [route_trace, victim_trace, unit_trace, rescue_burst, casualty_burst]
        )

        # ── Frame label ───────────────────────────────────────────────────
        time_str     = step_to_elapsed_str(i)
        phase        = get_phase_label(i)
        flood_extent = format_flood_extent(int(np.sum(flood_depth > 0.05)))
        frame_title  = (
            f"{time_str} — {phase} | "
            f"{flood_extent} · "
            f"{info.get('active_incidents', 0)} active · "
            f"{info.get('units_busy', 0)} units moving"
        )

        plotly_frames.append(go.Frame(
            data=traces, name=str(i),
            layout=go.Layout(title_text=frame_title),
        ))
        slider_steps.append({
            "args": [[str(i)], {
                "frame":      {"duration": speed_ms, "redraw": True},
                "mode":       "immediate",
                "transition": {"duration": transition_ms},
            }],
            "label":  step_to_elapsed_str(i),
            "method": "animate",
        })

    # ── Assemble figure ───────────────────────────────────────────────
    fig = go.Figure(data=plotly_frames[0].data, frames=plotly_frames)
    fig.update_layout(
        mapbox={
            "style": "white-bg",
            "center": {"lat": center_lat, "lon": center_lon},
            "zoom": 13.5,
            "layers": [{
                "below": "traces",
                "sourcetype": "raster",
                "sourceattribution": "Esri World Imagery",
                "source": [
                    "https://server.arcgisonline.com/ArcGIS/rest/services/"
                    "World_Imagery/MapServer/tile/{z}/{y}/{x}"
                ],
            }],
        },
        title=dict(
            text=f"{step_to_elapsed_str(0)} — Press Play to animate",
            font=dict(color="#94a3b8", size=13,
                      family="Fira Code, monospace"),
            x=0.01,
        ),
        height=660,
        margin={"r": 0, "t": 44, "l": 0, "b": 0},
        paper_bgcolor="#0a0f1e",
        plot_bgcolor="#0a0f1e",
        font=dict(color="#e2e8f0", family="Fira Sans, sans-serif"),
        legend=dict(
            bgcolor="rgba(6,12,26,0.88)",
            bordercolor="rgba(0,212,255,0.2)",
            borderwidth=1,
            font=dict(color="#94a3b8", size=11,
                      family="Fira Code, monospace"),
            x=0.01, y=0.99,
            xanchor="left", yanchor="top",
        ),
        updatemenus=[{
            "type": "buttons",
            "direction": "left",
            "showactive": False,
            "x": 0.12, "y": -0.04,
            "xanchor": "right", "yanchor": "top",
            "bgcolor": "#0a1628",
            "bordercolor": "rgba(0,212,255,0.3)",
            "font": {"color": "#00d4ff", "size": 13,
                     "family": "Fira Code, monospace"},
            "buttons": [
                {
                    "label": "▶ Play",
                    "method": "animate",
                    "args": [None, {
                        "frame": {"duration": speed_ms, "redraw": True},
                        "fromcurrent": True,
                        "transition": {"duration": transition_ms, "easing": "linear"},
                    }],
                },
                {
                    "label": "⏸ Pause",
                    "method": "animate",
                    "args": [[None], {
                        "frame": {"duration": 0, "redraw": False},
                        "mode": "immediate",
                        "transition": {"duration": 0},
                    }],
                },
            ],
        }],
        sliders=[{
            "steps": slider_steps,
            "transition": {"duration": transition_ms},
            "x": 0.13, "len": 0.87, "y": -0.04,
            "currentvalue": {
                "prefix": "Time: ",
                "visible": True,
                "xanchor": "right",
                "font": {"color": "#00d4ff", "size": 13,
                         "family": "Fira Code, monospace"},
            },
            "font":        {"color": "#64748b"},
            "bgcolor":     "#0a1628",
            "bordercolor": "rgba(0,212,255,0.25)",
            "tickcolor":   "rgba(0,212,255,0.15)",
        }],
    )
    return fig
