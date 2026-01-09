import pandas as pd
from funs import TEA
import matplotlib.pyplot as plt


case_scale = [1, 2.5, 5, 7.5, 10, 20]
tea = TEA()

#  Ammonia Cracking Base Case
with open('Process_Data\\NH3_Cracking_126_FinalComp_APEAresult.xlsm', 'rb') as f:
    df_base_prjsum = pd.read_excel(f, sheet_name='Project Summary', header=2)
    df_ammonia_equipment = pd.read_excel(f, sheet_name='Equipment', header=2)
    df_ammonia_util = pd.read_excel(f, sheet_name='Utility Summary', header=2)
    df_ammonia_rawmaterial = pd.read_excel(f, sheet_name='RawMaterial Summary', header=2)

base_sum, base_opex = tea.get_APEA_result(df_base_prjsum)
base_sum['scale'] = 1
base_opex['scale'] = 1

case_summary = {key: [] for key in base_sum.keys()}
case_opex = {key: [] for key in base_opex.keys()}
case_ammonia_demand = []
case_ammonia_cost = []
for c in case_scale:
    sum, fertilizer_sales, opex, ammonia_demand, ammonia_cost, _ = tea.get_ammonia_cost_at_scale(c)
    sum['scale'] = c
    opex['scale'] = c

    for key in case_summary.keys():
        case_summary[key].append(sum[key])

    for key in case_opex.keys():
        case_opex[key].append(opex[key])

    case_ammonia_demand.append(ammonia_demand)
    case_ammonia_cost.append(ammonia_cost)


case_summary = pd.DataFrame(case_summary)
case_opex = pd.DataFrame(case_opex)

#%%
""" It has economy of scale, but linear property. """
fig, ax = plt.subplots(1, 2, figsize=(9, 5))

ax[0].plot(case_summary['scale'], case_summary['total CAPEX'], marker='o', linestyle='-')
ax[0].plot(case_summary['scale'],
           [case_summary['total CAPEX'].iloc[0] * scale for scale in case_summary['scale'].tolist()],
           linestyle='-', color='#3b3b3b')

ax[0].grid(True, linestyle='--', alpha=0.7)
ax[0].set_xlabel("Scale of Plant")
ax[0].set_ylabel("Total CAPEX [USD]")

ax[1].plot(case_summary['scale'], case_summary['annual OPEX'], marker='o', linestyle='-')
ax[1].plot(case_summary['scale'],
           [case_summary['annual OPEX'].iloc[0] * scale for scale in case_summary['scale'].tolist()],
           linestyle='-', color='#3b3b3b')

ax[1].grid(True, linestyle='--', alpha=0.7)
ax[1].set_xlabel("Scale of Plant")
ax[1].set_ylabel("Annual OPEX [USD/year]")

plt.subplots_adjust(wspace=.3)

plt.show()
plt.close()

#%%
# plt.plot(case_opex['scale'], case_opex['raw materials'], '-o', label='Prj Sheet')
# plt.plot(case_opex['scale'], [case_opex['raw materials'].iloc[0] * scale for scale in case_opex['scale'].tolist()],
#          linestyle='-', color='#3b3b3b')
# plt.grid(True, linestyle='--', alpha=0.7)
# plt.xlabel('Scale of Plant')
# plt.ylabel('Raw Materials [USD/year]')
# plt.show()
#
case_ammonia_demand_lbmol = [d / 17 for d in case_ammonia_demand]
plt.plot(case_scale, case_ammonia_demand_lbmol, '-o', label='Prj Sheet')
plt.plot(case_scale, [case_ammonia_demand_lbmol[0] * scale for scale in case_scale],
         linestyle='-', color='#3b3b3b')
plt.grid(True, linestyle='--', alpha=0.7)
plt.xlabel('Scale of Plant')
plt.ylabel('Ammonia Feed [lbmol/hr]')
plt.show()

plt.plot(case_scale, case_ammonia_cost, '-o', label='Prj Sheet')
plt.plot(case_scale, [case_ammonia_cost[0] * scale for scale in case_scale],
         linestyle='-', color='#3b3b3b')
plt.grid(True, linestyle='--', alpha=0.7)
plt.xlabel('Scale of Plant')
plt.ylabel('Ammonia Cost [USD/hr]')
plt.show()


#%%

case_scale = [1, 2.5, 5, 7.5, 10, 20, 30]
df_mjsp, energy_production, annual_prod_saf, main_h2_demand, opex_names, data_all, _ = \
    tea.economic_analysis(
        'Process_Data\\Pyrolysis_551_Scale0010_Streams.xlsx',
        'Process_Data\\Pyrolysis_551_Scale0010_APEA.xlsm',
        ['Base']
    )

case_lcoh = []
for scale in case_scale:
    lcoh_ammonia, _, _ = tea.get_LCOH('Ammonia', main_h2_demand * scale, opex_names)
    case_lcoh.append(lcoh_ammonia)
#%%
params = {
    'legend.fontsize': 'x-large',
    'axes.labelsize': 'x-large',
    'axes.titlesize': 'xx-large',
    'xtick.labelsize': 'x-large',
    'ytick.labelsize': 'x-large'}
plt.rcParams.update(params)

fig, ax = plt.subplots(figsize=(5, 6))
plt.plot(case_scale, case_lcoh, '-o', color='#3f75a2', label='Ammonia Cracking')
plt.axhline(0.68, linestyle='-.', color='black', label='Grey Hydrogen')
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend()
plt.xlabel('Scale of Plant')
plt.ylabel('LCOH [USD/kg H2]')
plt.tight_layout()
plt.show()
