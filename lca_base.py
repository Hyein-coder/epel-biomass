import matplotlib.pyplot as plt
import os
import pandas as pd
import numpy as np
from funs_lca import get_WTWa_conventional, get_WTWa_ftjet, get_WTWa_pyrolysis

## with Carbon Neutrality
case_list = [
    "Allocation", "Displacement",
    # "FullCCS_Allocation", "FullCCS_Displacement",
    "Allocation_KRmix", "Displacement_KRmix"
    # "FullCCS_Allocation_KRmix", "FullCCS_Displacement_KRmix"
]
case_pretty_name = [
    'Allocation', 'Displacement',
    # 'Allocation w/CCS', 'Displacement w/CCS',
    # '', '',
    '', ''
]

df_case = []
case_biogen_carb = []
fig_folder = os.path.join(os.getcwd(), 'Figure')
if not os.path.exists(fig_folder):
    os.makedirs(fig_folder)

h2_source = ['Base', 'SMR', 'Ammonia', 'PEM', 'Mix']
name_for_h2 = ['Base', 'BH', 'Ammonia', 'PEM', 'Mix']
mix_rate = 0.5

# name_h2_source = ['Base', 'wCCS', 'SMR', 'Ammonia', 'PEM']
file_wtwa = 'Process_Data\\WTWa_LCA.xlsx'
for i, case_name in enumerate(case_list):
    # case_name = "Displacement_CcsZeroEmission"
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
    for k, case in enumerate(h2_source[:-1]):
        lca_case = get_WTWa_pyrolysis(case, file_name, file_wtwa)
        lca_total[name_for_h2[k]] = lca_case

        biogen_carb_wtp = lca_case['WTP']['CO2_Biogenic']
        biogen_carb_wtwa = biogen_carb_wtp + biogen_carb_ptwa
        lca_biogen_carb[case] = biogen_carb_wtwa

    lca_mix = {}
    weights = [1 - mix_rate, mix_rate]
    for cat, ser_base in lca_total['Base'].items():
        ser_ammonia = lca_total['Ammonia'][cat]
        df_cat = pd.concat([ser_base, ser_ammonia], axis=1)
        lca_mix[cat] = (df_cat * weights).sum(axis=1)
    lca_total['Mix'] = lca_mix
    mix_kind = ['Base', 'Ammonia']
    lca_biogen_carb['Mix'] = sum([lca_biogen_carb[a] * b for a, b in zip(mix_kind, weights)])

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

    # Create the bar chart
    plt.figure(figsize=(8, 5))
    plt.bar(lca_to_draw.index, lca_to_draw['GHG-100'], color=lca_colors)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    # plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.axhline(y=ghg_threshold_saf, color='r', linewidth=1)

    plt.xlabel("Cases")
    plt.ylabel("WTWa GHG-100 emissions [g/MJ SAF]")
    plt.savefig(os.path.join(fig_folder, f'fig_LCA_{case_name}.png'))
    plt.savefig(os.path.join(fig_folder, f'fig_LCA_{case_name}.eps'))
    plt.show()

    df_LCA.columns = [case_pretty_name[i]]
    df_case.append(df_LCA)
    case_biogen_carb.append(lca_biogen_carb)

summary = pd.concat(df_case, axis=1)
sum_avg = (summary['Allocation'] + summary['Displacement'])/2
case_biogen_carb.append(
    {k: sum([cbc[k] for cbc in case_biogen_carb]) / 2 for k in h2_source}
)
#%%
# Plotting
# colors = ['#4d7358', '#e39e54', '#7d9d86', '#d6b185']   # '#e8d174', '#d64d4d'
colors = ['#e39e54', '#eec498',      # '#b57e43','#e8b176',
          '#708f79', '#b7c7bc']   # '#4d7358', '#94ab9a',
fs = 18
ax = summary.iloc[2:].plot(kind='bar', figsize=(14, 5), color=colors, fontsize=fs)
plt.axhline(y=ghg_threshold_saf, color='b', linewidth=1)
plt.axhline(y=ghg_conventional, color='b', linestyle='-.', linewidth=1)
# plt.title("Emission Comparison", fontsize=fs+2)
plt.ylabel("WTWa GHG Emissions \n [g CO2e/MJ SAF]", fontsize=fs+2)
# plt.xlabel("Technologies", fontsize=fs+2)
plt.xticks(rotation=0, fontsize=fs)
plt.legend(fontsize=fs-1)
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig(os.path.join(fig_folder, 'fig_LCA_compare.png'))
plt.savefig(os.path.join(fig_folder, 'fig_LCA_compare.eps'))
plt.show()

