"""
Sensitivity analysis on DLCA optimization problem parameters
"""
import pandas as pd

from funs_dLCA import define_traj, build_model_DLCA, build_model_Static, solve_model
import matplotlib.pyplot as plt
import numpy as np
import pyomo.environ as pyo
import os

param_name = ['timeframe', 'timegap', 'lifetime', 'seq_duration']
param0 = [25, 5, 10, 10]

list_perturbation = [-0.5, -0.2, 0, 0.2, 0.5]
param_set = {param: [param0[idx] * (1+k) for k in list_perturbation] for idx, param in enumerate(param_name)}

# list_timeframe = [10, 20, 30, 50]
# list_timegap = [0, 3, 5, 10, 15]
# list_lifetime = [5, 10, 20, 50]
# list_seq_duration = [1, 5, 10, 20, 30]
# param_set = {
#     'timeframe': list_timeframe,
#     'timegap': list_timegap,
#     'lifetime': list_lifetime,
#     'seq_duration': list_seq_duration
# }

def solve_scenario(_param):
    _timeframe, _timegap, _lifetime, _seq_duration = [round(p) for p in _param]
    emission = {'val': 10, 'lifetime': _lifetime}
    sequestration = {'val': emission['val'] / _seq_duration, 'duration': _seq_duration}
    plant, traj_emission, traj_sequester = define_traj(_timeframe, _timegap, emission, sequestration)

    model_DLCA = build_model_DLCA(_timeframe, _timegap, emission, sequestration)
    res_DLCA = solve_model(model_DLCA)

    model_full = build_model_Static(_timeframe, _timegap, emission, sequestration)
    for k in model_full.T:
        model_full.schedule_opt[k].set_value(1)

    _res = {
        'Plant': plant,
        'Emission': traj_emission,
        'Sequestration': traj_sequester,
        'Model_DLCA': model_DLCA,
        'Model_full': model_full,
        'res_DLCA': res_DLCA
    }
    return _res

record = {param: [] for param in param_set.keys()}
for param, val_list in param_set.items():
    for val in val_list:
        p = param0
        p[param_name.index(param)] = val
        res = solve_scenario(p)
        record[param].append(res)

#%%
rec_obj = {param: [] for param in param_set.keys()}
rec_TDGWP = {param: [] for param in param_set.keys()}
rec_Topt = {param: [] for param in param_set.keys()}
rec_traj_op = {param: [] for param in param_set.keys()}
dict_obj = {'Perturbation': list_perturbation}
dict_dTDGWP = {'Perturbation': list_perturbation}
for param, rec in record.items():
    obj = []
    diff_TDGWP = []
    for r in rec:
        rec_obj[param].append((pyo.value(r['Model_DLCA'].max_operation), pyo.value(r['Model_full'].max_operation)))
        rec_Topt[param].append((pyo.value(r['Model_DLCA'].T_opt.at(-1)), pyo.value(r['Model_full'].T_opt.at(-1))))
        traj_op_dlca = []
        traj_op_full = []
        for k in r['Model_DLCA'].T_opt:
            traj_op_dlca.append(pyo.value(r['Model_DLCA'].schedule_opt[k]))
            traj_op_full.append(pyo.value(r['Model_full'].schedule_opt[k]))
        rec_traj_op[param].append((traj_op_dlca, traj_op_full))
        rec_TDGWP[param].append((pyo.value(r['Model_DLCA'].total_DLCA), pyo.value(r['Model_full'].total_DLCA)))
        obj.append(pyo.value(r['Model_DLCA'].max_operation)/pyo.value(r['Model_full'].max_operation))
        diff_TDGWP.append(pyo.value(r['Model_full'].total_DLCA) - pyo.value(r['Model_DLCA'].total_DLCA))
    dict_obj[param] = obj
    dict_dTDGWP[param] = diff_TDGWP

df_obj = pd.DataFrame(dict_obj)
df_dTDGWP = pd.DataFrame(dict_dTDGWP)
df_obj.set_index('Perturbation', inplace=True)
df_dTDGWP.set_index('Perturbation', inplace=True)

df_obj.plot(kind='line')
plt.title('Objective')
plt.show()

df_dTDGWP.plot(kind='line')
plt.title('Difference TDGWP')
plt.show()

param = 'timeframe'
fig, ax = plt.subplots(1,2)
for p, traj_op in zip(param_set[param], rec_traj_op[param]):
    traj_op_dlca, traj_op_full = traj_op
    traj_t = [k for k,_ in enumerate(traj_op_dlca)]
    label = f'{param} = {p}'
    ax[0].step(traj_t, traj_op_dlca, label=label)
    ax[1].step(traj_t, traj_op_full, label=label)
plt.show()

#%%
# Plot
for df in [df_obj, df_dTDGWP]:
    df.rename(columns={'seq_duration': 'Forest Growth Period',
                       'timeframe': 'Time Fame of the Analysis',
                       'timegap': 'Time Gap',
                       'lifetime': 'Project Lifetime'},
              inplace=True)

fig, axes = plt.subplots(1, 2, figsize=(20, 6))
params = {
    'legend.fontsize': 'large',
    'axes.labelsize': 'x-large',
    'axes.titlesize': 'x-large',
    'xtick.labelsize': 'x-large',
    'ytick.labelsize': 'x-large'}
plt.rcParams.update(params)

title = ['Relative productivity', 'TDGWP Difference']
for idx, df in enumerate([df_obj, df_dTDGWP]):
    # Reverse order of categories for vertical layout
    categories = df.columns[::-1]

    # Extract values
    base = df.loc[0.0][categories].values
    low_05 = df.loc[-0.5][categories].values
    low_02 = df.loc[-0.2][categories].values
    high_02 = df.loc[0.2][categories].values
    high_05 = df.loc[0.5][categories].values

    # Left side (negative values)
    ax = axes[idx]
    ax.barh(categories, low_05-base, color='royalblue', label='-50% Perturbation')
    ax.barh(categories, low_02-base, color='lightskyblue', label='-20% Perturbation')

    # Right side
    ax.barh(categories, high_05-base, color='orangered', label='+50% Perturbation')
    ax.barh(categories, high_02-base, color='orange', label='+20% Perturbation')

    # Decorations
    ax.axvline(0, color='black')
    ax.set_xlabel(title[idx])
    ax.set_title(f"{title[idx]} Sensitivity by Perturbation Level")

    ax.grid(axis='x')
axes[0].legend(loc='lower left')
plt.tight_layout()

plt.savefig(os.path.join(os.getcwd(), 'Figure', 'DLCA_opt_sensitivity.png'))
plt.savefig(os.path.join(os.getcwd(), 'Figure', 'DLCA_opt_sensitivity.eps'))
plt.show()

param = 'timeframe'
fig, ax = plt.subplots(figsize=(7,5))
styles_traj = ['-', '--', '-.', (0, (3, 5, 1, 5, 1, 5)), ':']
markers_traj = ['o', '^', 's', 'x', 'd']
max_seq = []
for idx, traj_op in enumerate(rec_traj_op[param]):
    p = param_set[param][idx]
    traj_op_dlca, _ = traj_op
    traj_t = [k for k,_ in enumerate(traj_op_dlca)]
    label = f'{param} = {round(p)}'
    ax.step(traj_t, [f*100 for f in traj_op_dlca], label=label,
            linestyle=styles_traj[idx], marker=markers_traj[idx])

    try:
        t_max = ([f > 0.99999 for f in traj_op_dlca]).index(1)
        model = record[param][idx]['Model_DLCA']
        max_seq.append(pyo.value(model.traj_DLCA[t_max]))
    except:
        max_seq.append(None)

plt.xlabel("Year")
plt.ylabel("Fractional Operation Rate [%]")
plt.grid(axis='both', alpha=0.8)
plt.legend(loc='upper left', bbox_to_anchor=(1, 1))

plt.tight_layout()
plt.savefig(os.path.join(os.getcwd(), 'Figure', 'DLCA_opt_timeframe.png'))
plt.savefig(os.path.join(os.getcwd(), 'Figure', 'DLCA_opt_timeframe.eps'))
plt.show()

plt.bar(param_set[param][1:], max_seq[1:])
plt.show()

""" 
Longer the timeframe, the GHG residence dynamics disappear and DLCA constraints' influence becomes weaker.
-> N2O vs. CO2?? (For a journal paper...) 
"""
