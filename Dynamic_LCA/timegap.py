from funs_dLCA import atm_concentration_CO2, atm_concentration_CH4, atm_concentration_N2O
from funs_dLCA import aGWP_CO2, aGWP_CH4, aGWP_N2O
import matplotlib.pyplot as plt

time_horizon = 50
traj_time = [i for i in range(time_horizon + 1)]
traj_agwp = [i*5 for i in range(round(time_horizon/5) + 1)]

params = {
    'legend.fontsize': 'x-large',
    'axes.labelsize': 'xx-large',
    'axes.titlesize': 'xx-large',
    'xtick.labelsize': 'x-large',
    'ytick.labelsize': 'x-large'}
plt.rcParams.update(params)

# Create the first plot
fig, ax1 = plt.subplots()

# Create a second y-axis sharing the same x-axis
ax2 = ax1.twinx()

# Plot the second line
ax2.bar(traj_agwp, [aGWP_CO2(t) for t in traj_agwp],
        width=3, color='none', edgecolor='grey', hatch='//', label='Y2 Line', zorder=1)
ax2.set_ylabel(r'Absolute GWP [W/m$^2$/kg]', color='grey')
ax2.tick_params(axis='y', labelcolor='grey')

# Plot the first line
ax1.plot(traj_time, [atm_concentration_CO2(t) for t in traj_time], 'b-', label='Y1 Line', zorder=2)
ax1.set_xlabel('Time-gap [year]')
ax1.set_ylabel(r'CO$_2$ Concentration [ppb]', color='b')
ax1.tick_params(axis='y', labelcolor='b')
ax1.grid(True, which='both', axis='both', linestyle='--', linewidth=0.5)

# Optional: Add legends
fig.tight_layout()
plt.show()

#%%
lw = 1.5
time100 = [i for i in range(100+1)]
fig, ax = plt.subplots()

ax.plot(time100, [atm_concentration_CO2(t) for t in time100], '-', linewidth=lw, label='CO2')
ax.plot(time100, [atm_concentration_CH4(t) for t in time100], '--', linewidth=lw, label='CH4')
ax.plot(time100, [atm_concentration_N2O(t) for t in time100], '-.', linewidth=lw, label='N2O')

ax.legend()
ax.set_xlabel('Time [year]')
ax.set_ylabel('Atmospheric Load [ppb]')

ax.grid(True, linestyle='--', linewidth=0.5)
fig.tight_layout()
plt.show()


#%%
import numpy as np
fig, ax = plt.subplots()

categories = ['GWP20', 'GWP100']
time_window = [20, 100]
CO2 = [aGWP_CO2(t)/aGWP_CO2(t) for t in time_window]
CH4 = [aGWP_CH4(t)/aGWP_CO2(t) for t in time_window]
N2O = [aGWP_N2O(t)/aGWP_CO2(t) for t in time_window]

x = np.arange(len(categories))
width = 0.25

params = {
    'legend.fontsize': 'xx-large',
    'axes.labelsize': 'xx-large',
    'axes.titlesize': 'xx-large',
    'xtick.labelsize': 'xx-large',
    'ytick.labelsize': 'xx-large'}
plt.rcParams.update(params)

# Plot
fig, ax = plt.subplots(figsize=(8, 6))
bars1 = ax.bar(x - width, CO2, width, label='CO2', color='steelblue')
bars2 = ax.bar(x, CH4, width, label='CH4', color='peru')
bars3 = ax.bar(x + width, N2O, width, label='N2O', color='seagreen')

# Add value labels
for bars in [bars1, bars2, bars3]:
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + 0.01, f'{height:.0f}',
                ha='center', va='bottom', fontsize=17)

# Labels and formatting
ax.set_ylabel(r'GWP [g CO$_2$ equivalent]')
# ax.set_ylim(0, 0.52)
ax.set_xticks(x)
ax.set_xticklabels(categories)
ax.legend()
plt.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.show()

#%%
