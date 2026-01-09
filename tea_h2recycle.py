from funs import *

"""
Utilities are excluded in off gas reformer - should be added for a detailed comparison. 
"""
file_stream = "Process_Data\\Pyrolysis_610_Scale0010_Streams.xlsx"
file_apea = "Process_Data\\Pyrolysis_610_Scale0010_APEA.xlsm"

with open(file_stream, 'rb') as f:
    df_material = pd.read_excel(f, sheet_name='Material', header=3)
    df_work = pd.read_excel(f, sheet_name='Work', header=3)
    df_heat = pd.read_excel(f, sheet_name='Heat', header=3)

idx_material = get_idx_material(df_material)
hourly_revenue_fuel, energy_production_fuel, _ = get_fuel_products(df_material, idx_material)
hourly_revenue_work, energy_production_work = get_work_products(df_work)
hourly_revenue = {**hourly_revenue_fuel, **hourly_revenue_work}
energy_production = {**energy_production_fuel, **energy_production_work}
annual_prod_saf = get_annual_prod_saf(file_stream)

r510_now = calc_cost_r510(df_material, idx_material)
hydrotreat_catalysts = calc_cost_HTcat(df_material, idx_material)
ogr_now = calc_cost_OffGasReformer(df_material, idx_material)

with open(file_apea, 'rb') as f:
    df_prjsum = pd.read_excel(f, sheet_name='Project Summary', header=2)
    df_rawmaterial = pd.read_excel(f, sheet_name='RawMaterial Summary', header=2).dropna(how='all')

# Main process
main_now, main_opex = get_APEA_result(df_prjsum)

# Overall
processes = [main_now, hydrotreat_catalysts, r510_now, ogr_now]
process_names = ['Main', 'Catalysts', 'R-510', 'OffGasReforming']
opex_names = [k for k in main_opex.keys()]

cost_summary, opex_summary, df_process = resume_cost_summary(processes, process_names, opex_names)
mjsp_base, cost_summary, opex_summary = cal_MJSP(cost_summary, opex_summary, hourly_revenue, annual_prod_saf)
