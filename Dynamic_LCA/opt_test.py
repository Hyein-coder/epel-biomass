"""
Solve optimization problem constrained by DLCA method
"""
import pandas as pd

from funs_dLCA import define_traj, build_model_DLCA, build_model_Static, solve_model
import matplotlib.pyplot as plt
import numpy as np
import pyomo.environ as pyo
import os

timeframe = 25
timegap = 5
emission = {'val': 10, 'lifetime': 10}
sequestration = {'val': 1, 'duration': 10}
plant, traj_emission, traj_sequester = define_traj(timeframe, timegap, emission, sequestration)

# Solve
model_DLCA = build_model_DLCA(timeframe, timegap, emission, sequestration)
res_DCLA = solve_model(model_DLCA)
model_Compare = build_model_Static(timeframe, timegap, emission, sequestration,
                                   total_target=pyo.value(model_DLCA.total_StaticLCA))
model_Full = build_model_Static(timeframe, timegap, emission, sequestration)
for k in model_Full.T:
    model_Full.schedule_opt[k].set_value(1)

names = ['DLCA', 'Compare', 'Full']
models = [model_DLCA, model_Compare, model_Full]
results = [solve_model(m) for m in models]

for n, r in zip(names, results):
    if r is not None:
        print(f'[{n}]: {str(r.solver.Message)}')
# Show results
# print(f'Sum of schedule_operation: [DLCA] {pyo.value(model_DLCA.max_operation):.2f} [Static] {pyo.value(model_Static.max_operation):.2f}')
# print(f'Total DLCA (should be 0): [DLCA] {pyo.value(model_DLCA.total_DLCA):.6f} [Static] {pyo.value(model_Static.total_DLCA):.6f}')
summary = pd.DataFrame({
    'Productivity': [pyo.value(m.max_operation) for m in models],
    'GWP': [pyo.value(m.total_StaticLCA) for m in models],
    'TDGWP': [pyo.value(m.total_DLCA) for m in models]
}, index=names)
print(summary)

#%%
opt_schedule_operation = {}
opt_traj_emission = {}
opt_traj_DLCA = {}
opt_traj_StaticGWP = {}

draw_names = ['Compare', 'TDGWP']
draw_models =[model_Compare, model_DLCA]
for name, model in zip(draw_names, draw_models):
    opt_schedule_operation[name] = [pyo.value(model.schedule_operation[k]) for k in model.T]
    opt_traj_emission[name] = [traj_emission[k] * opt_schedule_operation[name][k] for k in range(timeframe)]
    opt_traj_DLCA[name] = [pyo.value(model.traj_DLCA[k]) for k in model.T]
    opt_traj_StaticGWP[name] = [pyo.value(model.traj_net[k]) for k in model.T]

fig, ax = plt.subplots(figsize=(12,5))
offset_models = [0, 0.15, 0.3]
color_emission = ['#727272', '#a3a3a3']
color_sequester = ['#38761d', '#739f60']
style_traj = ['--', '-.']
color_traj = ['black', 'blue']
for idx, name in enumerate(draw_names):
    ax.bar([k + offset_models[idx] for k in range(timeframe)], opt_traj_emission[name], width=0.4,
           label=f'[{name}] Emission', align='center', color=color_emission[idx])
    ax.bar([k + offset_models[idx] for k in range(timeframe)], traj_sequester, width=0.4,
           label=f'[{name}] Sequestration', align='edge', color=color_sequester[idx])
ax.set_xlabel('Year')
ax.set_ylabel(r'Emission profile [g CO$_2$e/yr]')
ax.legend(loc='lower left')

ax2 = ax.twinx()
for idx, name in enumerate(draw_names):
    ax2.plot([k + offset_models[idx] for k in range(timeframe)], np.cumsum(opt_traj_DLCA[name]),
             color=color_traj[idx], linestyle=style_traj[idx], label=name)
for idx, name in enumerate(draw_names):
    ax2.plot([k + offset_models[idx] for k in range(timeframe)], np.cumsum(opt_traj_StaticGWP[name]),
             color=color_traj[idx], linestyle=':', label=name)
ax2.set_ylabel(r'Cumulative TDGWP [g CO$_2$e]')
ax2.legend(loc='upper left', bbox_to_anchor=(0.75, 1.))
ax2.grid(axis='both', linestyle=':', alpha=0.7)
ax2.set_ylim([-75, 75])

plt.savefig(os.path.join(os.getcwd(), 'Figure', 'DLCA_opt_test.png'))
plt.savefig(os.path.join(os.getcwd(), 'Figure', 'DLCA_opt_test.eps'))
plt.tight_layout()
plt.show()

#%%
fig, ax = plt.subplots()
name = 'TDGWP'
ax.bar([k for k in range(timeframe)], opt_traj_emission[name], width=0.4,
       label=f'[{name}] Emission', align='center', color=color_emission[0])
ax.bar([k for k in range(timeframe)], traj_sequester, width=0.4,
       label=f'[{name}] Sequestration', align='edge', color=color_sequester[0])
ax.set_xlabel('Year')
ax.set_ylabel(r'Emission profile [g CO$_2$e/yr]')
ax.legend(loc='lower left')

ax2 = ax.twinx()
ax2.plot([k for k in range(timeframe)], np.cumsum(opt_traj_StaticGWP[name]),
         color=color_traj[0], linestyle=style_traj[0], label='Static GWP')
ax2.plot([k for k in range(timeframe)], np.cumsum(opt_traj_DLCA[name]),
         color=color_traj[1], linestyle=style_traj[1], label='TDGWP')
ax2.set_ylabel(r'Cumulative GWP [g CO$_2$e]')
ax2.legend(loc='upper right')
ax2.grid(axis='both', linestyle=':', alpha=0.7)

plt.savefig(os.path.join(os.getcwd(), 'Figure', 'DLCA_opt_test_01.png'))
plt.savefig(os.path.join(os.getcwd(), 'Figure', 'DLCA_opt_test_01.eps'))
plt.tight_layout()
plt.show()
