"""
Sensitivity analysis on pyrolysis operation plan based on TDGWP metric
"""
from funs_lca import get_WTWa_conventional, get_WTWa_ftjet, get_WTWa_pyrolysis
from funs_dLCA import define_traj, build_model_DLCA, build_model_Static, solve_model, get_dlca_full_operation
import matplotlib.pyplot as plt
import numpy as np
import pyomo.environ as pyo
import os

list_timeframe = [20, 30, 40, 50, 60]
list_timegap = [1, 3, 5, 10, 20]
list_forest_period = [3, 5, 12, 36, 66]
list_emission_perturb = [-0.3, -0.1, 0., 0.1, 0.3]

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

case = 'Base'
emission_target = 0.9 * lca_total['Conventional']['WTWa']['GHG-100'] * saf_prod/1e6
ramping_rate = 0.3

emission_val = lca_total[case]['WTWa']['CO2'] * saf_prod/1e6
tot_sequestration_val = -lca_total[case]['WTWa']['CO2_Biogenic'] * saf_prod/1e6

