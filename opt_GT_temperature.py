"""
Apply final parameters
"""
import pandas as pd
import win32com.client as win32
import os
import time

#%%
excel = win32.Dispatch("Excel.Application")
wb = None
for workbook in excel.Workbooks:
    if workbook.Name == 'Pyrolysis_564_ASW_GT_temperature.xlsx':
        wb = workbook
        break
if wb is None:
    wb = excel.Workbooks.Open(os.path.abspath('../Aspen/Pyrolysis_564_ASW_GT_temperature.xlsx'))
ws = wb.Worksheets("Input")
# ws.Activate()
ws_equip = wb.Worksheets("Equipment")
ws_summary = wb.Worksheets("Summary")
#%%
# gt_temp_list = [2500]
gt_temp_list = [1900, 2000, 2100, 2200, 2300, 2400]
res_list = []
cell_check = ws_summary.Range("B4")
for temp in gt_temp_list:
    ws.Range('B2').Value = temp
    check_prev = cell_check.Value

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

    if cell_check.Value == check_prev:
        print('Wait_Again')
        time.sleep(30)

    equip_data = ws_equip.Range("A5:B152")()
    reb_cost = {d[0]: d[1] for d in equip_data if '-reb' in d[0]}
    res_list.append((equip_data, reb_cost))

