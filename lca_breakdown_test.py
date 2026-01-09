#%%
import math
from funs import convert_to_grams
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np

file_LCA_breakdown = 'Process_Data\\Pyrolysis_532-4_AmmoniaCrackingWithLNGShip_Greet.xlsx'
with open(file_LCA_breakdown, 'rb') as f:
    raw_lca = pd.read_excel(f, sheet_name='Base')

nc_for_each_process = 5
num_process = math.ceil(raw_lca.shape[1] / nc_for_each_process)

lca_process_raw = []
lca_process_name = []

for n in range(num_process):
    lp = pd.DataFrame(raw_lca.iloc[:, nc_for_each_process * n + 1:nc_for_each_process * n + 3])
    lp.index = raw_lca.iloc[:, nc_for_each_process * n]
    lp = lp.rename(columns={lp.columns[-1]: 'Units'})

    lca_process_raw.append(lp)
    lca_process_name.append(lp.columns[0])

idx_start_lp_final = np.where(lca_process_raw[0].index.get_loc('Well to Use'))[0][0]
idx_end_lp_final = np.where(lca_process_raw[0].index.get_loc('OnSite'))[0][0]
lp_final = convert_to_grams(lca_process_raw[0].iloc[idx_start_lp_final:idx_end_lp_final,:])
lp_final.columns = ['Total']

lp_main = lca_process_raw[lca_process_name.index('Residue-to-Jet')]
idx_start_lp_main_resource = np.where(lp_main.index.get_loc('Resources'))[0][0]
idx_end_lp_main_resource = lp_main.index.get_loc('Urban Emissions')
lp_main_resources = lp_main.iloc[idx_start_lp_main_resource:idx_end_lp_main_resource,:]

idx_start_lp_main_onsite = lp_main_resources.index.get_loc('OnSite')
lp_main_onsite_resources = lp_main_resources.iloc[idx_start_lp_main_onsite:, :]

#%%
convert_MJ_to_Btu = 947.8602
node_connection = [(0,1), (1,2), (1,3), (3,4), (2,None), (4,None)]

lca_process = [None for _ in range(len(lca_process_raw))]
lca_process_raw_onsite = [None for _ in range(len(lca_process_raw))]
lca_process_raw.reverse()
for i_reversed, lp in enumerate(lca_process_raw):
    i = len(lca_process_raw) - i_reversed - 1
    name_i = lp.columns[0]

    base_info = lp.loc['Base']
    if base_info.iloc[0] == 'SAF':
        base_conversion_factor = 1
    else:
        base_material = base_info.iloc[0]
        base_for_main = lp_main_onsite_resources.loc[base_material]
        if base_for_main.iloc[1] == 'Btu':
            base_conversion_factor = base_for_main.iloc[0] / convert_MJ_to_Btu
        else:
            print(f"Resource {base_material} has a unit of {base_for_main.iloc[1]} in the main process.")

    idx_start_well_to_use = 2
    try:
        idx_end_well_to_use = np.where(lp.index.get_loc('OnSite'))[0][0]
    except KeyError:
        idx_end_well_to_use = lp.index.get_loc('Flow properties')

    # print(lca_process.iloc[idx_start_onsite_emission:idx_end_onsite_emission, :])
    lp_now_raw = lp.iloc[idx_start_well_to_use:idx_end_well_to_use, :]
    lp_now_in_grams = convert_to_grams(lp_now_raw)
    lp_now = lp_now_in_grams.map(
        lambda x: x * base_conversion_factor if isinstance(x, (int, float)) and not isinstance(x, bool) else x
    )

    i_connection = list(filter(lambda tup: tup[0] == i, node_connection))

    for i_to, i_from in i_connection:
        if i_from is None:
            break
        else:
            lp_prv = lca_process[i_from]
            lp_prv = lp_prv.map(lambda x: -x if not isinstance(x, bool) else x)
            lp_now = lp_now.join(lp_prv, rsuffix='_prv')
    lp_onsite = pd.DataFrame(lp_now.sum(axis=1))
    lp_onsite.columns = [lp_now.columns[0]]
    lca_process[i] = lp_onsite

    idx_end_raw_onsite = lp.index.get_loc('Flow properties')
    try:
        idx_start_raw_onsite = np.where(lp.index.get_loc('OnSite'))[0][0]
    except KeyError:
        idx_start_raw_onsite = 2

    # print(lca_process.iloc[idx_start_onsite_emission:idx_end_onsite_emission, :])
    lp_now_raw_onsite = lp.iloc[idx_start_raw_onsite:idx_end_raw_onsite, :]
    lp_now_raw_onsite_in_grams = convert_to_grams(lp_now_raw_onsite)
    lp_raw_onsite = lp_now_raw_onsite_in_grams.map(
        lambda x: x * base_conversion_factor if isinstance(x, (int, float)) and not isinstance(x, bool) else x
    )
    lp_compare = lp_onsite.join(lp_raw_onsite, rsuffix='_raw')
    lca_process_raw_onsite[i] = lp_raw_onsite

lca_per_process = lp_final
for lp_onsite in lca_process:
    lca_per_process = lca_per_process.join(lp_onsite, rsuffix='_next')

lca_final_computed = lca_per_process.iloc[:,1:].sum(axis=1)

