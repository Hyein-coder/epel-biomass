import pandas as pd
from funs_lca import H2Mix
import matplotlib.pyplot as plt
import numpy as np
import os

fig_folder = os.path.join(os.getcwd(), 'Figure')
#%%
portion = [0.1 * i for i in range(10)]

pyromix = H2Mix(1)
res = [pyromix.mjsp_with_ammonia(p) for p in portion]
mjsp_res = {'MJSP': [v for v, d in res]}
mjsp_df = pd.DataFrame(mjsp_res, index=portion)
breakdown_res = [d for v, d in res]

lcoh_ammonia = [pyromix.get_LCOH(p) for p in portion]

ghg = [pyromix.ghg_with_ammonia(p) for p in portion]
ghg_mean = [g[0] for g in ghg]
ghg_min = [min(g[2]) for g in ghg]
ghg_max = [max(g[2]) for g in ghg]
ghg_threshold = pyromix.ghg_threshold_saf

#%%
fig, ax1 = plt.subplots(figsize=(8, 5))

ghg_color = '#94ab9a'
ghg_fs = 16
bars = ax1.bar(portion, ghg_max, color=ghg_color, width=0.07, alpha=0.7)
ax1.set_xlabel('Ammonia Portion', fontsize=ghg_fs)
ax1.set_ylabel('Maximum GHG Emission \n [g CO2e/MJ SAF]', color=ghg_color, fontsize=ghg_fs)
ax1.tick_params(axis='y', labelcolor=ghg_color)
ax1.set_ylim(0, max(ghg_max) + 10)
ax1.grid(axis='y', linestyle='--', alpha=0.7)

ax1.axhline(ghg_threshold, color='green', linestyle='-', linewidth=1)
ax1.text(0.4, ghg_threshold-10, f'SAF Regulation = {ghg_threshold:.1f}', color='green', fontsize=ghg_fs-2)

ax2 = ax1.twinx()
# mjsp_cmap = plt.get_cmap('twilight', len(case_scale)+1)
mjsp_colors = ['#777777',  '#555555', '#333333', '#111111']
markers = ["o", "s", "D", "^", "v", "<", ">", "p", "*", "h", "H", "+", "x", "|", "_"]
lines = ['-', '--', '-.', ':', '--.']
ax2.plot(portion, mjsp_df['MJSP'], color='black', marker='D', linestyle='--', linewidth=1.5, label='MJSP [$/L]')
ax2.plot(portion, lcoh_ammonia, color='steelblue', marker='^', linestyle='-.', linewidth=1.5,
         label=r'Ammonia H$_2$ [\$/lb]')
ax2.axhline(0.68, linestyle=':', color='black', linewidth=1.5, label=r'Gray H$_2$ [\$/lb]')
ax2.set_ylabel(r'Production Cost', color='black', fontsize=ghg_fs)
ax2.tick_params(axis='y', labelcolor='black')
ax2.set_ylim(0, mjsp_df.max().max() + 0.5)
ax2.legend(loc='lower right', fontsize=ghg_fs-3, title_fontsize=ghg_fs-3)

# Title and layout
# plt.title('GHG Emission (bar) and MJSP (line)', fontsize=14)
fig.tight_layout()
plt.savefig(os.path.join(fig_folder, 'h2_pathway_mix.png'))
plt.savefig(os.path.join(fig_folder, 'h2_pathway_mix.eps'))
plt.show()

#%%
p_opt = .655
gm, ge, gall = pyromix.ghg_with_ammonia(p_opt)
colors = ['#b57e43', '#e8b176',
          '#4d7358', '#94ab9a']
# '#e39e54', '#eec498', '#708f79', '#b7c7bc'
gall = pd.DataFrame(gall, index=pyromix.lca_methods, columns=[f'Ammonia {p_opt*100:.1f}%']).transpose()

fs = 18
ax = gall.plot(kind='bar', figsize=(8, 5), color=colors, fontsize=fs)
plt.axhline(y=ghg_threshold, color='b', linewidth=1)
# plt.axhline(y=ghg_conventional, color='b', linestyle='-.', linewidth=1)
plt.ylabel("WTWa GHG Emissions \n [g CO2e/MJ SAF]", fontsize=fs+2)
# plt.xlabel("Technologies", fontsize=fs+2)
plt.xticks(rotation=0, fontsize=fs)
plt.legend(fontsize=fs-1, loc='upper left', bbox_to_anchor=(1,1))
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
# plt.savefig(os.path.join(fig_folder, 'fig_LCA_compare.png'))
# plt.savefig(os.path.join(fig_folder, 'fig_LCA_compare.eps'))
plt.show()


#%%
breakdown = pd.concat([d for v, d in res])
breakdown.index = portion

cmap_breakdown = plt.get_cmap("twilight")
colors_breakdown = cmap_breakdown(np.linspace(0, 1, len(breakdown.columns)+1))
markers = ["o", "s", "D", "^", "v", "<", ">", "p", "*", "h", "H", "+", "x", "|", "_"]
lines = ['-', '--', '-.', ':', '--.']
fig, ax = plt.subplots(figsize=(8,5))
for idx, column in enumerate(breakdown.columns):
    plt.plot(breakdown.index, breakdown[column], marker=markers[idx], color=colors_breakdown[idx], label=column)

plt.legend(loc='upper left', bbox_to_anchor=(1.02, .9))
plt.tight_layout()
plt.show()

