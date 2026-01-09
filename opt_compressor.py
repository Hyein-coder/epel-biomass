import time
import numpy as np
import os
import pythoncom
import win32com.client as win32
import matplotlib.pyplot as plt
import GPyOpt       # Number of variables no more than 20
from funs_opt import cal_MJSP
import pandas as pd
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

excel, wb = dispatch_excel_file("Pyrolysis_Jones_551_571_ASW_compressors")
ws = wb.Worksheets("Summary")

#%%
now = time.localtime()
now_str = time.strftime('%Y%m%d_%H%M%S', now)
wb.Worksheets.Add()
rws = excel.ActiveSheet
rws.Name = now_str
# ws.Activate()
#%%
GLOBAL_I = 0

init_pres_401 = 50
init_pres_631 = 15
fin_pres_415 = 365
fin_pres_639 = 365
pres_margin = 20

util_air_limit = 105
comp_inlet_limit = 200
mixed_domain = [
    {'name': 'E411.TEMP', 'type': 'continuous', 'domain': (util_air_limit, comp_inlet_limit), 'dimensionality': 1},     # 0
    {'name': 'E412.TEMP', 'type': 'continuous', 'domain': (util_air_limit, comp_inlet_limit), 'dimensionality': 1},     # 1
    {'name': 'E631.TEMP', 'type': 'continuous', 'domain': (util_air_limit, comp_inlet_limit), 'dimensionality': 1},     # 2
    {'name': 'E632.TEMP', 'type': 'continuous', 'domain': (util_air_limit, comp_inlet_limit), 'dimensionality': 1},     # 3
    {'name': 'E633.TEMP', 'type': 'continuous', 'domain': (util_air_limit, comp_inlet_limit), 'dimensionality': 1},     # 4
    {'name': 'C411.PRES', 'type': 'continuous', 'domain': (init_pres_401+pres_margin, fin_pres_415-pres_margin),
     'dimensionality': 1},      # 5
    {'name': 'C412.PRES', 'type': 'continuous', 'domain': (init_pres_401+pres_margin, fin_pres_415-pres_margin),
     'dimensionality': 1},      # 6
    {'name': 'C631.PRES', 'type': 'continuous', 'domain': (init_pres_631+pres_margin, fin_pres_639-80),
     'dimensionality': 1},      # 7
    {'name': 'C632.PRES', 'type': 'continuous', 'domain': (init_pres_631+pres_margin, fin_pres_639-80),
     'dimensionality': 1},      # 8
    {'name': 'C633.PRES', 'type': 'continuous', 'domain': (init_pres_631+pres_margin, fin_pres_639-80),
     'dimensionality': 1},      # 9
    {'name': 'C634.PRES', 'type': 'continuous', 'domain': (init_pres_631+pres_margin, fin_pres_639-80),
     'dimensionality': 1}       # 10
]
xdim = 11

Constraints = [
    {'name': 'c1', 'constraint': 'x[:,0] - x[:,1]'},
    {'name': 'c2', 'constraint': 'x[:,2] - x[:,3]'},
    {'name': 'c3', 'constraint': 'x[:,3] - x[:,4]'},
    {'name': 'l6', 'constraint': '1.5 - x[:,6] / (x[:,5]-5)'},
    {'name': 'l8', 'constraint': '1.5 - x[:,8] / x[:,7]'},
    {'name': 'l9', 'constraint': '1.5 - x[:,9] / (x[:,8]-5)'},
    {'name': 'l10', 'constraint': '1.5 - x[:,10] / (x[:,9]-5)'},
    {'name': 'u6', 'constraint': 'x[:,6] / (x[:,5]-5) - 3'},
    {'name': 'u8', 'constraint': 'x[:,8] / x[:,7] - 3'},
    {'name': 'u9', 'constraint': 'x[:,9] / (x[:,8]-5) - 3'},
    {'name': 'u10', 'constraint': 'x[:,10] / (x[:,9]-5) - 3'}
]

NameList = []
for i in range(len(mixed_domain)):
    NameList.append(mixed_domain[i]['name'])
dim_input = len(mixed_domain)

def run():
    # excel.Application.Run("AspenSimulationWorkbook.xla! ASWRestartActiveSimulation")
    # excel.Application.Run("AspenSimulationWorkbook.xla! ASWRunActiveSimulation")
    check_cell = ws.Range("C8")
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
                print("wait")
                time.sleep(20)

                for cnt_advance in range(10):
                    if check_prev == check_cell.Value:
                        print(f"Wait just in advance #{cnt_advance}")
                        time.sleep(5)
                    else:
                        break
                if check_prev == check_cell.Value:
                    print("still stuck")
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
    cost_cnt = 0
    while True:
        try:
            _dict = {
                "TCC": ws.Range("B4").Value,
                "TOC": ws.Range("B5").Value,
                "TRMC": ws.Range("B6").Value,
                "TPS": ws.Range("B7").Value,
                "TUC": ws.Range("C8").Value,
                "SAF": ws.Range("B13").Value
            }
            _dict["MJSP"] = cal_MJSP(_dict["SAF"], _dict["TCC"], _dict["TOC"] + _dict["TUC"], _dict["TPS"])
            return _dict
        except BaseException as e:
            if isinstance(e, KeyboardInterrupt):
                raise
            cost_cnt += 1
            time.sleep(1)
            assert cost_cnt < 10
            pass
a = get_cost()
dim_cost = len(a.keys())
rws.Range(rws.Cells(1, 1), rws.Cells(1, dim_input + dim_cost)).Value = NameList + list(a.keys())
rws.Range(rws.Cells(1, dim_input + dim_cost + 1), rws.Cells(1, dim_input + dim_cost + 1)).Value = ['ERROR']

def objective_function(x):
    global GLOBAL_I

    cntt = 0
    while True:
        try:
            print("Cool time")
            time.sleep(10)

            cell = ws.Range('G8:G18')
            x_val = x.tolist()[0]
            cell.Value = [[xx, ] for xx in x_val]
            time.sleep(1)

            e = run()

            GLOBAL_I += 1
            cost = get_cost()
            obj = cost["MJSP"]
            rws.Range(rws.Cells(GLOBAL_I+1, 1), rws.Cells(GLOBAL_I+1, dim_input)).Value = x_val
            rws.Range(rws.Cells(GLOBAL_I+1, dim_input+1), rws.Cells(GLOBAL_I+1, dim_input+dim_cost)).Value \
                = list(cost.values())
            rws.Range(rws.Cells(GLOBAL_I+1, dim_input+dim_cost+1), rws.Cells(GLOBAL_I+1, dim_input+dim_cost+1)).Value\
                = [e]
            rws.Range(rws.Cells(GLOBAL_I+1, dim_input+dim_cost+2), rws.Cells(GLOBAL_I+1, dim_input+dim_cost+2)).Value\
                = [obj+e]

            print(GLOBAL_I, ' : ', obj, ' iserror', e)
            wb.Save()
            return obj + e

        except BaseException as e:
            if isinstance(e, KeyboardInterrupt):
                raise
            cntt += 1
            print('Critical..', cntt)
            # time.sleep(10)
            assert cntt < 10

#%%
x0 = np.array([[
    130, 180, 200, 200, 200,
    226, 345, 49, 96, 140, 280]])
objective_function(x0)


#%%
num_point = 11

idx = 0
lb, ub = mixed_domain[idx]['domain']
space = np.linspace(lb, ub, num_point)
for val in space:
    x = x0.copy()
    x[0, idx] = val
    objective_function(x)

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
init_ws_names = ["20250603_135559"]
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
init_data = 20
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

used_range = rws.UsedRange
data = used_range.Value

# Convert to DataFrame
df = pd.DataFrame(data[1:], columns=data[0])

fig, ax = plt.subplots(1, 2)
ax[0].plot(df['MJSP'])
ax[0].grid(alpha=0.8)

min_mjsp_row = df.loc[df['MJSP'].idxmin()]
mjsp_cummin = df['MJSP'].cummin()
ax[1].plot(mjsp_cummin)
ax[1].grid(alpha=0.8)
# plt.ylim([-1, 0])
plt.show()

""" 20250609_014814_v572
E411.TEMP    1.314663e+02
E412.TEMP    1.356946e+02
E631.TEMP    1.087532e+02
E632.TEMP    1.180012e+02
E633.TEMP    1.321341e+02
C411.PRES    2.183072e+02
C412.PRES    3.272914e+02
C631.PRES    4.139116e+01
C632.PRES    9.270137e+01
C633.PRES    1.588731e+02
C634.PRES    2.826058e+02
TCC          3.433440e+08
TOC          1.640890e+08
TRMC         7.998150e+07
TPS          7.790640e+07
TUC         -8.547592e+06
SAF          2.334692e+02
MJSP         2.466227e+00
ERROR        0.000000e+00
None         2.466227e+00
Name: 76, dtype: float64
"""