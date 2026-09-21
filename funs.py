import pandas as pd
import numpy as np
import re
import os

lb2kg = 0.453592
class TEA(object):
    def __init__(self):
        self.ammonia_file_name = lambda c: f'NH3_Cracking_130_scale{round(c * 10):04d}_APEAresult.xlsm'

        self.comp_GHG = ['CO2', 'NO2', 'METHANE', 'CO']
        self.operation_hr = 8000
        self.scale_ammonia = [1, 2.5, 5, 7.5, 10, 20, 30]

        self.economic_period = 30
        self.irr_desire = 0.1
        self.tax_rate = 0.35
        self.salvage_value = 0

        # Cost parameters
        self.elec_price_usd_per_mmbtu = 19.05
        self.fuel_price_usd_per_mmbtu = 14.38
        self.product_price_stream = {
            '316GAS': 0.75757,  # $/LB
            '326SAF': 0,
            '336DIES': 0.6
        }
        self.product_price_work = {
            'ELC-': self.elec_price_usd_per_mmbtu
        }
        self.hydrogen_feed_stream = ['250H2', '532H2']
        self.sulf_feed_stream = ['262SLF', '263SLF']
        self.emission_in_stream = ['80AIR', '120AIR', '610AIR']
        self.emission_out_stream = ['699WWT', '691VENT', '788WWT', '705VENT']
        self.co2_captured_stream = ['623CO2']

        # Carbon Capture for Storage - Base case: Rao, 2022 - converted to 1Q-2022 base
        self.ccs_base_case = {
            'base stream': 862853,
            'total CAPEX': 297930841,
            'heat consumption [mmBTU/hr]': 3315,
            'electricity [mmBTU/hr]': 3315 * 0.14
        }
        # PSA for H2 Separation - Base case: Byun, 2020 - converted to 1Q-2022 base
        self.psa_base_case = {
            'base stream': 700,  # m3/hr
            'total CAPEX': 780993,
            'annual OPEX': 5078
        }
        # R510 - Base case: Jones, 2013
        self.r510_base_case = {
            'base stream': 9600,
            'total CAPEX': 5266304
        }

        self.cost_idx_1Q2022 = 3230
        self.cost_idx_Jones = 2250
        self.r202_Ru_info = {
            'LHSV': 0.5,
            'price': 60 * 2.2 / self.cost_idx_Jones * self.cost_idx_1Q2022  # USD/lb -> USD/kg
        }
        self.r220_Ru_info = {
            'LHSV': 0.5,
            'price': 60 * 2.2 / self.cost_idx_Jones * self.cost_idx_1Q2022  # USD/lb -> USD/kg
        }
        self.r225_Mo_info = {
            'LHSV': 0.22,
            'price': 15.5 * 2.2 / self.cost_idx_Jones * self.cost_idx_1Q2022  # USD/lb -> USD/kg
        }

        # SMR - Base case: Katebah, 2022, SMR with CCS
        self.cost_idx_smr = 2340
        self.smr_base_case = {
            'base stream': 45922,
            'total CAPEX': 424e6 / self.cost_idx_smr * self.cost_idx_1Q2022,
            'annual OPEX': 147e6 / self.cost_idx_smr * self.cost_idx_1Q2022,
            'NG feed': 156136,
            'CO2 emission': 55107,
            'Water consumption': 9.74 * 45922
        }

        # OffGas Reformer - Jones, 2013
        self.ogr_base_case = {
            'base stream': (8846 + 995) / 0.91,  # Produced Hydrogen
            'total CAPEX': 69144535 / self.cost_idx_Jones * self.cost_idx_1Q2022
        }

        self.idx_names = {
            "BIO": "Biomass", "H2": "Hydrogen gas", "AP-UTIL-LPS": "LP steam", "AP-UTIL-HPS": "MP steam",
            "SLF": "Sulfiding agent", "SND": "Sand", "WT": "Water", "AIR": "Air", "AP-UTIL-HPS-INTG": "HP steam"
        }
        self.unit_category = ['Feed', 'Pyrolysis', 'Hydrotreating', 'Product Finishing', 'Hydrogen Recovery',
                              'Hydrocracking', 'Offgas Combustion', 'Balance of Plant (Steam)']

    def get_idx_material(self, df_material):
        idx_material = {}

        idx_MIXED = df_material['Stream Name'].astype(str).tolist().index('MIXED Substream')
        idx_Vapor = df_material['Stream Name'].astype(str).tolist().index('Vapor Phase')

        df_stream_GENERAL = df_material.iloc[:idx_MIXED]
        df_stream_MIXED = df_material.iloc[idx_MIXED:idx_Vapor]

        idx_mass_flow = df_stream_GENERAL['Stream Name'].astype(str).tolist().index('Mass Flows')
        idx_mass_frac = df_stream_GENERAL['Stream Name'].astype(str).tolist().index('Mass Fractions')
        df_stream_mass_flow = df_stream_GENERAL[idx_mass_flow:idx_mass_frac]

        # GENERAL DATA
        idx_material['mass flow [lb/hr]'] = df_stream_GENERAL['Stream Name'].astype(str).tolist().index('Mass Flows')
        idx_material['vol flow [cuft/hr]'] = df_stream_GENERAL['Stream Name'].astype(str).tolist().index('Volume Flow')
        idx_material['density [lb/cuft]'] = df_material['Stream Name'].astype(str).tolist().index('Mass Density')

        # Mass Flow Rate of GHG Components
        for comp in self.comp_GHG:
            idx_material[comp] = idx_mass_flow + df_stream_mass_flow['Stream Name'].astype(str).tolist().index(comp)

        # MIXED Substream DATA
        idx_material['LHV at 15C [Btu/lb]'] = idx_MIXED + df_stream_MIXED['Stream Name'].astype(str).tolist().index(
            'Lower heating value(mass basis) at 15C, reference 15C, for a petroleum mixture'
        )
        idx_material['heat capacity [Btu/lb/R]'] = idx_MIXED + df_stream_MIXED['Stream Name'].astype(str).tolist().index(
            'Mass heat capacity, mixture'
        )
        return idx_material

    def get_annual_prod_saf(self, file_stream):
        with open(file_stream, 'rb') as f:
            df_material = pd.read_excel(f, sheet_name='Material', header=3)
        idx_material = self.get_idx_material(df_material)
        annual_prod_saf = df_material['326SAF'][idx_material['vol flow [cuft/hr]']] * self.operation_hr * 28.3168  # L/yr
        return annual_prod_saf

    def get_annual_prod_saf_ton(self, file_stream):
        with open(file_stream, 'rb') as f:
            df_material = pd.read_excel(f, sheet_name='Material', header=3)
        idx_material = self.get_idx_material(df_material)
        annual_prod_saf_ton = df_material['326SAF'][idx_material['mass flow [lb/hr]']] * self.operation_hr / 2e3  # ton/yr
        return annual_prod_saf_ton

    def get_saf_density(self, file_stream):
        with open(file_stream, 'rb') as f:
            df_material = pd.read_excel(f, sheet_name='Material', header=3)
        idx_material = self.get_idx_material(df_material)
        saf_density = df_material['326SAF'][idx_material['density [lb/cuft]']] / 28.3168 * lb2kg  # kg/L
        return saf_density

    def get_biomass_info(self, file_apea):
        with open(file_apea, 'rb') as f:
            df_rawmaterial = pd.read_excel(f, sheet_name='RawMaterial Summary', header=2).dropna(how='all')
        df_main_biomass = df_rawmaterial.query("Description == '90BIO'")
        biomass_demand = sum(df_main_biomass['Rate per Hour'])
        biomass_cost = sum(df_main_biomass['Cost per Hour'])
        biomass_price = biomass_cost / biomass_demand
        biomass_info = {'Demand [lb/hr]': biomass_demand, 'Cost [$/hr]': biomass_cost, 'Price [$/lb]': biomass_price}
        return biomass_info

    def unit_cost_interpolation(self, base_stream, base_case):
        r_scale = base_stream / base_case['base stream']
        now_case = {}
        for k, v in base_case.items():
            if not isinstance(v, str):
                now_case[k] = base_case[k] * r_scale
            elif 'CAPEX' in v:  # six-tenth rule
                now_case[k] = base_case[k] * (r_scale ** 0.6)
            elif 'OPEX' in v:
                now_case[k] = base_case[k] * (r_scale ** 0.7)
            else:
                now_case[k] = base_case[k] * r_scale
        return now_case

    def catalyst_charging_cost(self, base_stream, cat_info):
        base_stream_m3_hr = base_stream / 35.315
        cat_charging_m3 = base_stream_m3_hr / cat_info['LHSV']
        cat_cost = cat_charging_m3 * cat_info['price']
        return cat_cost

    def get_APEA_result(self, df_prjsum):
        prj_now = {
            'total CAPEX': df_prjsum['VALUE'][148],
        }
        prj_opex = {
            'raw materials': df_prjsum['VALUE'][149],
            'utilities': df_prjsum['VALUE'][152],
            'operating labor': df_prjsum['VALUE'][155],
            'maintenance': df_prjsum['VALUE'][156],
            'operating charges': df_prjsum['VALUE'][157],
            'plant overhead': df_prjsum['VALUE'][158],
            'G and A cost': df_prjsum['VALUE'][160]
        }
        prj_now['annual OPEX'] = sum([c for c in prj_opex.values()])
        for k, v in prj_opex.items():
            prj_now[k] = v
        return prj_now, prj_opex

    def resume_cost_summary(self, processes, process_names, opex_names):
        df_process = pd.DataFrame(processes).transpose()
        df_process.columns = process_names

        cost_summary = {
            'total CAPEX': 0,
            'annual OPEX': 0
        }

        for k in cost_summary.keys():
            cost_summary[k] = np.nansum(df_process.loc[k])

        opex_summary = {}
        for k in opex_names:
            try: opex_summary[k] = np.nansum(df_process.loc[k])
            except KeyError: opex_summary[k] = 0

        return cost_summary, opex_summary, df_process

    def get_main_wo_h2(self, main_now, df_rawmaterial):
        df_main_h2 = df_rawmaterial.query("Description in " + str(self.hydrogen_feed_stream))
        main_h2_demand = sum(df_main_h2['Rate per Hour'])  # lb/hr
        main_h2_cost = sum(df_main_h2['Cost per Hour']) * self.operation_hr  # USD/yr

        main_wo_h2 = main_now.copy()
        main_wo_h2['annual OPEX'] -= main_h2_cost
        main_wo_h2['raw materials'] -= main_h2_cost
        return main_wo_h2, main_h2_demand

    def get_main_partial_grey(self, main_now, df_rawmaterial, grey_portion):
        df_main_h2 = df_rawmaterial.query("Description in " + str(self.hydrogen_feed_stream))
        total_h2_demand = sum(df_main_h2['Rate per Hour'])  # lb/hr
        main_h2_cost = sum(df_main_h2['Cost per Hour']) * self.operation_hr  # USD/yr

        main_partial_grey = main_now.copy()
        main_partial_grey['annual OPEX'] -= main_h2_cost * (1 - grey_portion)
        main_partial_grey['raw materials'] -= main_h2_cost * (1 - grey_portion)
        main_h2_demand = total_h2_demand * (1 - grey_portion)
        return main_partial_grey, main_h2_demand

    def cal_MJSP(self, cost_summary, opex_summary, hourly_revenue, annual_prod_saf):
        inv_irr = 1 / (1 + self.irr_desire)
        sum_of_irr = inv_irr * (1 - inv_irr ** self.economic_period) / (1 - inv_irr)

        depreciation = cost_summary['total CAPEX'] * (1 - self.salvage_value) / self.economic_period
        opex_summary['capital investment'] = (cost_summary['total CAPEX'] -
                                              sum_of_irr * self.tax_rate * depreciation) / sum_of_irr / (1 - self.tax_rate)  # USD/yr

        cost_summary['minimum revenue'] = sum([c for c in opex_summary.values()])

        sales_summary = {}
        for k, v in hourly_revenue.items():
            sales_summary[k] = v * self.operation_hr  # USD/yr
        cost_summary['co-product sales'] = sum([r for r in sales_summary.values()])
        opex_summary['co-product sales'] = -cost_summary['co-product sales']     # USD/yr

        cost_summary['MJSP'] = (cost_summary['minimum revenue'] - cost_summary[
            'co-product sales']) / annual_prod_saf  # USD/L
        return cost_summary['MJSP'], cost_summary, opex_summary

    def convert_to_grams(self, df):
        conversion_factors = {'g': 1, 'kg': 1000, 'mg': 1/1000, 'ug': 1e-6}

        converted_values = []
        for idx, row in df.iterrows():
            val, unit = row.iloc[0], row.iloc[1]
            if unit in conversion_factors:
                converted_values.append(val * conversion_factors[unit])
            else:
                converted_values.append(True)

        df_converted = pd.DataFrame(converted_values, index=df.index, columns=df.columns[:1])

        return df_converted

    def get_util_and_rawmaterial_base(self, file_apea):
        with open(file_apea, 'rb') as f:
            df_util_base = pd.read_excel(f, sheet_name='Utility Summary', header=2).dropna(how='all')
            df_rawmaterial_base = pd.read_excel(f, sheet_name='RawMaterial Summary', header=2).dropna(how='all')

        df_util_base['Category'] = df_util_base['Item Description'].apply(lambda x: self.unit_category[int(x.split('-')[1][0])])

        rule_rawmaterial = lambda x: int(x[0]) if int(x[0]) < len(self.unit_category) else 0
        df_rawmaterial_base['Category'] = df_rawmaterial_base['Description'].apply(
            lambda x: self.unit_category[rule_rawmaterial(x)])
        df_rawmaterial_base['Description'] = df_rawmaterial_base['Description'].apply(
            lambda x: x[re.search(r'[A-Z]', x, re.I).start():]
        )
        return df_util_base, df_rawmaterial_base

    def get_util_and_rawmaterial_sum(self, file_apea, dfp_per_h2_source, name_h2_source):
        df_util_base, df_rawmaterial_base = self.get_util_and_rawmaterial_base(file_apea)
        df_util_all_case = []
        for dfp in dfp_per_h2_source:
            if 'utilities description' not in dfp.index:
                dfp.loc['utilities description'] = [None] * len(dfp.columns)
            util_add = dfp.loc[['utilities description', 'utilities', 'Category']].iloc[:,1:]
            for unit in util_add.columns:
                if isinstance(util_add.loc['utilities description', unit], list):
                    for d in util_add.loc['utilities description', unit]:
                        util_add[unit + '-' + d] = [d, dfp.loc[d, unit], dfp.loc['Category', unit]]
                    util_add.drop(unit, axis=1, inplace=True)
            df_util_add = pd.DataFrame([[name, util_add.loc['utilities description', name],
                                         util_add.loc['utilities', name]/self.operation_hr,
                                         util_add.loc['Category', name]]
                                        for name in util_add.columns.to_list()],
                                       columns=['Item Description', 'Description', 'Cost per Hour', 'Category'])
            df_util_all_case.append(pd.concat([df_util_base, df_util_add], ignore_index=True))

        df_util_cost = pd.concat([dfu.groupby('Description')['Cost per Hour'].sum() for dfu in df_util_all_case], axis=1)
        df_util_cost.columns = name_h2_source

        df_rawmaterial_wo_H2 = df_rawmaterial_base.copy()
        idx_H2 = df_rawmaterial_wo_H2[df_rawmaterial_wo_H2['Description'].str.contains('H2', na=False)].index
        df_rawmaterial_wo_H2.loc[idx_H2, 'Cost per Hour'] = 0
        df_rawmaterial_wo_H2.loc[idx_H2, 'Rate per Hour'] = 0

        df_rawmaterial_all_case = []
        for i, dfp in enumerate(dfp_per_h2_source):
            rawmaterial_add = dfp.loc[['raw materials description', 'raw materials', 'Category']].iloc[:,1:]
            df_rawmaterial_add = pd.DataFrame([[rawmaterial_add.loc['raw materials description', name],
                                                rawmaterial_add.loc['raw materials', name]/self.operation_hr,
                                                rawmaterial_add.loc['Category', name]]
                                               for name in rawmaterial_add.columns.to_list()],
                                              columns=['Description', 'Cost per Hour', 'Category'])
            if i > 0:
                df_rawmaterial_all_case.append(pd.concat([df_rawmaterial_wo_H2, df_rawmaterial_add], ignore_index=True))
            else:
                df_rawmaterial_all_case.append(pd.concat([df_rawmaterial_base, df_rawmaterial_add], ignore_index=True))

        df_rawmaterial_cost = pd.concat([dfr.groupby('Description')['Cost per Hour'].sum() for dfr in df_rawmaterial_all_case],
                                        axis=1)
        df_rawmaterial_cost.columns = name_h2_source

        df_util_and_rawmaterial_cost = pd.concat([df_util_cost, df_rawmaterial_cost])
        df_util_and_rawmaterial_cost = df_util_and_rawmaterial_cost.rename(index=self.idx_names)

        df_util_rate = pd.concat([dfu.groupby('Description')['Rate'].sum() for dfu in df_util_all_case], axis=1)
        df_util_rate.columns = name_h2_source
        util_filtered = df_util_all_case[0][['Description', 'Rate Units']].dropna()
        util_unique_units = util_filtered.drop_duplicates()
        util_description = util_unique_units.set_index(['Description'])
        df_util_rate = pd.concat([df_util_rate, util_description], axis=1)

        df_rawmaterial_rate = pd.concat(
            [dfr.groupby('Description')['Rate per Hour'].sum() for dfr in df_rawmaterial_all_case], axis=1)
        df_rawmaterial_rate.columns = name_h2_source
        rawmaterial_filtered = df_rawmaterial_all_case[0][['Description', 'Rate Units']].dropna()
        rawmaterial_unique_units = rawmaterial_filtered.drop_duplicates()
        rawmaterial_description = rawmaterial_unique_units.set_index(['Description'])
        df_rawmaterial_rate = pd.concat([df_rawmaterial_rate, rawmaterial_description], axis=1)

        df_util_and_rawmaterial_rate = pd.concat([df_util_rate, df_rawmaterial_rate])
        df_util_and_rawmaterial_rate = df_util_and_rawmaterial_rate.rename(index=self.idx_names)
        return df_util_and_rawmaterial_cost, df_util_and_rawmaterial_rate

    def get_ammonia_cost_at_scale(self, c):
        file_name = self.ammonia_file_name(c)
        with open(os.path.join('Process_Data', file_name), 'rb') as f:
            df_prjsum = pd.read_excel(f, sheet_name='Project Summary', header=2)
            df_rawmaterial = pd.read_excel(f, sheet_name='RawMaterial Summary', header=2).dropna(how='all')
            df_ammonia_coproduct = pd.read_excel(f, sheet_name='Product Summary', header=2).dropna(how='all')

        sum, opex = self.get_APEA_result(df_prjsum)
        sum['Category'] = 'Ammonia'
        sum['raw materials description'] = 'Ammonia'
        sum['utilities description'] = 'Electricity'

        df_rawmaterial['Description'] = df_rawmaterial['Description'].apply(str)
        ammonia_idx = [i for i, item in enumerate(df_rawmaterial['Description'].tolist()) if 'NH3' in item]
        ammonia_demand = df_rawmaterial['Rate per Hour'].iloc[ammonia_idx]
        ammonia_cost = df_rawmaterial['Cost per Hour'].iloc[ammonia_idx]
        ammonia_price = [df_rawmaterial['Units'].iloc[ammonia_idx].item(), ammonia_cost.item() / ammonia_demand.item()]

        fertilizer_sales = df_ammonia_coproduct['Cost per Hour'].iloc[0]
        return sum, fertilizer_sales, opex, ammonia_demand, ammonia_cost, ammonia_price

    def calc_util_and_rawmaterial_price(self, file_apea):
        df_util_base, df_rawmaterial_base = self.get_util_and_rawmaterial_base(file_apea)
        util_price = pd.DataFrame(
            [df_util_base['Description'], df_util_base['Rate Units'], df_util_base['Cost per Hour'] / df_util_base['Rate']],
            index=['Description', 'Units', 'Price per Rate']
        ).transpose()
        rawmaterial_price = pd.DataFrame(
            [df_rawmaterial_base['Description'], df_rawmaterial_base['Units'],
             df_rawmaterial_base['Cost per Hour'] / df_rawmaterial_base['Rate per Hour']],
            index=['Description', 'Units', 'Price per Rate']
        ).transpose()
        _, _, _, _, _, ammonia_price = self.get_ammonia_cost_at_scale(1)
        user_price = pd.DataFrame.from_dict(
            {
                'Natural Gas': ['MMBTU/H', self.fuel_price_usd_per_mmbtu],
                'Ammonia': ammonia_price
             },
            orient='index', columns=['Units', 'Price per Rate']
        )

        df_ur_price = pd.concat([util_price.groupby('Description').first(),
                                 rawmaterial_price.groupby('Description').first(),
                                 user_price])
        df_ur_price = df_ur_price.rename(index=self.idx_names)
        return df_ur_price

    def get_equipment_breakdown(self, file_apea, dfp_per_h2_source, name_h2_source, unit_rule=None):
        with open(file_apea, 'rb') as f:
            df_equipment_base = pd.read_excel(f, sheet_name='Equipment', header=2).dropna()
        df_equipment_base = df_equipment_base[df_equipment_base['Component Type'].str.strip() != 'C']
        if unit_rule is None:
            unit_category = self.unit_category
            unit_category.append(None)
            unit_rule = lambda x: unit_category[int(x.split('-')[1][0]) if len(x.split('-')) > 1 else -1]

        df_equipment_base['Category'] = df_equipment_base['Component Name'].apply(unit_rule)
        df_equipment_base = df_equipment_base.dropna(subset=['Category'])

        df_equip_all_case = []
        for dfp in dfp_per_h2_source:
            equip_add = dfp.loc[['total CAPEX', 'Category']].iloc[:, 1:]
            df_equip_add = pd.DataFrame(
                [['Additional', name, equip_add.loc['total CAPEX', name], equip_add.loc['Category', name]]
                 for name in equip_add.columns.to_list()],
                columns=['Area Name', 'Component Name', 'Total Direct Cost', 'Category'])
            df_equip_all_case.append(pd.concat([df_equipment_base, df_equip_add], ignore_index=True))

        df_equip_sum = pd.concat([dfe.groupby('Category')['Total Direct Cost'].sum() for dfe in df_equip_all_case], axis=1)
        df_equip_sum.columns = name_h2_source
        return df_equip_sum, df_equip_all_case

    def get_fuel_products(self, df_material, idx_material):
        hourly_revenue = {}
        energy_production_in_MW = {}
        mass_production = {}
        for s, price in self.product_price_stream.items():
            mass_flow = df_material[s][idx_material['mass flow [lb/hr]']]
            mass_production[s] = mass_flow
            hourly_revenue[s] = mass_flow * price   # $/hr

            lhv_15C = df_material[s][idx_material['LHV at 15C [Btu/lb]']]
            heat_capacity = df_material[s][idx_material['heat capacity [Btu/lb/R]']]
            dT_in_F = (25-15) * 5/9
            lhv_standard = lhv_15C + heat_capacity * dT_in_F
            energy_production_Btu_hr = lhv_standard * mass_flow
            energy_production_in_MW[s] = energy_production_Btu_hr * 2.9307e-7

        return hourly_revenue, energy_production_in_MW, mass_production

    def get_work_products(self, df_work):
        hourly_revenue = {}
        energy_production_in_MW = {}
        for s, price in self.product_price_work.items():
            s_col = df_work.filter(like=s).columns
            energy_production_MMBtu_hr = - df_work.loc[0][s_col].sum() * 0.002544  # hp = 2544.434187 BTU/hr = 0.002544 MMBTU/hr
            hourly_revenue[s] = energy_production_MMBtu_hr * price  # $/hr
            energy_production_in_MW[s] = energy_production_MMBtu_hr * 1e6 * 2.9307e-7  # MW

        return hourly_revenue, energy_production_in_MW

    def get_resource_flow(self, file_stream):
        with open(file_stream, 'rb') as f:
            df_material = pd.read_excel(f, sheet_name='Material', header=3)
        idx_material = self.get_idx_material(df_material)
        resource_flow = {
            'Water': df_material['700BFW'][idx_material['mass flow [lb/hr]']],
            'Gaseous hydrogen': sum([df_material[s][idx_material['mass flow [lb/hr]']] for s in self.hydrogen_feed_stream]),
            'Sulfur agent': sum([df_material[s][idx_material['mass flow [lb/hr]']] for s in self.sulf_feed_stream]),
            'Sand': df_material['122SND'][idx_material['mass flow [lb/hr]']],
            'Biomass feed': df_material['90BIO'][idx_material['mass flow [lb/hr]']]
        }
        return resource_flow

    def get_emission_flow(self, file_stream, ccs_portion=0.):
        with open(file_stream, 'rb') as f:
            df_material = pd.read_excel(f, sheet_name='Material', header=3)
        idx_material = self.get_idx_material(df_material)

        emission_flow = {key: 0 for key in self.comp_GHG}
        for c in emission_flow.keys():
            emission_mass_flow_rate = 0

            for s_in in self.emission_in_stream:
                emission_mass_flow_rate -= df_material[s_in][idx_material[c]]

            for s_out in self.emission_out_stream:
                emission_mass_flow_rate += df_material[s_out][idx_material[c]]

            emission_flow[c] = emission_mass_flow_rate

        captured_flow = {}
        for c in emission_flow.keys():
            captured_mass_flow_rate = 0
            emission_mass_flow_rate = 0
            for s in self.co2_captured_stream:
                captured_mass_flow_rate += df_material[s][idx_material[c]] * ccs_portion
                emission_mass_flow_rate += df_material[s][idx_material[c]] * (1-ccs_portion)
            captured_flow[c] = captured_mass_flow_rate
            emission_flow[c] += emission_mass_flow_rate

        return emission_flow, captured_flow

    def calc_cost_CCS(self, df_material, idx_material, df_heat, capture_portion=0.):
        # Heat Leftover
        df_heat = df_heat.set_index('Stream Name')
        col_heat_gen = df_heat.filter(like='-Q').columns
        heat_gen = df_heat[col_heat_gen].loc['QCALC Btu/hr'].sum() / 1e6  # mmBtu/hr

        co2_EGR = df_material['622X'][idx_material['mass flow [lb/hr]']]
        co2_left = df_material['623CO2'][idx_material['mass flow [lb/hr]']]
        co2_seq = co2_left * capture_portion + co2_EGR
        ccs_now = self.unit_cost_interpolation(co2_seq, self.ccs_base_case)

        ## Fuel 값이 예전에 정리할 때랑 값이 다름..?
        ccs_now['Fuel'] = max(ccs_now['heat consumption [mmBTU/hr]'] - heat_gen, 0) * self.fuel_price_usd_per_mmbtu * self.operation_hr
        ccs_now['Electricity'] = ccs_now['electricity [mmBTU/hr]'] * self.elec_price_usd_per_mmbtu * self.operation_hr
        ccs_now['annual OPEX'] = ccs_now['Fuel'] + ccs_now['Electricity']   # $/yr

        utilities_list = ['Fuel', 'Electricity']
        ccs_now['utilities'] = sum([ccs_now[k] for k in utilities_list])
        ccs_now['utilities description'] = utilities_list
        ccs_now['Category'] = 'Carbon Capture'
        return ccs_now

    def calc_cost_PSA(self, df_material, idx_material):
        h2_recovery = df_material['404'][idx_material['vol flow [cuft/hr]']] * 0.02832
        psa_now = self.unit_cost_interpolation(h2_recovery, self.psa_base_case)
        psa_now['raw materials'] = psa_now['annual OPEX']   # 68% of OPEX is reactants cost
        psa_now['raw materials description'] = 'Adsorbent'
        psa_now['Category'] = 'Hydrogen Recovery'
        return psa_now

    def calc_cost_r510(self, df_material, idx_material):
        recycle_in_340 = df_material['340'][idx_material['mass flow [lb/hr]']]
        r510_now = self.unit_cost_interpolation(recycle_in_340, self.r510_base_case)
        r510_now['Category'] = 'Hydrocracking'
        return r510_now

    def calc_cost_HTcat(self, df_material, idx_material):
        r202_cat_cost = self.catalyst_charging_cost(df_material['255'][idx_material['vol flow [cuft/hr]']], self.r202_Ru_info)
        r220_cat_cost = self.catalyst_charging_cost(df_material['210'][idx_material['vol flow [cuft/hr]']], self.r220_Ru_info)
        r225_cat_cost = self.catalyst_charging_cost(df_material['272'][idx_material['vol flow [cuft/hr]']], self.r225_Mo_info)
        hydrotreat_catalysts = {'R-202': r202_cat_cost, 'R-220': r220_cat_cost, 'R-225': r225_cat_cost}
        hydrotreat_catalysts['total CAPEX'] = sum([c for c in hydrotreat_catalysts.values()])
        hydrotreat_catalysts['Category'] = 'Hydrotreating'
        return hydrotreat_catalysts

    def calc_cost_OffGasReformer(self, df_material, idx_material):
        h2_produced = df_material['404'][idx_material['mass flow [lb/hr]']]
        ogr_now = self.unit_cost_interpolation(h2_produced, self.ogr_base_case)
        ogr_now['Category'] = 'Hydrogen Recovery'
        return ogr_now

    def calc_cost_Ammonia(self, main_h2_demand):
        n = main_h2_demand / 6570.404761
        if round(n, 1) in self.scale_ammonia:
            cost_sum, fertilizer_sales, opex, ammonia_demand, ammonia_cost, _ = self.get_ammonia_cost_at_scale(n)
        else:
            smaller_than_n = [x for x in self.scale_ammonia if x < n]
            greater_than_n = [x for x in self.scale_ammonia if x > n]
            n1 = max(smaller_than_n) if smaller_than_n else self.scale_ammonia[1]
            n2 = min(greater_than_n) if greater_than_n else self.scale_ammonia[-1]

            result1 = self.get_ammonia_cost_at_scale(n1)
            result2 = self.get_ammonia_cost_at_scale(n2)
            coeff1 = (n2 - n) / (n2 - n1)
            coeff2 = (n - n1) / (n2 - n1)
            result_linapprox = []
            for item1, item2 in zip(result1, result2):
                if isinstance(item1, dict):
                    item_linapprox = {k: v for k, v in item1.items()}
                    for k, v in item1.items():
                        if isinstance(v, float) or isinstance(v, int):
                            item_linapprox[k] = coeff1 * item1[k] + coeff2 * item2[k]
                elif isinstance(item1, list):
                    item_linapprox = []
                    for i1, i2 in zip(item1, item2):
                        if isinstance(i1, str):
                            item_linapprox.append(i1)
                        else:
                            item_linapprox.append(coeff1 * i1 + coeff2 * i2)
                else:
                    item_linapprox = coeff1 * item1 + coeff2 * item2
                result_linapprox.append(item_linapprox)
            cost_sum, fertilizer_sales, opex, ammonia_demand, ammonia_cost, _ = result_linapprox

        return cost_sum, fertilizer_sales, opex, ammonia_demand, ammonia_cost

    def calc_cost_SMR(self, main_h2_demand):
        smr_NG_price_US = 0.092306 / self.cost_idx_smr * self.cost_idx_1Q2022  # $/lb
        smr_NG_price_KR = self.fuel_price_usd_per_mmbtu / 14.38 * .372983  # $/lb
        smr_base_case = self.smr_base_case
        # smr_base_case['raw materials'] = smr_base_case['NG feed'] * smr_NG_price_US * operation_hr
        # smr_base_case['utilities'] = smr_base_case['annual OPEX'] - smr_base_case['raw materials']

        smr_base_NG_cost_US = smr_base_case['NG feed'] * smr_NG_price_US * self.operation_hr
        smr_base_NG_cost_KR = smr_base_case['NG feed'] * smr_NG_price_KR * self.operation_hr
        smr_base_case['utilities'] = smr_base_case['annual OPEX'] - smr_base_NG_cost_US
        smr_base_case['raw materials'] = smr_base_NG_cost_KR

        smr_now = self.unit_cost_interpolation(main_h2_demand, smr_base_case)
        smr_now['Category'] = 'SMR'
        smr_now['raw materials description'] = 'Natural Gas'
        smr_now['utilities description'] = 'Electricity'
        return smr_now, 0

    def calc_cost_PEM(self, main_h2_demand):
        #  PEM Electrolyzer - DOE, 2024 Report based on 2022$
        electrolysis_energy = 40  # kWh/kg H2
        pem_efficiency = 0.7
        pem_electrolyzer_cost = 2000  # 2022$/kW

        # pem_cap_factor, pem_elec_price = 0.74, 0.03   # Renewable Energy - Wind & PV, price: $/kWh
        pem_elec_price_kwh = self.elec_price_usd_per_mmbtu / 293.071
        pem_cap_factor = 0.5  # Renewable Energy - Korea PV (most risky), price: $/kWh

        pem_maintenance_per_capex = 0.11  # replacement cost
        pem_g_and_a_per_opex = 0.08

        pem_elec_demand = main_h2_demand / pem_efficiency * lb2kg * electrolysis_energy  # kW
        pem_capex = pem_elec_demand / pem_cap_factor * pem_electrolyzer_cost  # 2022$
        pem_opex = pem_elec_demand * pem_elec_price_kwh * self.operation_hr

        pem_now = {
            'total CAPEX': pem_capex,
            'annual OPEX': pem_opex,
            'utilities': pem_opex,
            'electricity': pem_elec_demand,
            'maintenance': pem_capex * pem_maintenance_per_capex,
            'G and A cost': pem_opex * pem_g_and_a_per_opex,
            'Category': 'PEM',
            'utilities description': 'Electricity'
        }
        return pem_now, 0

    def calc_cost_biomass_transport(self, df_material, idx_material):
        hub_to_plant = 4  # $/truck-load/mile
        load_per_truck = 15     # tonne/truck_load

        biomass_feed = df_material['90BIO'][idx_material['mass flow [lb/hr]']]
        annual_biomass_feed = biomass_feed * self.operation_hr
        lb_to_tonne = 1/2204.62

        with open('Process_Data\\Biomass_supply_summary.xlsx', 'rb') as f:
            df_transport = pd.read_excel(f).dropna()

        cost = hub_to_plant * annual_biomass_feed * lb_to_tonne / load_per_truck
        transport_now = {'annual OPEX': cost, 'feed transport': cost}
        return transport_now

    def calc_h2_unit_alone(self, name, main_h2_demand):
        if name == 'SMR':
            now, fertilizer_sales = self.calc_cost_SMR(main_h2_demand)
        elif name == 'PEM':
            now, fertilizer_sales = self.calc_cost_PEM(main_h2_demand)
        else:   # Ammonia
            now, fertilizer_sales, _, _, _ = self.calc_cost_Ammonia(main_h2_demand)
        return now, fertilizer_sales

    def calc_h2_opex_and_dfprocess(self, name, main_wo_h2, opex_names, main_h2_demand, annual_prod_saf, hourly_revenue,
                                   base_processes, base_process_names):
        now, fertilizer_sales = self.calc_h2_unit_alone(name, main_h2_demand)
        processes = [main_wo_h2, now] + base_processes[1:]
        process_names = ['Main', name] + base_process_names[1:]

        hourly_revenue = hourly_revenue.copy()
        hourly_revenue['Fertilizer'] = fertilizer_sales

        cost_sum, opex_sum, df_process = self.resume_cost_summary(processes, process_names, opex_names)
        mjsp, cost_sum, opex_sum = self.cal_MJSP(cost_sum, opex_sum, hourly_revenue, annual_prod_saf)
        return cost_sum, opex_sum, df_process

    def get_atomic_flow_idx(self, df_material):
        idx_MIXED = df_material['Stream Name'].astype(str).tolist().index('MIXED Substream')
        idx_CISOLID = df_material['Stream Name'].astype(str).tolist().index('CISOLID Substream')
        idx_NC = df_material['Stream Name'].astype(str).tolist().index('NC Substream')

        df_stream_MIXED = df_material.iloc[idx_MIXED:idx_CISOLID]
        df_stream_CISOLID = df_material.iloc[idx_CISOLID:idx_NC]
        df_stream_NC = df_material.iloc[idx_NC:]

        idx_MIXED_mass_flow = df_stream_MIXED['Stream Name'].astype(str).tolist().index('Mass Flows')
        idx_MIXED_carbon_fraction = df_stream_MIXED['Stream Name'].astype(str).tolist().index(
            'Mass fraction of carbon atoms')

        idx_CISOLID_mass_flow = df_stream_CISOLID['Stream Name'].astype(str).tolist().index('Mass Flows')
        idx_CISOLID_carbon_fraction = df_stream_CISOLID['Stream Name'].astype(str).tolist().index(
            'Mass fraction of carbon atoms')

        idx_NC_mass_flow = df_stream_NC['Stream Name'].astype(str).tolist().index('Mass Flows')
        df_stream_NC_mass_flow = df_stream_NC.iloc[idx_NC_mass_flow:idx_NC_mass_flow + 3]
        idx_NC_bio_mass_flow = df_stream_NC_mass_flow['Stream Name'].astype(str).tolist().index('BIOMASS')
        idx_NC_char_mass_flow = df_stream_NC_mass_flow['Stream Name'].astype(str).tolist().index('CHAR')

        idx_NC_comp_attr = df_stream_NC['Stream Name'].astype(str).tolist().index('Component Attributes')
        df_stream_NC_comp_attr = df_stream_NC[idx_NC_comp_attr:]

        idx_NC_comp_attr_bio = df_stream_NC_comp_attr['Stream Name'].astype(str).tolist().index('BIOMASS')
        idx_NC_comp_attr_char = df_stream_NC_comp_attr['Stream Name'].astype(str).tolist().index('CHAR')
        df_stream_NC_bio = df_stream_NC_comp_attr[idx_NC_comp_attr_bio:idx_NC_comp_attr_char]
        df_stream_NC_char = df_stream_NC_comp_attr[idx_NC_comp_attr_char:]
        df_stream_NC_bio_percent = df_stream_NC_bio.applymap(lambda x: x / 100 if not isinstance(x, str) else x)
        df_stream_NC_char_percent = df_stream_NC_char.applymap(lambda x: x / 100 if not isinstance(x, str) else x)

        idx_NC_bio_carbon_fraction = df_stream_NC_bio['Stream Name'].astype(str).tolist().index('Carbon')
        idx_NC_char_carbon_fraction = df_stream_NC_char['Stream Name'].astype(str).tolist().index('Carbon')

        atomic_flow_idx = [
            (df_stream_MIXED, idx_MIXED_mass_flow, df_stream_MIXED, idx_MIXED_carbon_fraction),
            (df_stream_CISOLID, idx_CISOLID_mass_flow, df_stream_CISOLID, idx_CISOLID_carbon_fraction),
            (df_stream_NC_mass_flow, idx_NC_bio_mass_flow, df_stream_NC_bio_percent, idx_NC_bio_carbon_fraction),
            (df_stream_NC_mass_flow, idx_NC_char_mass_flow, df_stream_NC_char_percent, idx_NC_char_carbon_fraction)
        ]
        return atomic_flow_idx

    def calc_carbon_efficiency(self, file_stream, ccs_portion=0):
        with open(file_stream, 'rb') as f:
            df_material = pd.read_excel(f, sheet_name='Material', header=3)

        atomic_flow_idx = self.get_atomic_flow_idx(df_material)
        material_in = [
            "609XX", "610AIR", "622XX", "611XX", "406XX", "250H2", "773XX", "700BFW", "777XX", "769XX",
            "771XX", "712XX", "306XX", "140XX", "130XX", "532H2", "262SLF", "263SLF", "126XX", "160WT",
            "80AIR", "120AIR", "122SND", "90BIO", "125XX", "150XX", "791XX"
        ]

        material_out = [
            "138X", "146X", "150X", "125X", "126X", "140X", "142XX",
            "311DUM", "321DUM", "306X", "316GAS", "326SAF", "705VENT", "788WWT",
            "712X", "769X", "791X", "771X", "777X", "773X", "699WWT", "691VENT",
            "406X", "331-DUM", "340DUM", "336DIES", "295X", "305X", "281X", "609X",
            "623CO2", "622X", "611X", "138D", "146D", "139D", "142D",
            "145D", "326DUM"
        ]

        atomic_flow_stream = {"in": material_in, "out": material_out}
        atomic_flow_data = {}
        for io_state, streams in atomic_flow_stream.items():
            for s in streams:
                d = []
                for df_mass, idx_mass, df_carbon, idx_carbon in atomic_flow_idx:
                    if s in df_mass.columns:
                        mflow = df_mass[s].iloc[idx_mass]
                        cfrac = df_carbon[s].iloc[idx_carbon]
                        d.extend([mflow, cfrac])
                    else:
                        d.extend([None, None])
                atomic_flow_data[s] = [io_state] + d
        atomic_flow_df = pd.DataFrame(atomic_flow_data,
                                      index=['io_state', 'MIXED_mflow', 'MIXED_cfrac', 'CISOLID_mflow', 'CISOLID_cfrac',
                                             'NC_bio_mflow', 'NC_bio_cfrac', 'NC_char_mflow', 'NC_char_cfrac'])
        atomic_flow_df.fillna(0, inplace=True)
        atomic_flow_df.loc['MIXED_cflow'] = atomic_flow_df.iloc[1] * atomic_flow_df.iloc[2]
        atomic_flow_df.loc['CISOLID_cflow'] = atomic_flow_df.iloc[3] * atomic_flow_df.iloc[4]
        atomic_flow_df.loc['NC_bio_cflow'] = atomic_flow_df.iloc[5] * atomic_flow_df.iloc[6]
        atomic_flow_df.loc['NC_char_cflow'] = atomic_flow_df.iloc[7] * atomic_flow_df.iloc[8]
        rows_cflow = [row for row in atomic_flow_df.index if 'cflow' in row]
        atomic_flow_df.loc['total_cflow'] = atomic_flow_df.loc[rows_cflow, :].sum()

        cols_wo_x = [col for col in atomic_flow_df.columns if "X" not in col]
        df_wo_x = atomic_flow_df.loc[:, cols_wo_x]
        cols_wo_dum = [col for col in df_wo_x.columns if "DUM" not in col]
        atomic_meaningful_df = df_wo_x.loc[:, cols_wo_dum]

        # atomic_meaningful_df = atomic_flow_df

        columns_in = atomic_meaningful_df.columns[atomic_meaningful_df.loc['io_state'] == "in"]
        carbon_in = atomic_meaningful_df.loc['total_cflow', columns_in].astype(float).sum()
        mass_in = atomic_meaningful_df.filter(like='mflow', axis=0).loc[:, columns_in].sum().sum()

        columns_out = atomic_meaningful_df.columns[atomic_meaningful_df.loc['io_state'] == "out"]
        carbon_out = atomic_meaningful_df.loc['total_cflow', columns_out].astype(float).sum()
        mass_out = atomic_meaningful_df.filter(like='mflow', axis=0).loc[:, columns_out].sum().sum()

        carbon_net = carbon_in - carbon_out

        yet_captured_carbon = atomic_meaningful_df.loc['total_cflow', '623CO2']

        carbon_efficiency_saf = atomic_meaningful_df.loc['total_cflow', '326SAF'] / carbon_in
        carbon_efficiency_coprod = atomic_meaningful_df.loc['total_cflow', ['316GAS', '336DIES']].sum() / carbon_in
        carbon_efficiency_ccs = yet_captured_carbon * ccs_portion / carbon_in
        carbon_efficiency_vent = (atomic_meaningful_df.filter(like='VENT').loc['total_cflow'].sum()
                                  + yet_captured_carbon * (1-ccs_portion)) / carbon_in
        carb_eff = {
            "SAF": carbon_efficiency_saf,
            "Co-products": carbon_efficiency_coprod,
            "CO2 captured": carbon_efficiency_ccs,
            "Vent": carbon_efficiency_vent
        }
        return carb_eff, carbon_net

    def get_LCOH(self, name, main_h2_demand, opex_names):
        process, fertilizer_sales = self.calc_h2_unit_alone(name, main_h2_demand)
        cs, os, dp = self.resume_cost_summary([process], [name], opex_names)
        lcoh, cs, os = self.cal_MJSP(cs, os, {'fertilizer': fertilizer_sales}, main_h2_demand*self.operation_hr)  # $/LB
        return lcoh, cs, os

    def economic_analysis(self, file_stream, file_apea, name_h2_source, ccs_portion=0., ammonia_portion=None):
        with open(file_stream, 'rb') as f:
            df_material = pd.read_excel(f, sheet_name='Material', header=3)
            df_heat = pd.read_excel(f, sheet_name='Heat', header=3)
            try:
                df_work = pd.read_excel(f, sheet_name='Work', header=3)
            except:
                df_work = None

        idx_material = self.get_idx_material(df_material)
        hourly_revenue_fuel, energy_production_fuel, _ = self.get_fuel_products(df_material, idx_material)
        hourly_revenue_work, energy_production_work = self.get_work_products(df_work)
        hourly_revenue = {**hourly_revenue_fuel, **hourly_revenue_work}
        energy_production = {**energy_production_fuel, **energy_production_work}
        annual_prod_saf = self.get_annual_prod_saf(file_stream)

        #%% Unit Operations
        # Heat Leftover
        ccs_now = self.calc_cost_CCS(df_material, idx_material, df_heat, ccs_portion)
        psa_now = self.calc_cost_PSA(df_material, idx_material)
        r510_now = self.calc_cost_r510(df_material, idx_material)
        hydrotreat_catalysts = self.calc_cost_HTcat(df_material, idx_material)
        # transport_now = calc_cost_biomass_transport(df_material, idx_material)

        with open(file_apea, 'rb') as f:
            df_prjsum = pd.read_excel(f, sheet_name='Project Summary', header=2)
            df_rawmaterial = pd.read_excel(f, sheet_name='RawMaterial Summary', header=2).dropna(how='all')

        # Main process
        main_now, main_opex = self.get_APEA_result(df_prjsum)

        # Overall
        processes = [main_now, ccs_now, psa_now, hydrotreat_catalysts, r510_now]
        process_names = ['Main', 'CCS', 'PSA', 'Catalysts', 'R-510']
        opex_names = [k for k in main_opex.keys()]

        cost_summary, opex_summary, df_process = self.resume_cost_summary(processes, process_names, opex_names)
        mjsp_base, cost_summary, opex_summary = self.cal_MJSP(cost_summary, opex_summary, hourly_revenue, annual_prod_saf)
        main_wo_h2, main_h2_demand = self.get_main_wo_h2(main_now, df_rawmaterial)

        cost_per_h2_source = [cost_summary]
        opex_per_h2_source = [opex_summary]
        dfp_per_h2_source = [df_process]
        for name in name_h2_source[1:]:
            cost_h2, opex_h2, df_h2 = self.calc_h2_opex_and_dfprocess(
                name, main_wo_h2, opex_names, main_h2_demand, annual_prod_saf, hourly_revenue, processes, process_names
            )
            cost_per_h2_source.append(cost_h2)
            opex_per_h2_source.append(opex_h2)
            dfp_per_h2_source.append(df_h2)

        if ammonia_portion is not None:
            partial_main, partial_h2_demand = self.get_main_partial_grey(main_now, df_rawmaterial, 1-ammonia_portion)
            partial_cost, partial_opex, partial_df = self.calc_h2_opex_and_dfprocess(
                'Ammonia', partial_main, opex_names, partial_h2_demand, annual_prod_saf, hourly_revenue,
                processes, process_names
            )

            cost_per_h2_source.append(partial_cost)
            opex_per_h2_source.append(partial_opex)
            dfp_per_h2_source.append(partial_df)
            name_h2_source_new = name_h2_source + ['Mix']
        else:
            name_h2_source_new = name_h2_source

        data_all = {'cost': cost_per_h2_source, 'opex': opex_per_h2_source, 'df_process': dfp_per_h2_source}
        df_summary = pd.DataFrame(opex_per_h2_source)
        df_summary.index = name_h2_source_new
        df_summary = df_summary.reindex(columns=['capital investment', 'raw materials', 'utilities',
                                                 'operating labor', 'maintenance', 'operating charges',
                                                 'plant overhead', 'G and A cost', 'co-product sales'])
        df_summary.rename(columns={"G and A cost": "governance and admin."}, inplace=True)
        df_mjsp = df_summary / annual_prod_saf
        return df_mjsp, energy_production, annual_prod_saf, main_h2_demand, opex_names, data_all, name_h2_source_new
