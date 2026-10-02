import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

from funs import TEA
from plotting import plot_stack_bar

# _PLOTTING_STYLE.md (SA_RC lives only in the notebook; inlined here)
SA_RC = {
    'figure.dpi': 150, 'figure.facecolor': 'white', 'figure.autolayout': True,
    'axes.facecolor': 'white', 'axes.edgecolor': '#444444', 'axes.linewidth': 0.8,
    'axes.spines.top': True, 'axes.spines.right': True, 'axes.labelsize': 12,
    'axes.labelcolor': 'black', 'axes.labelweight': '500', 'axes.grid': False,
    'xtick.labelsize': 12, 'xtick.color': 'black', 'ytick.labelsize': 10, 'ytick.color': 'black',
    'font.family': 'sans-serif',
    'font.sans-serif': ['Helvetica Neue LT Pro', 'Helvetica Neue', 'Arial', 'DejaVu Sans'],
    'font.size': 10, 'font.weight': '300', 'text.color': 'black',
    'patch.edgecolor': 'black', 'patch.linewidth': 0.7, 'patch.force_edgecolor': True,
    'legend.fontsize': 8, 'legend.title_fontsize': 9, 'legend.framealpha': 0.0,
    'legend.edgecolor': '#444444', 'lines.linewidth': 0.7, 'lines.markersize': 3,
    'savefig.dpi': 150, 'savefig.bbox': 'tight', 'savefig.facecolor': 'white',
}

tea = TEA()

# case_scale = [7.5, 8.6, 10]
case_scale = [1, 2.5, 5, 7.5, 10, 20, 30]
fig_folder = os.path.join(os.getcwd(), 'Figure')
if not os.path.exists(fig_folder):
    os.makedirs(fig_folder)
fig_tag = 'wo_price_model'
name_h2_source = ['Base', 'SMR', 'Ammonia', 'PEM']

case_data = {'cost summary': [], 'Ammonia summary': [], 'Ammonia price': [], 'Util and raw material': [],
             'mjsp': [], 'Equipment': [], 'SAF Production': [], 'mjsp value': [], 'LCOH': [],
             'Ammonia equipment': [], 'Base equipment': [], 'Equip all case': [],
             'Mix summary': [],
             'CCS summary': [], 'CCS mjsp': []}
for n in case_scale:
    # 551 model: same simulation as tea_scale_up_price_models.py / tea_pareto_front.py
    file_stream = f'Process_Data\\Pyrolysis_551_Scale{int(n * 10):04d}_Streams.xlsx'
    file_apea = f'Process_Data\\Pyrolysis_551_Scale{int(n * 10):04d}_APEA.xlsm'  # Fixed Biomass Price
    df_mjsp, energy_production, annual_prod_saf, main_h2_demand, opex_names, data_all, name_h2_source_new = \
        tea.economic_analysis(file_stream, file_apea, name_h2_source, ccs_portion=0., ammonia_portion=0.655)

    dfp_per_h2_source = data_all['df_process']
    df_equip_sum, df_equip_all_case = tea.get_equipment_breakdown(file_apea, dfp_per_h2_source, name_h2_source_new)
    df_util_and_rawmaterial_sum, df_util_and_rawmaterial_rate = tea.get_util_and_rawmaterial_sum(file_apea, dfp_per_h2_source, name_h2_source_new)

    case_data['cost summary'].append(data_all['cost'][name_h2_source_new.index('Base')])
    case_data['Ammonia summary'].append(data_all['cost'][name_h2_source_new.index('Ammonia')])
    case_data['Mix summary'].append(data_all['cost'][name_h2_source_new.index('Mix')])
    case_data['Util and raw material'].append(df_util_and_rawmaterial_sum)
    case_data['mjsp'].append(df_mjsp)
    case_data['Equipment'].append(df_equip_sum)
    case_data['SAF Production'].append(annual_prod_saf)
    case_data['mjsp value'].append([data_all['cost'][i]['MJSP'] for i in range(len(name_h2_source))])

    # LCOH of subunits
    lcoh_smr, _, _ = tea.get_LCOH('SMR', main_h2_demand, opex_names)
    lcoh_ammonia, _, _ = tea.get_LCOH('Ammonia', main_h2_demand, opex_names)
    lcoh_pem, _, _ = tea.get_LCOH('PEM', main_h2_demand, opex_names)
    ammonia_info = tea.calc_cost_Ammonia(main_h2_demand)

    case_data['LCOH'].append([lcoh_smr, lcoh_ammonia, lcoh_pem])
    case_data['Ammonia price'].append(ammonia_info)

    file_ammonia = f'NH3_Cracking_130_scale{round(n * 10):04d}_APEAresult.xlsm'
    with open(os.path.join('Process_Data', file_ammonia), 'rb') as f:
        df_ammonia_equip = pd.read_excel(f, sheet_name='Equipment', header=2)
    case_data['Ammonia equipment'].append(df_ammonia_equip)

    with open(file_apea, 'rb') as f:
        df_base_equip = pd.read_excel(f, sheet_name='Equipment', header=2)
    case_data['Base equipment'].append(df_base_equip)
    case_data['Equip all case'].append(df_equip_all_case)

    df_mjsp_ccs, _, _, _, _, data_all_ccs, name_h2_source_new_ccs = \
        tea.economic_analysis(file_stream, file_apea, name_h2_source[:1], ccs_portion=.60, ammonia_portion=0.)
    case_data['CCS summary'].append(data_all_ccs['cost'][0])
    case_data['CCS mjsp'].append(df_mjsp_ccs)

cost_summary_all = pd.DataFrame(case_data['cost summary'])
cost_summary_all['case scale'] = case_scale
cost_summary_all['saf production'] = case_data['SAF Production']

cost_ammonia_all = pd.DataFrame(case_data['Ammonia summary'])
cost_ammonia_all['case scale'] = case_scale
cost_ammonia_all['saf production'] = case_data['SAF Production']

cost_mix_all = pd.DataFrame(case_data['Mix summary'])
cost_mix_all['case scale'] = case_scale
cost_mix_all['saf production'] = case_data['SAF Production']

cost_ccs_all = pd.DataFrame(case_data['CCS summary'])
cost_ccs_all['case scale'] = case_scale
cost_ccs_all['saf production'] = case_data['SAF Production']
#%% Scale-up graph
lca_colors = plt.cm.viridis(np.linspace(0, 1, 4))

fig, ax = plt.subplots(1, 4, figsize=(15,5))
ax[0].plot(cost_summary_all['case scale'], cost_summary_all['total CAPEX'], '-o', label='Base', color=lca_colors[0])
ax[0].plot(cost_mix_all['case scale'], cost_mix_all['total CAPEX'], '-o', label='Mix', color=lca_colors[2])
ax[0].plot(cost_ccs_all['case scale'], cost_ccs_all['total CAPEX'], '-o', label='CCS', color=lca_colors[3])
ax[0].plot(cost_summary_all['case scale'],
           [cost_summary_all['total CAPEX'].iloc[0] * scale for scale in case_scale],
           '-', linewidth=1, color='#3b3b3b')
ax[0].set_title('CAPEX [USD]')
ax[0].grid(axis='y', linestyle='--', alpha=0.7)
ax[0].grid(axis='x', linestyle='--', alpha=0.7)

ax[1].plot(cost_summary_all['case scale'], cost_summary_all['annual OPEX'], '-o', label='Base', color=lca_colors[0])
ax[1].plot(cost_mix_all['case scale'], cost_mix_all['annual OPEX'], '-o', label='Mix', color=lca_colors[2])
ax[1].plot(cost_ccs_all['case scale'], cost_ccs_all['annual OPEX'], '-o', label='CCS', color=lca_colors[3])
ax[1].set_title('OPEX [USD/year]')
ax[1].plot(cost_summary_all['case scale'],
           [cost_mix_all['annual OPEX'].iloc[0] * scale for scale in case_scale],
           '-', linewidth=1, color='#3b3b3b')
ax[1].grid(axis='y', linestyle='--', alpha=0.7)
ax[1].grid(axis='x', linestyle='--', alpha=0.7)

ax_coprod = ax[2]
ax_coprod.plot(cost_summary_all['case scale'], cost_summary_all['co-product sales'], '-o', label='Base', color=lca_colors[0])
ax_coprod.plot(cost_mix_all['case scale'], cost_mix_all['co-product sales'], '-o', label='Mix', color=lca_colors[2])
ax_coprod.plot(cost_ccs_all['case scale'], cost_ccs_all['co-product sales'], '-o', label='Mix', color=lca_colors[2])
ax_coprod.set_title('Co-product sales [USD/year]')
ax_coprod.grid(axis='y', linestyle='--', alpha=0.7)
ax_coprod.grid(axis='x', linestyle='--', alpha=0.7)

ax_mjsp = ax[3]
ax_mjsp.plot(cost_summary_all['case scale'], cost_summary_all['MJSP'], '-o', label='Base', color=lca_colors[0])
ax_mjsp.plot(cost_mix_all['case scale'], cost_mix_all['MJSP'], '-o', label='Mix', color=lca_colors[2])
ax_mjsp.plot(cost_ccs_all['case scale'], cost_ccs_all['MJSP'], '-o', label='CCS', color=lca_colors[3])
ax_mjsp.set_title('MJSP [USD/L SAF]')
ax_mjsp.grid(axis='y', linestyle='--', alpha=0.7)
ax_mjsp.grid(axis='x', linestyle='--', alpha=0.7)
ax_mjsp.legend()

plt.savefig(os.path.join(fig_folder, f'scale_up_{fig_tag}_mjsp.png'))
plt.savefig(os.path.join(fig_folder, f'scale_up_{fig_tag}_mjsp.eps'))
plt.show()

#%%
util_and_rawmaterial_all = {case: pd.DataFrame([d[case].map(lambda x: x/case_data['SAF Production'][idx])
                                                for idx, d in enumerate(case_data['Util and raw material'])],
                                               index=case_scale)
                            for case in case_data['Util and raw material'][0].columns}

fig, ax = plt.subplots(1, 2, figsize=(15,5))
cmap = plt.get_cmap("twilight")
colors = cmap(np.linspace(0, 1, len(util_and_rawmaterial_all['Base'].columns)+1))
markers = ["o", "s", "D", "^", "v", "<", ">", "p", "*", "h", "H", "+", "x", "|", "_"]

ax_base = ax[0]
for idx, c in enumerate(util_and_rawmaterial_all['Base'].columns):
    ax_base.plot(util_and_rawmaterial_all['Base'].index, util_and_rawmaterial_all['Base'][c],
                 label=c, color=colors[idx], marker=markers[idx])
ax_base.set_title('Base case')
ax_base.set_ylabel('MJSP [$/L SAF]')
ax_base.grid(axis='y', linestyle='--', alpha=0.7)
ax_base.grid(axis='x', linestyle='--', alpha=0.7)

ax_amm = ax[1]
for idx, c in enumerate(util_and_rawmaterial_all['Mix'].columns):
    ax_amm.plot(util_and_rawmaterial_all['Mix'].index, util_and_rawmaterial_all['Mix'][c],
                label=c, color=colors[idx], marker=markers[idx])
ax_amm.set_title('Mixed case')
ax_amm.grid(axis='y', linestyle='--', alpha=0.7)
ax_amm.grid(axis='x', linestyle='--', alpha=0.7)

title = 'Raw Materials and\n Utilities'
fig.legend(util_and_rawmaterial_all['Mix'].columns,
           loc='upper right', bbox_to_anchor=(.97, .9), title=title)
plt.tight_layout()
plt.subplots_adjust(right=0.85)  # Leave space for legend on the right

plt.savefig(os.path.join(fig_folder, f'scale_up_{fig_tag}_opex.png'))
plt.savefig(os.path.join(fig_folder, f'scale_up_{fig_tag}_opex.eps'))
plt.show()

#%% MJSP Breakdown
# x-axis in SAF production scale [MMt/yr]; short ton (2000 lb) -> metric tonne x0.907185
saf_mmt = [round(tea.get_annual_prod_saf_ton(
    f'Process_Data\\Pyrolysis_551_Scale{int(n * 10):04d}_Streams.xlsx') * 0.907185 / 1e6, 3)
    for n in case_scale]
mjsp_all = {case: pd.DataFrame([case_data['mjsp'][idx].loc[case] for idx in range(len(case_data['mjsp']))],
                               index=saf_mmt)
            for case in ['Ammonia', 'Mix']}
mjsp_ccs = {'Base': pd.DataFrame([case_data['CCS mjsp'][idx].loc['Base'] for idx in range(len(case_data['mjsp']))],
                               index=saf_mmt)}
# Base-case MJSP breakdown for base_summary (kept out of mjsp_all: line plot above uses 2 subplots)
mjsp_base = pd.DataFrame([case_data['mjsp'][idx].loc['Base'] for idx in range(len(case_data['mjsp']))],
                         index=saf_mmt)

fig, ax = plt.subplots(1, 2, figsize=(15,5), sharey='row')
colors = cmap(np.linspace(0, 1, len(mjsp_all['Ammonia'].columns)+1))
markers = ["o", "s", "D", "^", "v", "<", ">", "p", "*", "h", "H", "+", "x", "|", "_"]
for i_case, case in enumerate(mjsp_all.keys()):
    ax_case = ax[i_case]
    df_case = mjsp_all[case]
    for i_col, col in enumerate(df_case.columns):
        ax_case.plot(df_case.index[:6], df_case[col].iloc[:6], label=col, color=colors[i_col], marker=markers[i_col])
    ax_case.set_title(case)
    ax_case.grid(axis='y', linestyle='--', alpha=0.7)
    ax_case.grid(axis='x', linestyle='--', alpha=0.7)

title = 'MJSP [$/L SAF]'
fig.legend(mjsp_all['Ammonia'].columns, loc='upper right', bbox_to_anchor=(.97, .9), title=title)
plt.tight_layout()
plt.subplots_adjust(right=.8)
plt.show()

plt.rcParams.update(SA_RC)  # _PLOTTING_STYLE.md
colors_stack_bar = ['#FAE8BC', '#F0B1AC', '#BBDBB4', '#F5D3A6', '#8DB1B1', '#DAB7DB', '#E5C1C6', '#FBCBA4', '#B5D7EB']
plot_stack_bar(mjsp_all['Ammonia'], 'MJSP [$/L SAF]', colors_stack_bar,
               save_name=os.path.join(fig_folder, f'scale_up_{fig_tag}_Ammonia_summary'), figsize=(10,5),
               xlabel='SAF production [MMt/yr]', fs=13)
plot_stack_bar(mjsp_all['Mix'], 'MJSP [$/L SAF]', colors_stack_bar,
               save_name=os.path.join(fig_folder, f'scale_up_{fig_tag}_mix_summary'), figsize=(10,5),
               xlabel='SAF production [MMt/yr]', fs=13)
plot_stack_bar(mjsp_ccs['Base'], 'MJSP [$/L SAF]', colors_stack_bar,
               save_name=os.path.join(fig_folder, f'scale_up_{fig_tag}_ccs_summary'), figsize=(10,5),
               xlabel='SAF production [MMt/yr]', fs=13)
mjsp_base.rename_axis('saf production [MMt/yr]').to_excel(os.path.join('Result', 'scale_up_base_summary.xlsx'))   # data sheet for plot_scale_up_from_xlsx.py
# §3.1 figure: same size/fonts as scale_up_price_model_mjsp (SA_RC, 3-decimal x labels)
plot_stack_bar(mjsp_base.set_axis([f'{v:.3f}' for v in mjsp_base.index]), 'MJSP [$/L SAF]', colors_stack_bar,
               save_name=os.path.join(fig_folder, f'scale_up_{fig_tag}_base_summary'), figsize=(9, 3.6),
               xlabel='SAF production [MMt/yr]', fs=None)

#%%
ratio_mjsp_to_capex = {
    case: [mjsp_all[case]['capital investment'].iloc[idx] / df[case].sum()
           for idx, df in enumerate(case_data['Equipment'])]
    for case in ['Ammonia', 'Mix']
}

equip_all = {case: pd.DataFrame([df[case].map(lambda x: x * ratio_mjsp_to_capex[case][idx])
                                 for idx, df in enumerate(case_data['Equipment'])],
                                index=case_scale) for case in ['Ammonia', 'Mix']}
params = {
    'legend.fontsize': 'x-large',
    'axes.labelsize': 'xx-large',
    'axes.titlesize': 'xx-large',
    'xtick.labelsize': 'x-large',
    'ytick.labelsize': 'x-large'}
plt.rcParams.update(params)

# fig, ax = plt.subplots(1, 2, figsize=(15,5), sharey='row')
fig, ax = plt.subplots(figsize=(9,5))
colors = cmap(np.linspace(0, 1, len(equip_all['Ammonia'].columns)+1))
markers = ["o", "s", "D", "^", "v", "<", ">", "p", "*", "h", "H", "+", "x", "|", "_"]
# for i_case, case in enumerate(equip_all.keys()):
i_case = 0
case = "Mix"
ax_case = ax
df_case = equip_all[case]
for i_col, col in enumerate(df_case.columns):
    ax_case.plot(df_case[col].index.astype(str), df_case[col], label=col, color=colors[i_col], marker=markers[i_col])
# ax_case.set_title(case)
ax_case.grid(axis='y', linestyle='--', alpha=0.7)
ax_case.grid(axis='x', linestyle='--', alpha=0.7)

ax.set_ylabel('MJSP [$/L SAF]')
title = 'CAPEX Breakdown'
fig.legend(equip_all['Ammonia'].columns, loc='upper left',
           bbox_to_anchor=(.62, .9))
plt.tight_layout()
plt.subplots_adjust(right=.61)
plt.savefig(os.path.join(fig_folder, f'scale_up_{fig_tag}_capex'))
plt.show()

# label_lim = 0.01
# plot_stack_bar(equip_all['Base'], 'Base Case CAPEX [$/L SAF]', colors_stack_bar, label_lim)
# plot_stack_bar(equip_all['Ammonia'], 'Ammonia Case CAPEX [$/L SAF]', colors_stack_bar, label_lim)
#

#%% Draw MJSP Record
df_mjsp_value = pd.DataFrame(case_data['mjsp value'])

#%% Equipment Inspection
ammonia_fert_sales = [ai[1] for ai in case_data['Ammonia price']]
ammonia_demand = [ai[3] for ai in case_data['Ammonia price']]
ammonia_cost = [ai[4] for ai in case_data['Ammonia price']]
ammonia_equip = [ai[['Component Name', 'Total Direct Cost']] for ai in case_data['Ammonia equipment']]
base_equip = [ai[['Component Name', 'Total Direct Cost']].set_index('Component Name')
              for ai in case_data['Base equipment']]
base_equip_concat = pd.concat([be[~be.index.isna()] for be in base_equip], axis=1, join='outer')
base_equip_concat.columns = case_scale

#%
base_equip_categorized = [ai[0].set_index('Component Name') for ai in case_data['Equip all case']]
base_uni_category_data = [be.query('Category == "Offgas Combustion"') for be in base_equip_categorized]
base_uni_category = pd.concat([be['Total Direct Cost'] for be in base_uni_category_data], axis=1, join='outer')
base_uni_category.columns = case_scale

cmap = plt.get_cmap('nipy_spectral')
num_lines = len(base_uni_category)
colors = [cmap(i / num_lines) for i in range(num_lines)]

for i, (idx, row) in enumerate(base_uni_category.iterrows()):
    plt.plot(base_uni_category.columns, row, label=f'Row {idx}', color=colors[i])
plt.legend()
plt.show()

#%
base_equip_categorized = [ai[0].set_index('Component Name') for ai in case_data['Equip all case']]
base_dupli_unit_data = [be[be.index.str.startswith('GT')] for be in base_equip_categorized]
base_dupli_unit = pd.concat([be['Total Direct Cost'] for be in base_dupli_unit_data], axis=1, join='outer')
base_dupli_unit.columns = case_scale

cmap = plt.get_cmap('nipy_spectral')
num_lines = len(base_dupli_unit)
colors = [cmap(i / num_lines) for i in range(num_lines)]
plt.plot(base_dupli_unit.columns, base_dupli_unit.sum(axis=0))
# for i, (idx, row) in enumerate(base_dupli_unit.iterrows()):
#     plt.plot(base_dupli_unit.columns, row, label=f'Row {idx}', color=colors[i])
# plt.legend()
plt.show()
#%
base_equip_sorted = base_equip_concat[[10.0, 18.5, 20.0]].sort_values(by=10.0, ascending=False)
count = 0
for idx, row in base_equip_sorted.iterrows():
    count += 1
    if count > 20:
        plt.plot(base_equip_sorted.columns, row, label=f'Row {idx}')
plt.show()
# ammonia_equip_concat = pd.concat([ae.set_index('Component Name') for ae in ammonia_equip], axis=1)

#%% Ammonia economies of scale
lcoh_ammonia_data = [lcoh[1] for lcoh in case_data['LCOH']]
grey_h2_price = 0.68

plt.plot(case_scale, lcoh_ammonia_data, '-o', color='black', label='Ammonia Cracking')
plt.axhline(grey_h2_price, color='black', linestyle='--', linewidth=2, label='Grey H2')
plt.grid(linestyle=':', alpha=0.7)
plt.ylabel(r'LCOH [\$/lb H$_2$]')
plt.tight_layout()
plt.show()
