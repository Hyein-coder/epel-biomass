"""Redraw the two §3.1 scale-up figures from their recorded data sheets (no TEA re-run):
(upper) Figure/scale_up_wo_price_model_base_summary.png <- Result/scale_up_base_summary.xlsx (tea_scale_up.py)
(lower) Figure/scale_up_price_model_mjsp.png <- Result/scale_up_price_model_mjsp.xlsx (tea_scale_up_price_models.py)
Combined into one figure (upper/lower subplots) -> Figure/composite_scale_up_mjsp.png."""
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from plotting import plot_stack_bar

# _PLOTTING_STYLE.md (SA_RC lives only in the notebook; inlined here)
SA_RC = {
    'figure.dpi': 150, 'figure.facecolor': 'white', 'figure.autolayout': True,
    'axes.facecolor': 'white', 'axes.edgecolor': '#444444', 'axes.linewidth': 0.8,
    'axes.spines.top': True, 'axes.spines.right': True, 'axes.labelsize': 12,
    'axes.labelcolor': 'black', 'axes.labelweight': '500', 'axes.grid': False,
    'xtick.labelsize': 12, 'xtick.color': 'black', 'ytick.labelsize': 12, 'ytick.color': 'black',
    'font.family': 'sans-serif',
    'font.sans-serif': ['Helvetica Neue LT Pro', 'Helvetica Neue', 'Arial', 'DejaVu Sans'],
    'font.size': 10, 'font.weight': '300', 'text.color': 'black',
    'patch.edgecolor': 'black', 'patch.linewidth': 0.7, 'patch.force_edgecolor': True,
    'legend.fontsize': 8, 'legend.title_fontsize': 9, 'legend.framealpha': 0.0,
    'legend.edgecolor': '#444444', 'lines.linewidth': 0.7, 'lines.markersize': 3,
    'savefig.dpi': 150, 'savefig.bbox': 'tight', 'savefig.facecolor': 'white',
}
plt.rcParams.update(SA_RC)

FIGSIZE = (9, 7.2)
XLABEL = 'SAF production [MMt/yr]'
X_COL = 'saf production [MMt/yr]'
fig_folder = 'Figure'

# --- Upper: base-case MJSP breakdown (stacked bar + total) ---
df_base = pd.read_excel(os.path.join('Result', 'scale_up_base_summary.xlsx'), index_col=0)
sheets = pd.read_excel(os.path.join('Result', 'scale_up_price_model_mjsp.xlsx'), sheet_name=None, index_col=0)
df_price = sheets.pop('biomass price')
xlabels = [f'{v:.2f}' for v in df_price.pop(X_COL)]
# upper panel reuses lower-panel tick labels (same 7 scale-up cases, row order)
df_base.index = xlabels

stack_hatches = ['///', '\\\\\\', 'xxx', '...', 'ooo', '+++', '---', '|||', '**']   # one per cost column
fig, (ax_top, ax) = plt.subplots(2, 1, figsize=FIGSIZE)
# 10 legend entries in 2 rows across the top; ytop leaves headroom above the tallest stack
# total bar red = raw-materials color of the former colored palette
plot_stack_bar(df_base, 'MJSP [$/L SAF]', ax=ax_top, hatches=stack_hatches, total_color='#F0B1AC',
               xlabel=XLABEL, fs=None, ytop=1.55,
               legend_kw=dict(loc='upper center', ncol=5, columnspacing=1.0))

# --- Lower: biomass price bars (hatched) + MJSP mean line / price-model range band per case ---
mjsp = {name.removeprefix('MJSP '): df.drop(columns=X_COL) for name, df in sheets.items()}
x = np.arange(len(df_price))

bar_hatches = ['///', 'xxx', '...']   # color-free bars, one hatch per price model
line_colors = ['#D6AE5C', '#D57F78', '#85B27C']   # base_summary palette, darkened: Base / Ammonia / CCS
case_styles = ['-', '--', ':']
case_markers = ['o', 's', '^']

df_price.plot(kind='bar', color='white', edgecolor='black', ax=ax, width=0.7)
for container, hatch in zip(ax.containers, bar_hatches):
    for bar in container:
        bar.set_hatch(hatch)
ax.set_ylabel("Biomass price [$/lb]")
ax.set_xlabel(XLABEL)
ax.set_xticklabels(xlabels, rotation=0)
ax.set_ylim(0, ax.get_ylim()[1] * 1.2)

ax2 = ax.twinx()
for cfg_idx, (name, df) in enumerate(mjsp.items()):
    ax2.fill_between(x, df.min(axis=1), df.max(axis=1), color=line_colors[cfg_idx], alpha=0.25, linewidth=0)
    ax2.plot(x, df.mean(axis=1), color=line_colors[cfg_idx], linewidth=2,
             linestyle=case_styles[cfg_idx], marker=case_markers[cfg_idx], markersize=5, label=name)
ax2.set_ylabel("MJSP [$/L SAF]")
ax2.set_ylim(0, ax2.get_ylim()[1] * 1.2)

handles, labels = ax.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax.legend(handles + h2, labels + l2, loc='upper left')
plt.savefig(os.path.join(fig_folder, 'composite_scale_up_mjsp.png'))
