import os
import time
import matplotlib.pyplot as plt
import pythoncom
import win32com.client as win32
import numpy as np
import copy


def latin_hypercube_sampling(n_samples, n_variables):
    cut = np.linspace(0, 1, n_samples + 1)
    u = np.random.rand(n_samples, n_variables)
    lhs = np.zeros_like(u)
    for j in range(n_variables):
        lhs[:, j] = u[:, j] * (cut[1] - cut[0]) + cut[:-1]
        np.random.shuffle(lhs[:, j])
    return lhs

def generate_perturbed_samples(data, n_samples=5, target_sum=100.0, adjust_comp="HMW Sugars"):
    components = list(data.keys())
    original_values = np.array([data[c]['DryWtPct'] for c in components])
    n_components = len(components)
    adjust_index = components.index(adjust_comp)

    included_indices = [i for i in range(n_components) if i != adjust_index]
    lhs_samples = latin_hypercube_sampling(n_samples, len(included_indices))
    scales = 0.1 * original_values[included_indices]

    all_samples = []

    for s in range(n_samples):
        perturbed = original_values[included_indices] + (lhs_samples[s] - 0.5) * 2 * scales
        perturbed = np.maximum(perturbed, 0.0)  # No negative values

        sum_others = np.sum(perturbed)
        adjusted_value = max(0.0, target_sum - sum_others)  # Adjust to meet 100

        # Rebuild full DryWtPct list
        full_drywt = []
        j = 0
        for i in range(n_components):
            if i == adjust_index:
                full_drywt.append(round(adjusted_value, 4))
            else:
                full_drywt.append(round(perturbed[j], 4))
                j += 1

        # Build the full perturbed data dict
        sample_data = {k: {} for k in data.keys()}
        tot_sum = sum([data[comp]["TotWtPct"] for comp in components])
        for i, comp in enumerate(components):
            mw = data[comp]["MW"]
            drywt = full_drywt[i]
            totwt = drywt / 100 * tot_sum
            coeff = totwt / mw

            sample_data[comp]['DryWtPct'] = drywt
            sample_data[comp]['TotWtPct'] = totwt
            sample_data[comp]['MW'] = mw
            sample_data[comp]['Coefficient'] = coeff

        all_samples.append(sample_data)

    return all_samples


def cal_MJSP(saf, TCC, TOC, TPS):
    """
    :param saf: SAF volumetric production rate [L/hr]
    :param TCC: Total Project Capital Cost [USD]
    :param TOC: Total Operating Cost [USD/yr]
    :param TPS: Total Product Sales [USD/yr]
    :return: mjsp
    """
    try:
        saf_LPH = saf * 28.3168  # cuft -> L

        irr_desire = 0.1
        project_life = 20
        salvage_value = 0
        tax_rate = 0.35
        operation_hour = 8000

        inv_irr = 1 / (1 + irr_desire)
        sum_of_irr = inv_irr * (1 - inv_irr ** project_life) / (1 - inv_irr)

        depreciation = TCC * (1 - salvage_value) / project_life
        cap_annual = (TCC - sum_of_irr * tax_rate * depreciation) / sum_of_irr / (1 - tax_rate)  # USD/yr

        cost_annual = cap_annual + TOC - TPS
        mjsp = cost_annual / (saf_LPH * operation_hour)
    except:
        mjsp = 100
    return mjsp

def dispatch_excel_file(file_name):
    excel = win32.Dispatch("Excel.Application")
    wb = None
    for workbook in excel.Workbooks:
        if workbook.Name == f'{file_name}.xlsx':
            wb = workbook
            break
    if wb is None:
        wb = excel.Workbooks.Open(os.path.abspath(f'../Aspen/{file_name}.xlsx'))
    excel.Run("AspenSimulationWorkbook.xla! ASWActivateActiveSimulation")
    return excel, wb


class AspenCost(object):
    def __init__(self, file_name, econ_eval, info_interactive):
        self.excel, self.wb = dispatch_excel_file(file_name)
        self.ws = self.wb.Worksheets("InteractiveSheet")
        self.econ_eval = econ_eval

        now = time.localtime()
        now_str = time.strftime('%Y%m%d_%H%M%S', now)
        self.wb.Worksheets.Add()
        self.rws = self.excel.ActiveSheet
        self.rws.Name = now_str

        self.input_cell = self.ws.Range(info_interactive['input']['cell'])
        self.input_name = info_interactive['input']['name']
        dim_input = len(self.input_name)
        print(f"Does input dimension match?  {bool(len(self.input_cell) == dim_input)}")

        self.output_cell = self.ws.Range(info_interactive['output']['cell'])
        self.output_name = info_interactive['output']['name']
        dim_output = len(self.output_name)

        if dim_output == 1:
            self.check_cell = self.output_cell
        else:
            self.check_cell = self.output_cell(1,1)

        self.len_rec = dim_input + dim_output + 1
        self.rws.Range(self.rws.Cells(1,1), self.rws.Cells(1, self.len_rec)).Value = \
            self.input_name + self.output_name + ["ERROR"]

    def run(self):
        check_prev = self.check_cell.Value
        self.excel.Run("AspenSimulationWorkbook.xla! ASWInitandRunActiveSimulation")
        time.sleep(15)
        cnt = 0
        error = 0

        while True:
            try:
                time.sleep(1)
                state = self.excel.StatusBar
                time.sleep(0.25)
                if 'FALSE' == state:
                    if self.econ_eval:
                        print("Wait_for_Costing_Result")
                        time.sleep(60)
                    else:
                        time.sleep(2)

                    for cnt_advance in range(10):
                        if check_prev == self.check_cell.Value:
                            print(f"Wait just in advance #{cnt_advance}")
                            time.sleep(5)
                        else:
                            break
                    if check_prev == self.check_cell.Value:
                        print("Still stuck")
                        error = 99
                    return error
                elif 'fail' in state.lower():
                    print('Error_Detected')
                    return 100
                else:
                    cnt += 1
                    print('PASSED ', cnt)
                    assert cnt < 60

            except:
                cnt += 1
                print('passed, ', cnt)
                assert cnt < 60

    def get_output(self):
        while True:
            try:
                _val = self.output_cell.Value
                _dict = {
                    k: v[0] for k, v in zip(self.output_name, _val)
                }
                return _dict
            except:
                time.sleep(0.5)
                pass

    # def check_quality(self):
    #     _cnt = 0
    #     while True:
    #         try:
    #             _val = self.qual_cell.Value
    #             _dict = {
    #                 k: v[0] for k, v in zip(self.qual_name, _val)
    #             }
    #             _dict["HHV"] = _dict["HHV"] * 0.001055 / 0.453592  # Btu/lb -> MJ/kg
    #             _dict["SG"] = _dict["SG"] * .453592 / 0.0283168  # lb/cuft -> kg/m3
    #
    #             # C <= 0
    #             _const = [
    #                 42.8 - _dict["HHV"],
    #                 775 - _dict["SG"],
    #                 _dict["SG"] - 840,
    #                 # _dict["MFP"] + 40,
    #                 # 38 - _dict["MBP"],
    #                 8 - _dict["ARM"],
    #                 _dict["ARM"] - 25,
    #                 _dict["SLF"] - 0.003
    #             ]
    #
    #             _violate = [(v > 0) * 10 for v in _const]
    #             return _violate, _dict
    #         except:
    #             _cnt += 1
    #             time.sleep(0.5)
    #             assert _cnt < 10

    def evaluate(self, x):
        global GLOBAL_I

        cntt = 0
        while True:
            try:
                print("Cool time")
                time.sleep(10)
                x_val = x.tolist()[0]
                self.input_cell.Value = [[xx, ] for xx in x_val]
                time.sleep(1)

                e_sim = self.run()
                GLOBAL_I += 1
                output = self.get_output()
                cost = list(output.values())[0]

                self.rws.Range(self.rws.Cells(GLOBAL_I + 1, 1), self.rws.Cells(GLOBAL_I + 1, self.len_rec)).Value = \
                   x_val + list(output.values()) + e_sim
                print(f"{GLOBAL_I}: {cost}, error: {e_sim}")
                self.wb.Save()
                return cost + e_sim

            except:
                cntt += 1
                print('Critical..', cntt)
                assert cntt < 10
