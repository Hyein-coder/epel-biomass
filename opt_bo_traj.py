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

def get_data(ws):
    used_range = ws.UsedRange
    data = used_range.Value
    _df = pd.DataFrame(data[1:], columns=data[0])
    return _df

#%%
f_pyro = "Pyrolysis_Jones_571_ASW"
excel, wb_pyro = dispatch_excel_file(f_pyro)
pyro_data = []
for sheet_pyro in ['20250606_192743_D1', '20250607_065115_D2', '20250607_173844_D3']:
    pyro_ws = wb_pyro.Worksheets(sheet_pyro)
    pyro_data.append(get_data(pyro_ws))

_, wb_comp = dispatch_excel_file("Pyrolysis_Jones_551_571_ASW_compressors")
comp_data = []
for sheet_comp in ['20250609_014814_v572']:
    comp_ws = wb_comp.Worksheets(sheet_comp)
    comp_data.append(get_data(comp_ws))

fig_folder = os.path.join(os.getcwd(), 'Figure_BO')

#%%
name = ['Distillation Columns', 'Compressors']
params = {
    'legend.fontsize': 'x-large',
    'axes.labelsize': 'xx-large',
    'axes.titlesize': 'xx-large',
    'xtick.labelsize': 'x-large',
    'ytick.labelsize': 'x-large'}
plt.rcParams.update(params)

fig, ax = plt.subplots(1, 2, sharey=True, figsize=(8,5))
for idx, d_idx in enumerate([pyro_data, comp_data]):
    axi = ax[idx]
    for di in d_idx:
        axi.plot(di['MJSP'].cummin() - di['MJSP'].iloc[0], linewidth=2)
    axi.grid(alpha=0.8)
    axi.set_title(name[idx])
    if idx < 1:
        axi.set_ylabel('Improved MJSP [$/L]')

plt.tight_layout()
plt.savefig(os.path.join(fig_folder, 'bo_improvement.png'))
plt.savefig(os.path.join(fig_folder, 'bo_improvement.eps'))

plt.show()
