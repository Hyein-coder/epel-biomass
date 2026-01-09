import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np

from funs import unit_cost_interpolation, catalyst_charging_cost, resume_cost_summary, cal_MJSP, \
    get_APEA_result, plot_stack_bar, plot_pie_chart, get_util_and_rawmaterial_items, get_equipment_breakdown

file_name = {
    'Stream': 'Process_Data\\Pyrolysis_541_JonesBaseCaseScale_Streams.xlsx',
    'APEA': 'Process_Data\\Pyrolysis_541_JonesBaseCaseScale_APEA.xlsm'
}

operation_hr = 8000

with open(file_name['Stream'], 'rb') as f:
    df_material = pd.read_excel(f, sheet_name='Material', header=3)
    df_work = pd.read_excel(f, sheet_name='Work', header=3)
    df_heat = pd.read_excel(f, sheet_name='Heat', header=3)

idx_material = {
    'mass flow [lb/hr]': 15,
    'vol flow [cuft/hr]': 157,
    'LHV at 15C [Btu/lb]': 174,
    'heat capacity [Btu/lb/R]': 467,
    'CO2': 23,
    'NO2': 32,
    'CH4': 24,
    'CO': 22
}
# Products
# name: cost
product_stream = {
    '316GAS': 0,  # $/LB
    '326SAF': 0,
    '336DIES': 0
}
product_work = {
    'ELECGEN': 6.89 / 100 * 293.07   # cent/kWh -> $/MMBTU
}

hourly_revenue = {}
energy_production = {}
for s, price in product_stream.items():
    mass_flow = df_material[s][idx_material['mass flow [lb/hr]']]
    hourly_revenue[s] = mass_flow * price   # $/hr

    lhv_15C = df_material[s][idx_material['LHV at 15C [Btu/lb]']]
    heat_capacity = df_material[s][idx_material['heat capacity [Btu/lb/R]']]
    dT_in_F = (25-15) * 5/9
    lhv_standard = lhv_15C + heat_capacity * dT_in_F
    energy_production_Btu_hr = lhv_standard * mass_flow
    energy_production_MW = energy_production_Btu_hr * 2.9307e-7
    energy_production[s] = energy_production_MW
energy_gge_btu = 116090   # BTU/gal
energy_gge_MWh = energy_gge_btu * 2.9307e-7     # MWh/gal

for s, price in product_work.items():
    energy_production_MMBtu_hr = - df_work[s][0] * 0.002544  # hp = 2544.434187 BTU/hr = 0.002544 MMBTU/hr
    hourly_revenue[s] = energy_production_MMBtu_hr * price   # $/hr
    energy_production[s] = energy_production_MMBtu_hr * 1e6 * 2.9307e-7  # MW
# ELECGEN -- 2608.3 kW

# In-out Streams
hydrogen_feed_stream = ['250H2', '532H2']
resource_flow = {
    'Water': df_material['700BFW'][idx_material['mass flow [lb/hr]']],
    'Gaseous hydrogen': sum([df_material[s][idx_material['mass flow [lb/hr]']] for s in hydrogen_feed_stream]),
    'Sulfur agent': sum([df_material[s][idx_material['mass flow [lb/hr]']] for s in ['262SLF', '263SLF']]),
    'Sand': df_material['122SND'][idx_material['mass flow [lb/hr]']],
    'Biomass feed': df_material['90BIO'][idx_material['mass flow [lb/hr]']]
}

emission_flow = {
    'CO2': 0, 'NO2': 0, 'CH4': 0, 'CO': 0
}
emission_gwp100_weight = {
    'CO2': 1, 'NO2': 0, 'CH4': 30, 'CO': 0
}
gwp100 = 0
emission_in = ['80AIR', '120AIR', '610AIR']
emission_out = ['699WWT', '691VENT']

for c in emission_flow.keys():
    emission_mass_flow_rate = 0

    for s_in in emission_in:
        emission_mass_flow_rate -= df_material[s_in][idx_material[c]]

    for s_out in emission_out:
        emission_mass_flow_rate += df_material[s_out][idx_material[c]]

    emission_flow[c] = emission_mass_flow_rate  # lb/hr
    gwp100 += emission_flow[c] * emission_gwp100_weight[c]

energy_production_sum_MW = sum([e for e in energy_production.values()])
gwp100_per_MJ = gwp100 / energy_production_sum_MW * 453.592 / 3600  # g CO2e/MJ fuel
#%% Unit Operations
# Heat Leftover
df_heat = df_heat.set_index('Stream Name')
col_heat_gen = df_heat.filter(like='-Q').columns
heat_gen = df_heat[col_heat_gen].loc['QCALC Btu/hr'].sum() / 1e6  # mmBtu/hr

bi_22to11 = 2250 / 3230
# Carbon Capture for Storage - Base case: Rao, 2022 - converted to 1Q-2022 base -> 2011 base
ccs_base_case = {
    'base stream': 862853,
    'total CAPEX': 297930841 * bi_22to11,
    'heat consumption [mmBTU/hr]': 3315
}

co2_seq = df_material['621CO2'][idx_material['mass flow [lb/hr]']]
ccs_now = unit_cost_interpolation(co2_seq, ccs_base_case)

fuel_price_usd_per_mmbtu = 5.1
ccs_now['annual OPEX'] = (ccs_now['heat consumption [mmBTU/hr]'] - heat_gen) * fuel_price_usd_per_mmbtu * operation_hr   # $/yr
ccs_now['utilities'] = ccs_now['annual OPEX']
ccs_now['utilities description'] = 'Fuel'
ccs_now['Category'] = 'Carbon Capture'

# PSA for H2 Separation - Base case: Byun, 2020 - converted to 1Q-2022 base
psa_base_case = {
    'base stream': 700, # m3/hr
    'total CAPEX': 780993 * bi_22to11,
    'annual OPEX': 5078 * bi_22to11
}

h2_recovery = df_material['604'][idx_material['vol flow [cuft/hr]']] * 0.02832
psa_now = unit_cost_interpolation(h2_recovery, psa_base_case)
psa_now['raw materials'] = psa_now['annual OPEX']   # 68% of OPEX is reactants cost
psa_now['raw materials description'] = 'Adsorbent'
psa_now['Category'] = 'Hydrogen Recovery'

# R510 - Base case: Jones, 2013
r510_base_case = {
    'base stream': 9600,
    'total CAPEX': 5266304 * bi_22to11
}

recycle_in_340 = df_material['340'][idx_material['mass flow [lb/hr]']]
r510_now = unit_cost_interpolation(recycle_in_340, r510_base_case)
r510_now['Category'] = 'Hydrocracking'

# Catalysts Charging

r202_Ru_info = {
    'LHSV': 0.5,
    'rare metal content': 1,
    'price': 60 * 2.2,     # USD/lb -> USD/kg
    'density': 2500      # kg/m3 (Carbon supported Ru-based catalysts), but not used
}
r202_cat_cost = catalyst_charging_cost(df_material['255'][idx_material['vol flow [cuft/hr]']], r202_Ru_info)

r220_Ru_info = {
    'LHSV': 0.5,
    'rare metal content': 1,
    'price': 60 * 2.2,     # USD/lb -> USD/kg
    'density': 2500      # kg/m3 (Carbon supported Ru-based catalysts), but not used
}
r220_cat_cost = catalyst_charging_cost(df_material['210'][idx_material['vol flow [cuft/hr]']], r220_Ru_info)

r225_Mo_info = {
    'LHSV': 0.22,
    'rare metal content': 1,
    'price': 15.5 * 2.2,     # USD/lb -> USD/kg
    'density': 5000      # kg/m3 (MoS2 catalysts), but not used
}
r225_cat_cost = catalyst_charging_cost(df_material['272'][idx_material['vol flow [cuft/hr]']], r225_Mo_info)

hydrotreat_catalysts = {
    'R-202': r202_cat_cost,
    'R-220': r220_cat_cost,
    'R-225': r225_cat_cost
}
hydrotreat_catalysts['total CAPEX'] = sum([c for c in hydrotreat_catalysts.values()])
hydrotreat_catalysts['Category'] = 'Hydrotreating'

#
with open(file_name['APEA'], 'rb') as f:
    df_prjsum = pd.read_excel(f, sheet_name='Project Summary', header=2)
    df_rawmaterial = pd.read_excel(f, sheet_name='RawMaterial Summary', header=2).dropna(how='all')

# Main process
main_now, main_opex = get_APEA_result(df_prjsum)

# Overall
processes = [main_now, ccs_now, psa_now, hydrotreat_catalysts, r510_now]
process_names = ['Main', 'CCS', 'PSA', 'Catalysts', 'R-510']
opex_names = [k for k in main_opex.keys()]

cost_summary, opex_summary, df_process = resume_cost_summary(processes, process_names, opex_names)

annual_prod_gge = sum([energy_production[s]/energy_gge_MWh*operation_hr for s in product_stream.keys()])    # gal/yr
mjsp_main, cost_summary, opex_summary = cal_MJSP(cost_summary, opex_summary, hourly_revenue, annual_prod_gge,
                                                 operation_hr)

df_main_h2 = df_rawmaterial.query("Description in " + str(hydrogen_feed_stream))
main_h2_demand = sum(df_main_h2['Rate per Hour'])  # lb/hr
main_h2_cost = sum(df_main_h2['Cost per Hour']) * operation_hr  # USD/yr

main_wo_h2 = main_now.copy()
main_wo_h2['annual OPEX'] -= main_h2_cost
main_wo_h2['raw materials'] -= main_h2_cost

#  SMR-CCS case
# SMR - Base case: Katebah, 2022, SMR with CCS
cost_idx_smr = 2340
cost_idx_1Q2022 = 3230
smr_base_case = {
    'base stream': 45922,
    'total CAPEX': 424e6 / cost_idx_smr * cost_idx_1Q2022 * bi_22to11,
    'annual OPEX': 147e6 / cost_idx_smr * cost_idx_1Q2022 * bi_22to11,
    'NG feed': 156136,
    'CO2 emission': 55107
}
smr_NG_price_US = 0.092306 / cost_idx_smr * cost_idx_1Q2022 * bi_22to11  # $/lb
smr_NG_price_JonesReport = 5.1 / 52.728   # $/lb

# smr_base_case['raw materials'] = smr_base_case['NG feed'] * smr_NG_price_US * operation_hr
# smr_base_case['utilities'] = smr_base_case['annual OPEX'] - smr_base_case['raw materials']

smr_base_NG_cost_US = smr_base_case['NG feed'] * smr_NG_price_US * operation_hr
smr_base_NG_cost_KR = smr_base_case['NG feed'] * smr_NG_price_JonesReport * operation_hr
smr_base_case['utilities'] = smr_base_case['annual OPEX'] - smr_base_NG_cost_US
smr_base_case['raw materials'] = smr_base_NG_cost_KR

smr_now = unit_cost_interpolation(main_h2_demand, smr_base_case)
smr_now['Category'] = 'SMR'
smr_now['raw materials description'] = 'Natural Gas'
smr_now['utilities description'] = 'Electricity'

processes_smr = [main_wo_h2, smr_now] + processes[1:]
process_names_smr = ['Main', 'SMR'] + process_names[1:]

cost_summary_smr, opex_summary_smr, df_process_smr = resume_cost_summary(processes_smr, process_names_smr, opex_names)
mjsp_smr, cost_summary_smr, opex_summary_smr = cal_MJSP(cost_summary_smr, opex_summary_smr, hourly_revenue,
                                                        annual_prod_gge, operation_hr)

#
df_summary = pd.DataFrame([opex_summary, opex_summary_smr])
df_summary.index = ['Base', 'SMR-CCS']
df_summary = df_summary.reindex(columns=['capital investment', 'raw materials', 'utilities',
                                         'operating labor', 'maintenance', 'operating charges',
                                         'plant overhead', 'G and A cost', 'co-product sales'])
df_summary.rename(columns={"G and A cost": "governance and admin."}, inplace=True)

df_mjsp = df_summary.map(lambda x: x / annual_prod_gge)
# colors = ['#DFFF00', '#9FE2BF', '#FFBF00', '#40E0D0', '#FF7F50', '#6495ED', '#DE3163', '#CCCCFF']
colors = ['#FAE8BC', '#F0B1AC', '#BBDBB4', '#F5D3A6', '#8DB1B1', '#DAB7DB', '#E5C1C6', '#FBCBA4', '#B5D7EB']

fig, ax = plot_stack_bar(df_mjsp, 'MFSP [$/gal GGE]', colors)

#
with open(file_name['APEA'], 'rb') as f:
    df_equipment = pd.read_excel(f, sheet_name='Equipment', header=2).dropna()
    df_util = pd.read_excel(f, sheet_name='Utility Summary', header=2).dropna(how='all')

unit_category = ['Feed', 'Pyrolysis', 'Hydrotreating', 'Product Finishing', '',
                 'Hydrocracking', 'Hydrogen Recovery', 'Balance of Plant (Steam)']
df_util['Category'] = df_util['Item Description'].apply(lambda x: unit_category[int(x.split('-')[1][0])])

rule_rawmaterial = lambda x: int(x[0]) if int(x[0]) < len(unit_category) else 0
df_rawmaterial['Category'] = df_rawmaterial['Description'].apply(lambda x: unit_category[rule_rawmaterial(x)])

# Equipment Summary
df_all_case = [df_process, df_process_smr]
case_name = ['Base', 'SMR']

df_equip_sum, _ = get_equipment_breakdown(df_all_case, case_name, df_equipment, unit_category)
plot_pie_chart(df_equip_sum.transpose(), 'Installed Equipment Cost')

#%%
df_util_and_rawmaterial_sum = get_util_and_rawmaterial_items(df_all_case, case_name, df_util, df_rawmaterial,
                                                             operation_hr)
plot_pie_chart(df_util_and_rawmaterial_sum.transpose(), 'Raw Materials and\n Utilities Cost', (0.93, 0.9))
