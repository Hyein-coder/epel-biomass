"""
Solve emission-minimization problem
"""
import pandas as pd

from funs_lca import get_WTWa_pyrolysis
from Dynamic_LCA.funs_dLCA import define_traj, get_dlca_full_operation, get_emission_target,\
    build_model_PyroOperation, build_model_PyroCashflow, solve_model, build_model_PyroMinEmission
import matplotlib.pyplot as plt
import numpy as np
import pyomo.environ as pyo
import os

timeframe = 25  # 2050 net-zero
timegap = 0
forest_period = 12  # average forest growth rate

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

model_min_emission = build_model_PyroMinEmission(timeframe, timegap, emission, sequestration)
res_min_emission = solve_model(model_min_emission)



