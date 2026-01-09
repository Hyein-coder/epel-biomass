import matplotlib.pyplot as plt
import os
import pandas as pd
import numpy as np
from funs_lca import get_WTWa_conventional, get_WTWa_ftjet, get_WTWa_pyrolysis

## with Carbon Neutrality
case_list = [
    "Allocation", "Displacement",
    "Allocation_KRmix", "Displacement_KRmix"
]
case_pretty_name = [
    'Allocation (U.S.)', 'Displacement (U.S.)',
    'Allocation (Korea)', 'Displacement (Korea)'
]

df_case = []
case_biogen_carb = []
fig_folder = os.path.join(os.getcwd(), 'Figure')
if not os.path.exists(fig_folder):
    os.makedirs(fig_folder)

case_ccs = ['Base', 'CCS025', 'CCS050', 'CCS075', 'CCS100']
name_for_cases = ['Base', 'CCS 25%', 'CCS 50%', 'CCS 75%', 'CCS 100%']

file_wtwa = 'Process_Data\\WTWa_LCA.xlsx'
for i, case_name in enumerate(case_list):
    file_name = f'Process_Data\\Pyrolysis_572_LCA_{case_name}.xlsx'

    lca_conventional = get_WTWa_conventional(file_wtwa)
    if 'woBiogenic' in case_name:
        lca_ftjet = get_WTWa_ftjet(file_wtwa, False)
    else:
        lca_ftjet = get_WTWa_ftjet(file_wtwa)
    lca_total = {'Conventional': lca_conventional, 'FTjet': lca_ftjet}

    biogen_carb_ptwa = lca_ftjet['PTWa']['CO2_Biogenic']
    lca_biogen_carb = {'Conventional': lca_conventional['PTWa']['CO2_Biogenic'],
                       'FTjet': lca_ftjet['WTWa']['CO2_Biogenic']}
    for k, case in enumerate(case_ccs):
        lca_case = get_WTWa_pyrolysis(case, file_name, file_wtwa)
        lca_total[name_for_cases[k]] = lca_case

        biogen_carb_wtp = lca_case['WTP']['CO2_Biogenic']
        biogen_carb_wtwa = biogen_carb_wtp + biogen_carb_ptwa
        lca_biogen_carb[case] = biogen_carb_wtwa

    data_WTWa = {}
    for name, data in lca_total.items():
        for key, val in data.items():
            data_WTWa[name + '-' + key] = val
    df_WTWa = pd.DataFrame(data_WTWa)

    df_LCA = pd.DataFrame(df_WTWa.filter(like='WTWa').loc['GHG-100'])
    df_LCA.index = df_LCA.index.str.replace('-WTWa', '', regex=False)
    ghg_threshold_saf = 0.9 * df_LCA.loc['Conventional', 'GHG-100']
    ghg_conventional = df_LCA.loc['Conventional', 'GHG-100']
    lca_to_draw = pd.DataFrame(df_LCA.iloc[2:])

    lca_colors = plt.cm.viridis(np.linspace(0, 1, len(lca_to_draw.index)))

    df_LCA.columns = [case_pretty_name[i]]
    df_case.append(df_LCA)
    case_biogen_carb.append(lca_biogen_carb)

summary = pd.concat(df_case, axis=1)
sum_avg = summary.sum(axis=1)/2

#%%
# Plotting
params = {
    'legend.fontsize': 'large',
    'axes.labelsize': 'x-large',
    'axes.titlesize': 'xx-large',
    'xtick.labelsize': 'x-large',
    'ytick.labelsize': 'x-large'}
plt.rcParams.update(params)

# colors = ['#4d7358', '#e39e54', '#7d9d86', '#d6b185']   # '#e8d174', '#d64d4d'
colors = ['#e39e54', '#e39e54',      # '#b57e43','#e8b176',
          '#708f79', '#708f79']   # '#4d7358', '#94ab9a',
styles = ['-o', '-D', ':^', ':x']

opt_ccs = 60
opt_summary = (summary.loc['CCS 50%'] * (75-opt_ccs) + summary.loc['CCS 75%'] * (opt_ccs-50)) / (75-50)

fig, ax = plt.subplots(figsize=(6,4))
for idx, col in enumerate(summary.columns):
    plt.plot([0, 25, 50, 75, 100], summary[col].iloc[2:], styles[idx], color=colors[idx], label=col)
    # plt.plot([opt_ccs], opt_summary[col], styles[idx], color=colors[idx])
plt.axhline(y=ghg_threshold_saf, color='b', linewidth=1)
plt.xticks([0, 25, 50, 75, 100])  # Set x-axis ticks exactly
plt.legend()
plt.ylabel("WTWa GHG Emissions \n [g CO2e/MJ SAF]")
plt.xlabel(r"Portion of Captured CO$_2$ [%]")
plt.grid(True, alpha=0.6)
plt.tight_layout()
plt.savefig(os.path.join(fig_folder, "ccs_fig_LCA.png"))
plt.savefig(os.path.join(fig_folder, "ccs_fig_LCA.eps"))
plt.show()


