"""
Solve optimization problem based on CAPEX
"""
import pandas as pd

from funs_lca import get_WTWa_pyrolysis
from Dynamic_LCA.funs_dLCA import define_traj, get_dlca_full_operation, get_emission_target,\
    build_model_PyroOperation, build_model_PyroCashflow, build_model_PyroMinEmission, solve_model, policy_scale
import matplotlib.pyplot as plt
import numpy as np
import pyomo.environ as pyo
import os

#%%
timeframe = 25
timegap = 0
forest_period = 12

file_wtwa = '..\\Process_Data\\WTWa_LCA.xlsx'
file_name = '..\\Process_Data\\Pyrolysis_551_LCA_Allocation.xlsx'
saf_prod = 11413.86104 * 20038.63661 * 1055.06/1e6  # LB/hr * BTU/lb * J/BTU -> MJ

target = get_emission_target(file_wtwa)     # g/MJ
lca_case = get_WTWa_pyrolysis('Base', file_name, file_wtwa)
wtwa_emission = lca_case['WTWa']['CO2']
wtwa_biogenic = lca_case['WTWa']['CO2_Biogenic']

emission = {'val': wtwa_emission, 'lifetime': 20}
sequestration = {'val': -wtwa_biogenic / forest_period, 'duration': forest_period}
ramping_rate = None
plant, traj_emission, traj_sequester = define_traj(timeframe, timegap, emission, sequestration)  # g/MJ/yr
traj_DLCA_full_operation = get_dlca_full_operation(traj_emission, traj_sequester, timeframe)

model_max_cashflow = build_model_PyroCashflow(timeframe, timegap, emission, sequestration,
                                              total_target=target, ramping_rate=ramping_rate)
res_max_cashflow = solve_model(model_max_cashflow)

model_max_operation = build_model_PyroOperation(timeframe, timegap, emission, sequestration,
                                                total_target=target, ramping_rate=ramping_rate,
                                                fix_capacity=pyo.value(model_max_cashflow.capacity))
res_max_operation = solve_model(model_max_operation)

model_min_emission = build_model_PyroMinEmission(timeframe, timegap, emission, sequestration,
                                                 fix_capacity=pyo.value(model_max_cashflow.capacity))
res_min_emission = solve_model(model_min_emission)

names = ['MaxProfit', 'MaxOperation', 'MinEmission']
models = [model_max_cashflow, model_max_operation, model_min_emission]
results = [res_max_cashflow, res_max_operation, res_min_emission]

# Show results
for n, r in zip(names, results):
    if r is not None:
        print(f'[{n}]: {str(r.solver.Message)}')
# print(f'capacity: [DLCA] {pyo.value(model_DLCA.capacity):.1f} [Static] {pyo.value(model_Static.capacity):.1f}')
summary = {
    'Capacity': [pyo.value(m.capacity) for m in models],
    'Profit': [sum([pyo.value(m.cashflow[k]) for k in m.T]) for m in models],
    'GWP': [pyo.value(m.total_StaticLCA) for m in models],
    'TDGWP': [pyo.value(m.total_DLCA) for m in models]
}
df_summary = pd.DataFrame(summary, index=names)
print(df_summary)

opt_schedule_operation = {}
opt_cost_fixed = {}
opt_cost_variable = {}
opt_sales = {}
opt_cashflow = {}
opt_traj_emission = {}
opt_traj_DLCA = {}
opt_traj_DLCA_tpy = {}
opt_traj_StaticGWP = {}
opt_penetration = {}

params = {
    'legend.fontsize': 'medium',
    'axes.labelsize': 'x-large',
    'axes.titlesize': 'xx-large',
    'xtick.labelsize': 'x-large',
    'ytick.labelsize': 'x-large'}
plt.rcParams.update(params)

for name, model in zip(names, models):
    opt_schedule_operation[name] = [pyo.value(model.schedule_operation[k]) for k in model.T]
    opt_traj_emission[name] = [traj_emission[k] * opt_schedule_operation[name][k] for k in range(timeframe)]
    opt_traj_DLCA[name] = [pyo.value(model.traj_DLCA[k]) for k in model.T]
    opt_traj_DLCA_tpy[name] = [pyo.value(model.traj_DLCA[k]) * saf_prod/1e6 for k in model.T]
    opt_traj_StaticGWP[name] = [pyo.value(model.traj_net[k]) for k in model.T]

    opt_cost_fixed[name] = [pyo.value(model.cost_fixed[k])/1e9 for k in model.T_opt]
    opt_cost_variable[name] = [pyo.value(model.cost_variable[k])/1e9 for k in model.T_opt]
    opt_sales[name] = [pyo.value(model.sales[k])/1e9 for k in model.T_opt]
    opt_cashflow[name] = [pyo.value(model.cashflow[k])/1e9 for k in model.T_opt]
    opt_penetration[name] = [pyo.value(model.penetration[k]) for k in model.T_opt]

#%%
# for c in model_max_cashflow.component_objects(pyo.Constraint, active=True):
#     print("Constraint:", c)
#     for index in c:
#         con = c[index]
#         print("  Index:", index)
#         print("    Lower:", con.lower() if con.lower is not None else con.lower)
#         print("    Value:", pyo.value(con.body))
#         print("    Upper:", con.upper() if con.upper is not None else con.upper)

#%%
fig, ax = plt.subplots(figsize=(12, 5))
color_minus = ['#0077b6', '#ee9b00', '#588157']
color_plus = ['#023e8a', '#ca6702', '#3a5a40']
style_traj = ['--', ':', '-.']
color_traj = ['#03045e', '#432818', '#344e41']
offset_models = [0, 0.15, 0.3]
markers_traj = ['o', '^', '*']

for idx, name in enumerate(names):
    ax.bar([k + offset_models[idx] for k in range(timeframe)], opt_traj_emission[name], width=0.2,
           label=f'[{name}] Emission', align='center', color=color_minus[idx])
    ax.bar([k + offset_models[idx] for k in range(timeframe)], traj_sequester, width=0.2,
           label=f'[{name}] Sequestration', align='edge', color=color_plus[idx])
ax.set_xlabel('Year')
ax.set_ylabel(r'Emission profile [tonne CO$_2$e/yr]')
ax.legend(loc='lower right')

ax2 = ax.twinx()
for idx, name in enumerate(names):
    ax2.plot([k + offset_models[idx] for k in range(timeframe)], np.cumsum(opt_traj_DLCA[name]),
             color=color_traj[idx], linestyle=style_traj[idx], label=name)
ax2.set_ylabel(r'Cumulative TDGWP [g CO$_2$e/MJ]')
ax2.axhline(target, color='red', linewidth=0.8, label='SAF Target')
ax2.legend(loc='upper right')
ax2.grid(axis='both', linestyle=':', alpha=0.7)
# ax2.set_ylim([-270, 350])
plt.tight_layout()
plt.savefig(os.path.join(os.getcwd(), 'Figure', 'DLCA_opt_pyro_cost_Emission.eps'))
plt.savefig(os.path.join(os.getcwd(), 'Figure', 'DLCA_opt_pyro_cost_Emission.png'))
plt.show()

fig, ax3 = plt.subplots()
ax4 = ax3.twinx()
for idx, name in enumerate(names):
    fc = opt_cost_fixed[name]
    vc = opt_cost_variable[name]
    ax3.bar([k + offset_models[idx] for k in range(emission['lifetime'])], [-(f+v) for f, v in zip(fc, vc)],
            width=0.3, align='edge',
            label=f'[{name}] Expense', color=color_minus[idx])
    ax3.bar([k + offset_models[idx] for k in range(emission['lifetime'])], opt_sales[name],
            width=0.3, align='center',
            label=f'[{name}] Revenue', color=color_plus[idx])
    ax4.plot([k + offset_models[idx] for k in range(emission['lifetime'])], np.cumsum(opt_cashflow[name]),
             color=color_traj[idx], linestyle=style_traj[idx], label=name)
ax3.set_ylabel('Annual Expense / Revenue [B$]')
ax3.legend(loc='upper left')
ax4.set_ylabel(r'Cumulative Cashflow [B$]')
ax4.grid(axis='both', linestyle=':', alpha=0.7)
ax4.legend(loc='lower right')
plt.tight_layout()

plt.savefig(os.path.join(os.getcwd(), 'Figure', 'DLCA_opt_pyro_cost_Cashflow.eps'))
plt.savefig(os.path.join(os.getcwd(), 'Figure', 'DLCA_opt_pyro_cost_Cashflow.png'))
plt.show()

#%% MaxOp = MaxCash
fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharex=True)
offset_models = [0, 0.3]
ax_twin = axes[1].twinx()
for idx, name in enumerate(['MaxProfit', 'MaxOperation']):
    axes[1].bar([2025 + k + offset_models[idx] for k in range(emission['lifetime'])], opt_cashflow[name],
                width=0.4, color=color_minus[idx], label=name)
    ax_twin.step([2025 + k + offset_models[idx] for k in range(timeframe)], opt_schedule_operation[name],
                 color=color_plus[idx], label=name)
    axes[0].step([2025 + k + offset_models[idx] for k in range(timeframe)], opt_traj_DLCA_tpy[name], color=color_plus[idx],
                 label=f'{name}')
axes[1].set_xlabel('Year')
axes[1].set_ylabel('Annual Cashflow [B$/yr]')
axes[1].grid(axis='y', linestyle=':')
axes[1].legend(loc='upper left', title='Cashflow')
ax_twin.set_ylabel('Fractional Operation Rate')
ax_twin.legend(loc='upper left', title='Operation rate', bbox_to_anchor=(0., .8))

axes[0].set_xlabel('Year')
axes[0].set_ylabel('TDGWP [tonne CO2e/yr]')
axes[0].grid(axis='both', linestyle=':')
axes[0].legend()
plt.tight_layout()

plt.savefig(os.path.join(os.getcwd(), 'Figure', 'DLCA_maxop_maxcash.eps'))
plt.savefig(os.path.join(os.getcwd(), 'Figure', 'DLCA_maxop_maxcash.png'))
plt.show()

#%%
fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharex=True)
offset_models = [0, 0.3]
ax_twin = axes[1].twinx()
for idx, name in enumerate(['MaxProfit', 'MinEmission']):
    axes[1].bar([2025 + k + offset_models[idx] for k in range(emission['lifetime'])], opt_cashflow[name],
                width=0.4, color=color_minus[idx+1], label=name)
    ax_twin.step([2025 + k + offset_models[idx] for k in range(timeframe)], opt_schedule_operation[name],
                 color=color_plus[idx+1], label=name)
    axes[0].step([2025 + k + offset_models[idx] for k in range(timeframe)], opt_traj_DLCA_tpy[name],
                 color=color_plus[idx+1],
                 label=f'{name}')
axes[1].set_xlabel('Year')
axes[1].set_ylabel('Annual Cashflow [B$/yr]')
axes[1].grid(axis='y', linestyle=':')
axes[1].legend(loc='upper left', title='Cashflow')
policy_scale[25] = policy_scale[15]
ax_twin.step([2025 + k + offset_models[-1] for k in policy_scale.keys()],
             [v/pyo.value(model_max_cashflow.capacity) for v in policy_scale.values()],
             linestyle='--', color='red')
ax_twin.set_ylabel('Fractional Operation Rate')
ax_twin.legend(loc='upper left', title='Operation rate', bbox_to_anchor=(0., .8))
ax_twin.set_xlim([2024, 2046])

axes[0].set_xlabel('Year')
axes[0].set_ylabel('TDGWP [tonne CO2e/yr]')
axes[0].grid(axis='both', linestyle=':')
axes[0].legend()
plt.tight_layout()

plt.savefig(os.path.join(os.getcwd(), 'Figure', 'DLCA_maxcash_minemission.eps'))
plt.savefig(os.path.join(os.getcwd(), 'Figure', 'DLCA_maxcash_minemission.png'))
plt.show()
