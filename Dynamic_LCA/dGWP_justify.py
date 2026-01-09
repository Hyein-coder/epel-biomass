"""
Justify why you need dynamic LCA method
"""

from funs_dLCA import DLCA
import matplotlib.pyplot as plt
import numpy as np

#%% Compare single emission vs. continuous emission

emission_val = 10
timeframe = 100
timegap = [i for i in range(10)]

traj_time = [i for i in range(timeframe)]
dlca = DLCA(timeframe)
traj_dGWP_density = [dlca.dGWP_density_CO2(k) for k in range(timeframe)]

sequestration_val = -2
sequestration_duration = 5

record = []
for tg in timegap:
    traj_emission = [0 for _ in range(timeframe)]
    traj_emission[0] += emission_val

    traj_sequester = [0 for _ in range(tg)] + [sequestration_val for _ in range(sequestration_duration)]
    traj_sequester += [0 for _ in range(timeframe - len(traj_sequester))]

    traj_net = [traj_emission[k] + traj_sequester[k] for k in range(timeframe)]
    traj_DLCA = [traj_net[k] * traj_dGWP_density[k] for k in range(timeframe)]
    record.append(traj_DLCA)

plt.scatter(timegap, [sum(traj) for traj in record])
plt.show()

#%% continuous operation

operation_time = 10
traj_emission = [emission_val for _ in range(operation_time)] + [0 for _ in range(timeframe - operation_time)]

record = []
for tg in timegap:
    mini_traj = [sequestration_val for _ in range(sequestration_duration)]
    traj_sequester_each_year = []
    for ot in range(operation_time):
        mini_traj_each_year = [0 for _ in range(tg + ot)] + mini_traj + [0 for _ in range(timeframe - tg - ot -
                                                                                          sequestration_duration)]
        traj_sequester_each_year.append(mini_traj_each_year)
    traj_sequester = [sum([traj[k] for traj in traj_sequester_each_year]) for k in range(timeframe)]

    traj_net = [traj_emission[k] + traj_sequester[k] for k in range(timeframe)]
    traj_DLCA = [traj_net[k] * traj_dGWP_density[k] for k in range(timeframe)]
    record.append(traj_DLCA)

plt.scatter(timegap, [sum(traj) for traj in record])
plt.show()

#%% Single case continuous operation for visualization

operation_time = 10
traj_emission = [emission_val for _ in range(operation_time)] + [0 for _ in range(timeframe - operation_time)]

timegap = [5]

record_sequester = []
record_cumDLCA = []
for tg in timegap:
    mini_traj = [sequestration_val] * sequestration_duration
    traj_sequester_each_year = []
    for ot in range(operation_time):
        mini_traj_each_year = [0] * (tg + ot) + mini_traj + [0] * (timeframe - tg - ot - sequestration_duration)
        traj_sequester_each_year.append(mini_traj_each_year)
    traj_sequester = [sum([traj[k] for traj in traj_sequester_each_year]) for k in range(timeframe)]

    traj_net = [traj_emission[k] + traj_sequester[k] for k in range(timeframe)]
    traj_DLCA = [traj_net[k] * traj_dGWP_density[k] for k in range(timeframe)]
    traj_cumDLCA = np.cumsum(traj_DLCA)

    record_sequester.append(traj_sequester)
    record_cumDLCA.append(traj_cumDLCA)

params = {
    'legend.fontsize': 'x-large',
    'axes.labelsize': 'xx-large',
    'axes.titlesize': 'xx-large',
    'xtick.labelsize': 'x-large',
    'ytick.labelsize': 'x-large'}
plt.rcParams.update(params)

fig, ax = plt.subplots()

ax.bar(traj_time, traj_emission, width=0.4, label='Emission', align='center', color='gray')
colors = ['seagreen', 'orange']
styles = ['--', '-.']
align = ['center', 'edge']
for idx, traj in enumerate(record_sequester):
    ax.bar(traj_time, traj, width=0.4, label=r'$T_{gap}$' + f' = {timegap[idx]} year', align=align[idx], color=colors[idx])
    ax.plot(traj_time, record_cumDLCA[idx], color='black', linestyle=styles[idx])

ax.set_xlabel('Year')
ax.set_ylabel(r'Emission profile [g CO$_2$e/MJ]')
ax.legend()

ax.set_xlim([0, 25])
ax.grid(axis='both', alpha=0.7)
plt.tight_layout()
plt.show()

#%% Single Time Emission

timeframe10 = 11
dlca10 = DLCA(timeframe10)
emission = 10
dgwp_emission = [dlca10.dGWP_density_CO2(0) * emission] + [0 for _ in range(timeframe10-1)]
cum_dgwp_emission = np.cumsum(dgwp_emission)

traj1 = [-emission] + [0 for _ in range(timeframe10-1)]
traj2 = [0 for _ in range(5)] + [-emission] + [0 for _ in range(timeframe10 - 5 - 1)]
traj3 = [-emission/3 for _ in range(3)] + [0 for _ in range(timeframe10 - 3)]
traj_time10 = [t for t in range(timeframe10)]
traj_list = [traj1, traj2, traj3]
dgwp = [[dlca10.dGWP_density_CO2(t) * ti[t] for t in range(timeframe10)] for ti in traj_list]
cum_dgwp = [np.cumsum(di) for di in dgwp]

fig, ax = plt.subplots()

ax.bar([0], emission, width=0.4, label='Emission', align='center', color='gray')
colors = ['seagreen', 'orange', 'purple']
styles = ['--', '-', '-.']
align = ['center', 'center', 'edge']
labels = ['Simultaneous', 'With Time-lag', 'Periodic']
for idx, traj in enumerate(traj_list):
    ax.bar(traj_time10, traj, width=0.4, align=align[idx], color=colors[idx], label=labels[idx])
    ax.plot(traj_time10, cum_dgwp[idx] + cum_dgwp_emission, color=colors[idx], linestyle=styles[idx])

ax.set_xlabel('Year')
ax.set_ylabel(r'Emission [g CO$_2$e]')
ax.legend()
ax.set_xlim([-.5, timeframe10-1])
ax.grid(True, which='both', axis='both', linestyle='--', linewidth=0.5)

plt.tight_layout()
plt.show()
