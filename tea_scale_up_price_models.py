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

        df_mjsp, energy_production, annual_prod_saf, main_h2_demand, opex_names, data_all, name_h2_source_new = \
            tea.economic_analysis(file_stream, file_apea, name_h2_source, ammonia_portion=.655)
        df_mjsp_ccs, _, _, _, _, data_ccs, _ = \
            tea.economic_analysis(file_stream, file_apea, name_h2_source[:1], ccs_portion=0.6)
        df_mjsp_all = pd.concat([df_mjsp.loc[['Base', 'Mix']], df_mjsp_ccs])
        df_mjsp_all.index = ['Base', 'Ammonia', 'CCS']

        annual_prod_saf_ton = tea.get_annual_prod_saf_ton(file_stream)  # ton/yr
        biomass_info = tea.get_biomass_info(file_apea)

        case_data['Case Scale'].append(n)
        case_data['SAF Production'].append(annual_prod_saf_ton)     # ton/yr
        case_data['MJSP'].append(df_mjsp_all)

        case_data['Base'].append(data_all['cost'][name_h2_source_new.index('Base')])
        case_data['Ammonia'].append(data_all['cost'][name_h2_source_new.index('Mix')])
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

colors_price = plt.cm.Greys(np.linspace(1, 0, 6))
bar_colors_price = ['#1c5d8e', '#2986cc', '#69aadb']
# ccs_colors = ['#8e4d1c', '#cc6f29', '#db9a69']
# price_colors = plt.cm.viridis(np.linspace(0, 1, 4))
styles_price = ['-', '-.', ':']
markers_model = ["o", "x", "^"]

ms = 9
lw = 2
params = {'legend.fontsize': 'x-large',
          # 'figure.figsize': (15, 5),
         'axes.labelsize': 'xx-large',
         'axes.titlesize':'xx-large',
         'xtick.labelsize':'x-large',
         'ytick.labelsize':'x-large'}
plt.rcParams.update(params)

fig, ax = plt.subplots(figsize=(13, 5))
df_price.plot(kind='bar', color=bar_colors_price, ax=ax)
ax.set_ylabel("Biomass Price [$/lb]")
ax.set_xlabel("Domestic Aviation Fuel Demand Coverage [%]")
ax.set_xticklabels(ax.get_xticklabels(), rotation=0)

ax2 = ax.twinx()
offset = 0.2
for model_idx, (name, df) in enumerate(mjsp.items()):
    for price_idx, col in enumerate(df.columns):
        price_offset = offset * (price_idx-1)
        if price_idx < 1:
            ax2.plot([k+price_offset for k, _ in enumerate(df.index)], df[col],
                     color=colors_price[price_idx], marker=markers_model[model_idx],
                     linestyle=styles_price[price_idx], label=name)
        else:
            ax2.plot([k+price_offset for k, _ in enumerate(df.index)], df[col],
                     color=colors_price[price_idx], marker=markers_model[model_idx],
                     linestyle=styles_price[price_idx])

ax2.set_ylabel("MJSP [$/L SAF]")
ax2.grid(axis='y', alpha=0.5)
plt.legend(loc='upper left', bbox_to_anchor=(0.2,1.))

plt.tight_layout()
plt.savefig(os.path.join(fig_folder, 'scale_up_price_model_mjsp.png'))
plt.savefig(os.path.join(fig_folder, 'scale_up_price_model_mjsp.eps'))
plt.show()
