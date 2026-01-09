import pandas as pd

from funs_lca import get_WTWa_pyrolysis
from Dynamic_LCA.funs_dLCA import define_traj, get_dlca_full_operation, get_emission_target,\
    solve_model, build_model_PyroPareto, build_model_PyroCashflow
import matplotlib.pyplot as plt
import numpy as np
import pyomo.environ as pyo
import os
import datetime

timeframe = 25
timegap = 0
forest_period = 12
tag = 'carbcredit'
credit_price = 70   # USD/ton

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

#%% 1) Utopia point
sf_init = [1, 1]
emission_ub = target
profit_lb = 0

w_utopia = [1, 0]
results_utopia = []
pareto_utopia = []
for w in w_utopia:
    m = build_model_PyroPareto(timeframe, timegap, emission, sequestration, w, emission_ub, profit_lb, sf_init,
                               saf_target=target, credit_price=credit_price)
    r = solve_model(m)
    results_utopia.append((m, r))
    pareto_utopia.append((pyo.value(m.total_DLCA), -pyo.value(m.total_cashflow)))

j_utopia = (pareto_utopia[0][0], pareto_utopia[1][1])
j_nadir = (max([p[0] for p in pareto_utopia]), max([p[1] for p in pareto_utopia]))
sf = [jn - ju for jn, ju in zip(j_nadir, j_utopia)]
capacity = 30
#%%
weights = []
j_DLCA = []
j_NegProfit = []
sol_stat = []
results = {}

n_iter = 4
w_init = [1/(n_iter+1) * (x+1) for x in range(n_iter)]
# weights = [0, 0.5, 0.55, 0.6, 0.7, 0.75, 0.77, 0.8, 0.83, 0.85, 0.88, 0.9, 1]

for w in w_init:
    m = build_model_PyroPareto(timeframe, timegap, emission, sequestration,
                               w, emission_ub, profit_lb, sf, fix_capacity=capacity,
                               saf_target=target, credit_price=credit_price)
    r = solve_model(m)
    weights.append(w)
    j_DLCA.append(pyo.value(m.total_DLCA))
    j_NegProfit.append(-pyo.value(m.total_cashflow))
    sol_stat.append(str(r.solver.Message))
    results[w] = (m, r)

#%%
d_dense_scaled = .1
for k in range(4):
    df = pd.DataFrame({'weights': weights + w_utopia,
                       'DLCA': j_DLCA + [p[0] for p in pareto_utopia],
                       'NegProfit': j_NegProfit + [p[1] for p in pareto_utopia],
                       'stat': sol_stat + ['Utopia' for _ in pareto_utopia]})
    df['scaledDLCA'] = df['DLCA'] / sf[0]
    df['scaledNegProfit'] = df['NegProfit'] / sf[1]
    df_sorted = df.sort_values(by=['weights'])

    df_sorted['diffDLCA'] = df_sorted['scaledDLCA'].shift(-1) - df['scaledDLCA']
    df_sorted['diffNegProfit'] = df_sorted['scaledNegProfit'].shift(-1) - df['scaledNegProfit']
    df_sorted['diffDLCA'].iloc[-1] = 0.
    df_sorted['diffNegProfit'].iloc[-1] = 0.

    df_sorted['distance'] = np.sqrt(df_sorted['diffDLCA'] ** 2 + df_sorted['diffNegProfit'] ** 2)
    l_avg = sum(df_sorted['distance']) / len(df_sorted['distance'])

    for i1, i2 in zip(df_sorted.index[:-1], df_sorted.index[1:]):
        w1 = df_sorted.loc[i1, 'weights']
        w2 = df_sorted.loc[i2, 'weights']
        n = round(df_sorted.loc[i1, 'distance'] / l_avg * 2)

        p1 = (df_sorted.loc[i1, 'scaledDLCA'], df_sorted.loc[i1, 'scaledNegProfit'])
        p2 = (df_sorted.loc[i2, 'scaledDLCA'], df_sorted.loc[i2, 'scaledNegProfit'])
        angle = np.arctan(-(p1[1] - p2[1])/(p1[0] - p2[0]))
        d_emission = d_dense_scaled * np.cos(angle)
        d_profit = d_dense_scaled * np.sin(angle)
        ub1 = emission_ub - d_emission * sf[0]
        ub2 = -profit_lb - d_profit * sf[1]

        if n > 1:
            w_new = [w1 + (w2 - w1)/n * (x+1) for x in range(n-1)]
            for w in w_new:
                m = build_model_PyroPareto(timeframe, timegap, emission, sequestration,
                                           w, ub1, -ub2, sf, fix_capacity=capacity,
                                           saf_target=target, credit_price=credit_price)
                print("Started at:", datetime.datetime.now().strftime("%d %H:%M:%S"))
                r = solve_model(m, print_lv=1)
                weights.append(w)
                j_DLCA.append(pyo.value(m.total_DLCA))
                j_NegProfit.append(-pyo.value(m.total_cashflow))
                sol_stat.append(str(r.solver.Message))
                results[w] = (m, r)

#%%
results_combined = [(m, r) for m, r in results.values()] + results_utopia
df = pd.DataFrame({'weights': weights + w_utopia,
                   'DLCA': j_DLCA + [p[0] for p in pareto_utopia],
                   'NegProfit': j_NegProfit + [p[1] for p in pareto_utopia],
                   'stat': sol_stat + ['Utopia' for _ in pareto_utopia],
                   'credit': [sum([pyo.value(m.credit[k]) for k in m.T]) for m, _ in results_combined]})
df['scaledDLCA'] = df['DLCA'] / sf[0]
df['scaledNegProfit'] = df['NegProfit'] / sf[1]
df_sorted = df.sort_values(by=['weights'])

df_sorted['diffDLCA'] = df_sorted['scaledDLCA'].shift(-1) - df['scaledDLCA']
df_sorted['diffNegProfit'] = df_sorted['scaledNegProfit'].shift(-1) - df['scaledNegProfit']
df_sorted['diffDLCA'].iloc[-1] = 0.
df_sorted['diffNegProfit'].iloc[-1] = 0.

df_sorted['distance'] = np.sqrt(df_sorted['diffDLCA'] ** 2 + df_sorted['diffNegProfit'] ** 2)
df_sorted.to_csv(os.path.join(os.getcwd(), 'Figure', f'DLCA_pareto_data_{tag}.csv'))

#%%
fig, ax = plt.subplots(1,2)
ax0 = ax[0]
ax0.scatter(df['DLCA'], df['credit'] / 1e9)
ax0.grid(axis='both', linestyle=':')
ax0.set_xlabel("Discounted GHG emission [g CO2e/MJ]")
ax0.set_ylabel("Carbon Credit [B$/yr]")

ax1 = ax[1]
ax1.scatter(-df['NegProfit']/1e9, df['credit'] / 1e9)
ax1.grid(axis='both', linestyle=':')
ax1.set_xlabel("NPV [B$/yr]")
ax1.set_ylabel("Carbon Credit [B$/yr]")

#%%
summary = pd.DataFrame({
    'Capacity': [pyo.value(m.capacity) for m, _ in results.values()],
    'Profit': [sum([pyo.value(m.cashflow[k]) for k in m.T]) for m, _ in results.values()],
    'TDGWP': [pyo.value(m.total_DLCA) for m, _ in results.values()]
}, index=weights)
print(summary)

#%%
params = {
    'legend.fontsize': 'medium',
    'axes.labelsize': 'x-large',
    'axes.titlesize': 'xx-large',
    'xtick.labelsize': 'x-large',
    'ytick.labelsize': 'x-large'}
plt.rcParams.update(params)

fig, ax = plt.subplots()
ax.scatter(summary['TDGWP'], summary['Profit']/1e9)
ax.axvline(target, color='r')
ax.axhline(0, color='b')
ax.grid(axis='both', linestyle=':')
ax.set_xlabel("Discounted GHG emission [g CO2e/MJ]")
ax.set_ylabel("Overall Profit [B$/yr]")
# ax.yaxis.set_inverted(True)
plt.tight_layout()

plt.savefig(os.path.join(os.getcwd(), 'Figure', f'DLCA_pareto_{tag}.eps'))
plt.savefig(os.path.join(os.getcwd(), 'Figure', f'DLCA_pareto_{tag}.png'))
plt.show()

#%%
# fig_zoom, ax_zoom = plt.subplots()
# ax_zoom.scatter(summary['TDGWP'], summary['Profit']/1e9)
# ax_zoom.axvline(target, color='r')
# ax_zoom.axhline(0, color='b')
# ax_zoom.grid(axis='both', linestyle=':')
# ax_zoom.set_xlabel("Discounted GHG emission [g CO2e/MJ]")
# ax_zoom.set_ylabel("Overall Profit [B$/yr]")
# ax_zoom.set_ylim([-0.01, 0.6])
# ax_zoom.set_xlim([-300,-200])
# plt.tight_layout()
#
# plt.savefig(os.path.join(os.getcwd(), 'Figure', f'DLCA_pareto_zoom_{tag}.eps'))
# plt.savefig(os.path.join(os.getcwd(), 'Figure', f'DLCA_pareto_zoom_{tag}.png'))
# plt.show()
