import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

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

def plot_lookahead_ablation():
    fig, ax = plt.subplots()

    # Data from Table II
    n_steps = [1, 2, 3, 5, 7]
    scores = [699.1, 877.9, 789.7, 795.5, 800.7]
    errors = [357.4, 396.3, 419.2, 365.0, 364.9]

    ax.errorbar(n_steps, scores, yerr=errors, fmt='-o', color='#1a9641', 
                ecolor='gray', elinewidth=1, capsize=3, markersize=5, 
                linewidth=1.5, label='Mean Score $\pm$ Std Dev')

    # Highlight the optimal point
    ax.scatter([2], [877.9], color='red', s=80, zorder=5, label='Optimal N=2')

    ax.set_xlabel('Lookahead Horizon ($N$ steps)')
    ax.set_ylabel('Simulation Score')
    ax.set_xticks(n_steps)
    ax.legend(loc='lower right')
    
    plt.title('Predictive Lookahead Efficacy')
    plt.savefig('results/ieee_figures/fig3_lookahead_ablation.pdf')
    plt.savefig('results/ieee_figures/fig3_lookahead_ablation.png', dpi=300)
    plt.close()
    print("✅ Saved fig3_lookahead_ablation.png + .pdf")

plot_lookahead_ablation()
