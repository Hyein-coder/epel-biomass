"""
CO2 Mix for SAF Regulation
"""
import pandas as pd
from funs_lca import H2Mix
import matplotlib.pyplot as plt
import numpy as np
import os
from funs import TEA
from funs_lca import get_WTWa_conventional, get_WTWa_pyrolysis

fig_folder = os.path.join(os.getcwd(), 'Figure')
res_folder = os.path.join(os.getcwd(), 'Result')
save_heading = 'CO2_ver551'
#%%
portion = [0.1 * i for i in range(10)]
tea = TEA()
file_stream = f'Process_Data\\Pyrolysis_551_Scale{int(10):04d}_Streams.xlsx'
file_apea = f'Process_Data\\Pyrolysis_551_Scale{int(10):04d}_APEA.xlsm'  # Fixed Biomass Price
h2_sources = ['Base']

file_wtwa = 'Process_Data\\WTWa_LCA.xlsx'
lca_conventional = get_WTWa_conventional(file_wtwa)
ghg_threshold_saf = 0.9 * lca_conventional['WTWa']['GHG-100']

file_lca_woCCS = f'Process_Data\\Pyrolysis_551_LCA_Allocation.xlsx'
lca_woCCS = get_WTWa_pyrolysis('Base', file_lca_woCCS, file_wtwa)
ghg_woCCS = lca_woCCS['WTWa']['GHG-100']

file_lca_withCCS = f'Process_Data\\Pyrolysis_551_LCA_Allocation.xlsx'   # TODO: 이거 데이터가 없음
lca_withCCS = get_WTWa_pyrolysis('CCS100', file_lca_withCCS, file_wtwa)
ghg_withCCS = lca_withCCS['WTWa']['GHG-100']

mjsp_data = []
ghg_data = []
for p in portion:
    df_mjsp, energy_production, annual_prod_saf, main_h2_demand, opex_names, data_all, name_h2_source_new =\
        tea.economic_analysis(file_stream, file_apea, h2_sources, ccs_portion=p)
    mjsp_data.append([data_all['cost'][i]['MJSP'] for i in range(len(h2_sources))])
    ghg_data.append(p * ghg_withCCS + (1 - p) * ghg_woCCS)
    data_all['df_process'][0].to_excel(f'{res_folder}\\{save_heading}_{int(p * 100):03d}.xlsx')

#%%

fig, ax1 = plt.subplots(figsize=(8, 5))

ghg_color = '#94ab9a'
bars = ax1.bar(portion, ghg_data, color=ghg_color, width=0.07, alpha=0.7)
ax1.set_xlabel('CCS Portion')
ax1.set_ylabel('WTWa Emission')
ax1.grid(axis='y', linestyle='--', alpha=0.7)

ax1.axhline(ghg_threshold_saf, color='green')

ax2 = ax1.twinx()
ax2.plot(portion, mjsp_data, color='black', marker='D')
ax2.set_ylabel('Production Cost')

fig.tight_layout()
plt.show()

