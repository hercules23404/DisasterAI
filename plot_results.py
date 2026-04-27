import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set style for IEEE paper
try:
    plt.style.use('seaborn-v0_8-paper')
except:
    plt.style.use('seaborn-paper')

sns.set_theme(style="whitegrid", context="paper")

RESULTS_DIR = 'results'
os.makedirs(RESULTS_DIR, exist_ok=True)

# Load data
baseline_df = pd.read_csv(os.path.join(RESULTS_DIR, 'baseline_comparison.csv'))
ablation_df = pd.read_csv(os.path.join(RESULTS_DIR, 'ablation_lookahead.csv'))

# 1. Baseline Comparison: Simulation Score
plt.figure(figsize=(6, 4))
sns.barplot(data=baseline_df, x='mode', y='simulation_score', errorbar='sd', capsize=.1, palette='viridis')
plt.title('Baseline Comparison: Simulation Score', fontsize=12)
plt.ylabel('Simulation Score', fontsize=10)
plt.xlabel('Dispatch Mode', fontsize=10)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(RESULTS_DIR, 'fig1_baseline_scores.png'), dpi=300)
plt.close()

# 2. Baseline Comparison: Mean Response Time
plt.figure(figsize=(6, 4))
sns.barplot(data=baseline_df, x='mode', y='mean_response_time', errorbar='sd', capsize=.1, palette='mako')
plt.title('Baseline Comparison: Mean Response Time', fontsize=12)
plt.ylabel('Mean Response Time (Timesteps)', fontsize=10)
plt.xlabel('Dispatch Mode', fontsize=10)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(RESULTS_DIR, 'fig2_baseline_response_time.png'), dpi=300)
plt.close()

# 3. Ablation Study: Simulation Score vs N
plt.figure(figsize=(6, 4))
sns.lineplot(data=ablation_df, x='N_value', y='simulation_score', marker='o', errorbar='sd', color='b')
plt.title('Ablation Study: Simulation Score vs Lookahead Steps (N)', fontsize=12)
plt.ylabel('Simulation Score', fontsize=10)
plt.xlabel('Lookahead Steps (N)', fontsize=10)
plt.xticks([1, 2, 3, 5, 7])
plt.tight_layout()
plt.savefig(os.path.join(RESULTS_DIR, 'fig3_ablation_scores.png'), dpi=300)
plt.close()

# 4. Ablation Study: Mean Response Time vs N
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
