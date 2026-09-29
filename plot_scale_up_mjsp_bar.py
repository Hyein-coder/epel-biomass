"""Grouped bar plot of MJSP (Base / Full-Ammonia / 60% CCS) vs scale.

Data = _Scale_Up_Sensitivity.md §1 table (original linear-CAPEX numbers, the
manuscript-matching basis). Values are hardcoded from that table, not re-run.
"""
import os
import numpy as np
import matplotlib.pyplot as plt

# _PLOTTING_STYLE.md (SA_RC lives only in the notebook; inlined here)
SA_RC = {
    'figure.dpi': 150, 'figure.facecolor': 'white', 'figure.autolayout': True,
    'axes.facecolor': 'white', 'axes.edgecolor': '#444444', 'axes.linewidth': 0.8,
    'axes.spines.top': True, 'axes.spines.right': True, 'axes.labelsize': 12,
    'axes.labelcolor': 'black', 'axes.labelweight': '500', 'axes.grid': False,
    'xtick.labelsize': 12, 'xtick.color': 'black', 'ytick.labelsize': 10, 'ytick.color': 'black',
    'font.family': 'sans-serif',
    'font.sans-serif': ['Helvetica Neue LT Pro', 'Helvetica Neue', 'Arial', 'DejaVu Sans'],
    'font.size': 10, 'font.weight': '300', 'text.color': 'black',
    'patch.edgecolor': 'black', 'patch.linewidth': 0.7, 'patch.force_edgecolor': True,
    'legend.fontsize': 8, 'legend.title_fontsize': 9, 'legend.framealpha': 0.0,
    'legend.edgecolor': '#444444', 'lines.linewidth': 0.7, 'lines.markersize': 3,
    'savefig.dpi': 150, 'savefig.bbox': 'tight', 'savefig.facecolor': 'white',
}

SCALES: list[float] = [1, 2.5, 5, 7.5, 10, 20, 30]
SAF_MMT: list[float] = [0.046, 0.114, 0.228, 0.342, 0.457, 0.913, 1.370]  # SAF kt/yr (§1) / 1000
MJSP: dict[str, list[float]] = {  # $/L SAF, §1 table
    'Base':          [1.582, 1.231, 1.004, 0.881, 0.781, 0.711, 0.678],
    'Full-Ammonia':  [3.426, 3.022, 2.778, 2.645, 2.532, 2.441, 2.403],
    '60% CCS':       [1.743, 1.392, 1.165, 1.041, 0.941, 0.872, 0.839],  # §1 = 60% capture, not full-CCS
}

plt.rcParams.update(SA_RC)
# Base black; vivid green/orange for the H2 configs (Base / Full-Ammonia / 60% CCS)
colors = {'Base': '#000000', 'Full-Ammonia': '#548235', '60% CCS': '#ed7d31'}

x = np.arange(len(SCALES))
w = 0.27
fig, ax = plt.subplots(figsize=(8, 5))
for i, (case, vals) in enumerate(MJSP.items()):
    ax.bar(x + (i - 1) * w, vals, w, label=case, color=colors[case])

ax.set_xlabel('SAF production [MMt/yr]')
ax.set_ylabel('MJSP [\\$/L SAF]')  # escape $ so mathtext keeps the currency sign
ax.set_xticks(x)
ax.set_xticklabels([f'{s:.3f}' for s in SAF_MMT])
ax.set_ylim(0, ax.get_ylim()[1] * 1.2)
ax.legend()

out = os.path.join('Figure', 'scale_up_mjsp_bar.png')
fig.savefig(out, dpi=150)
print('saved', out)

# check: bars match the source table (Ammonia > CCS > Base at every scale)
assert all(a > c > b for a, c, b in zip(MJSP['Full-Ammonia'], MJSP['60% CCS'], MJSP['Base']))
