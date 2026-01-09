import os
import time
import numpy as np
from funs_opt import AspenCost

file_name = "Pyrolysis_Jones_565_ASW"

mixed_domain = [
    {'name': 'PYROTEMP', 'type': 'continuous', 'domain': (750, 1020), 'dimensionality': 1}, # 0
    {'name': 'GAS.N', 'type': 'continuous', 'domain': (27, 40), 'dimensionality': 1},    # 1
    {'name': 'GAS.F', 'type': 'continuous', 'domain': (13, 25), 'dimensionality': 1},    # 2
    {'name': 'GAS.RR', 'type': 'continuous', 'domain': (1.4, 15), 'dimensionality': 1},   # 3
    {'name': 'SAF.N', 'type': 'continuous', 'domain': (10, 30), 'dimensionality': 1},    # 4
    {'name': 'SAF.F', 'type': 'continuous', 'domain': (5, 15), 'dimensionality': 1},    # 5
    {'name': 'SAF.RR', 'type': 'continuous', 'domain': (.46, 1.5), 'dimensionality': 1},   # 6
    {'name': 'DSL.N', 'type': 'continuous', 'domain': (13, 30), 'dimensionality': 1},    # 7
    {'name': 'DSL.F', 'type': 'continuous', 'domain': (7, 15), 'dimensionality': 1},    # 8
    {'name': 'DSL.RR', 'type': 'continuous', 'domain': (.23, 1.2), 'dimensionality': 1}    # 9
    # {'name': 'Q.PRES', 'type': 'continuous', 'domain': (750, 1020), 'dimensionality': 1},   # 10
    # {'name': 'Q.TEMP1', 'type': 'continuous', 'domain': (750, 1020), 'dimensionality': 1},  # 11
    # {'name': 'Q.TEMP2', 'type': 'continuous', 'domain': (750, 1020), 'dimensionality': 1},  # 12
]
NameList = []
for i in range(len(mixed_domain)):
    NameList.append(mixed_domain[i]['name'])

info_interactive = {
    'input': {'cell': "B7", 'name': ['PYROTEMP']},
    'output': {'cell': "B19", 'name': ['UtilSummary']}
}
# info_interactive = {
#     'input': {'cell': "B7:B16", 'name': NameList},
#     'output': {'cell': "N24:N29", 'name': ["TCC", "TOC", "TRC", "TUC", "TPS", "SAF"]},
#     'quality': {'cell': "N2:N7", 'name': ["HHV", "SG", "SLF", "ARM", "MFP", "MBP"]}
# }

aspen = AspenCost(file_name, info_interactive)
x0 = np.array([[
    930, 30, 16, 3.5,
    20, 11, 0.45,
    20, 12, 0.7
]])
aspen.evaluate(x0)
