import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

from funs import TEA

tea = TEA()
operation_hr = 8000

case_scale = [1, 2.5, 5, 7.5, 10, 20, 30]
case_price_model_and_folder = [
    ('FR Price', 'Process_Data'),
    ('FR-Log Linear', 'Process_Data\\galik_naive'),
    ('Fixed Elasticity', 'Process_Data\\galik_elasticity_fixed_0.3')
]
# case_price_model_and_folder = [
#     ('FR Price', 'Process_Data'),
#     ('FR-Log Linear', 'Process_Data\\Pyrolysis_572_galik_naive'),
#     ('Fixed Elasticity', 'Process_Data\\Pyrolysis_572_galik_elasticity_fixed')
# ]
name_h2_source = ['Base', 'Ammonia']

fig_folder = os.path.join(os.getcwd(), 'Figure')
if not os.path.exists(fig_folder):
    os.makedirs(fig_folder)

case_data = {'Case Scale': [], 'Base': [], 'Ammonia': [], 'SAF Production': [],
             'Price Model': [], 'Biomass Price': [], 'Biomass Feed': [],
             'CCS': [], 'MJSP': []}
for model, folder in case_price_model_and_folder:
    for n in case_scale:
        print(model, str(n))
        file_stream = f'Process_Data\\Pyrolysis_551_Scale{int(n * 10):04d}_Streams.xlsx'
        file_apea = folder + f'\\Pyrolysis_551_Scale{int(n * 10):04d}_APEA.xlsm'
        # file_stream = f'Process_Data\\Pyrolysis_Jones_572_2MC_{int(n * 10):04d}_Streams.xlsx'
        # file_apea = folder + f'\\Pyrolysis_Jones_572_2MC_{int(n * 10):04d}_APEAresults.xlsm'

        # full ammonia (ammonia_portion=None -> 'Ammonia' row, all grey H2 stripped) and full CCS (ccs_portion=1.0)
        df_mjsp, energy_production, annual_prod_saf, main_h2_demand, opex_names, data_all, name_h2_source_new = \
            tea.economic_analysis(file_stream, file_apea, name_h2_source)
        df_mjsp_ccs, _, _, _, _, data_ccs, _ = \
            tea.economic_analysis(file_stream, file_apea, name_h2_source[:1], ccs_portion=1.0)
        df_mjsp_all = pd.concat([df_mjsp.loc[['Base', 'Ammonia']], df_mjsp_ccs])
        df_mjsp_all.index = ['Base', 'Ammonia', 'CCS']

        annual_prod_saf_ton = tea.get_annual_prod_saf_ton(file_stream)  # ton/yr
        biomass_info = tea.get_biomass_info(file_apea)

        case_data['Case Scale'].append(n)
        case_data['SAF Production'].append(annual_prod_saf_ton)     # ton/yr
        case_data['MJSP'].append(df_mjsp_all)

        case_data['Base'].append(data_all['cost'][name_h2_source_new.index('Base')])
        case_data['Ammonia'].append(data_all['cost'][name_h2_source_new.index('Ammonia')])
        case_data['CCS'].append(data_ccs['cost'][name_h2_source_new.index('Base')])

        case_data['Price Model'].append(model)
        case_data['Biomass Price'].append(biomass_info['Price [$/lb]'])
        case_data['Biomass Feed'].append(biomass_info['Demand [lb/hr]'])

cost_base_all = pd.DataFrame(case_data['Base'])
cost_base_all['case scale'] = case_data['Case Scale']
cost_base_all['case price model'] = case_data['Price Model']
cost_base_all['biomass price'] = case_data['Biomass Price']
cost_base_all['biomass feed'] = case_data['Biomass Feed']
cost_base_all['saf production'] = case_data['SAF Production']

cost_ammonia_all = pd.DataFrame(case_data['Ammonia'])
cost_ammonia_all['case scale'] = case_data['Case Scale']
cost_ammonia_all['case price model'] = case_data['Price Model']
cost_ammonia_all['biomass price'] = case_data['Biomass Price']
cost_ammonia_all['biomass feed'] = case_data['Biomass Feed']
cost_ammonia_all['saf production'] = case_data['SAF Production']

cost_ccs_all = pd.DataFrame(case_data['CCS'])
cost_ccs_all['case scale'] = case_data['Case Scale']
cost_ccs_all['case price model'] = case_data['Price Model']
cost_ccs_all['biomass price'] = case_data['Biomass Price']
cost_ccs_all['biomass feed'] = case_data['Biomass Feed']
cost_ccs_all['saf production'] = case_data['SAF Production']

#%%
unique_cats = cost_base_all['case price model'].unique()
df_price = pd.concat([cost_base_all.query(f"`case price model`=='{model}'")['biomass price'].reset_index(drop=True)
                      for model in unique_cats], axis=1)
df_price.columns = unique_cats
df_price.index = case_scale

mjsp = {}
for name, df in {"Base": cost_base_all, "Ammonia": cost_ammonia_all, "CCS": cost_ccs_all}.items():
    data_chosen = pd.concat([df.query(f"`case price model`=='{model}'")['MJSP'].reset_index(drop=True)
                             for model in unique_cats], axis=1)
    data_chosen.columns = unique_cats
    data_chosen.index = case_scale
    mjsp[name] = data_chosen

supply_rate_in_tpd = {
    "Forest Residue": 3127378 / operation_hr * 24,
    "Log": (2843071 + 3274200) / operation_hr * 24
}   # ton/day
supply_rate_in_coverage = {
    k: v/(case_data['Biomass Feed'][0] * 24 / 2e3) for k, v in supply_rate_in_tpd.items()
}

# _PLOTTING_STYLE.md SA_RC (no grid/title, transparent legend, png only)
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
plt.rcParams.update(SA_RC)

bar_colors = ['#F0B1AC', '#BBDBB4', '#B5D7EB']   # one color per price model (MJSP bars); from base_summary palette
styles_price = ['-', '-.', ':']      # one linestyle per price model (biomass price lines)
markers_model = ['o', 'x', '^']      # one marker per price model

# x-axis = SAF production [MMt/yr] (scale-only; identical across price models and H2 configs)
m0 = unique_cats[0]
saf_mmt = (cost_base_all[cost_base_all['case price model'] == m0]
           .set_index('case scale').loc[case_scale, 'saf production'] / 1e6)
xlabels = [f'{v:.3f}' for v in saf_mmt]

x = np.arange(len(case_scale))

# --- Figure 1 (_base): bar = MJSP of Base plant per price model; line = biomass price ---
mjsp_bar = mjsp['Base']
fig, ax = plt.subplots(figsize=(9, 4.5))
mjsp_bar.plot(kind='bar', color=bar_colors, edgecolor='black', ax=ax, width=0.7)   # MJSP bars, one color per price model
ax.set_ylabel("MJSP [$/L SAF]")
ax.set_xlabel("SAF production [MMt/yr]")
ax.set_xticklabels(xlabels, rotation=0)
ax.set_ylim(0, ax.get_ylim()[1] * 1.2)

ax2 = ax.twinx()
for price_idx, col in enumerate(df_price.columns):   # biomass price lines, all black
    ax2.plot(x, df_price[col], color='black', marker=markers_model[price_idx],
             linestyle=styles_price[price_idx], linewidth=2, markersize=5, label=col)
ax2.set_ylabel("Biomass price [$/lb]")
ax2.set_ylim(0, ax2.get_ylim()[1] * 1.2)

handles, labels = ax.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax.legend(handles + h2, labels + l2, loc='upper left')
plt.savefig(os.path.join(fig_folder, 'scale_up_price_model_mjsp_base.png'))

# --- Figure 2: bar = biomass price per price model (hatched); line = MJSP mean + price-model range band per case ---
bar_hatches = ['///', 'xxx', '...']   # color-free bars, one hatch per price model
line_colors = ['#D6AE5C', '#D57F78', '#85B27C']   # base_summary palette, darkened: Base / Ammonia / CCS
case_styles = ['-', '--', ':']       # one linestyle per case
case_markers = ['o', 's', '^']       # one marker per case

fig, ax = plt.subplots(figsize=(9, 4.5))
df_price.plot(kind='bar', color='white', edgecolor='black', ax=ax, width=0.7)
for container, hatch in zip(ax.containers, bar_hatches):   # one hatch per price model
    for bar in container:
        bar.set_hatch(hatch)
ax.set_ylabel("Biomass price [$/lb]")
ax.set_xlabel("SAF production [MMt/yr]")
ax.set_xticklabels(xlabels, rotation=0)
ax.set_ylim(0, ax.get_ylim()[1] * 1.2)

ax2 = ax.twinx()
for cfg_idx, (name, df) in enumerate(mjsp.items()):   # per case: mean line = mean over price models; band = their full range
    ax2.fill_between(x, df.min(axis=1), df.max(axis=1),
                     color=line_colors[cfg_idx], alpha=0.25, linewidth=0)
    ax2.plot(x, df.mean(axis=1), color=line_colors[cfg_idx], linewidth=2,
             linestyle=case_styles[cfg_idx], marker=case_markers[cfg_idx], markersize=5, label=name)
ax2.set_ylabel("MJSP [$/L SAF]")
ax2.set_ylim(0, ax2.get_ylim()[1] * 1.2)

handles, labels = ax.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax.legend(handles + h2, labels + l2, loc='upper left')
plt.savefig(os.path.join(fig_folder, 'scale_up_price_model_mjsp.png'))

# report data
print("Biomass price [$/lb] by scale x price model:\n", df_price)
for name, df in mjsp.items():
    print(f"\nMJSP [$/L] {name}:\n", df)
print("\nSAF production [MMt/yr]:\n", saf_mmt.to_string())
