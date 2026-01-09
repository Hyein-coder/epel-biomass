import pandas as pd
import pythoncom
import win32com.client as win32
import os
import time
import numpy as np
from funs_opt import cal_MJSP, generate_perturbed_samples
#%%
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

excel, wb = dispatch_excel_file("Pyrolysis_Jones_571_ASW")

ws = wb.Worksheets("InteractiveSheet")
# ws.Activate()

#%%
input_domain = [
    {'component': 'PHENOLS', 'mw': 150, 'coeff': 2.2,
     'equivalent': ['PHENOL1', 'PHENOL2', 'PHENOL3'], 'equiv_mw': [108, 110, 154], 'equiv_coeff': [3.06, 3, 2.14]},
    {'component': 'CYC-5A', 'mw': 98, 'coeff': 1.8,
     'equivalent': ['CYC-5A1'], 'equiv_mw': [84], 'equiv_coeff': [2.1]},
    {'component': 'CYC-6A', 'mw': 84, 'coeff': 2.4,
     'equivalent': ['CYC-6A1', 'CYC-6A2', 'CYC-6A3'], 'equiv_mw': [98, 114, 98], 'equiv_coeff': [2.06, 1.77, 2.06]},
    {'component': 'ARM-A', 'mw': 106, 'coeff': 3.5,
     'equivalent': ['ARM-A1', 'ARM-A2'], 'equiv_mw': [108, 138], 'equiv_coeff': [3.44, 2.69]},
    {'component': 'ARM-B', 'mw': 132, 'coeff': 1.5,
     'equivalent': ['ARM-B1', 'ARM-B2'], 'equiv_mw': [160, 152], 'equiv_coeff': [1.24, 1.30]}
]
input_name = []

for d in input_domain:
    input_name.extend([d['component']] + d['equivalent'])

dim_input = sum([len(d['equivalent'])+1 for d in input_domain])
input_cell = ws.Range("B64:B79")
input_original = input_cell.Value
print(f"Does input dimension match?  {bool(len(input_cell)==dim_input)}")

#%%
check_cell = ws.Range("N5")

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
                print("wait")
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

            # C <= 0
            _const = [
                (42.8 - _dict["LHV"]) / 42.8,
                (775 - _dict["SG"]) / 775,
                (_dict["SG"] - 840) / 840,
                (_dict["MFP"] + 40) / 40,
                (38 - _dict["MBP"]) / 38,
                (8 - _dict["ARM"]) / 8,
                (_dict["ARM"] - 25) / 25,
                (_dict["SLF"] - 0.0032) / 0.0032,
                (_dict["GT10"] - 70) / 70,
                (_dict["GT90"] - 170) / 170,
                (40 - _dict["DFP"]) / 40,
                (_dict["DT90"] - 360) / 360,
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

rec_list = input_name + cost_name + ["MJSP"] + qual_name + ["ERRSIM"] + [f'ERR_{i}' for i in range(dim_qual_const)]
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
            # violate = [0]

            rws.Range(rws.Cells(GLOBAL_I+1, 1), rws.Cells(GLOBAL_I+1, dim_rec)).Value =\
                x_val + list(cost.values()) + list(quality.values()) + [e_sim] + violate

            print(f"{GLOBAL_I}: {cost['MJSP']}, error: {e_sim + sum(violate)}")
            wb.Save()
            return cost['MJSP'] + e_sim + sum(violate)

        except BaseException as e:
            if isinstance(e, KeyboardInterrupt):
                raise
            cntt += 1
            print('Critical..', cntt)
            assert cntt < 10

#%%
x0 = np.array([[
    2.2, 0, 0, 0, 1.8, 0, 2.4, 0, 0, 0, 3.5, 0, 0, 1.5, 0, 0
]])
objective_function(x0)

#%%
for domain in input_domain:
    comp_original = domain['component']
    idx_original = input_name.index(comp_original)
    for comp_equiv, coeff in zip(domain['equivalent'], domain['equiv_coeff']):
        # if comp_equiv in ['PHENOL1', 'PHENOL2', 'ARM-A2']:
        x = x0.copy()
        x[0, idx_original] = 0
        x[0, input_name.index(comp_equiv)] = coeff
        # print(x)
        objective_function(x)
# pythoncom.CoUninitialize()

#%%
import pandas as pd
import matplotlib.pyplot as plt


used_range = rws.UsedRange
data = used_range.Value

df = pd.DataFrame(data[1:], columns=data[0])
df = df.dropna()
df['tag'] = ['Origin'] + ['']