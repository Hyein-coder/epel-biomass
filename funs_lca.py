import pandas as pd
import numpy as np
from funs import TEA


payload_saf = 0.200251125  # g/kg-km
def get_WTWa_conventional(file_name):
    with open(file_name, 'rb') as f:
        df_raw_conventional = pd.read_excel(f, sheet_name='WTWa_conventional')
        df_raw_conventional = df_raw_conventional.set_index(df_raw_conventional.columns[0])
    data_conventional = {
        'WTP': df_raw_conventional.loc['WTP Emissions g/kJ Fuel'].transpose() * 1000,
        'PTWa': df_raw_conventional.loc['PTWa Emissions g/kJ Fuel'].transpose() * 1000
    }
    data_conventional['WTWa'] = data_conventional['WTP'] + data_conventional['PTWa']
    return data_conventional

def get_WTWa_ftjet(file_name, wBio=True):
    with open(file_name, 'rb') as f:
        if wBio:
            df_raw_wake = pd.read_excel(f, sheet_name='WTWa_ftjet')
        else:
            df_raw_wake = pd.read_excel(f, sheet_name='WTWa_ftjet_woBio')

        df_raw_wake = df_raw_wake.set_index('FT-jet-from-biomass')
    eff_PTWa_ftjet_MJ_g = 0.044114941 * payload_saf
    data_ftjet = {
        'WTP': df_raw_wake.loc['WTP mg/MJ fuel'].transpose() * 1e-3,
        'PTWa': df_raw_wake.loc['PTWa Emissions g/(kg*km)'].transpose() / eff_PTWa_ftjet_MJ_g
    }
    data_ftjet['WTWa'] = data_ftjet['WTP'] + data_ftjet['PTWa']
    return data_ftjet

def get_WTWa_pyrolysis(case_name, file_name, file_wtwa):
    data_ftjet = get_WTWa_ftjet(file_wtwa)

    with open(file_name, 'rb') as f:
        df_case = pd.read_excel(f, sheet_name=case_name)
        df_case.columns = ['Description', 'Value', 'Unit']
    idx_wtp_emissions = df_case['Description'].astype(str).tolist().index('Emissions')
    idx_wtp_resources = df_case['Description'].astype(str).tolist().index('Resources')
    df_emissions = df_case.iloc[idx_wtp_emissions:idx_wtp_resources]
    df_emissions = df_emissions.set_index('Description')

    unit_conversion = {"kg": 1000, "g": 1, "mg": 1e-3, "ug": 1e-6}
    df_emissions['Value in grams'] = df_emissions.apply(
        lambda row: row['Value'] * unit_conversion[row['Unit']]
        if row['Unit'] in unit_conversion.keys() else np.nan,
        axis=1
    )
    df_wtp_case_grams = df_emissions['Value in grams'].dropna()
    data_case = {
        'WTP': df_wtp_case_grams,
        'PTWa': data_ftjet['PTWa']
    }
    data_case['WTWa'] = data_case['WTP'] + data_case['PTWa']
    return data_case

class H2Mix(object):
    def __init__(self, base_scale):
        self.file_stream = f'Process_Data\\Pyrolysis_551_Scale{int(base_scale * 10):04d}_Streams.xlsx'
        self.file_apea = f'Process_Data\\Pyrolysis_551_Scale{int(base_scale * 10):04d}_APEA.xlsm'
        self.tea = TEA()

        with open(self.file_stream, 'rb') as f:
            self.df_material = pd.read_excel(f, sheet_name='Material', header=3)
            self.df_work = pd.read_excel(f, sheet_name='Work', header=3)
            self.df_heat = pd.read_excel(f, sheet_name='Heat', header=3)

        self.idx_material = self.tea.get_idx_material(self.df_material)
        hourly_revenue_fuel, energy_production_fuel, _ = self.tea.get_fuel_products(self.df_material, self.idx_material)
        hourly_revenue_work, energy_production_work = self.tea.get_work_products(self.df_work)
        self.hourly_revenue = {**hourly_revenue_fuel, **hourly_revenue_work}
        self.energy_production = {**energy_production_fuel, **energy_production_work}
        self.annual_prod_saf = self.tea.get_annual_prod_saf(self.file_stream)

        # % Unit Operations
        # Heat Leftover
        ccs_now = self.tea.calc_cost_CCS(self.df_material, self.idx_material, self.df_heat)
        psa_now = self.tea.calc_cost_PSA(self.df_material, self.idx_material)
        r510_now = self.tea.calc_cost_r510(self.df_material, self.idx_material)
        hydrotreat_catalysts = self.tea.calc_cost_HTcat(self.df_material, self.idx_material)
        # transport_now = calc_cost_biomass_transport(df_material, idx_material)

        with open(self.file_apea, 'rb') as f:
            self.df_prjsum = pd.read_excel(f, sheet_name='Project Summary', header=2)
            self.df_rawmaterial = pd.read_excel(f, sheet_name='RawMaterial Summary', header=2).dropna(how='all')

        # Main process
        self.main_now, self.main_opex = self.tea.get_APEA_result(self.df_prjsum)

        # Overall
        self.processes = [self.main_now, ccs_now, psa_now, hydrotreat_catalysts, r510_now]
        self.process_names = ['Main', 'CCS', 'PSA', 'Catalysts', 'R-510']
        self.opex_names = [k for k in self.main_opex.keys()]

        # LCA
        file_wtwa = 'Process_Data\\WTWa_LCA.xlsx'
        lca_conventional = get_WTWa_conventional(file_wtwa)
        self.ghg_threshold_saf = 0.9 * lca_conventional['WTWa']['GHG-100']

        self.lca_methods = [
            "Allocation", "Displacement",
            "Allocation_KRmix", "Displacement_KRmix",
        ]
#             "FullCCS_Allocation", "FullCCS_Displacement",
#         "FullCCS_Allocation_KRmix", "FullCCS_Displacement_KRmix"

        ghg_base = []
        ghg_ammonia = []
        for lca in self.lca_methods:
            file_lca = f'Process_Data\\Pyrolysis_551_LCA_{lca}.xlsx'
            lca_base = get_WTWa_pyrolysis('Base', file_lca, file_wtwa)
            lca_ammonia = get_WTWa_pyrolysis('Ammonia', file_lca, file_wtwa)
            ghg_base.append(lca_base['WTWa']['GHG-100'])
            ghg_ammonia.append(lca_ammonia['WTWa']['GHG-100'])
        self.ghg_base = ghg_base
        self.ghg_ammonia = ghg_ammonia

    def mjsp_with_ammonia(self, ammonia_portion):
        main, main_h2_demand = self.tea.get_main_partial_grey(self.main_now, self.df_rawmaterial, 1 - ammonia_portion)
        cost_h2, opex_h2, df_h2 = self.tea.calc_h2_opex_and_dfprocess(
            'Ammonia', main, self.opex_names, main_h2_demand, self.annual_prod_saf, self.hourly_revenue,
            self.processes, self.process_names
        )
        df_summary = pd.DataFrame(opex_h2, index=['Summary'])
        df_summary = df_summary.reindex(columns=['capital investment', 'raw materials', 'utilities',
                                                 'operating labor', 'maintenance', 'operating charges',
                                                 'plant overhead', 'G and A cost', 'co-product sales'])
        df_summary.rename(columns={"G and A cost": "governance and admin."}, inplace=True)
        df_mjsp = df_summary.map(lambda x: x / self.annual_prod_saf)
        mjsp = df_mjsp.sum(axis=1)['Summary']
        return mjsp, df_mjsp

    def ghg_with_ammonia(self, ammonia_portion):
        res_all = [self.ghg_base[i] * (1 - ammonia_portion) + self.ghg_ammonia[i] * ammonia_portion
                   for i in range(len(self.ghg_base))]
        res_mean = sum(res_all) / len(res_all)
        res_error = [res_mean - min(res_all), max(res_all) - res_mean]
        return res_mean, res_error, res_all

    def get_LCOH(self, ammonia_portion):
        main, total_h2_demand = self.tea.get_main_wo_h2(self.main_now, self.df_rawmaterial)
        lcoh_ammonia, _, _ = self.tea.get_LCOH('Ammonia', total_h2_demand * ammonia_portion, self.opex_names)
        return lcoh_ammonia
