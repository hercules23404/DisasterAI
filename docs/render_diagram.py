"""Render the DisasterAI workflow diagram — polished dark-mode PNG."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
from matplotlib.patches import FancyArrowPatch
import matplotlib.patheffects as pe
import numpy as np

# ── palette ────────────────────────────────────────────────────────────────
BG         = "#020617"
GRID_LINE  = "#0D1526"

C_DAT_BG   = "#071526"; C_DAT_BDR  = "#22D3EE"; C_DAT_TXT  = "#BAE6FD"
C_SIM_BG   = "#031509"; C_SIM_BDR  = "#4ADE80"; C_SIM_TXT  = "#BBF7D0"
C_DSH_BG   = "#0D0519"; C_DSH_BDR  = "#A78BFA"; C_DSH_TXT  = "#DDD6FE"
C_EXP_BG   = "#130B00"; C_EXP_BDR  = "#FBBF24"; C_EXP_TXT  = "#FDE68A"

C_PNL_BG   = "#060C1A"; C_PNL_BDR  = "#1E3A5F"
C_ARROW    = "#3B5270"; C_ARROW_HL = "#7DD3FC"
C_LBL      = "#64748B"
C_TITLE    = "#F1F5F9"
C_SUB      = "#475569"
MONO       = "monospace"
SANS       = "DejaVu Sans"

W, H   = 20, 28
DPI    = 250

fig, ax = plt.subplots(figsize=(W, H), facecolor=BG)
ax.set_facecolor(BG)
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")

# subtle dot-grid
for xi in np.linspace(0.02, 0.98, 40):
    for yi in np.linspace(0.02, 0.98, 54):
        ax.plot(xi, yi, ".", color=GRID_LINE, ms=0.9, alpha=0.5, zorder=0)

# ── helpers ────────────────────────────────────────────────────────────────
def panel(x, y, w, h, bg, bdr, title, title_col, dashed=False):
    ls = (0, (6, 4)) if dashed else "solid"
    bx = FancyBboxPatch((x, y), w, h,
                         boxstyle="round,pad=0.005", lw=1.5,
                         linestyle=ls, edgecolor=bdr, facecolor=bg,
                         zorder=2, transform=ax.transAxes)
    ax.add_patch(bx)
    # title bar
    bar = FancyBboxPatch((x, y + h - 0.026), w, 0.026,
                          boxstyle="round,pad=0.0",
                          lw=0, edgecolor="none",
                          facecolor=bdr + "28",          # 16% opacity tint
                          zorder=3, transform=ax.transAxes)
    ax.add_patch(bar)
    ax.text(x + 0.014, y + h - 0.013, title,
            transform=ax.transAxes, color=title_col,
            fontsize=8, fontfamily=MONO, fontweight="bold",
            ha="left", va="center", zorder=4)

def node(cx, cy, w, h, lines, bg, bdr, tc, fs=7.4):
    bx = FancyBboxPatch((cx - w/2, cy - h/2), w, h,
                         boxstyle="round,pad=0.005", lw=1.4,
                         edgecolor=bdr, facecolor=bg,
                         zorder=5, transform=ax.transAxes)
    # inner glow strip at top
    strip = FancyBboxPatch((cx - w/2, cy + h/2 - 0.010), w, 0.010,
                            boxstyle="square,pad=0",
                            lw=0, edgecolor="none",
                            facecolor=bdr + "30",
                            zorder=5, transform=ax.transAxes)
    ax.add_patch(bx)
    ax.add_patch(strip)
    ax.text(cx, cy, "\n".join(lines),
            transform=ax.transAxes, color=tc,
            fontsize=fs, fontfamily=MONO,
            ha="center", va="center", linespacing=1.6,
            zorder=6)

def arr(x0, y0, x1, y1, col=C_ARROW, lw=1.3, dashed=False,
        lbl="", bend=0.0, lbl_col=None):
    ls = "--" if dashed else "-"
    ax.annotate("",
                xy=(x1, y1), xytext=(x0, y0),
                xycoords="axes fraction", textcoords="axes fraction",
                arrowprops=dict(arrowstyle="-|>", color=col, lw=lw,
                                linestyle=ls,
                                connectionstyle=f"arc3,rad={bend}",
                                mutation_scale=14),
                zorder=7)
    if lbl:
        mx, my = (x0+x1)/2, (y0+y1)/2
        ax.text(mx, my, lbl,
                transform=ax.transAxes,
                color=lbl_col or C_LBL, fontsize=6.4, fontfamily=MONO,
                ha="center", va="center", zorder=8,
                bbox=dict(boxstyle="round,pad=0.18",
                          fc=BG, ec=C_PNL_BDR, lw=0.7, alpha=0.92))

def polyline(pts, col, lw=1.3, dashed=False, arrow_end=True):
    """Draw a multi-segment path; optionally put arrowhead at end."""
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    ls = (0, (5, 4)) if dashed else "-"
    ax.plot(xs, ys, color=col, lw=lw, linestyle=ls,
            transform=ax.transAxes, zorder=7, solid_capstyle="round")
    if arrow_end:
        dx = xs[-1] - xs[-2]
        dy = ys[-1] - ys[-2]
        norm = (dx**2 + dy**2)**0.5
        ax.annotate("",
                    xy=(xs[-1], ys[-1]),
                    xytext=(xs[-1] - dx*0.001/norm, ys[-1] - dy*0.001/norm),
                    xycoords="axes fraction", textcoords="axes fraction",
                    arrowprops=dict(arrowstyle="-|>", color=col, lw=lw,
                                    mutation_scale=14),
                    zorder=7)

# ═══════════════════════════════════════════════════════════════════════════
# TITLE
# ═══════════════════════════════════════════════════════════════════════════
ax.text(0.5, 0.977, "DisasterAI — System Workflow",
        transform=ax.transAxes, color=C_TITLE,
        fontsize=18, fontfamily=SANS, fontweight="bold",
        ha="center", va="top", zorder=10)
ax.text(0.5, 0.963, "Multi-Agent Flood Rescue Simulation  ·  Mumbai, India",
        transform=ax.transAxes, color=C_SUB,
        fontsize=8.5, fontfamily=MONO,
        ha="center", va="top", zorder=10)
ax.plot([0.04, 0.96], [0.953, 0.953], color="#1E3A5F", lw=0.9, zorder=8)

# ═══════════════════════════════════════════════════════════════════════════
# [1] DATA INGESTION
# ═══════════════════════════════════════════════════════════════════════════
panel(0.02, 0.840, 0.96, 0.104,
      C_PNL_BG, C_DAT_BDR, "[1]  DATA INGESTION  ·  one-time startup", C_DAT_TXT)

# source nodes
SW, SH = 0.110, 0.048
src = [(0.095, 0.910, ["SRTM DEM", "30 m tiles"]),
       (0.240, 0.910, ["OpenStreetMap", "roads + buildings"]),
       (0.390, 0.910, ["WorldPop", "pop. grid"]),
       (0.540, 0.910, ["GDACS API", "live alerts"])]
for cx, cy, ln in src:
    node(cx, cy, SW, SH, ln, C_DAT_BG, C_DAT_BDR, C_DAT_TXT)

# loader nodes
LW, LH = 0.165, 0.055
ldrs = [(0.180, 0.864, ["terrain_loader.py", "144×144 elev grid  REM", "NetworkX road graph"]),
        (0.380, 0.864, ["building_loader.py", "centroids → pixels"]),
        (0.540, 0.864, ["population_loader.py", "density grid"]),
        (0.720, 0.864, ["disaster_alerts.py", "severity multiplier", "Green / Orange / Red"])]
for cx, cy, ln in ldrs:
    node(cx, cy, LW, LH, ln, C_DAT_BG, C_DAT_BDR, C_DAT_TXT)

# arrows src → loaders
arr(0.095, 0.886, 0.135, 0.864, C_DAT_BDR, 1.1)
arr(0.240, 0.886, 0.225, 0.864, C_DAT_BDR, 1.1)
arr(0.240, 0.886, 0.380, 0.864, C_DAT_BDR, 1.1, bend=-0.15)
arr(0.390, 0.886, 0.540, 0.864, C_DAT_BDR, 1.1)
arr(0.540, 0.886, 0.720, 0.864, C_DAT_BDR, 1.1, bend=-0.12)

# down-arrow INIT → ENV
arr(0.50, 0.840, 0.50, 0.818, C_ARROW_HL, 1.6,
    lbl="grids + graphs", lbl_col=C_ARROW_HL)

# ═══════════════════════════════════════════════════════════════════════════
# [2] SIMULATION LOOP
# ═══════════════════════════════════════════════════════════════════════════
panel(0.02, 0.360, 0.96, 0.450,
      C_PNL_BG, C_SIM_BDR,
      "[2]  SIMULATION LOOP  ·  environment.py  ·  Gym step()", C_SIM_TXT)

# inner dashed sub-panels
panel(0.035, 0.370, 0.445, 0.415,
      "#030E03", C_SIM_BDR, "  propagation + prediction", C_SIM_TXT, dashed=True)
panel(0.520, 0.370, 0.445, 0.415,
      "#030E03", C_SIM_BDR, "  routing + resolution", C_SIM_TXT, dashed=True)

# ── left column ────────────────────────────────────────────────────────────
LX = 0.258
NW2, NH2 = 0.380, 0.064
GAP = 0.074   # centre-to-centre gap

ly = [0.771, 0.771-GAP, 0.771-2*GAP, 0.771-3*GAP, 0.771-4*GAP]
sim_l = [
    (ly[0], ["hazard_propagation.py", "Min-Heap Priority Queue  O(n log n)", "→ flood_depth grid"]),
    (ly[1], ["flood_predictor.py", "N-step lookahead  N=2", "→ predicted_flood grid"]),
    (ly[2], ["victims.py", "spawn in newly flooded buildings"]),
    (ly[3], ["risk_scorer.py", "flood depth + health decay + isolation", "→ composite score"]),
    (ly[4], ["dispatch_engine.py", "Hungarian Algorithm  O(n³)", "cost = dist + (1-risk)*1000", "→ unit-victim assignments"]),
]
for cy, ln in sim_l:
    h = NH2 * 1.12 if len(ln) > 3 else NH2
    node(LX, cy, NW2, h, ln, C_SIM_BG, C_SIM_BDR, C_SIM_TXT)

for i in range(len(sim_l)-1):
    y0 = sim_l[i][0]   - NH2/2
    y1 = sim_l[i+1][0] + NH2/2
    arr(LX, y0, LX, y1, C_SIM_BDR, 1.2)

# ── right column ───────────────────────────────────────────────────────────
RX = 0.742
ry = [0.771, 0.771-GAP, 0.771-2*GAP, 0.771-3*GAP, 0.771-4*GAP]
sim_r = [
    (ry[0], ["pathfinding.py", "A* Search  ·  flood-aware weights", "edge = inf  if  depth > 0.2 m", "→ safe road routes"]),
    (ry[1], ["movement", "advance units along A* paths"]),
    (ry[2], ["rescue / death check", "unit @ victim  ->  rescue", "health <= 0  ->  death"]),
    (ry[3], ["reward_function.py", "+rescued*(1+risk)  +preemptive", "-victims*risk   -deaths*2", "-idle penalties"]),
    (ry[4], ["state tensor  H x W x 6", "ch0 flood depth    ch1 predicted flood", "ch2 composite risk  ch3 victim locs", "ch4 unit locs       ch5 pop vuln."]),
]
for cy, ln in sim_r:
    h = NH2 * 1.12 if len(ln) > 3 else NH2
    node(RX, cy, NW2, h, ln, C_SIM_BG, C_SIM_BDR, C_SIM_TXT)

for i in range(len(sim_r)-1):
    y0 = sim_r[i][0]   - NH2/2
    y1 = sim_r[i+1][0] + NH2/2
    arr(RX, y0, RX, y1, C_SIM_BDR, 1.2)

# ── cross-column: dispatch → pathfinding ────────────────────────────────────
# from right edge of dispatch (bottom-left node) to top of pathfinding (top-right)
disp_x  = LX + NW2/2
disp_y  = sim_l[-1][0]       # y of dispatch centre
path_x  = RX - NW2/2
path_y  = sim_r[0][0]        # y of pathfinding centre
arr(disp_x, disp_y, path_x, path_y,
    C_SIM_BDR, 1.4, lbl="dispatch\norders", bend=-0.22, lbl_col=C_SIM_TXT)

# ── feedback: state tensor → flood propagation (L-shaped polyline) ──────────
# go: right edge of state → right → up → left → top of flood
state_y = sim_r[-1][0]
flood_y = sim_l[0][0]
rx_edge = RX + NW2/2 + 0.010       # just past right edge of state
lx_edge = LX - NW2/2 - 0.010       # just past left edge of flood
mid_y   = (state_y + flood_y) / 2  # mid-height to route above

# path: state_right → far-right column → up to flood level → back to flood_left
polyline([(RX + NW2/2, state_y),
          (rx_edge + 0.025, state_y),
          (rx_edge + 0.025, flood_y),
          (LX - NW2/2, flood_y)],
         C_SIM_BDR, lw=1.5)
ax.text(rx_edge + 0.038, (state_y + flood_y)/2, "next\nstep",
        transform=ax.transAxes,
        color=C_SIM_BDR, fontsize=6.5, fontfamily=MONO,
        ha="center", va="center", rotation=90, zorder=9,
        bbox=dict(boxstyle="round,pad=0.15", fc=BG, ec="none"))

# ═══════════════════════════════════════════════════════════════════════════
# arrows out of sim loop
# ═══════════════════════════════════════════════════════════════════════════
arr(0.28, 0.360, 0.20, 0.335, C_ARROW_HL, 1.5,
    lbl="simulation history", lbl_col=C_ARROW_HL)
arr(0.72, 0.360, 0.80, 0.335, C_EXP_BDR, 1.2,
    lbl="controlled runs", dashed=True, lbl_col=C_EXP_TXT, bend=0.0)

# ═══════════════════════════════════════════════════════════════════════════
# [3] DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════
panel(0.02, 0.040, 0.455, 0.272,
      C_PNL_BG, C_DSH_BDR,
      "[3]  DASHBOARD  ·  Streamlit + Plotly + Folium", C_DSH_TXT)

DW, DH = 0.360, 0.060
dash = [(0.248, 0.262, ["Operations View", "live map animation  ·  KPIs", "event log"]),
        (0.248, 0.192, ["Technical View", "baseline comparisons", "ablation study charts"]),
        (0.248, 0.120, ["Comparison View", "algorithm metrics  ·  response time"])]
for cx, cy, ln in dash:
    node(cx, cy, DW, DH, ln, C_DSH_BG, C_DSH_BDR, C_DSH_TXT)

# ═══════════════════════════════════════════════════════════════════════════
# [4] EXPERIMENTS
# ═══════════════════════════════════════════════════════════════════════════
panel(0.525, 0.040, 0.455, 0.272,
      C_PNL_BG, C_EXP_BDR,
      "[4]  EXPERIMENTS  ·  offline evaluation", C_EXP_TXT)

EW, EH = 0.360, 0.060
exps = [(0.752, 0.262, ["baselines.py", "Greedy Myopic  ·  Nearest-Unit", "Priority Queue  ·  Random"]),
        (0.752, 0.190, ["ablation.py", "lookahead horizon  N = 1 ... 7"]),
        (0.752, 0.118, ["rl_agent.py", "QMIX policy training", "Stable-Baselines3"])]
for cx, cy, ln in exps:
    node(cx, cy, EW, EH, ln, C_EXP_BG, C_EXP_BDR, C_EXP_TXT)

# results → dashboard
arr(0.525, 0.176, 0.475, 0.176, C_LBL, 1.2,
    lbl="results CSV", dashed=True)

# ═══════════════════════════════════════════════════════════════════════════
# LEGEND
# ═══════════════════════════════════════════════════════════════════════════
legend = [(C_DAT_BG, C_DAT_BDR, C_DAT_TXT, "[1] Data / Loaders"),
          (C_SIM_BG, C_SIM_BDR, C_SIM_TXT, "[2] Simulation Engine"),
          (C_DSH_BG, C_DSH_BDR, C_DSH_TXT, "[3] Dashboard Views"),
          (C_EXP_BG, C_EXP_BDR, C_EXP_TXT, "[4] Experiments")]
lx0 = 0.028
for i, (bg, bdr, tc, lbl) in enumerate(legend):
    ox = lx0 + i * 0.185
    b = FancyBboxPatch((ox, 0.016), 0.024, 0.014,
                       boxstyle="round,pad=0.002", lw=1.1,
                       edgecolor=bdr, facecolor=bg,
                       transform=ax.transAxes, zorder=9)
    ax.add_patch(b)
    ax.text(ox + 0.028, 0.023, lbl,
            transform=ax.transAxes,
            color=tc, fontsize=6.5, fontfamily=MONO,
            ha="left", va="center", zorder=10)

ax.text(0.976, 0.010,
        "DisasterAI  ·  Mumbai Urban Flood Response  ·  2026",
        transform=ax.transAxes,
        color="#334155", fontsize=5.8, fontfamily=MONO,
        ha="right", va="bottom", zorder=10)

plt.tight_layout(pad=0)
out = "workflow_diagram.png"
plt.savefig(out, dpi=DPI, bbox_inches="tight",
            facecolor=BG, edgecolor="none")
print(f"Saved: {out}")
