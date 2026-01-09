import numpy as np

evaluation_moment = 2100
emission_moment = 2030
rotation_time = 10

zero_moment = emission_moment - rotation_time
timeframe = evaluation_moment - emission_moment
traj_years = [zero_moment + i for i in range(evaluation_moment - zero_moment + 1)]

emission = {'CO2': 50, 'CH4': 0, 'N2O': 0}
biogenic_CO2 = 50

construction_emission = 50
construction_time = 2020
# rad_eff = {'CO2': 1.759e-15, 'CH4': 7.54e-14, 'N2O': 3.7e-13}

def aGWP_CO2(t):
    # (Levasseur, 2010)
    # Bern carbon-climate model using a background CO2
    # concentration of 378 ppm form IPCC 2007 report

    a0 = 0.217
    a1 = 0.259
    a2 = 0.338
    a3 = 0.186
    t1 = 172.9  # year
    t2 = 18.51
    t3 = 1.186

    rad_eff_CO2 = 1.759e-15
    agwp = rad_eff_CO2 * (a0*t + a1 * t1 * (1 - np.exp(-t/t1)) + a2 * t2 * (1 - np.exp(-t/t2))
                          + a3 * t3 * (1 - np.exp(-t/t3)))
    return agwp

def aGWP_CH4(t):
    tau_CH4 = 12
    rad_eff_CH4 = 7.54e-14
    agwp = rad_eff_CH4 * tau_CH4 * (1 - np.exp(-t/tau_CH4))
    return agwp

def aGWP_N2O(t):
    tau_N2O = 114
    rad_eff_N2O = 3.7e-13
    agwp = rad_eff_N2O * tau_N2O * (1 - np.exp(-t/tau_N2O))
    return agwp

def dGWP_density_CO2(t):
    return sum([aGWP_CO2(k+1) for k in range(timeframe-t)])/sum([aGWP_CO2(k+1) for k in range(timeframe)])

def dGWP_density_CH4(t):
    return sum([aGWP_CH4(k+1) for k in range(timeframe-t)])/sum([aGWP_CH4(k+1) for k in range(timeframe)])

def dGWP_density_N2O(t):
    return sum([aGWP_N2O(k+1) for k in range(timeframe-t)])/sum([aGWP_N2O(k+1) for k in range(timeframe)])

def gwp_from_my_equation(T):
    return sum([np.array([aGWP_CO2(t+1), aGWP_CH4(t+1), aGWP_N2O(t+1)]) for t in range(T)]) / \
        sum([aGWP_CO2(t+1) for t in range(T)])

idx_emission = traj_years.index(emission_moment)
emission_vec = np.array([[i] for i in emission.values()])

static_GWP = [0 for _ in traj_years]
static_GWP[idx_emission] = (gwp_from_my_equation(20) @ emission_vec)[0] - biogenic_CO2
static_GWP[traj_years.index(construction_time)] += construction_emission * dGWP_density_CO2(emission_moment - construction_time)
cum_staticGWP = np.cumsum(static_GWP)

biogenic_annual = biogenic_CO2 / rotation_time
dGWP_at_emission_moment = (np.array([dGWP_density_CO2(0), dGWP_density_CH4(0), dGWP_density_N2O(0)]) @ emission_vec)[0]

idx_start_preseq = traj_years.index(emission_moment - rotation_time)
dGWP_preseq = [0 for _ in range(idx_start_preseq)]

dGWP_preseq.extend([dGWP_density_CO2(-rotation_time + k) * -biogenic_annual for k in range(rotation_time)])
dGWP_preseq.append(dGWP_at_emission_moment)
dGWP_preseq.extend([0 for _ in traj_years[idx_emission+1:]])
dGWP_preseq[traj_years.index(construction_time)] += construction_emission * dGWP_density_CO2(emission_moment - construction_time)

cum_dGWP_preseq = np.cumsum(dGWP_preseq)

dGWP_postseq = [0 for _ in range(idx_emission)]
dGWP_postseq.append(dGWP_at_emission_moment)
dGWP_postseq.extend([dGWP_density_CO2(k) * -biogenic_annual for k in range(rotation_time)])
if len(dGWP_postseq) < len(traj_years):
    dGWP_postseq.extend([0 for _ in range(len(traj_years) - len(dGWP_postseq))])
else:
    dGWP_postseq = dGWP_postseq[:len(traj_years)]
dGWP_postseq[traj_years.index(construction_time)] += construction_emission * dGWP_density_CO2(emission_moment - construction_time)

cum_dGWP_postseq = np.cumsum(dGWP_postseq)

gwp_array = np.array([static_GWP, dGWP_preseq, dGWP_postseq])
cum_array = np.array([cum_staticGWP, cum_dGWP_preseq, cum_dGWP_postseq])
print(cum_array[:,-1])
