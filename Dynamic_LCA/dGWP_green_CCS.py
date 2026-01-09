import numpy as np
from funs_dLCA import DLCA
import matplotlib.pyplot as plt

timeframe = 100
moment_emission_reduction = 1
emissions2_val = 1

record = []
for ccs_start in range(timeframe):

    traj_time = [i for i in range(timeframe)]
    dLCA = DLCA(timeframe)
    traj_dGWP_density = [dLCA.dGWP_density_CO2(k) for k in range(timeframe)]

    emissions1 = [1 for _ in range(moment_emission_reduction)]
    emissions2 = [emissions2_val for _ in range(timeframe - moment_emission_reduction)]
    traj_emission = [*emissions1, *emissions2]

    emission_construction = 10
    traj_construction = [0 for _ in range(timeframe)]
    traj_construction[moment_emission_reduction] = emission_construction

    # biogenic_delay = 0
    # biogenic1 = [-4.5 for _ in range(moment_emission_reduction + biogenic_delay)]
    # biogenic2 = [-5.5 for _ in range(timeframe - moment_emission_reduction - biogenic_delay)]
    # traj_biogenic = [*biogenic1, *biogenic2]

    record_inner = []
    for ccs_carbon in [-5 * i for i in range(10)]:
        # ccs_carbon = -100
        # ccs_start = 5
        ccs_duration = 10
        traj_ccs = [0 for _ in range(ccs_start)] + [ccs_carbon for _ in range(ccs_duration)] +\
                   [10 for _ in range(timeframe - ccs_start - ccs_duration)]

        traj_net = [traj_emission[k] + traj_ccs[k] + traj_construction[k] for k in range(timeframe)]
        traj_dLCA = [traj_net[k] * traj_dGWP_density[k] for k in range(timeframe)]
        record_inner.append(sum(traj_dLCA))
    record.append(record_inner)

for c in range(len(record[0])):
    plt.plot([i for i in range(len(record))], [record[i][c] for i in range(len(record))], label=-10 * c)
plt.legend()
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
