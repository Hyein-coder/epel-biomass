import pandas as pd
import pythoncom
import win32com.client as win32
import os
import time
import numpy as np
from funs_opt import cal_MJSP, generate_perturbed_samples
import matplotlib.pyplot as plt

fig_folder = os.path.join(os.getcwd(), 'Figure_BO')
#%%
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
rws = wb.Worksheets("20250608_211122_TSOL2")

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

constraint = {
    'LHV': (42.8, np.inf),
    'SG': (775, 840),
    'SLF': (0, 0.3),
    'MBP': (38, np.inf),
    'MFP': (-np.inf, -40),
    'ARM': (8, 25),
    'GT10': (-np.inf, 70),
    'GT90': (-np.inf, 170),
    'DFP': (40, np.inf),
    'DT90': (-np.inf, 360)
}

#%%
used_range = rws.UsedRange
data = used_range.Value

df = pd.DataFrame(data[1:], columns=data[0])
df = df.dropna()
df_diff = df - df.iloc[0]
df_diff['tag'] = ['Origin'] + [d['component'] for d in input_domain for _ in d['equivalent']]

quality = ['LHV', 'SG', 'SLF', 'ARM', 'MBP', 'GT10', 'GT90', 'DFP', 'DT90']  # 'MFP',
prop_to_draw = quality + ['SAF']
prop_units = ['MJ/kg', '-', 'wt%', 'vol%', '°C', '°C', '°C', '°C', '°C', 'cuft/hr']

d_max = df_diff[prop_to_draw].max().max()
d_min = df_diff[prop_to_draw].min().min()
quality_diff = [
    np.array([constraint[k][0] - df.iloc[0][k] for k in quality]),
    np.array([constraint[k][1] - df.iloc[0][k] for k in quality])
]
quality_diff_in_range = [np.maximum(np.minimum(qd, d_max+200), d_min-200) for qd in quality_diff]
quality_mean = sum([x for x in quality_diff_in_range])/2
quality_err = quality_diff_in_range[1] - quality_mean

marker_tag = ['o', '^', 'x', 'd', '*']
color_tag = ['r', 'b', 'g', 'orange', 'purple']
list_tag = [d['component'] for d in input_domain]

params = {
    'legend.fontsize': 'x-large',
    'axes.labelsize': 'x-large',
    'axes.titlesize': 'xx-large',
    'xtick.labelsize': 'x-large',
    'ytick.labelsize': 'x-large'}
plt.rcParams.update(params)

fig, ax = plt.subplots(figsize=(9, 5))
ax.errorbar(quality, quality_mean, yerr=quality_err, fmt='.', markersize=0.1, color='k',
            capsize=8, ecolor='k', elinewidth=1.2)
plotted_tags = set()
for k in df_diff.index[1:]:
    tag = df_diff.iloc[k]['tag']
    idx_tag = list_tag.index(tag)
    label = tag if tag not in plotted_tags else None
    ax.plot(prop_to_draw, df_diff.iloc[k][prop_to_draw], marker_tag[idx_tag], color=color_tag[idx_tag], label=label,
            markersize=8)
    plotted_tags.add(tag)
ax.set_ylim([d_min-15, d_max+15])
plt.xticks(np.arange(len(prop_to_draw)), labels=[f'{p}\n({u})' for p, u in zip(prop_to_draw, prop_units)],
           rotation=0)
ax.grid(alpha=0.8, linestyle='--')
ax.legend(loc='upper left', bbox_to_anchor=(1,1))
plt.tight_layout()

plt.savefig(os.path.join(fig_folder, 'oil_compound_sensitivity_nocut.png'))
plt.savefig(os.path.join(fig_folder, 'oil_compound_sensitivity_nocut.eps'))

plt.show()

#%% Draw MFP
df['change'] = ['Origin'] + [equiv for d in input_domain for equiv in d['equivalent']]
df['tag'] = ['Origin'] + [d['component'] for d in input_domain for _ in d['equivalent']]
quality_special = 'MFP'
unit_special = '°C'
bottom = -273.15

fig, ax = plt.subplots()
for idx, tag in enumerate(list_tag):
    df_tag = df[df['tag'] == tag]
    df_valid = df_tag[df_tag['MFP'] > -270]
    ax.bar(df_valid['change'], df_valid[quality_special]-bottom, color=color_tag[idx], bottom=bottom)
# ax.bar(df['change'], df[quality_special])
ax.axhline(constraint[quality_special][1], linestyle='--', color='k')
ax.tick_params(axis='x', labelrotation=-45)
ax.set_ylabel(f'{quality_special} ({unit_special})')
ax.grid(axis='y', alpha=0.7)
plt.tight_layout()

plt.savefig(os.path.join(fig_folder, f'oil_compound_{quality_special}_nocut.png'))
plt.savefig(os.path.join(fig_folder, f'oil_compound_{quality_special}_nocut.eps'))

plt.show()

