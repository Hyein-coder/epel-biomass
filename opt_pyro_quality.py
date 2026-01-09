import pythoncom
import win32com.client as win32
import os
import time
import pandas as pd
import numpy as np
from funs_opt import cal_MJSP
import GPyOpt

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
    excel.Run("AspenSimulationWorkbook.xla! ASWActivateActiveSimulation")
    return excel, wb

excel, wb = dispatch_excel_file("Pyrolysis_Jones_565_ASW_woFP")

ws = wb.Worksheets("InteractiveSheet")
# ws.Activate()

#%%
""" Deactivate T-310 & 320 Calculators """
# mixed_domain = [
#     {'name': 'SAF.DF', 'type': 'continuous', 'domain': (0.33, 0.66), 'dimensionality': 1},   # 1
#     {'name': 'DSL.DF', 'type': 'continuous', 'domain': (.535, 1.), 'dimensionality': 1}    # 2
# ]
mixed_domain = [
    {'name': 'SAF.DF', 'type': 'continuous', 'domain': (0.33, 0.16), 'dimensionality': 1},   # 1
    {'name': 'DSL.DF', 'type': 'continuous', 'domain': (.535, .25), 'dimensionality': 1}    # 2
]

NameList = []
for i in range(len(mixed_domain)):
    NameList.append(mixed_domain[i]['name'])
dim_input = len(mixed_domain)

check_cell = ws.Range("N29")
input_cell = ws.Range("B34:B35")
print(f"Does input dimension match?  {bool(len(input_cell)==dim_input)}")

cost_cell = ws.Range("N29")
cost_name = ["SAF"]
dim_cost = len(cost_name)

qual_cell = ws.Range("M2:M6")
qual_name = ["LHV", "SG", "SLF", "ARM", "MBP"]
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
                time.sleep(10)

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

        except:
            cnt += 1
            print('passed, ', cnt)
            assert cnt < 60

def get_cost():
    cnt_cost = 0
    while True:
        try:
            _val = cost_cell.Value
            if not isinstance(_val, list):
                _val = [[_val]]
            _dict = {
                k: v[0] for k, v in zip(cost_name, _val)
            }
            return _dict
        except:
            cnt_cost += 1
            time.sleep(0.5)
            assert cnt_cost < 20
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

            # C <= 0
            _const = [
                42.8 - _dict["LHV"],
                775 - _dict["SG"],
                _dict["SG"] - 840,
                # _dict["MFP"] + 40,
                38 - _dict["MBP"],
                0.08 - _dict["ARM"],
                _dict["ARM"] - 0.25,
                _dict["SLF"] - 0.0032
            ]

            _violate = [(v > 0) * 10 for v in _const]
            return _violate, _dict
        except:
            _cnt += 1
            time.sleep(0.5)
            assert _cnt < 10
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

rec_list = NameList + qual_name + cost_name + ["ERRSIM"] + [f'ERR_{i}' for i in range(dim_qual_const)]
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
            time.sleep(10)
            x_val = x.tolist()[0]
            input_cell.Value = [[xx, ] for xx in x_val]
            time.sleep(1)

            e_sim = run()
            GLOBAL_I += 1
            cost = get_cost()
            violate, quality = check_quality()
            rws.Range(rws.Cells(GLOBAL_I+1, 1), rws.Cells(GLOBAL_I+1, dim_rec)).Value =\
                x_val + list(quality.values()) + list(cost.values()) + [e_sim] + violate
            print(f"{GLOBAL_I} - error: {e_sim + sum(violate)}")
            wb.Save()
            return e_sim + sum(violate)

        except:
            cntt += 1
            print('Critical..', cntt)
            assert cntt < 10

#%%
x = np.array([[0.3345, 0.538]])
objective_function(x)

#%%
x0 = np.array([[0.3345, 0.535]])
num_point = 30
# idx = 2
# lb, ub = mixed_domain[idx]['domain']
# space = np.linspace(lb, ub, num_point)
# for val in space:
#     x = x0.copy()
#     x[0, idx] = val
#     objective_function(x)

for idx, domain in enumerate(mixed_domain):
    if domain['type'] == 'continuous':
        lb, ub = domain['domain']
        space = np.linspace(lb, ub, num_point)
    else:
        lb = domain['domain'][0]
        ub = domain['domain'][-1]
        space = [round(i) for i in np.linspace(lb, ub, num_point)]
    for val in space:
        x = x0.copy()
        x[0, idx] = val
        # print(val)
        objective_function(x)
""" Changing a single variable does not satisfy the quality condition. """

#%%
init_data = 50
max_iter = 500

# init_ws = wb.Worksheets("Init")
# X_init, Y_init = [], []
# i = 2
# while init_ws.Cells(i, 1)() != None:
#     X_init.append(init_ws.Range(init_ws.Cells(i, 1), init_ws.Cells(i, dim_input))()[0])
#     Y_init.append([init_ws.Cells(i, 'Q')()])
#     i += 1
# X_init = np.array(X_init)
# Y_init = np.array(Y_init)

myBopt = GPyOpt.methods.BayesianOptimization(
    f=objective_function,
    domain=mixed_domain,
    exact_feval=True,
    normalize_Y=False,
    verbosity=True,
    evaluator_type='thompson_sampling',
    initial_design_numdata=init_data,
    acquisition='EI'
)

start = time.time()
myBopt.run_optimization(max_iter, eps=0)
end = time.time()
print(end-start)
np.round(myBopt.X, 2)

myBopt.plot_convergence()
myBopt.plot_acquisition()

# pythoncom.CoUninitialize()

