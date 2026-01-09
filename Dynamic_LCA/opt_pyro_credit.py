import pandas as pd

from funs_lca import get_WTWa_pyrolysis
from Dynamic_LCA.funs_dLCA import define_traj, get_dlca_full_operation, get_emission_target,\
    solve_model, build_model_PyroCashflow, DLCA
import matplotlib.pyplot as plt
import numpy as np
import pyomo.environ as pyo
import os
import datetime

timeframe = 25
timegap = 0
forest_period = 12
credit_price = 70*5

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

f_list = [-10, -9, -8, -7, -6, -5, -2, -1, -0.1, 0.1, 0.5, 1, 2, 5, 7, 10, 20]
# f_minus = [-f for f in f_list]
targets = []
results = []
for t in [target * f for f in f_list]:
    m = build_model_PyroCashflow(timeframe, timegap, emission, sequestration,
                                 total_target=t, apply_policy=True, saf_target=target, credit_price=credit_price)
    r = solve_model(m)
    results.append((m, r))
    targets.append(t)

def get_stat(sol_res):
    message = str(sol_res.solver.Message)
    if 'Optimal Solution Found' in message:
        stat = 1
    elif 'locally infeasible point' in message:
        stat = -1
    else:
        stat = -2
    return stat

res_DLCA = [pyo.value(m.total_DLCA) for m, _ in results]
res_profit = [pyo.value(m.total_cashflow) for m, _ in results]
res_credit = [sum([pyo.value(m.credit[k]) for k in m.T]) for m, _ in results]
res_stat = [get_stat(r) for _, r in results]
res_capacity = [pyo.value(m.capacity) for m, _ in results]

#%%
idx_valid = [i for i, s in enumerate(res_stat) if s > 0]
def get_by_indices(l, indices):
    return [l[i] for i in indices]

plt.plot(get_by_indices(res_DLCA, idx_valid), get_by_indices(res_profit, idx_valid), 'o', label='NPV')
plt.plot(get_by_indices(res_DLCA, idx_valid), get_by_indices(res_credit, idx_valid), 'o', label='Carbon credit')
plt.plot(get_by_indices(res_DLCA, idx_valid), [res_profit[i] - res_credit[i] for i in idx_valid], 'o', label='The rest')
plt.xlabel("Emission rate")
plt.grid(alpha=0.6)
plt.legend()
plt.show()

# plt.plot(res_DLCA, res_capacity, 'o')
# plt.ylabel("Capacity")
# plt.show()

#%%
opt_time = {}
opt_schedule_operation = {}
opt_traj_DLCA = {}
opt_traj_DLCA_long = {}
opt_traj_StaticGWP = {}
dlca_long = DLCA(timeframe)
opt_traj_cashflow = {}
opt_traj_credit = {}

offset_models = [0, 0.3]
for name, mr in zip(targets, results):
    model, r = mr
    opt_time[name] = [2025 + k for k in model.T]
    opt_schedule_operation[name] = [pyo.value(model.schedule_operation[k]) for k in model.T]
    opt_traj_DLCA[name] = [pyo.value(model.traj_DLCA[k]) for k in model.T]
    opt_traj_DLCA_long[name] = [pyo.value(model.traj_net[k]) * dlca_long.dGWP_density_CO2(k) for k in model.T]
    opt_traj_StaticGWP[name] = [pyo.value(model.traj_net[k]) for k in model.T]
    opt_traj_cashflow[name] = [pyo.value(model.cashflow[k]) for k in model.T]
    opt_traj_credit[name] = [pyo.value(model.credit[k]) for k in model.T]
summary_tf = pd.DataFrame({
    'Productivity': [sum(opt_schedule_operation[name])/emission['lifetime'] for name in targets],
    '2050': [sum(opt_traj_DLCA_long[name]) for name in targets],
})
print(summary_tf)

target_draw = [targets[idx_valid[0]], targets[idx_valid[2]]]

fig, ax_all = plt.subplots(1, 2, figsize=(12,5))
color_emission = ['#727272', '#a3a3a3']
color_sequester = ['#38761d', '#739f60']
style_traj = ['--', '-.']
color_traj = ['black', 'blue']
ax = ax_all[0]
for idx, name in enumerate(target_draw):
    ax.bar([k + offset_models[idx] for k in opt_time[name]], opt_schedule_operation[name], width=0.4,
           label=f'{name:.0f}', align='center', color=color_emission[idx])
ax.set_xlabel('Year')
ax.set_ylabel(r'Fractional Operation')
ax.legend(loc='upper left', title='Operation')

ax2 = ax.twinx()
for idx, name in enumerate(target_draw):
    ax2.plot([2025 + k + offset_models[idx] for k in range(timeframe)], np.cumsum(opt_traj_StaticGWP[name]) * saf_prod/1e6,
             color=color_traj[idx], linestyle=style_traj[idx], label=f'{name:.0f}')
ax2.set_ylabel(r'Static GWP Emission [tonne CO$_2$e]')
ax2.axhline(target * saf_prod/1e6, color='red', linewidth=0.8, label='SAF Target')
ax2.legend(loc='upper left', title='Emission', bbox_to_anchor=(0.0,0.8))
ax2.grid(axis='both', linestyle=':', alpha=0.7)
# ax2.set_ylim([-270, 350])

ax3 = ax_all[1]
for idx, name in enumerate(target_draw):
    ax3.plot([k + offset_models[idx] for k in opt_time[name]], opt_traj_cashflow[name],
            color=color_traj[idx], linestyle=style_traj[idx], marker='o', label=f'{name:.0f} Cashflow')
    ax3.bar([k + offset_models[idx] for k in opt_time[name]], opt_traj_credit[name], width=0.4, align='center',
            color=color_traj[idx], label=f'{name:.0f} Carbon Credit')
ax3.set_ylabel(r'[USD/yr]')
ax3.legend()
ax3.grid(axis='both', alpha=0.7)

plt.tight_layout()
# plt.xlim([2025-3, 2025+27])

plt.savefig(os.path.join(os.getcwd(), 'Figure', 'DLCA_opt_pyro_credit.png'))
plt.savefig(os.path.join(os.getcwd(), 'Figure', 'DLCA_opt_pyro_credit.eps'))
plt.show()
