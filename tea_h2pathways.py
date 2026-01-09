import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import os

from funs import TEA
from plotting import plot_stack_bar, plot_pie_chart

tea = TEA()
file_name = {
    'Stream': 'Process_Data\\Pyrolysis_551_Scale0010_Streams.xlsx',
    'APEA': 'Process_Data\\Pyrolysis_551_Scale0010_APEA.xlsm',
}
# file_name = {
#     'Stream': os.path.join(os.getcwd(), 'Process_Data\\Pyrolysis_Jones_572_2MC_0010_Streams.xlsx'),
#     'APEA': os.path.join(os.getcwd(), 'Process_Data\\Pyrolysis_Jones_572_2MC_0010_APEAresults.xlsm')
# }
h2_source = ['Base', 'SMR', 'Ammonia', 'PEM']
name_for_h2_source = ['Base', 'BH', 'Ammonia', 'PEM']

fig_folder = os.path.join(os.getcwd(), 'Figure')
ccs_portion = 0.
if not os.path.exists(fig_folder):
    os.makedirs(fig_folder)

df_mjsp, energy_production, annual_prod_saf, main_h2_demand, opex_names, data_all, h2_source = \
    tea.economic_analysis(file_name['Stream'], file_name['APEA'], h2_source, ccs_portion=ccs_portion,
                          ammonia_portion=.5)
dfp_per_h2_source = data_all['df_process']
if len(h2_source) > len(name_for_h2_source):
    name_for_h2_source.append(h2_source[-1])

#%%
df_mjsp.index = name_for_h2_source
colors = ['#FAE8BC', '#F0B1AC', '#BBDBB4', '#F5D3A6', '#8DB1B1', '#DAB7DB', '#E5C1C6', '#FBCBA4', '#B5D7EB']
fig, ax = plot_stack_bar(df_mjsp, 'MJSP [$/L]', colors, save_name=os.path.join(fig_folder, 'mjsp'))

df_equip_sum, df_equip_all_case = tea.get_equipment_breakdown(file_name['APEA'], dfp_per_h2_source, name_for_h2_source)
plot_pie_chart(df_equip_sum.transpose(), None, save_name=os.path.join(fig_folder, 'equipment'))

df_util_and_rawmaterial_sum, df_util_and_rawmaterial_rate = \
    tea.get_util_and_rawmaterial_sum(file_name['APEA'], dfp_per_h2_source, name_for_h2_source)
ur_exclude_idx = ['Biomass', 'Hydrogen gas', 'Electricity']
ur_fixed = df_util_and_rawmaterial_sum.loc[ur_exclude_idx]
ur_to_sort = df_util_and_rawmaterial_sum.drop(index=ur_exclude_idx)
ur_sorted = ur_to_sort.sort_values(by='Base', ascending=False)
ur_final = pd.concat([ur_fixed, ur_sorted])
plot_pie_chart(ur_final.transpose(), None, (0.93, 0.9),
               save_name=os.path.join(fig_folder, 'opex'), fix_order=True)

# LCOH of subunits
lcoh_smr, _, _ = tea.get_LCOH('SMR', main_h2_demand, opex_names)
lcoh_ammonia, _, _ = tea.get_LCOH('Ammonia', main_h2_demand, opex_names)
lcoh_pem, _, _ = tea.get_LCOH('PEM', main_h2_demand, opex_names)

#%%
emission_flow, captured_flow = tea.get_emission_flow(file_name['Stream'], ccs_portion=ccs_portion)

with open(file_name['Stream'], 'rb') as f:
    df_material = pd.read_excel(f, sheet_name='Material', header=3)
idx_material = tea.get_idx_material(df_material)
hourly_revenue, energy_production_in_MW, mass_production = tea.get_fuel_products(df_material, idx_material)
saf_prod_MJph = energy_production_in_MW['326SAF'] * 3600
emission_lb_MJ = {k: v / saf_prod_MJph for k, v in emission_flow.items()}

#%%
materials_order = [
    'Biomass', 'Water', 'Sand', 'Sulfiding agent', 'Hydrogen gas', 'Natural Gas', 'Ammonia', 'Electricity', 'Fuel',
    'MP steam', 'LP steam'
]

df_util_and_rawmaterial_rate_reordered = df_util_and_rawmaterial_rate.loc[materials_order]
numeric_cols = df_util_and_rawmaterial_rate_reordered.columns.difference(['Rate Units'])
for c in ['Biomass', 'Hydrogen gas', 'Natural Gas', 'Ammonia']:
    df_util_and_rawmaterial_rate_reordered.loc[c, numeric_cols] = df_util_and_rawmaterial_rate_reordered.loc[c, numeric_cols] / 2000
    df_util_and_rawmaterial_rate_reordered.loc[c, 'Rate Units'] = 'tons/H'
for c in ['MP steam', 'LP steam']:
    df_util_and_rawmaterial_rate_reordered.loc[c, numeric_cols] = df_util_and_rawmaterial_rate_reordered.loc[c, numeric_cols] / 1000000
    df_util_and_rawmaterial_rate_reordered.loc[c, 'Rate Units'] = 'MMBTU/H'

df_util_and_rawmaterial_rate_reordered.loc['Electricity', numeric_cols] = df_util_and_rawmaterial_rate_reordered.loc['Electricity', numeric_cols]/1000
df_util_and_rawmaterial_rate_reordered.loc['Electricity', 'Rate Units'] = 'MW'

hourly_revenue_fuel, energy_production_fuel, mass_production = tea.get_fuel_products(df_material, idx_material)

mass_ton_production = {k: v/2000 for k, v in mass_production.items()}
with open(file_name['Stream'], 'rb') as f:
    df_work = pd.read_excel(f, sheet_name='Work', header=3)
hourly_revenue_work, energy_production_work = tea.get_work_products(df_work)

#%%
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

for c in ['Biomass', 'Water', 'BFW', 'Hydrogen gas', 'Ammonia']:
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
capex = pd.DataFrame([c['total CAPEX']/1e6 for c in data_all['cost']], index=h2_source, columns=['CAPEX']).transpose()
opex = pd.DataFrame(data_all['opex'], index=h2_source).transpose()
opex_million = opex.apply(lambda x: x/1e6)
capex_and_opex = pd.concat([capex, opex_million])
capex_and_opex.to_excel(os.path.join(fig_folder, 'TEA_summary.xlsx'))

