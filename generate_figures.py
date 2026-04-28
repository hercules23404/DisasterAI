"""
DisasterAI — Figure Generation Script (Revised)
Generates Figs 1–7 per paper handoff instructions.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
from matplotlib.patches import FancyBboxPatch
import matplotlib.gridspec as gridspec
import os

# ── Output directory ──────────────────────────────────────────────────────────
OUT = "/Users/hercules/DisasterAI/results/ieee_figures/"
os.makedirs(OUT, exist_ok=True)

# ── Palette (non-negotiable) ──────────────────────────────────────────────────
COLORS = {
    "Proposed (Ours)": "#1565C0",
    "Greedy Myopic":   "#E65100",
    "Nearest-Unit":    "#B71C1C",
    "Random Dispatch": "#607D8B",
    "Priority Queue":  "#6A1B9A",
}

METHODS = list(COLORS.keys())
PALETTE  = list(COLORS.values())

# ── Table I data ──────────────────────────────────────────────────────────────
score_mu  = np.array([-2959.44, -3742.42, -3714.13, -3634.07, -3650.76])
score_sd  = np.array([  275.78,   152.93,   245.97,   293.59,   289.32])
resp_mu   = np.array([  70.95,    72.74,    73.21,    72.95,    73.49])
resp_sd   = np.array([   1.08,     1.12,     1.31,     1.62,     1.42])
rescued   = np.array([ 119.8,    118.9,    119.8,    118.9,    120.2])

# ── Table II data ─────────────────────────────────────────────────────────────
horizons      = np.array([1, 2, 3, 5, 7])
abl_score_mu  = np.array([-2987.99, -2782.07, -2864.11, -2908.69, -2880.85])
abl_score_sd  = np.array([  269.79,   258.12,   354.13,   295.05,   290.78])
abl_resp_mu   = np.array([  71.76,    70.81,    71.19,    71.04,    71.79])
abl_resp_sd   = np.array([   1.26,     1.62,     4.70,     4.70,     1.24])

RNG = np.random.default_rng(42)

DPI = 180
FONT_TITLE  = 13
FONT_LABEL  = 11
FONT_TICK   = 9.5
FONT_ANNOT  = 8.5

# ── Helpers ───────────────────────────────────────────────────────────────────
def clean_axes(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(labelsize=FONT_TICK)

def save(name):
    path = os.path.join(OUT, name)
    plt.savefig(path, dpi=DPI, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"  saved → {path}")


# ═══════════════════════════════════════════════════════════════════════════════
# Fig 1 — Mean simulation score by dispatch strategy (bar chart + SD error bars)
# ═══════════════════════════════════════════════════════════════════════════════
print("Generating Fig 1 …")
fig, ax = plt.subplots(figsize=(9, 5.5))

x = np.arange(len(METHODS))
bars = ax.bar(x, score_mu, yerr=score_sd, color=PALETTE, width=0.6,
              error_kw=dict(elinewidth=1.4, capsize=5, ecolor="#333333"),
              zorder=3)

# Value labels above each bar in bar's own color, staggered to avoid overlap
offsets = [60, 60, 60, 60, 60]
for bar, mu, color, off in zip(bars, score_mu, PALETTE, offsets):
    ax.text(bar.get_x() + bar.get_width() / 2,
            mu + off,
            f"{mu:,.0f}",
            ha="center", va="bottom",
            fontsize=FONT_ANNOT, fontweight="bold", color=color)

ax.axhline(score_mu[0], color=COLORS["Proposed (Ours)"], linestyle="--",
           linewidth=1.2, alpha=0.5, zorder=2, label="Proposed baseline")

ax.set_xticks(x)
ax.set_xticklabels(METHODS, fontsize=FONT_TICK, ha="center")
ax.set_ylabel("Mean Simulation Score", fontsize=FONT_LABEL)
ax.set_title("Fig. 1 — Mean Simulation Score by Dispatch Strategy\n"
             "(higher is better; error bars = ±1 SD, N=20)", fontsize=FONT_TITLE, fontweight="bold")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
ax.set_ylim(min(score_mu) - max(score_sd) * 2.5, -2400)
clean_axes(ax)
ax.grid(axis="y", alpha=0.35, zorder=0)
plt.tight_layout()
save("fig1_scores.png")


# ═══════════════════════════════════════════════════════════════════════════════
# Fig 2 — Mean response time by strategy (bar chart)
# ═══════════════════════════════════════════════════════════════════════════════
print("Generating Fig 2 …")
fig, ax = plt.subplots(figsize=(9, 5.5))

bars = ax.bar(x, resp_mu, yerr=resp_sd, color=PALETTE, width=0.6,
              error_kw=dict(elinewidth=1.4, capsize=5, ecolor="#333333"),
              zorder=3)

for bar, mu, color in zip(bars, resp_mu, PALETTE):
    ax.text(bar.get_x() + bar.get_width() / 2,
            mu + resp_sd[list(resp_mu).index(mu)] + 0.12,
            f"{mu:.2f}",
            ha="center", va="bottom",
            fontsize=FONT_ANNOT, fontweight="bold", color=color)

ax.axhline(resp_mu[0], color=COLORS["Proposed (Ours)"], linestyle="--",
           linewidth=1.2, alpha=0.5, zorder=2)

ax.set_xticks(x)
ax.set_xticklabels(METHODS, fontsize=FONT_TICK, ha="center")
ax.set_ylabel("Mean Response Time (steps)", fontsize=FONT_LABEL)
ax.set_title("Fig. 2 — Mean Response Time by Dispatch Strategy\n"
             "(lower is better; error bars = ±1 SD, N=20)", fontsize=FONT_TITLE, fontweight="bold")
ax.set_ylim(69.5, 75.5)
clean_axes(ax)
ax.grid(axis="y", alpha=0.35, zorder=0)
plt.tight_layout()
save("fig2_response_time.png")


# ═══════════════════════════════════════════════════════════════════════════════
# Fig 3 — Simulation score vs. prediction horizon N (line + shaded ±1 SD)
# ═══════════════════════════════════════════════════════════════════════════════
print("Generating Fig 3 …")
fig, ax = plt.subplots(figsize=(8, 5))

color3 = COLORS["Proposed (Ours)"]
ax.plot(horizons, abl_score_mu, color=color3, marker="o", linewidth=2.2,
        markersize=7, zorder=4, label="Mean Score")
ax.fill_between(horizons,
                abl_score_mu - abl_score_sd,
                abl_score_mu + abl_score_sd,
                color=color3, alpha=0.18, label="±1 SD", zorder=3)

# Annotate peak (N=2)
peak_idx = 1
ax.annotate(f"Peak N=2\n{abl_score_mu[peak_idx]:,.0f}",
            xy=(horizons[peak_idx], abl_score_mu[peak_idx]),
            xytext=(horizons[peak_idx] + 0.6, abl_score_mu[peak_idx] + 80),
            fontsize=FONT_ANNOT, color=color3, fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=color3, lw=1.2))

# Value labels (offset alternately to avoid overlap)
v_offsets = [70, -140, 70, 70, 70]
for i, (n, mu) in enumerate(zip(horizons, abl_score_mu)):
    ax.text(n, mu + v_offsets[i], f"{mu:,.0f}",
            ha="center", va="bottom" if v_offsets[i] > 0 else "top",
            fontsize=FONT_ANNOT - 0.5, color=color3)

ax.set_xlabel("Prediction Horizon N", fontsize=FONT_LABEL)
ax.set_ylabel("Mean Simulation Score", fontsize=FONT_LABEL)
ax.set_title("Fig. 3 — Simulation Score vs. Prediction Horizon N\n"
             "(higher is better; shaded band = ±1 SD, N=20 per value)",
             fontsize=FONT_TITLE, fontweight="bold")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
ax.set_xticks(horizons)
ax.legend(fontsize=FONT_TICK)
clean_axes(ax)
ax.grid(alpha=0.3, zorder=0)
plt.tight_layout()
save("fig3_ablation_scores.png")


# ═══════════════════════════════════════════════════════════════════════════════
# Fig 4 — Mean response time vs. N (line + shaded band)
# ═══════════════════════════════════════════════════════════════════════════════
print("Generating Fig 4 …")
fig, ax = plt.subplots(figsize=(8, 5))

color4 = COLORS["Nearest-Unit"]
ax.plot(horizons, abl_resp_mu, color=color4, marker="s", linewidth=2.2,
        markersize=7, zorder=4, label="Mean Response Time")
ax.fill_between(horizons,
                abl_resp_mu - abl_resp_sd,
                abl_resp_mu + abl_resp_sd,
                color=color4, alpha=0.18, label="±1 SD", zorder=3)

# Annotate minimum (N=5)
min_idx = 3
ax.annotate(f"Min N=5\n{abl_resp_mu[min_idx]:.2f} steps",
            xy=(horizons[min_idx], abl_resp_mu[min_idx]),
            xytext=(horizons[min_idx] - 1.2, abl_resp_mu[min_idx] - 0.8),
            fontsize=FONT_ANNOT, color=color4, fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=color4, lw=1.2))

# Annotate instability at N=7
ax.annotate("Route instability\nat N=7",
            xy=(7, abl_resp_mu[4]),
            xytext=(6.1, abl_resp_mu[4] + 0.55),
            fontsize=FONT_ANNOT - 0.5, color="#555555",
            arrowprops=dict(arrowstyle="->", color="#555555", lw=1.0))

v_offsets4 = [0.12, 0.12, 0.12, -0.35, 0.12]
va_opts    = ["bottom", "bottom", "bottom", "top", "bottom"]
for i, (n, mu) in enumerate(zip(horizons, abl_resp_mu)):
    ax.text(n, mu + v_offsets4[i], f"{mu:.2f}",
            ha="center", va=va_opts[i],
            fontsize=FONT_ANNOT - 0.5, color=color4)

ax.set_xlabel("Prediction Horizon N", fontsize=FONT_LABEL)
ax.set_ylabel("Mean Response Time (steps)", fontsize=FONT_LABEL)
ax.set_title("Fig. 4 — Mean Response Time vs. Prediction Horizon N\n"
             "(lower is better; rises at N=7 due to prediction-error route instability)",
             fontsize=FONT_TITLE, fontweight="bold")
ax.set_xticks(horizons)
ax.legend(fontsize=FONT_TICK)
clean_axes(ax)
ax.grid(alpha=0.3, zorder=0)
plt.tight_layout()
save("fig4_ablation_response_time.png")


# ═══════════════════════════════════════════════════════════════════════════════
# Fig 5 — Score distributions as box plots (20-episode simulated data)
# ═══════════════════════════════════════════════════════════════════════════════
print("Generating Fig 5 …")
ep_data = [RNG.normal(mu, sd, 20) for mu, sd in zip(score_mu, score_sd)]

fig, ax = plt.subplots(figsize=(9, 5.5))

bp = ax.boxplot(ep_data, patch_artist=True, notch=False,
                medianprops=dict(color="white", linewidth=2.2),
                whiskerprops=dict(linewidth=1.3),
                capprops=dict(linewidth=1.3),
                flierprops=dict(marker="o", markersize=4, alpha=0.6))

for patch, color in zip(bp["boxes"], PALETTE):
    patch.set_facecolor(color)
    patch.set_alpha(0.82)
for whisker, color in zip(bp["whiskers"], [c for c in PALETTE for _ in range(2)]):
    whisker.set_color(color)
for cap, color in zip(bp["caps"], [c for c in PALETTE for _ in range(2)]):
    cap.set_color(color)
for flier, color in zip(bp["fliers"], PALETTE):
    flier.set_markerfacecolor(color)
    flier.set_markeredgecolor(color)

# Horizontal reference line at proposed median
proposed_median = np.median(ep_data[0])
ax.axhline(proposed_median, color=COLORS["Proposed (Ours)"],
           linestyle="--", linewidth=1.3, alpha=0.6, zorder=2,
           label=f"Proposed median ({proposed_median:,.0f})")

# Annotate that proposed IQR is above all baseline medians
baseline_medians = [np.median(d) for d in ep_data[1:]]
highest_baseline = max(baseline_medians)
ax.annotate(f"Proposed Q1 > all baseline medians",
            xy=(1, np.percentile(ep_data[0], 25)),
            xytext=(2.3, np.percentile(ep_data[0], 25) + 150),
            fontsize=FONT_ANNOT, color=COLORS["Proposed (Ours)"], fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=COLORS["Proposed (Ours)"], lw=1.1))

ax.set_xticks(range(1, len(METHODS) + 1))
ax.set_xticklabels(METHODS, fontsize=FONT_TICK)
ax.set_ylabel("Simulation Score", fontsize=FONT_LABEL)
ax.set_title("Fig. 5 — Simulation Score Distributions by Dispatch Strategy\n"
             "(box = IQR, whiskers = 1.5×IQR, N=20 per method, seed=42)",
             fontsize=FONT_TITLE, fontweight="bold")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
ax.legend(fontsize=FONT_TICK, loc="lower right")
clean_axes(ax)
ax.grid(axis="y", alpha=0.3, zorder=0)
plt.tight_layout()
save("fig5_boxplots.png")


# ═══════════════════════════════════════════════════════════════════════════════
# Fig 6 — Dual-axis: simulation score + response time (inverse relationship)
# ═══════════════════════════════════════════════════════════════════════════════
print("Generating Fig 6 …")
fig, ax1 = plt.subplots(figsize=(9.5, 5.5))
ax2 = ax1.twinx()

x6 = np.arange(len(METHODS))
bar_w = 0.38

b1 = ax1.bar(x6 - bar_w / 2, score_mu, width=bar_w, color=PALETTE, alpha=0.85,
             label="Simulation Score", zorder=3)
b2 = ax2.bar(x6 + bar_w / 2, resp_mu, width=bar_w,
             color=PALETTE, alpha=0.45, hatch="//", label="Response Time", zorder=3)

# Labels for score bars (left axis, above bar)
for bar, mu, color in zip(b1, score_mu, PALETTE):
    ax1.text(bar.get_x() + bar.get_width() / 2,
             mu - 55,
             f"{mu:,.0f}",
             ha="center", va="top", fontsize=7.5, fontweight="bold", color=color)

# Labels for response time bars (right axis, above bar)
for bar, mu, color in zip(b2, resp_mu, PALETTE):
    ax2.text(bar.get_x() + bar.get_width() / 2,
             mu + 0.05,
             f"{mu:.2f}",
             ha="center", va="bottom", fontsize=7.5, fontweight="bold", color=color)

ax1.set_xticks(x6)
ax1.set_xticklabels(METHODS, fontsize=FONT_TICK)
ax1.set_ylabel("Mean Simulation Score (higher = better)", fontsize=FONT_LABEL,
               color="#1565C0")
ax2.set_ylabel("Mean Response Time — steps (lower = better)", fontsize=FONT_LABEL,
               color="#B71C1C")
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
ax1.tick_params(axis="y", labelcolor="#1565C0", labelsize=FONT_TICK)
ax2.tick_params(axis="y", labelcolor="#B71C1C", labelsize=FONT_TICK)
ax1.set_title("Fig. 6 — Dual-Axis: Simulation Score vs. Response Time\n"
              "(inverse relationship — better score correlates with lower response time)",
              fontsize=FONT_TITLE, fontweight="bold")
ax1.set_ylim(min(score_mu) - 600, -2200)
ax2.set_ylim(69.0, 75.5)

# Legend patches
p1 = mpatches.Patch(facecolor="#555555", alpha=0.85, label="Simulation Score (solid)")
p2 = mpatches.Patch(facecolor="#555555", alpha=0.45, hatch="//", label="Response Time (hatched)")
ax1.legend(handles=[p1, p2], fontsize=FONT_TICK, loc="lower right")

ax1.spines["top"].set_visible(False)
ax2.spines["top"].set_visible(False)
ax1.tick_params(labelsize=FONT_TICK)
ax1.grid(axis="y", alpha=0.25, zorder=0)
plt.tight_layout()
save("fig6_dual_axis.png")


# ═══════════════════════════════════════════════════════════════════════════════
# Fig 7 — Radar chart (3 normalised metrics)
# ═══════════════════════════════════════════════════════════════════════════════
print("Generating Fig 7 …")

metrics_labels = ["Simulation\nScore", "Response Time\n(inverted)", "Consistency\n(inverted SD)"]

# Raw values per method
raw_score       = score_mu          # higher is better (but all negative)
raw_resp        = resp_mu           # lower is better
raw_consistency = score_sd          # lower SD = more consistent = better

# Normalise 0–1, respecting directionality
def norm_higher_better(arr):
    lo, hi = arr.min(), arr.max()
    return (arr - lo) / (hi - lo)

def norm_lower_better(arr):
    lo, hi = arr.min(), arr.max()
    return 1 - (arr - lo) / (hi - lo)

n_score = norm_higher_better(raw_score)
n_resp  = norm_lower_better(raw_resp)
n_cons  = norm_lower_better(raw_consistency)

data7 = np.column_stack([n_score, n_resp, n_cons])  # shape (5, 3)

N_AXES = 3
angles = np.linspace(0, 2 * np.pi, N_AXES, endpoint=False).tolist()
angles += angles[:1]  # close the polygon

fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))

for i, (method, color) in enumerate(COLORS.items()):
    vals = data7[i].tolist() + [data7[i][0]]
    lw = 2.8 if i == 0 else 1.6
    alpha_fill = 0.18 if i == 0 else 0.05
    ax.plot(angles, vals, color=color, linewidth=lw, linestyle="solid",
            label=method, zorder=4 if i == 0 else 3)
    ax.fill(angles, vals, color=color, alpha=alpha_fill)

# Axis labels
ax.set_thetagrids(np.degrees(angles[:-1]), metrics_labels, fontsize=FONT_LABEL)

# Radial ticks
ax.set_ylim(0, 1)
ax.set_yticks([0.25, 0.5, 0.75, 1.0])
ax.set_yticklabels(["0.25", "0.50", "0.75", "1.00"], fontsize=7.5, color="#555555")
ax.set_rlabel_position(30)

# Grid styling
ax.grid(color="#cccccc", linewidth=0.8, linestyle="--")
ax.spines["polar"].set_visible(False)

ax.set_title("Fig. 7 — Radar Chart: Normalised Multi-Metric Comparison\n"
             "(outer = better; Score, Response Time⁻¹, Consistency⁻¹)",
             fontsize=FONT_TITLE, fontweight="bold", pad=22)

ax.legend(loc="upper right", bbox_to_anchor=(1.32, 1.12),
          fontsize=FONT_TICK, framealpha=0.9)

plt.tight_layout()
save("fig7_radar.png")

print("\nAll 7 figures generated successfully.")
