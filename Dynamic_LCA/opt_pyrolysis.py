"""
Solve optimization problem from DLCA method
"""
import pandas as pd

from funs_lca import get_WTWa_conventional, get_WTWa_ftjet, get_WTWa_pyrolysis
from funs_dLCA import define_traj, build_model_DLCA, build_model_Static, solve_model, get_dlca_full_operation, DLCA
import matplotlib.pyplot as plt
import numpy as np
import pyomo.environ as pyo
import os

timeframe = 100
tf_short = 25
timegap = 5
forest_period = 12

# lb2g = 453.592
# emission = {'val': 211.5754, 'lifetime': 30}
# sequestration = {'val': 130.975 / 12, 'duration': 12}
# emission_target = emission['val'] - sequestration['val'] * 12

file_wtwa = '..\\Process_Data\\WTWa_LCA.xlsx'
file_name = '..\\Process_Data\\Pyrolysis_551_LCA_Allocation.xlsx'
saf_prod = 11413.86104 * 20038.63661 * 1055.06/1e6  # LB/hr * BTU/lb * J/BTU -> MJ

lca_conventional = get_WTWa_conventional(file_wtwa)
lca_ftjet = get_WTWa_ftjet(file_wtwa)
lca_total = {'Conventional': lca_conventional, 'FTjet': lca_ftjet}

biogen_carb_ptwa = lca_ftjet['PTWa']['CO2_Biogenic']
lca_biogen_carb = {'Conventional': lca_conventional['PTWa']['CO2_Biogenic'],
                   'FTjet': lca_ftjet['WTWa']['CO2_Biogenic']}

h2_source = ['Base', 'SMR', 'Ammonia', 'PEM']
name_for_h2 = ['Base', 'SMRB', 'Ammonia', 'PEM']

for k, case in enumerate(h2_source):
    lca_case = get_WTWa_pyrolysis(case, file_name, file_wtwa)
    lca_total[name_for_h2[k]] = lca_case

    biogen_carb_wtp = lca_case['WTP']['CO2_Biogenic']
    biogen_carb_wtwa = biogen_carb_wtp + biogen_carb_ptwa
    lca_biogen_carb[case] = biogen_carb_wtwa

#%%
case = 'Base'
emission = {'val': lca_total[case]['WTWa']['CO2']*saf_prod/1e6, 'lifetime': 20}     # g -> tonne
sequestration = {'val': -lca_total[case]['WTWa']['CO2_Biogenic']*saf_prod/1e6/forest_period, 'duration': forest_period}

emission_target = 0.9 * lca_total['Conventional']['WTWa']['GHG-100']*saf_prod/1e6
emission_target_bio = (lca_total[case]['WTWa']['CO2'] + lca_total[case]['WTWa']['CO2_Biogenic'])*saf_prod/1e6

ramping_rate = 0.3
plant, traj_emission_long, traj_sequester = define_traj(timeframe, timegap, emission, sequestration)
traj_DLCA_full_operation = get_dlca_full_operation(traj_emission_long, traj_sequester, timeframe)

model_DLCA = build_model_DLCA(timeframe, timegap, emission, sequestration, total_target=emission_target,
                              ramping_rate=ramping_rate)
model_Static = build_model_DLCA(tf_short, timegap, emission, sequestration, total_target=emission_target,
                                  ramping_rate=ramping_rate)
res_DLCA = solve_model(model_DLCA)
res_Static = solve_model(model_Static)

model_full = build_model_Static(timeframe, timegap, emission, sequestration)
for k in model_full.T:
    model_full.schedule_opt[k].set_value(1)

# Show results
for k in model_DLCA.T_opt:
    print(f'schedule_operation[{k}]: [DLCA] {pyo.value(model_DLCA.schedule_opt[k]):.2f} [Static] {pyo.value(model_Static.schedule_opt[k]):.2f}')
summary = {
    'Productivity': [pyo.value(m.max_operation)/emission['lifetime'] for m in [model_DLCA, model_Static, model_full]],
    'GWP': [pyo.value(m.total_StaticLCA) for m in [model_DLCA, model_Static, model_full]],
    'TDGWP': [pyo.value(m.total_DLCA) for m in [model_DLCA, model_Static, model_full]]
}
print(pd.DataFrame(summary, index=['DLCA', 'Static', 'Full']))
print(f'[DLCA]: {res_DLCA.solver.Message}')
print(f'[Static]: {res_Static.solver.Message}')
#%%
opt_time = {}
opt_schedule_operation = {}
opt_traj_DLCA = {}
opt_traj_DLCA_long = {}
opt_traj_DLCA_short = {}
opt_traj_StaticGWP = {}
dlca_long = DLCA(timeframe)
dlca_short = DLCA(tf_short)

params = {
    'legend.fontsize': 'medium',
    'axes.labelsize': 'x-large',
    'axes.titlesize': 'xx-large',
    'xtick.labelsize': 'x-large',
    'ytick.labelsize': 'x-large'}
plt.rcParams.update(params)

name_models = ['100 years', '25 years', 'full']
offset_models = [0, 0.3]
for name, model in zip(name_models, [model_DLCA, model_Static, model_full]):
    opt_time[name] = [2025 + k for k in model.T]
    opt_schedule_operation[name] = [pyo.value(model.schedule_operation[k]) for k in model.T]
    opt_traj_DLCA[name] = [pyo.value(model.traj_DLCA[k]) for k in model.T]
    opt_traj_DLCA_long[name] = [pyo.value(model.traj_net[k]) * dlca_long.dGWP_density_CO2(k) for k in model.T]
    opt_traj_DLCA_short[name] = [pyo.value(model.traj_net[k]) * dlca_short.dGWP_density_CO2(k) for k in range(tf_short)]
    opt_traj_StaticGWP[name] = [pyo.value(model.traj_net[k]) for k in model.T]
summary_tf = pd.DataFrame({
    'Productivity': [sum(opt_schedule_operation[name])/emission['lifetime'] for name in name_models],
    '2050': [sum(opt_traj_DLCA_short[name]) for name in name_models],
    '2125': [sum(opt_traj_DLCA_long[name]) for name in name_models]
})
print(summary_tf)

#%%
draw_models = name_models[:2]
fig, ax = plt.subplots()
color_emission = ['#727272', '#a3a3a3']
color_sequester = ['#38761d', '#739f60']
style_traj = ['--', '-.']
color_traj = ['black', 'blue']
for idx, name in enumerate(draw_models):
    ax.bar([k + offset_models[idx] for k in opt_time[name]], opt_schedule_operation[name], width=0.4,
           label=f'{name}', align='center', color=color_emission[idx])
ax.set_xlabel('Year')
ax.set_ylabel(r'Fractional Operation')
ax.legend(loc='upper left', title='Operation')

ax2 = ax.twinx()
for idx, name in enumerate(draw_models):
    ax2.plot([2025 + k + offset_models[idx] for k in range(tf_short)], np.cumsum(opt_traj_DLCA_short[name]) * saf_prod/1e6,
             color=color_traj[idx], linestyle=style_traj[idx], label=name)
ax2.set_ylabel(r'Cumulative TDGWP [tonne CO$_2$e]')
ax2.axhline(emission_target * saf_prod/1e6, color='red', linewidth=0.8, label='SAF Target')
ax2.legend(loc='upper left', title='Cum. TDGWP', bbox_to_anchor=(0.0,0.8))
ax2.grid(axis='both', linestyle=':', alpha=0.7)
# ax2.set_ylim([-270, 350])

plt.tight_layout()
plt.xlim([2025-3, 2025+27])

plt.savefig(os.path.join(os.getcwd(), 'Figure', 'DLCA_opt_pyro.png'))
plt.savefig(os.path.join(os.getcwd(), 'Figure', 'DLCA_opt_pyro.eps'))
plt.show()

