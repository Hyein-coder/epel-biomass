import pythoncom
import win32com.client as win32
import os
import time
import datetime
import pandas as pd
import numpy as np
from funs_opt import cal_MJSP
import GPyOpt
import matplotlib.pyplot as plt

pythoncom.CoInitialize()
def dispatch_excel_file(file_name):
    excel = win32.Dispatch("Excel.Application")
    wb = None
    for workbook in excel.Workbooks:
        if workbook.Name == f'{file_name}.xlsx':
            wb = workbook
            break
    if wb is None:
        wb = excel.Workbooks.Open(os.path.abspath(f'../Aspen/{file_name}.xlsx'))
    # excel.Run("AspenSimulationWorkbook.xla! ASWActivateActiveSimulation")
    return excel, wb

f = "Pyrolysis_Jones_571_ASW"
excel, wb = dispatch_excel_file(f)

ws = wb.Worksheets("InteractiveSheet")
# ws.Activate()

#%%
# ws.Range("B2").Value = 1
mixed_domain = [
    # {'name': 'PYROTEMP', 'type': 'continuous', 'domain': (910, 960), 'dimensionality': 1}, # 0
    {'name': 'GAS.N', 'type': 'discrete', 'domain': (range(27, 40)), 'dimensionality': 1},    # 1
    {'name': 'GAS.F', 'type': 'discrete', 'domain': (range(10, 20)), 'dimensionality': 1},    # 2
    {'name': 'GAS.RR', 'type': 'continuous', 'domain': (1, 15), 'dimensionality': 1},   # 3
    {'name': 'SAF.N', 'type': 'discrete', 'domain': (range(10, 30)), 'dimensionality': 1},    # 4
    {'name': 'SAF.F', 'type': 'discrete', 'domain': (range(5, 15)), 'dimensionality': 1},    # 5
    {'name': 'SAF.RR', 'type': 'continuous', 'domain': (0.3, 1.2), 'dimensionality': 1},   # 6
    {'name': 'DSL.N', 'type': 'discrete', 'domain': (range(10, 30)), 'dimensionality': 1},    # 7
    {'name': 'DSL.F', 'type': 'discrete', 'domain': (range(7, 15)), 'dimensionality': 1},    # 8
    {'name': 'DSL.RR', 'type': 'continuous', 'domain': (.3, 1.4), 'dimensionality': 1}    # 9
    # {'name': 'Q.PRES', 'type': 'continuous', 'domain': (750, 1020), 'dimensionality': 1},   # 10
    # {'name': 'Q.TEMP1', 'type': 'continuous', 'domain': (750, 1020), 'dimensionality': 1},  # 11
    # {'name': 'Q.TEMP2', 'type': 'continuous', 'domain': (750, 1020), 'dimensionality': 1},  # 12
]
NameList = []
for i in range(len(mixed_domain)):
    NameList.append(mixed_domain[i]['name'])
dim_input = len(mixed_domain)

Constraints = [
    {'name': 'GAS', 'constraint': 'x[:,1] - x[:,0] + 2'},   # feed + 2 <= col_height
    {'name': 'SAF', 'constraint': 'x[:,4] - x[:,3] + 2'},   # feed + 2 <= col_height
    {'name': 'DSL', 'constraint': 'x[:,7] - x[:,6] + 2'},   # feed + 2 <= col_height
]

check_cell = ws.Range("O24")
input_cell = ws.Range("B8:B16")
print(f"Does input dimension match?  {bool(len(input_cell)==dim_input)}")

cost_cell = ws.Range("O24:O29")
cost_name = ["TCC", "TOC", "TRC", "TPS", "TUC", "SAF"]
dim_cost = len(cost_name)

qual_cell = ws.Range("N2:N11")
qual_name = ["LHV", "SG", "SLF", "ARM", "MBP", "MFP", "GT10", "GT90", "DFP", "DT90"]
dim_qual = len(qual_name)

def run():
    check_prev = check_cell.Value
    excel.Run("AspenSimulationWorkbook.xla! ASWInitandRunActiveSimulation")
    time.sleep(15)
    cnt = 0
    error = 0

    while True:
        try:
            time.sleep(1)
            state = excel.StatusBar
            time.sleep(0.25)
            if 'FALSE' == state:
                print("Wait_for_Costing_Result")
                time.sleep(30)

                for cnt_advance in range(10):
                    if check_prev == check_cell.Value:
                        print(f"Wait just in advance #{cnt_advance}")
                        time.sleep(5)
                    else:
                        break
                if check_prev == check_cell.Value:
                    print("Still stuck")
                    error = 99
                return error
            elif 'fail' in state.lower():
                print('Error_Detected')
                return 100
            else:
                cnt += 1
                print('PASSED ', cnt)
                assert cnt < 60

        except BaseException as e:
            if isinstance(e, KeyboardInterrupt):
                raise
            cnt += 1
            print('passed, ', cnt)
            assert cnt < 60

def get_cost():
    while True:
        try:
            _val = cost_cell.Value
            _dict = {
                k: v[0] for k, v in zip(cost_name, _val)
            }
            mjsp = cal_MJSP(_dict["SAF"], _dict["TCC"], _dict["TOC"], _dict["TPS"])
            _dict["MJSP"] = mjsp
            return _dict
        except BaseException as e:
            if isinstance(e, KeyboardInterrupt):
                raise
            time.sleep(0.5)
            pass

def check_quality():
    """
    Based on Watanasari, 2023,
    except the property lack experimental data (freezing point)
    :return: if_violate, quality_value
    """
    _cnt = 0
    while True:
        try:
            _val = qual_cell.Value
            _dict = {
                k: v[0] for k, v in zip(qual_name, _val)
            }
            _dict["SG"] = _dict["SG"] * 1000    # lb/cuft -> kg/m3

            _qual_bound = {
                "LHV": (0.0, 0.0),
                "SG": (.0, .0),
                "SLF": (0., 0.),
                "ARM": (0., 0.),
                "MBP": (0., 0.),
                "MFP": (0., 0.),
                "GT10": (0., 0.),
                "GT90": (0., 0.),
                "DFP": (0., 0.),
                "DT90": (0., 0.)
            }
            # _qual_bound = {
            #     "LHV": (0.18, 1.06),
            #     "SG": (4.26, 13.0),
            #     "SLF": (0, 0),
            #     "ARM": (15.6, 0.1),
            #     "MBP": (0, 9.08),
            #     "MFP": (192, 37.9),
            #     "GT10": (2.69, 4.74),
            #     "GT90": (7.05, 5.27),
            #     "DFP": (21.41, 0),
            #     "DT90": (13.2, 11.9)
            # }

            # C <= 0
            _const = [
                (42.8 - _dict["LHV"] + _qual_bound["LHV"][0]) / 42.8,
                (775 - _dict["SG"] + _qual_bound["SG"][0]) / 775,
                (_dict["SG"] - 840 + _qual_bound["SG"][1]) / 840,
                (_dict["MFP"] + 40 + _qual_bound["MFP"][1]) / 40,
                (38 - _dict["MBP"] + _qual_bound["MBP"][0]) / 38,
                (8 - _dict["ARM"] + _qual_bound["ARM"][0]) / 8,
                (_dict["ARM"] - 25 + _qual_bound["ARM"][1]) / 25,
                (_dict["SLF"] - 0.0032 + _qual_bound["SLF"][1]) / 0.0032,
                (_dict["GT10"] - 70 + _qual_bound["GT10"][1]) / 70,
                (_dict["GT90"] - 170 + _qual_bound["GT90"][1]) / 170,
                (40 - _dict["DFP"] + _qual_bound["DFP"][0]) / 40,
                (_dict["DT90"] - 360 + _qual_bound["DT90"][1]) / 360,
            ]

            _violate = [max(v, 0) * 10 for v in _const]
            return _violate, _dict
        except BaseException as e:
            if isinstance(e, KeyboardInterrupt):
                raise
            _cnt += 1
            time.sleep(0.5)
            if _cnt > 10:
                _dict = {k: 0 for k in qual_name}
                _violate = [100] + [0]*11
                return _violate, _dict
#%%
a = get_cost()
b, c = check_quality()
dim_qual_const = len(b)
#%%
now = time.localtime()
now_str = time.strftime('%Y%m%d_%H%M%S', now)
wb.Worksheets.Add()
rws = excel.ActiveSheet
rws.Name = now_str

rec_list = NameList + cost_name + ["MJSP"] + qual_name + ["ERRSIM"] + [f'ERR_{i}' for i in range(dim_qual_const)] + ["OBJ"]
dim_rec = len(rec_list)
rws.Range(rws.Cells(1, 1), rws.Cells(1, len(rec_list))).Value = rec_list

#%%
GLOBAL_I = 0
def objective_function(x):
    global GLOBAL_I

    cntt = 0
    while True:
        try:
            print("Cool time")
            time.sleep(5)
            x_val = x.tolist()[0]
            input_cell.Value = [[xx, ] for xx in x_val]
            time.sleep(1)

            e_sim = run()
            GLOBAL_I += 1
            cost = get_cost()
            violate, quality = check_quality()
            obj_val = cost['MJSP'] + e_sim + sum(violate)
            # violate = [0]

            rws.Range(rws.Cells(GLOBAL_I+1, 1), rws.Cells(GLOBAL_I+1, dim_rec)).Value =\
                x_val + list(cost.values()) + list(quality.values()) + [e_sim] + violate + [obj_val]

            print(f"{GLOBAL_I}: {cost['MJSP']}, error: {e_sim + sum(violate)}")
            wb.Save()
            return cost['MJSP'] + e_sim + sum(violate)

        except BaseException as e:
            if isinstance(e, KeyboardInterrupt):
                raise
            cntt += 1
            print('Critical..', cntt)
            assert cntt < 10

x = np.array([[
    30, 15, 2.95,
    20, 12, 0.56748,
    20, 12, 0.7
]])
#%%
x0 = np.array([[
    30, 15, 3.6,
    20, 10, 0.43,
    20, 10, 0.72
]])
x_opt = np.array([[
3.000000e+01,
1.900000e+01,
1.134609e+01,
1.500000e+01,
1.300000e+01,
3.001860e-01,
2.300000e+01,
8.000000e+00,
6.614616e-01,
]])
objective_function(x_opt)

#%%
num_point = 11

# idx = 0
# lb, ub = mixed_domain[idx]['domain']
# space = np.linspace(lb, ub, num_point)
# for val in space:
#     x = x0.copy()
#     x[0, idx] = val
#     objective_function(x)

# for idx, domain in enumerate(mixed_domain):
#     if domain['type'] == 'continuous':
#         lb, ub = domain['domain']
#         space = np.linspace(lb, ub, num_point)
#     else:
#         lb = domain['domain'][0]
#         ub = domain['domain'][-1]
#         space = [round(i) for i in np.linspace(lb, ub, num_point)]
#     for val in space:
#         x = x0.copy()
#         x[0, idx] = val
#         # print(x)
#         objective_function(x)

#%% Initial Data Feeding
init_ws_names = ["20250607_065115"]
data_init_per_case = []
for name in init_ws_names:
    init_ws = wb.Worksheets(name)
    used_range = init_ws.UsedRange
    data = used_range.Value
    init_df = pd.DataFrame(data[1:], columns=data[0])
    data_init_per_case.append(init_df)

data_init = pd.concat(data_init_per_case)
X_init = np.array(data_init.iloc[:, :dim_input])
Y_init = np.array(data_init.iloc[:, -1:])
#%%
init_data = 5
max_iter = 300

myBopt = GPyOpt.methods.BayesianOptimization(
    f=objective_function,
    domain=mixed_domain,
    constraints=Constraints,
    exact_feval=True,
    normalize_Y=False,
    verbosity=True,
    evaluator_type='thompson_sampling',
    initial_design_numdata=init_data,
    # X=X_init, Y=Y_init,
    acquisition='EI'
)

max_time = 100
eps = 1e-6

start = time.time()
myBopt.run_optimization(max_iter, eps=0)
end = time.time()
print(end-start)
np.round(myBopt.X, 2)

myBopt.plot_convergence()
myBopt.plot_acquisition()

# pythoncom.CoUninitialize()

#%%
# rws = wb.Worksheets("20250603_135559_BO_SEP")
fig, ax = plt.subplots(1, 2)
min_mjsp_row = []
for sheet_name in ["20250606_192743_D1", "20250607_065115_D2", "20250607_173844_D3"]:
    rws = wb.Worksheets(sheet_name)
    used_range = rws.UsedRange
    data = used_range.Value

    # Convert to DataFrame
    df = pd.DataFrame(data[1:], columns=data[0])

    ax[0].plot(df['OBJ'])

    min_mjsp_row.append(df.loc[df['OBJ'].idxmin()])
    mjsp_cummin = df['MJSP'].cummin()
    ax[1].plot(mjsp_cummin)

ax[0].grid(alpha=0.8)
ax[1].grid(alpha=0.8)
# plt.ylim([-1, 0])
plt.show()
res = pd.concat(min_mjsp_row, axis=1)

#%%
""" OLD
df['MJSP'].idxmin()
129
df['MJSP'].iloc[129]
1.189250238048201
df.iloc[129]
PYROTEMP    9.371966e+02
GAS.N       2.700000e+01
GAS.F       1.000000e+01
GAS.RR      1.000000e+00
SAF.N       2.900000e+01
SAF.F       1.400000e+01
SAF.RR      1.200000e+00
DSL.N       1.400000e+01
DSL.F       1.200000e+01
DSL.RR      1.400000e+00
TCC         5.075841e+08
TOC         5.443260e+07
TRC         7.970031e+07
TPS         7.661370e+07
TUC         1.588720e+07
SAF         2.074090e+02
MJSP        1.189250e+00
LHV         4.390301e+01
SG          7.834543e+02
SLF         1.143640e-13
ARM         2.483397e+01
MBP         8.072000e+01
MFP        -1.437564e+02
GT10        6.311957e+01
GT90        9.501768e+01
DFP         1.809810e+02
DT90        2.519635e+02
ERRSIM      0.000000e+00
ERR_0       0.000000e+00
ERR_1       0.000000e+00
ERR_2       0.000000e+00
ERR_3       0.000000e+00
ERR_4       0.000000e+00
ERR_5       0.000000e+00
ERR_6       0.000000e+00
ERR_7       0.000000e+00
ERR_8       0.000000e+00
ERR_9       0.000000e+00
ERR_10      0.000000e+00
ERR_11      0.000000e+00
OBJ         1.189250e+00
Name: 129, dtype: float64
"""

""" NEW
GAS.N     3.000000e+01
GAS.F     1.900000e+01
GAS.RR    1.134609e+01
SAF.N     1.500000e+01
SAF.F     1.300000e+01
SAF.RR    3.001860e-01
DSL.N     2.300000e+01
DSL.F     8.000000e+00
DSL.RR    6.614616e-01
TCC       3.271940e+08
TOC       1.654300e+08
TRC       7.992572e+07
TPS       7.759570e+07
TUC       1.576013e+07
SAF       2.324355e+02
MJSP      2.623729e+00
LHV       4.370256e+01
SG        8.017196e+02
SLF       1.110920e-13
ARM       2.122455e+01
MBP       1.009340e+02
MFP      -6.168704e+02
GT10      6.921963e+01
GT90      9.484466e+01
DFP       1.215220e+02
DT90      2.542530e+02
ERRSIM    0.000000e+00
ERR_0     0.000000e+00
ERR_1     0.000000e+00
ERR_2     0.000000e+00
ERR_3     0.000000e+00
ERR_4     0.000000e+00
ERR_5     0.000000e+00
ERR_6     0.000000e+00
ERR_7     0.000000e+00
ERR_8     0.000000e+00
ERR_9     0.000000e+00
ERR_10    0.000000e+00
ERR_11    0.000000e+00
OBJ       2.623729e+00
Name: 75, dtype: float64

"""