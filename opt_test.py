import win32com.client as win32
import win32gui
import win32con
import os
import matplotlib.pyplot as plt
import pyautogui as pg
import time
import datetime
from funs_opt import AspenHandler
import pandas as pd
import numpy as np

"""
Refer just in case
https://github.com/YouMayCallMeJesus/AspenPlus-Python-Interface/blob/main/CodeLibrary.py#L215

"""
#%%

excel = win32.Dispatch("Excel.Application")
wb = None
for workbook in excel.Workbooks:
    if workbook.Name == 'Pyrolysis_533_ASW2.xlsx':
        wb = workbook
        break
if wb is None:
    wb = excel.Workbooks.Open(os.path.abspath('../Aspen/Pyrolysis_533_ASW2.xlsx'))
ws = wb.Worksheets("InteractiveSheet")

# ws.Activate()
excel.Run("AspenSimulationWorkbook.xla! ASWActivateActiveSimulation")
#%%
cell_in = ws.Range('B3:B13')
dim_in = len(cell_in)

GLOBAL_I = 1
val_try = [100, 120, 450, 450, 500]

def run(x):
    global GLOBAL_I
    cell_in.Value = [[v, ] for v in x]

    time.sleep(1)
    # Refer to AspenSimulationWkbook Manual
    excel.Run("AspenSimulationWorkbook.xla! ASWInitandRunActiveSimulation")
    time.sleep(15)
    print('Run_Completed?')
    error = None

    c = 0
    while True:
        try:
            c += 1
            time.sleep(1)
            state = excel.StatusBar
            if 'fail' in state.lower():
                print('FAIL')
                error = 'FAIL'
                break
            if 'false' in state.lower():
                print('PASSED!', str(c))
                time.sleep(45)
                print('Is Cost Result Ready?')
                error = 0
                break
            if c > 60:
                print('1_Minute_Passed')
                error = '1MINUTE'
                break
        except:
            print(c)
            if c > 60:
                raise RuntimeError('Error')
    return error

def get_cost():
    _dict = {
        "TCC": ws.Range("B17")(),
        "TOC": ws.Range("B18")(),
        "TRMC": ws.Range("B19")(),
        "TPS": ws.Range("B20")(),
        "TUC": ws.Range("B21")()
    }
    return _dict


#%%
now = time.localtime()
now_str = time.strftime('%Y%m%d_%H%M%S', now)
wb.Worksheets.Add()
rws = excel.ActiveSheet

rws.Name = now_str

name_input = ["E-411", "E-412", "E-632", "E-633", "E-634",
              "C-411", "C-412", "C-631", "C-632", "C-633", "C-634"]
name_output = ["OBJ", "TCC", "TOC", "TRMC", "TPS", "TUC"]
dim_out = len(name_output)
rws.Range(rws.Cells(1,1), rws.Cells(1,dim_in+dim_out)).Value = name_input + name_output
rws.Range(rws.Cells(1,dim_in+dim_out+1), rws.Cells(1,dim_in+dim_out+1)).Value = ["ERROR"]

#%%
def write_res(idx, val_in, error, val_out):
    rws.Range(rws.Cells(1+idx, 1), rws.Cells(1+idx, dim_in)).Value = val_in
    rws.Range(rws.Cells(1+idx, dim_in+1), rws.Cells(1+idx, dim_in+dim_out)).Value = val_out
    rws.Range(rws.Cells(1+idx, dim_in+dim_out+1), rws.Cells(1+idx, dim_in+dim_out+1)).Value = [error]

lb = [105, 105, 200, 200, 300, 1.2, 1.2, 1.2, 1.2, 1.2, 1.2]
ub = [240, 300, 500, 500, 600, 3, 3, 3, 3, 3, 3]

for i in range(3):
    val_rand = np.random.random(5).tolist()
    val_in_range = [l + (u-l)*r for r, l, u in zip(val_rand, lb, ub)]
    err = run(val_in_range)
    res = get_cost()
    obj = ws.Range("B31")()
    write_res(i+1, val_in_range, err, [obj] + [v for v in res.values()])

#%% APPLY FINAL PARAMETERS
xl_file = "../Aspen/Pyrolysis_533_ASW.xlsx"
with open(xl_file, 'rb') as f:
    result = pd.read_excel(f, sheet_name='20250508_223805')
result.rename(columns={'Unnamed: 11': "Error"}, inplace=True)

result['PenaltyObj'] = result['Obj'] + result['Error']
res_sorted = result.sort_values('PenaltyObj')

input_default = [110, 110, 400, 400, 540]
input_best = res_sorted.iloc[0,:5].to_list()

#%%
excel = win32.Dispatch("Excel.Application")
wb = None
for workbook in excel.Workbooks:
    if workbook.Name == 'Pyrolysis_533_ASW2.xlsx':
        wb = workbook
        break
if wb is None:
    wb = excel.Workbooks.Open(os.path.abspath('../Aspen/Pyrolysis_533_ASW2.xlsx'))
ws = wb.Worksheets("InteractiveSheet")
ws.Activate()
#%%
input_try = input_default
ws.Range('B3:B7').Value = [(i, ) for i in input_try]
time.sleep(1)
excel.Run("AspenSimulationWorkbook.xla! ASWCopyTagValuesToModel")
excel.Run("AspenSimulationWorkbook.xla! ASWInitandRunActiveSimulation")
time.sleep(15)
cnt = 0

while True:
    try:
        time.sleep(1)
        state = excel.StatusBar
        time.sleep(0.25)
        if 'FALSE' == state:
            print("Wait_for_Costing_Result")
            time.sleep(45)
            break
        elif 'fail' in state.lower():
            print('Error_Detected')
            break
        else:
            cnt += 1
            print('PASSED ', cnt)
            assert cnt < 60

    except:
        cnt += 1
        print('passed, ', cnt)
        assert cnt < 60

output_try = ws.Range('B12:B16')()
obj_try = ws.Range('B31')()

