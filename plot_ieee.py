"""
plot_ieee.py
────────────
Generates IEEE-standard figures for the DisasterAI research paper.
All figures use Times New Roman, single-column width (3.5in), 300 DPI.
"""

import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
import numpy as np
import pandas as pd
import os

# ── IEEE Standard Formatting ─────────────────────────────────────────
def set_ieee_style():
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Times New Roman"],
        "font.size": 10,
        "axes.labelsize": 10,
        "axes.titlesize": 10,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "legend.fontsize": 8,
        "figure.figsize": (3.5, 2.5),
        "figure.dpi": 300,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.05
    })
    sns.set_style("whitegrid", {"grid.linestyle": "--", "axes.edgecolor": "black"})

set_ieee_style()

RESULTS_DIR = "results"
OUT_DIR = os.path.join(RESULTS_DIR, "ieee_figures")
os.makedirs(OUT_DIR, exist_ok=True)

# ── Load Data ─────────────────────────────────────────────────────────
baseline_df = pd.read_csv(os.path.join(RESULTS_DIR, "baseline_comparison.csv"))
ablation_df = pd.read_csv(os.path.join(RESULTS_DIR, "ablation_lookahead.csv"))

# Compute summary stats
baseline_summary = baseline_df.groupby("mode", sort=False).agg(
    score_mean=("simulation_score", "mean"),
    score_std=("simulation_score", "std"),
    rt_mean=("mean_response_time", "mean"),
    rt_std=("mean_response_time", "std"),
    rescued_mean=("total_rescued", "mean"),
).reset_index()

ablation_summary = ablation_df.groupby("N_value", sort=False).agg(
    score_mean=("simulation_score", "mean"),
    score_std=("simulation_score", "std"),
    rt_mean=("mean_response_time", "mean"),
    rt_std=("mean_response_time", "std"),
).reset_index().sort_values("N_value")

# Reorder baselines for visual hierarchy (best → worst)
mode_order = ["Hungarian", "Greedy Myopic", "Nearest-Unit", "Random", "Priority Queue"]
baseline_summary["mode"] = pd.Categorical(baseline_summary["mode"], categories=mode_order, ordered=True)
baseline_summary = baseline_summary.sort_values("mode")

# ── Color palette ─────────────────────────────────────────────────────
COLORS = {
    "Hungarian": "#1a5276",
    "Greedy Myopic": "#2e86c1",
    "Nearest-Unit": "#5dade2",
    "Random": "#aed6f1",
    "Priority Queue": "#d5d8dc",
}
palette = [COLORS[m] for m in mode_order]
ablation_color = "#1a5276"


# ═══════════════════════════════════════════════════════════════════════
#  Fig 1: Baseline Simulation Score (Bar Chart with Error Bars)
# ═══════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots()
bars = ax.bar(
    range(len(baseline_summary)),
    baseline_summary["score_mean"],
    yerr=baseline_summary["score_std"],
    capsize=3,
    color=palette,
    edgecolor="black",
    linewidth=0.5,
    error_kw={"linewidth": 0.8},
)
ax.set_xticks(range(len(baseline_summary)))
ax.set_xticklabels(baseline_summary["mode"], rotation=30, ha="right")
ax.set_ylabel("Simulation Score")
ax.set_xlabel("Dispatch Strategy")
ax.axhline(y=0, color="black", linewidth=0.5, linestyle="-")

# Annotate the best bar
best_idx = baseline_summary["score_mean"].idxmax()
best_val = baseline_summary.loc[best_idx, "score_mean"]
ax.annotate(
    f"{best_val:.0f}",
    xy=(0, best_val),
    xytext=(0, best_val + 60),
    ha="center", fontsize=7, fontweight="bold",
)

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "fig1_baseline_scores.png"), dpi=300)
plt.savefig(os.path.join(OUT_DIR, "fig1_baseline_scores.pdf"))
plt.close()
print("✅ Fig 1: Baseline Simulation Scores")


# ═══════════════════════════════════════════════════════════════════════
#  Fig 2: Baseline Mean Response Time (Bar Chart with Error Bars)
# ═══════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots()
bars = ax.bar(
    range(len(baseline_summary)),
    baseline_summary["rt_mean"],
    yerr=baseline_summary["rt_std"],
    capsize=3,
    color=palette,
    edgecolor="black",
    linewidth=0.5,
    error_kw={"linewidth": 0.8},
)
ax.set_xticks(range(len(baseline_summary)))
ax.set_xticklabels(baseline_summary["mode"], rotation=30, ha="right")
ax.set_ylabel("Mean Response Time (steps)")
ax.set_xlabel("Dispatch Strategy")

# Annotate the best bar
best_idx = baseline_summary["rt_mean"].idxmin()
best_val = baseline_summary.loc[best_idx, "rt_mean"]
ax.annotate(
    f"{best_val:.1f}",
    xy=(0, best_val),
    xytext=(0, best_val - 3),
    ha="center", fontsize=7, fontweight="bold",
)

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "fig2_baseline_response_time.png"), dpi=300)
plt.savefig(os.path.join(OUT_DIR, "fig2_baseline_response_time.pdf"))
plt.close()
print("✅ Fig 2: Baseline Response Time")


# ═══════════════════════════════════════════════════════════════════════
#  Fig 3: Ablation — Simulation Score vs Lookahead N (Line + Shaded CI)
# ═══════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots()
ax.plot(
    ablation_summary["N_value"],
    ablation_summary["score_mean"],
    marker="o", markersize=5,
    color=ablation_color, linewidth=1.5,
    zorder=3,
)
ax.fill_between(
    ablation_summary["N_value"],
    ablation_summary["score_mean"] - ablation_summary["score_std"],
    ablation_summary["score_mean"] + ablation_summary["score_std"],
    alpha=0.15, color=ablation_color,
)
# Highlight best point
best_row = ablation_summary.loc[ablation_summary["score_mean"].idxmax()]
ax.scatter([best_row["N_value"]], [best_row["score_mean"]],
           color="#e74c3c", s=60, zorder=5, edgecolors="black", linewidth=0.5)
ax.annotate(
    f"N={int(best_row['N_value'])}\n{best_row['score_mean']:.0f}",
    xy=(best_row["N_value"], best_row["score_mean"]),
    xytext=(best_row["N_value"] + 1.2, best_row["score_mean"] + 50),
    fontsize=7, fontweight="bold",
    arrowprops=dict(arrowstyle="->", lw=0.6, color="black"),
)
ax.set_xlabel("Lookahead Steps (N)")
ax.set_ylabel("Simulation Score")
ax.set_xticks([1, 2, 3, 5, 7])

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "fig3_ablation_scores.png"), dpi=300)
plt.savefig(os.path.join(OUT_DIR, "fig3_ablation_scores.pdf"))
plt.close()
print("✅ Fig 3: Ablation Simulation Scores")


# ═══════════════════════════════════════════════════════════════════════
#  Fig 4: Ablation — Response Time vs Lookahead N (Line + Shaded CI)
# ═══════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots()
ax.plot(
    ablation_summary["N_value"],
    ablation_summary["rt_mean"],
    marker="s", markersize=5,
    color="#c0392b", linewidth=1.5,
    zorder=3,
)
ax.fill_between(
    ablation_summary["N_value"],
    ablation_summary["rt_mean"] - ablation_summary["rt_std"],
    ablation_summary["rt_mean"] + ablation_summary["rt_std"],
    alpha=0.15, color="#c0392b",
)
ax.set_xlabel("Lookahead Steps (N)")
ax.set_ylabel("Mean Response Time (steps)")
ax.set_xticks([1, 2, 3, 5, 7])

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "fig4_ablation_response_time.png"), dpi=300)
plt.savefig(os.path.join(OUT_DIR, "fig4_ablation_response_time.pdf"))
plt.close()
print("✅ Fig 4: Ablation Response Time")


# ═══════════════════════════════════════════════════════════════════════
#  Fig 5: Box Plot — Score Distribution by Strategy
# ═══════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(3.5, 2.8))
baseline_df["mode"] = pd.Categorical(baseline_df["mode"], categories=mode_order, ordered=True)
sns.boxplot(
    data=baseline_df, x="mode", y="simulation_score",
    palette=palette, linewidth=0.7, fliersize=2,
    ax=ax,
)
ax.set_xticklabels(mode_order, rotation=30, ha="right", fontsize=7)
ax.set_ylabel("Simulation Score")
ax.set_xlabel("")
ax.axhline(y=0, color="black", linewidth=0.4, linestyle=":")

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "fig5_score_boxplot.png"), dpi=300)
plt.savefig(os.path.join(OUT_DIR, "fig5_score_boxplot.pdf"))
plt.close()
print("✅ Fig 5: Score Distribution Box Plot")


# ═══════════════════════════════════════════════════════════════════════
#  Fig 6: Dual-Axis — Score vs Response Time (Grouped Bar)
# ═══════════════════════════════════════════════════════════════════════
fig, ax1 = plt.subplots(figsize=(3.5, 2.8))
x = np.arange(len(baseline_summary))
width = 0.35

bars1 = ax1.bar(x - width/2, baseline_summary["score_mean"],
                width, yerr=baseline_summary["score_std"],
                label="Sim. Score", color="#1a5276",
                edgecolor="black", linewidth=0.4, capsize=2,
                error_kw={"linewidth": 0.6})
ax1.set_ylabel("Simulation Score", color="#1a5276")
ax1.tick_params(axis="y", labelcolor="#1a5276")

ax2 = ax1.twinx()
bars2 = ax2.bar(x + width/2, baseline_summary["rt_mean"],
                width, yerr=baseline_summary["rt_std"],
                label="Resp. Time", color="#c0392b",
                edgecolor="black", linewidth=0.4, capsize=2,
                error_kw={"linewidth": 0.6})
ax2.set_ylabel("Response Time (steps)", color="#c0392b")
ax2.tick_params(axis="y", labelcolor="#c0392b")

ax1.set_xticks(x)
ax1.set_xticklabels(baseline_summary["mode"], rotation=30, ha="right", fontsize=7)
ax1.set_xlabel("")

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right", fontsize=6)

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "fig6_dual_axis.png"), dpi=300)
plt.savefig(os.path.join(OUT_DIR, "fig6_dual_axis.pdf"))
plt.close()
print("✅ Fig 6: Dual-Axis Score vs Response Time")


# ═══════════════════════════════════════════════════════════════════════
#  Fig 7: Radar / Spider Chart — Multi-metric Strategy Comparison
# ═══════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(3.5, 3.5), subplot_kw=dict(polar=True))

categories = ["Sim. Score", "Response\nTime (inv)", "Consistency\n(inv. std)"]
N_cats = len(categories)
angles = np.linspace(0, 2 * np.pi, N_cats, endpoint=False).tolist()
angles += angles[:1]  # close the polygon

for i, mode in enumerate(mode_order[:4]):  # top 4 strategies
    row = baseline_summary[baseline_summary["mode"] == mode].iloc[0]
    # Normalise each metric to [0, 1] for radar
    score_norm = (row["score_mean"] - (-28.2)) / (763.0 - (-28.2))
    rt_norm = 1.0 - (row["rt_mean"] - 19.2) / (31.5 - 19.2)  # inverted: lower is better
    std_norm = 1.0 - (row["score_std"] - 276.4) / (332.0 - 276.4)
    values = [score_norm, rt_norm, std_norm]
    values += values[:1]
    ax.plot(angles, values, linewidth=1.2, label=mode, color=palette[i])
    ax.fill(angles, values, alpha=0.08, color=palette[i])

ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories, fontsize=7)
ax.set_ylim(0, 1.1)
ax.set_yticklabels([])
ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), fontsize=6)

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "fig7_radar.png"), dpi=300)
plt.savefig(os.path.join(OUT_DIR, "fig7_radar.pdf"))
plt.close()
print("✅ Fig 7: Radar Chart")


print(f"\n📁 All IEEE figures saved to: {OUT_DIR}/")
print(f"   PNG (for preview) + PDF (for LaTeX \\includegraphics)")
