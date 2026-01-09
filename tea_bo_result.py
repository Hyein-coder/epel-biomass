import pandas as pd
import os

from funs import TEA
from plotting import plot_stack_bar, plot_pie_chart

tea = TEA()
file_old = {
    'Stream': 'Process_Data\\Pyrolysis_551_Scale0010_Streams.xlsx',
    'APEA': 'Process_Data\\Pyrolysis_551_Scale0010_APEA.xlsm'
}
file_pyro = {
    'Stream': 'Process_Data\\Pyrolysis_Jones_551_into572_Streams.xlsx',
    'APEA': 'Process_Data\\Pyrolysis_Jones_551_into572_APEAresult.xlsm'
}
file_comp = {
    'Stream': 'Process_Data\\Pyrolysis_Jones_572_Streams.xlsx',
    'APEA': 'Process_Data\\Pyrolysis_Jones_572_APEAresult.xlsm'
}
file_opt = {
    'Stream': 'Process_Data\\Pyrolysis_Jones_572_2MC_Streams.xlsx',
    'APEA': 'Process_Data\\Pyrolysis_Jones_572_2MC_APEAresult.xlsm'
}

files = [file_old, file_pyro, file_opt]
names = ['Base', 'Distillation\nColumns', 'Compressors']

fig_folder = os.path.join(os.getcwd(), 'Figure_BO')
if not os.path.exists(fig_folder):
    os.makedirs(fig_folder)

# tea.product_price_work = {}
equipment_names = {
    'C': 'Compressor',
    'COL': 'Vessel',
    'E': 'Heat Exchanger',
    'GT': 'Gas Turbine',
    'H': 'Furnace',
    'MC': 'Multi-stage Comp.',
    'P': 'Pump',
    'R': 'Reactor',
    'S': 'Separator',
    'T': 'Column',
    'V': 'Vessel'
}
unit_rule_per_kind = (lambda x: equipment_names[x.split('-')[0]] if x.split('-')[0] in equipment_names.keys() else x.split('-')[0])
data = {
    'df_mjsp': [], 'df_equip_per_process': [], 'df_equip_per_kind': [],
    'carb_eff': [], 'df_util_and_rawmaterial_sum': [], 'carb_net': [],
    'saf_prod': []
}
for name, file in zip(names, files):
    dfm, energy_production, annual_prod_saf, main_h2_demand, opex_names, data_all, h2_source = \
        tea.economic_analysis(file['Stream'], file['APEA'], ['Base'])
    dfp = data_all['df_process']
    dep, _ = tea.get_equipment_breakdown(file['APEA'], dfp, h2_source)
    dek, _ = tea.get_equipment_breakdown(file['APEA'], dfp, h2_source, unit_rule_per_kind)
    dur, _ = tea.get_util_and_rawmaterial_sum(file['APEA'], dfp, h2_source)

    dfm.index = [name]
    data['df_mjsp'].append(dfm)

    dep.columns = [name]
    dek.columns = [name]
    dur.columns = [name]
    data['df_equip_per_process'].append(dep)
    data['df_equip_per_kind'].append(dek)
    data['df_util_and_rawmaterial_sum'].append(dur)
    data['saf_prod'].append(annual_prod_saf)

    # carb_eff, carb_net = tea.calc_carbon_efficiency(file['Stream'])
    # data['carb_eff'] = carb_eff.values()
    # data['carb_net'] = carb_net

df_mjsp = pd.concat(data['df_mjsp'])
df_equip_per_process = pd.concat(data['df_equip_per_process'], axis=1)
df_util_and_rawmaterial_sum = pd.concat(data['df_util_and_rawmaterial_sum'], axis=1)

df_equip_per_kind = pd.concat(data['df_equip_per_kind'], axis=1)
# equipment_names = {
#     'C': 'Compressor',
#     'COL': 'Vessel',
#     'E': 'Heat Exchanger',
#     'GT': 'Gas Turbine',
#     'H': 'Furnace',
#     'MC': 'Multi-stage Comp.',
#     'P': 'Pump',
#     'R': 'Reactor',
#     'S': 'Separator',
#     'T': 'Tower',
#     'V': 'Vessel'
# }
# df_equip_per_kind = df_equip_per_kind.rename(index=equipment_names)

#%%
colors = ['#FAE8BC', '#F0B1AC', '#BBDBB4', '#F5D3A6', '#8DB1B1', '#DAB7DB', '#E5C1C6', '#FBCBA4', '#B5D7EB']
fig, ax = plot_stack_bar(df_mjsp, 'MJSP [$/L]', colors, save_name=os.path.join(fig_folder, 'BO_mjsp'))
plot_pie_chart(df_mjsp.iloc[:,:-1], 'Utilities and Raw Materials Cost',
               save_name=os.path.join(fig_folder, 'BO_utils_and_rawmaterials'))
plot_pie_chart(df_equip_per_process.transpose(), None, save_name=os.path.join(fig_folder, 'BO_equipment'))
plot_pie_chart(df_equip_per_kind.transpose(), 'Installed Equipment Cost',
               save_name=os.path.join(fig_folder, 'BO_equipment_per_kind'),
               lgd_anchor=(.97, .95))

ur_exclude_idx = ['Biomass', 'Hydrogen gas', 'Electricity']
ur_fixed = df_util_and_rawmaterial_sum.loc[ur_exclude_idx]
ur_to_sort = df_util_and_rawmaterial_sum.drop(index=ur_exclude_idx)
ur_sorted = ur_to_sort.sort_values(by='Base', ascending=False)
ur_final = pd.concat([ur_fixed, ur_sorted])
plot_stack_bar(ur_final.transpose(), 'OPEX', colors,
               save_name=os.path.join(fig_folder, 'BO_opex'))

