"""
TEA for CCS 0% 25% 50% 75% 100% and WTWa data inventory
"""

import pandas as pd
import os
import matplotlib.pyplot as plt
from funs import TEA
from plotting import plot_stack_bar, plot_pie_chart

tea = TEA()
file_name = {
    'Stream': 'Process_Data\\Pyrolysis_Jones_572_2MC_0010_Streams.xlsx',
    'APEA': 'Process_Data\\Pyrolysis_Jones_572_2MC_0010_APEAresults.xlsm'
}
ccs_experiment = [0, .158, .1585, .159]
# ccs_experiment = [0, 0.25, 0.5, 0.75, 1.]
ccs_name = [f'{c*100:.0f}%' for c in ccs_experiment]
name_for_h2_source = ['Base']

fig_folder = os.path.join(os.getcwd(), 'Figure')
if not os.path.exists(fig_folder):
    os.makedirs(fig_folder)

ccs_data = {'MJSP': [], 'energy_production': [], 'emission_flow': [], 'captured_flow': [],
            'resource_flow': [], 'ur_sum': [], 'carbon_net': [], 'data_all': [], 'dfp': []}
for ccs_portion in ccs_experiment:

    mjsp, energy_production, annual_prod_saf, main_h2_demand, opex_names, data_all, h2_source = \
        tea.economic_analysis(file_name['Stream'], file_name['APEA'], name_for_h2_source, ccs_portion=ccs_portion)
    dfp_per_h2_source = data_all['df_process']

    carb_eff, carbon_net = tea.calc_carbon_efficiency(file_name['Stream'], ccs_portion)
    emission_flow, captured_flow = tea.get_emission_flow(file_name['Stream'], ccs_portion)
    resource_flow = tea.get_resource_flow(file_name['Stream'])
    ur_sum, ur_rate = \
        tea.get_util_and_rawmaterial_sum(file_name['APEA'], dfp_per_h2_source, name_for_h2_source)

    data_now = [mjsp, energy_production, emission_flow, captured_flow,
                resource_flow, ur_sum, carbon_net, data_all, dfp_per_h2_source]
    for k, v in zip(ccs_data.keys(), data_now):
        ccs_data[k].append(v)

#%%
df_mjsp = pd.concat(ccs_data['MJSP'])
df_mjsp.index = ccs_name
colors = ['#FAE8BC', '#F0B1AC', '#BBDBB4', '#F5D3A6', '#8DB1B1', '#DAB7DB', '#E5C1C6', '#FBCBA4', '#B5D7EB']
fig, ax = plot_stack_bar(df_mjsp, 'MJSP [$/L]', colors,
                         xlabel=r'Portion of Captured CO$_2$',
                         figsize=(10,5),
                         save_name=os.path.join(fig_folder, 'ccs_mjsp'))

#%%
df_emission = pd.DataFrame(ccs_data['emission_flow']).transpose()
df_emission.columns = ccs_name

df_captured = pd.DataFrame(ccs_data['captured_flow']).transpose()
df_captured.columns = ccs_name

#%%
df_util_and_rawmaterial_sum = pd.concat(ccs_data['ur_sum'], axis=1)
df_util_and_rawmaterial_sum.columns = ccs_experiment

materials_order = [
    'Biomass', 'BFW', 'Sand', 'Sulfiding agent', 'Hydrogen gas', 'Natural Gas', 'Ammonia', 'Electricity', 'Fuel',
    'MP steam', 'LP steam', 'Water'
]

data_ur_rate = {}
ur_price = tea.calc_util_and_rawmaterial_price(file_name['APEA'])
for name, df in df_util_and_rawmaterial_sum.items():
    df_ur = pd.concat([df, ur_price], axis=1)
    df_ur = df_ur.dropna()
    df_ur = df_ur[df_ur['Price per Rate'] > 0]
    data_ur_rate[name] = df_ur[name] / df_ur['Price per Rate']
ur_units = ur_price['Units'].copy()
ur_rate = pd.DataFrame(data_ur_rate)

for c in ['Biomass', 'Water', 'BFW', 'Hydrogen gas']:
    ur_rate.loc[c] = ur_rate.loc[c] / 2000
    ur_units.loc[c] = 'tons/H'
for c in ['MP steam', 'LP steam']:
    ur_rate.loc[c] = ur_rate.loc[c] / 1000000
    ur_units.loc[c] = 'MMBTU/H'
for c in ['Electricity']:
    ur_rate.loc[c] = ur_rate.loc[c] / 1000
    ur_units.loc[c] = 'MWH'

ur_summary = pd.concat([ur_rate, ur_units], axis=1)
ur_summary = ur_summary.loc[materials_order]

#%%
dfp_ccs = [c[0] for c in ccs_data['dfp']]
df_util_and_rawmaterial_sum, df_util_and_rawmaterial_rate = \
    tea.get_util_and_rawmaterial_sum(file_name['APEA'], dfp_ccs, ccs_name)
df_util_and_rawmaterial_sum.loc['CCS portion'] = ccs_experiment
sorted_cols = df_util_and_rawmaterial_sum.loc['CCS portion'].sort_values().index
df_ur_sum_ordered = df_util_and_rawmaterial_sum[sorted_cols]

ur_exclude_idx = ['Biomass', 'Hydrogen gas', 'Electricity', 'Fuel']
ur_colors = [
     '#2f6ea5',  # Brighter Deep Blue
     '#c0c0c0',  # Brighter Gray
     '#ffbf50',  # Brighter Golden Yellow
     '#80d6d6',  # Brighter Muted Cyan
     '#e0e0e0',  # Brighter Light Gray
     '#f5d6a0',  # Brighter Warm Beige
     '#c2a2e0',  # Muted Pastel Lavender (Toned Down)
     '#B6C9ED',
     '#f09040',  # Brighter Burnt Orange
     '#00bfbf',  # Brighter Teal
     '#6eacf2',  # Brighter Steel Blue
     '#CFDBFA',     # Light Grey Lavender
     '#D2E1C0',  #
     '#008f8f',  # Brighter Dark Green
     '#DAADA0',    # Brighter Dead Rose
     # '#ffa500',   # Classical Orange
     # '#ffcc80',   # Soft Yellow-Orange (New)
     # '#80bf88',  # Muted Green
     '#F0EEE8'  # White Grey
]
ur_fixed = df_ur_sum_ordered.loc[ur_exclude_idx]
ur_to_sort = df_ur_sum_ordered.drop(index=ur_exclude_idx)
ur_sorted = ur_to_sort.sort_values(by='0%', ascending=False)
ur_final = pd.concat([ur_fixed, ur_sorted])

plot_stack_bar(ur_final.transpose()*8000/1e6, 'Annual Cost [M$/year]', xlabel=r'Portion of Captured CO$_2$',
               save_name=os.path.join(fig_folder, 'fig_ccs_util_raw'), label_lim=1,
               figsize=(10,5), colors=ur_colors, tot_sum=False)

#%%
data_all_sum = {k: [d[k] for d in ccs_data['data_all']] for k in ccs_data['data_all'][0].keys()}
capex = pd.DataFrame([c[0]['total CAPEX']/1e6 for c in data_all_sum['cost']], index=ccs_name, columns=['CAPEX']).transpose()
opex = pd.DataFrame([d[0] for d in data_all_sum['opex']], index=ccs_name).transpose()
opex_million = opex.apply(lambda x: x/1e6)
capex_and_opex = pd.concat([capex, opex_million])
capex_and_opex.to_excel(os.path.join(fig_folder, 'TEA_summary_CCS.xlsx'))

