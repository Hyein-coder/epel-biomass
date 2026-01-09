import numpy as np
from funs_dLCA import DLCA
import matplotlib.pyplot as plt

timeframe = 100
# moment_emission_reduction = 10

record = []
for moment_emission_reduction in range(timeframe):

    traj_time = [i for i in range(timeframe)]
    dLCA = DLCA(timeframe)
    traj_dGWP_density = [dLCA.dGWP_density_CO2(k) for k in range(timeframe)]

    emissions1 = [1 for _ in range(moment_emission_reduction)]

    biogenic_carbon = 0
    traj_biogenic = [-biogenic_carbon for _ in range(timeframe)]

    emission_construction = 10
    traj_construction = [0 for _ in range(timeframe)]
    traj_construction[moment_emission_reduction] = emission_construction

    # biogenic_delay = 0
    # biogenic1 = [-4.5 for _ in range(moment_emission_reduction + biogenic_delay)]
    # biogenic2 = [-5.5 for _ in range(timeframe - moment_emission_reduction - biogenic_delay)]
    # traj_biogenic = [*biogenic1, *biogenic2]

    record_inner = []
    for emissions2_val in [0.5 * i for i in range(3)]:
        emissions2 = [emissions2_val for _ in range(timeframe - moment_emission_reduction)]
        traj_emission = [*emissions1, *emissions2]

        traj_net = [traj_emission[k] + traj_biogenic[k] + traj_construction[k] for k in range(timeframe)]
        traj_dLCA = [traj_net[k] * traj_dGWP_density[k] for k in range(timeframe)]
        record_inner.append(sum(traj_dLCA))
    record.append(record_inner)

#%%
for c in range(len(record[0])):
    plt.plot([i for i in range(len(record))], [record[i][c] for i in range(len(record))], label=f"{c*0.1:.1f}")
plt.legend()
plt.grid(True, alpha=0.6)
plt.xlabel("Moment of Construction")
plt.ylabel("Total Emission")
plt.show()

# plt.plot(traj_time, traj_dGWP_density)
# plt.title("dGWP density")
# plt.show()
#
# plt.step(traj_time, traj_net)
# plt.step(traj_time, traj_dLCA)
# plt.title("Reduced Emission Impact")
# plt.show()
# print(sum(traj_dLCA))
