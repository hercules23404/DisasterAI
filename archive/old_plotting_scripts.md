# Archived Plotting Scripts

> These scripts were the original figure generators used before the consolidated `generate_figures.py` was written.
> They used old/placeholder data and inconsistent styling. Kept here for reference only.
> **Use `generate_figures.py` for all figure generation.**

---

## `plot_results.py` — CSV-driven seaborn plots (original)

```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

try:
    plt.style.use('seaborn-v0_8-paper')
except:
    plt.style.use('seaborn-paper')

sns.set_theme(style="whitegrid", context="paper")

RESULTS_DIR = 'results'
os.makedirs(RESULTS_DIR, exist_ok=True)

baseline_df = pd.read_csv(os.path.join(RESULTS_DIR, 'baseline_comparison.csv'))
ablation_df = pd.read_csv(os.path.join(RESULTS_DIR, 'ablation_lookahead.csv'))

plt.figure(figsize=(6, 4))
sns.barplot(data=baseline_df, x='mode', y='simulation_score', errorbar='sd', capsize=.1, palette='viridis')
plt.title('Baseline Comparison: Simulation Score', fontsize=12)
plt.ylabel('Simulation Score', fontsize=10)
plt.xlabel('Dispatch Mode', fontsize=10)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(RESULTS_DIR, 'fig1_baseline_scores.png'), dpi=300)
plt.close()

plt.figure(figsize=(6, 4))
sns.barplot(data=baseline_df, x='mode', y='mean_response_time', errorbar='sd', capsize=.1, palette='mako')
plt.title('Baseline Comparison: Mean Response Time', fontsize=12)
plt.ylabel('Mean Response Time (Timesteps)', fontsize=10)
plt.xlabel('Dispatch Mode', fontsize=10)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(RESULTS_DIR, 'fig2_baseline_response_time.png'), dpi=300)
plt.close()

plt.figure(figsize=(6, 4))
sns.lineplot(data=ablation_df, x='N_value', y='simulation_score', marker='o', errorbar='sd', color='b')
plt.title('Ablation Study: Simulation Score vs Lookahead Steps (N)', fontsize=12)
plt.ylabel('Simulation Score', fontsize=10)
plt.xlabel('Lookahead Steps (N)', fontsize=10)
plt.xticks([1, 2, 3, 5, 7])
plt.tight_layout()
plt.savefig(os.path.join(RESULTS_DIR, 'fig3_ablation_scores.png'), dpi=300)
plt.close()

plt.figure(figsize=(6, 4))
sns.lineplot(data=ablation_df, x='N_value', y='mean_response_time', marker='s', errorbar='sd', color='r')
plt.title('Ablation Study: Mean Response Time vs Lookahead Steps (N)', fontsize=12)
plt.ylabel('Mean Response Time (Timesteps)', fontsize=10)
plt.xlabel('Lookahead Steps (N)', fontsize=10)
plt.xticks([1, 2, 3, 5, 7])
plt.tight_layout()
plt.savefig(os.path.join(RESULTS_DIR, 'fig4_ablation_response_time.png'), dpi=300)
plt.close()

print("Successfully generated IEEE-style plots in results/ directory.")
```

---

## `plot_ieee.py` — Full IEEE-style matplotlib pipeline (v2)

```python
"""
plot_ieee.py — Generates IEEE-standard figures for the DisasterAI research paper.
All figures use Times New Roman, single-column width (3.5in), 300 DPI.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import os

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

baseline_df = pd.read_csv(os.path.join(RESULTS_DIR, "baseline_comparison.csv"))
ablation_df = pd.read_csv(os.path.join(RESULTS_DIR, "ablation_lookahead.csv"))

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

mode_order = ["Hungarian", "Greedy Myopic", "Nearest-Unit", "Random", "Priority Queue"]
COLORS = {
    "Hungarian": "#1a5276", "Greedy Myopic": "#2e86c1", "Nearest-Unit": "#5dade2",
    "Random": "#aed6f1", "Priority Queue": "#d5d8dc",
}
palette = [COLORS[m] for m in mode_order]

# Fig 1–7 generation code (see plot_ieee.py in git history)
# Superseded by generate_figures.py which uses the correct paper data (Table I & II).
```

---

## `plot_fig2.py` — Quick dual-axis baseline comparison

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def set_ieee_style():
    plt.rcParams.update({
        "font.family": "serif", "font.serif": ["Times New Roman"],
        "font.size": 10, "axes.labelsize": 10, "axes.titlesize": 10,
        "xtick.labelsize": 8, "ytick.labelsize": 8, "legend.fontsize": 8,
        "figure.figsize": (3.5, 2.5), "figure.dpi": 300,
        "savefig.bbox": "tight", "savefig.pad_inches": 0.05
    })
    sns.set_style("whitegrid", {"grid.linestyle": "--", "axes.edgecolor": "black"})

set_ieee_style()

def plot_baseline_comparison():
    fig, ax1 = plt.subplots()
    strategies = ['Hungarian', 'Greedy', 'Nearest', 'Priority Q.', 'Random']
    sim_scores = [763.0, 202.9, 159.1, -28.2, 2.8]    # OLD placeholder data
    resp_times = [19.2, 30.2, 30.0, 31.5, 30.4]
    x = np.arange(len(strategies))
    width = 0.4
    ax1.bar(x, sim_scores, width, color='#2c7bb6', label='Sim Score', zorder=3)
    ax1.set_ylabel('Mean Simulation Score')
    ax1.set_xticks(x)
    ax1.set_xticklabels(strategies, rotation=25, ha='right')
    ax1.axhline(0, color='black', linewidth=0.8)
    ax2 = ax1.twinx()
    ax2.plot(x, resp_times, color='#d7191c', marker='o', linewidth=2, markersize=6, label='Response Time')
    ax2.set_ylabel('Mean Response Time')
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc='upper right')
    plt.title('Dispatch Strategy Performance')
    plt.savefig('results/ieee_figures/fig2_baseline_comparison.pdf')
    plt.savefig('results/ieee_figures/fig2_baseline_comparison.png', dpi=300)
    plt.close()

plot_baseline_comparison()
```

---

## `plot_fig3.py` — Quick lookahead ablation line chart

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def set_ieee_style():
    plt.rcParams.update({
        "font.family": "serif", "font.serif": ["Times New Roman"],
        "font.size": 10, "axes.labelsize": 10, "axes.titlesize": 10,
        "xtick.labelsize": 8, "ytick.labelsize": 8, "legend.fontsize": 8,
        "figure.figsize": (3.5, 2.5), "figure.dpi": 300,
        "savefig.bbox": "tight", "savefig.pad_inches": 0.05
    })
    sns.set_style("whitegrid", {"grid.linestyle": "--", "axes.edgecolor": "black"})

set_ieee_style()

def plot_lookahead_ablation():
    fig, ax = plt.subplots()
    n_steps = [1, 2, 3, 5, 7]
    scores = [699.1, 877.9, 789.7, 795.5, 800.7]    # OLD placeholder data
    errors = [357.4, 396.3, 419.2, 365.0, 364.9]
    ax.errorbar(n_steps, scores, yerr=errors, fmt='-o', color='#1a9641',
                ecolor='gray', elinewidth=1, capsize=3, markersize=5,
                linewidth=1.5, label='Mean Score ± Std Dev')
    ax.scatter([2], [877.9], color='red', s=80, zorder=5, label='Optimal N=2')
    ax.set_xlabel('Lookahead Horizon (N steps)')
    ax.set_ylabel('Simulation Score')
    ax.set_xticks(n_steps)
    ax.legend(loc='lower right')
    plt.title('Predictive Lookahead Efficacy')
    plt.savefig('results/ieee_figures/fig3_lookahead_ablation.pdf')
    plt.savefig('results/ieee_figures/fig3_lookahead_ablation.png', dpi=300)
    plt.close()

plot_lookahead_ablation()
```

---

> **Note:** All four scripts above used old/placeholder data inconsistent with the final paper tables.
> The authoritative figures are in `results/ieee_figures/` and generated by `generate_figures.py`.
