import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# IEEE Standard Formatting
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

def plot_baseline_comparison():
    fig, ax1 = plt.subplots()

    # Data from Table I
    strategies = ['Hungarian', 'Greedy', 'Nearest', 'Priority Q.', 'Random']
    sim_scores = [763.0, 202.9, 159.1, -28.2, 2.8]
    resp_times = [19.2, 30.2, 30.0, 31.5, 30.4]

    x = np.arange(len(strategies))
    width = 0.4

    # Primary Axis: Simulation Score (Bar)
    bars = ax1.bar(x, sim_scores, width, color='#2c7bb6', label='Sim Score', zorder=3)
    ax1.set_ylabel('Mean Simulation Score')
    ax1.set_xticks(x)
    ax1.set_xticklabels(strategies, rotation=25, ha='right')
    ax1.axhline(0, color='black', linewidth=0.8)

    # Secondary Axis: Response Time (Line)
    ax2 = ax1.twinx()
    line = ax2.plot(x, resp_times, color='#d7191c', marker='o', linewidth=2, 
                    markersize=6, label='Response Time (steps)', zorder=4)
    ax2.set_ylabel('Mean Response Time')

    # Combined Legend
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc='upper right')

    plt.title('Dispatch Strategy Performance')
    plt.savefig('results/ieee_figures/fig2_baseline_comparison.pdf')
    plt.savefig('results/ieee_figures/fig2_baseline_comparison.png', dpi=300)
    plt.close()
    print("✅ Saved fig2_baseline_comparison.png + .pdf")

plot_baseline_comparison()
