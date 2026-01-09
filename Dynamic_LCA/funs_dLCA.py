import numpy as np
import pyomo.environ as pyo
from funs import TEA
import pickle
from funs_lca import get_WTWa_conventional, get_WTWa_ftjet, get_WTWa_pyrolysis

# (Levasseur, 2010)
# Bern carbon-climate model using a background CO2
# concentration of 378 ppm form IPCC 2007 report

a0 = 0.217
a1 = 0.259
a2 = 0.338
a3 = 0.186
t1 = 172.9  # year
t2 = 18.51
t3 = 1.186

tau_CH4 = 12
tau_N2O = 114

def atm_concentration_CO2(t):
    return a0 + a1 * np.exp(-t/t1) + a2 * np.exp(-t/t2) + a3 * np.exp(-t/t3)

def atm_concentration_CH4(t):
    return np.exp(-t/tau_CH4)

def atm_concentration_N2O(t):
    return np.exp(-t/tau_N2O)

def aGWP_CO2(t):
    rad_eff_CO2 = 1.759e-15
    agwp = rad_eff_CO2 * (a0*t + a1 * t1 * (1 - np.exp(-t/t1)) + a2 * t2 * (1 - np.exp(-t/t2))
                          + a3 * t3 * (1 - np.exp(-t/t3)))
    return agwp

def aGWP_CH4(t):
    rad_eff_CH4 = 7.54e-14
    agwp = rad_eff_CH4 * tau_CH4 * (1 - np.exp(-t/tau_CH4))
    return agwp

def aGWP_N2O(t):
    rad_eff_N2O = 3.7e-13
    agwp = rad_eff_N2O * tau_N2O * (1 - np.exp(-t/tau_N2O))
    return agwp

class DLCA(object):
    def __init__(self, timeframe):
        self.timeframe = timeframe

    def dGWP_density_CO2(self, t):
        return aGWP_CO2(self.timeframe - t) / aGWP_CO2(self.timeframe)
        # return sum([aGWP_CO2(k+1) for k in range(self.timeframe-t)])/sum([aGWP_CO2(k+1) for k in range(self.timeframe)])

    def dGWP_density_CH4(self, t):
        return aGWP_CH4(self.timeframe - t) / aGWP_CO2(self.timeframe)
        # return sum([aGWP_CH4(k+1) for k in range(self.timeframe-t)])/sum([aGWP_CH4(k+1) for k in range(self.timeframe)])

    def dGWP_density_N2O(self, t):
        return aGWP_N2O(self.timeframe - t) / aGWP_CO2(self.timeframe)
        # return sum([aGWP_N2O(k+1) for k in range(self.timeframe-t)])/sum([aGWP_N2O(k+1) for k in range(self.timeframe)])

def get_emission_target(_file_wtwa):
    lca_conventional = get_WTWa_conventional(_file_wtwa)
    _target = 0.9 * lca_conventional['WTWa']['GHG-100']  # g/MJ
    return _target

def get_wtwa(case, _file_wtwa, _file_name):
    lca_ftjet = get_WTWa_ftjet(_file_wtwa)
    _biogen_carb_ptwa = lca_ftjet['PTWa']['CO2_Biogenic']

    _lca_case = get_WTWa_pyrolysis(case, _file_name, _file_wtwa)
    _biogen_carb_wtp = _lca_case['WTP']['CO2_Biogenic']
    _biogen_carb_wtwa = _biogen_carb_wtp + _biogen_carb_ptwa
    return _lca_case['WTWa']['CO2'], _biogen_carb_wtwa

class PLANT(object):
    def __init__(self, emission, sequestration):
        """

        :param emission: {val: , duration: }
        :param sequestration: {val: , duration: }
        """
        self.emission_val = emission['val']
        self.emission_lifetime = emission['lifetime']
        self.sequestration_val = sequestration['val']
        self.sequestration_duration = sequestration['duration']

    def get_traj_emission(self, timeframe):
        traj_emission = [self.emission_val] * self.emission_lifetime + [0] * max(timeframe - self.emission_lifetime, 0)
        return traj_emission

    def get_traj_sequester(self, timeframe, timegap):
        mini_sequester = [-self.sequestration_val] * self.sequestration_duration
        traj_sequester_each_year = []
        for t in range(self.emission_lifetime):
            mini_seq_each_year = [0] * (timegap + t) + mini_sequester + [0] * max(timeframe - timegap - t, 0)
            traj_sequester_each_year.append(mini_seq_each_year)
        traj_seq = [sum([traj[k] for traj in traj_sequester_each_year]) for k in range(timeframe)]
        return traj_seq

def get_dlca_full_operation(traj_emission, traj_sequester, timeframe):
    dlca = DLCA(timeframe)
    traj_net = [traj_emission[k] + traj_sequester[k] for k in range(len(traj_emission))]
    traj_dlca = [traj_net[k] * dlca.dGWP_density_CO2(k) for k in range(len(traj_emission))]
    return traj_dlca

def define_traj(timeframe, timegap, emission, sequestration):
    plant = PLANT(emission, sequestration)
    traj_emission = plant.get_traj_emission(timeframe)
    traj_sequester = plant.get_traj_sequester(timeframe, timegap)
    return plant, traj_emission, traj_sequester

def define_common_components(model, timeframe, timegap, emission, sequestration,
                             ramping_rate=None):
    dlca = DLCA(timeframe)
    _, traj_emission, traj_sequester = define_traj(timeframe, timegap, emission, sequestration)

    # model = pyo.ConcreteModel()
    model.T = pyo.RangeSet(0, timeframe-1)
    model.T_opt = pyo.RangeSet(0, emission['lifetime']-1)  # Variables
    model.T_fixed = pyo.RangeSet(emission['lifetime'], timeframe-1)  # Fixed to 1.0

    model.schedule_opt = pyo.Var(model.T, bounds=(0.1, 1))

    def schedule_operation_rule(model, k):
        if k in model.T_opt:
            return model.schedule_opt[k]
        else:
            return 0.0  # Fixed value for k >= T_opt
    model.schedule_operation = pyo.Expression(model.T, rule=schedule_operation_rule)

    def traj_net_rule(_model, k):
        return traj_emission[k] * _model.schedule_operation[k] + traj_sequester[k]
    model.traj_net = pyo.Expression(model.T, rule=traj_net_rule)

    def traj_DLCA_rule(_model, k):
        return _model.traj_net[k] * dlca.dGWP_density_CO2(k)
    model.traj_DLCA = pyo.Expression(model.T, rule=traj_DLCA_rule)

    def total_DLCA_rule(_model):
        return sum(_model.traj_DLCA[k] for k in _model.T)
    model.total_DLCA = pyo.Expression(rule=total_DLCA_rule)

    def total_Static_rule(_model):
        return sum(_model.traj_net[k] for k in _model.T)
    model.total_StaticLCA = pyo.Expression(rule=total_Static_rule)

    if ramping_rate is not None:
        def ramping_rule_lower(_model, k):
            if k < 1:
                return pyo.Constraint.Skip
            elif k in _model.T_opt:
                return _model.schedule_operation[k] - _model.schedule_operation[k - 1] >= -ramping_rate
            else:
                return pyo.Constraint.Skip
        model.ramping_lower = pyo.Constraint(model.T_opt, rule=ramping_rule_lower)
        def ramping_rule_upper(_model, k):
            if k < 1:
                return pyo.Constraint.Skip
            elif k in _model.T_opt:
                return _model.schedule_operation[k] - _model.schedule_operation[k - 1] <= ramping_rate
            else:
                return pyo.Constraint.Skip
        model.ramping_upper = pyo.Constraint(model.T_opt, rule=ramping_rule_upper)

    return model

def define_max_operation_obj(model):
    def max_operation_rule(_model):
        return sum(_model.schedule_operation[k] for k in _model.T_opt)
    model.max_operation = pyo.Objective(rule=max_operation_rule, sense=pyo.maximize)
    return model

def build_model_DLCA(timeframe, timegap, emission, sequestration, total_target=0, ramping_rate=None):
    model = pyo.ConcreteModel()
    define_common_components(model, timeframe, timegap, emission, sequestration, ramping_rate=ramping_rate)
    define_max_operation_obj(model)
    model.total_constraint = pyo.Constraint(expr=model.total_DLCA == total_target)
    return model

def build_model_Static(timeframe, timegap, emission, sequestration, total_target=0, ramping_rate=None):
    model = pyo.ConcreteModel()
    define_common_components(model, timeframe, timegap, emission, sequestration, ramping_rate=ramping_rate)
    define_max_operation_obj(model)
    model.total_constraint = pyo.Constraint(expr=model.total_StaticLCA == total_target)
    return model

def solve_model(model, print_lv=5):
    solver = pyo.SolverFactory('ipopt')  # Use 'ipopt' for nonlinear constraints
    results = solver.solve(model, tee=True)
    if results.solver.Status == 'warning':
        results = solver.solve(model, tee=True, options={'max_iter': 10000, 'print_level': print_lv})
    return results

case_scale = [1, 2.5, 5, 7.5, 10, 20, 30]
tea = TEA()
# def get_pyro_base_cost(cp):
#     file_stream = f'..\\Process_Data\\Pyrolysis_551_Scale{int(cp * 10):04d}_Streams.xlsx'
#     file_apea = f'..\\Process_Data\\Pyrolysis_551_Scale{int(cp * 10):04d}_APEA.xlsm'
#     mjsp, energy_prod, annual_saf, h2_demand, opex_names, data, h2_source \
        # = tea.economic_analysis(file_stream, file_apea, ['Base'])
#     annual_saf_MJ = energy_prod['326SAF'] * 8000 * 3600   # MW = MJ/sec -> MJ/yr
#     base_cost = mjsp * annual_saf
#     cat_fixed = ['capital investment', 'plant overhead', 'governance and admin.']
#     cat_variable = ['raw materials', 'utilities', 'co-product sales', 'operating labor',
#                     'maintenance', 'operating charges']
#
#     fixed_cost = base_cost[cat_fixed].sum().sum()
#     variable_cost = base_cost[cat_variable].sum().sum()
#     return fixed_cost, variable_cost, annual_saf, annual_saf_MJ
#
# cashflow = {
#     'fixed_cost': [], 'variable_cost': [], 'annual_saf': [], 'annual_saf_MJ': []
# }
# for capacity in case_scale:
#     f, v, s, sMJ = get_pyro_base_cost(capacity)
#     cashflow['fixed_cost'].append(f)
#     cashflow['variable_cost'].append(v)
#     cashflow['annual_saf'].append(s)
#     cashflow['annual_saf_MJ'].append(sMJ)
#
# with open('cashflow_data.pkl', 'wb') as file:
#     pickle.dump(cashflow, file)

with open('cashflow_data.pkl', 'rb') as file:
    cashflow = pickle.load(file)
slope_annual_saf_MJ = (cashflow['annual_saf_MJ'][-1] - cashflow['annual_saf_MJ'][0]) / (case_scale[-1] - case_scale[0])

unit_saf = cashflow['annual_saf'][0]
policy_scale = {25: 35, 15: 24, 5: 4.8, 0: 2}


# relaxed_boundary = [0.95, 30.05]
# relaxed_cashflow_data = {
#     k: [d[idx] * relaxed_boundary[idx]/case_scale[idx] for idx in [0, -1]] for k, d in cashflow.items()
# }   # Variable cost has a reverse direction.
# extended_case_scale = [relaxed_boundary[0]] + case_scale + [relaxed_boundary[-1]]
# extended_cashflow = {
#     k: [relaxed_cashflow_data[k][0]] + d + [relaxed_cashflow_data[k][-1]] for k, d in cashflow.items()
# }

# irr = 0
irr = tea.irr_desire
def define_cashflow_prob(model, _saf_price, fix_capacity=None, apply_policy=False, _credit_price=0, _saf_target=0):
    model.capacity = pyo.Var(bounds=(1, 30))
    if fix_capacity is not None:
        model.capacity.fix(min(max(fix_capacity, 1), 30))

    # model.base_fc = model.capacity * cashflow['fixed_cost'][0]
    # model.base_vc = model.capacity * cashflow['variable_cost'][0]
    # model.base_saf = model.capacity * cashflow['annual_saf'][0]

    model.base_fc = pyo.Var()
    model.base_vc = pyo.Var()
    model.base_saf = pyo.Var()

    model.pw_fixed_cost = pyo.Piecewise(
        model.base_fc,
        model.capacity,
        pw_pts=case_scale,
        f_rule=cashflow['fixed_cost'],
        pw_constr_type='EQ',
        pw_repn='BIGM_BIN'
    )
    model.pw_variable_cost = pyo.Piecewise(
        model.base_vc,
        model.capacity,
        pw_pts=case_scale,
        f_rule=cashflow['variable_cost'],
        pw_constr_type='EQ',
        pw_repn='BIGM_BIN'
    )
    model.pw_saf = pyo.Piecewise(
        model.base_saf,
        model.capacity,
        pw_pts=case_scale,
        f_rule=cashflow['annual_saf'],
        pw_constr_type='EQ',
        pw_repn='BIGM_BIN'
    )   # L / yr

    def linear_saf_MJ_rule(_model):
        return cashflow['annual_saf_MJ'][0] + slope_annual_saf_MJ * (_model.capacity - case_scale[0])
    model.base_saf_MJ = pyo.Expression(rule=linear_saf_MJ_rule)

    def credit_rule(_model, k):
        return (_saf_target - _model.traj_net[k]) * _model.base_saf_MJ / 1e6 * _credit_price / (1+irr)**k
    model.credit = pyo.Expression(model.T, rule=credit_rule)

    def sales_rule(_model, k):
        production = _model.base_saf * _saf_price
        return production * _model.schedule_operation[k] / (1+irr)**k
    model.sales = pyo.Expression(model.T, rule=sales_rule)

    def cost_variable_rule(_model, k):
        expense = _model.base_vc
        return expense * _model.schedule_operation[k] / (1+irr)**k
    model.cost_variable = pyo.Expression(model.T, rule=cost_variable_rule)

    def cost_fixed_rule(_model, k):
        if k in _model.T_opt:
            return _model.base_fc / (1+irr)**k
        else:
            return 0.0
    model.cost_fixed = pyo.Expression(model.T, rule=cost_fixed_rule)

    def cashflow_rule(_model, k):
        return _model.sales[k] - _model.cost_fixed[k] - _model.cost_variable[k] + _model.credit[k]
    model.cashflow = pyo.Expression(model.T, rule=cashflow_rule)

    def penetration_rule(_model, k):
        return _model.schedule_operation[k] * _model.base_saf / unit_saf
    model.penetration = pyo.Expression(model.T, rule=penetration_rule)

    def policy_rule(_model, k):
        for policy_k, policy_v in policy_scale.items():
            if k > policy_k:
                return _model.penetration[k] >= policy_v
        return pyo.Constraint.Skip
    if apply_policy:
        model.policy_constraint = pyo.Constraint(model.T_opt, rule=policy_rule)

    model.scaling_factor = pyo.Suffix(direction=pyo.Suffix.EXPORT)
    model.scaling_factor[model.base_saf] = 1e6
    model.scaling_factor[model.base_fc] = 1e6
    model.scaling_factor[model.base_vc] = 1e6
    model.scaling_factor[model.sales] = 1e6
    model.scaling_factor[model.cost_fixed] = 1e6
    model.scaling_factor[model.cost_variable] = 1e6
    model.scaling_factor[model.cashflow] = 1e6
    model.scaling_factor[model.pw_fixed_cost] = 1e6
    model.scaling_factor[model.pw_variable_cost] = 1e6
    model.scaling_factor[model.pw_saf] = 1e6

    model.scaling_factor[model.base_saf_MJ] = 1e8
    model.scaling_factor[model.credit] = 1e6

    def total_cashflow_rule(_model):
        return sum(_model.cashflow[k] for k in _model.T_opt)
    model.total_cashflow = pyo.Expression(rule=total_cashflow_rule)
    return model

def define_max_cashflow_obj(model):
    model.max_cashflow = pyo.Objective(expr=model.total_cashflow, sense=pyo.maximize)
    return model

def define_cashflow_equality(model):
    model.cashflow_equality = pyo.Constraint(expr=model.total_cashflow == 0.)
    return model

def define_min_emission_obj(model):
    model.min_emission = pyo.Objective(expr=model.total_DLCA, sense=pyo.minimize)
    return model

def define_pareto_obj(model, weight_emission, scale_factor):
    def pareto_rule(_model):
        min_emission = _model.total_DLCA * weight_emission / scale_factor[0]
        max_cash = _model.total_cashflow * (1-weight_emission) / scale_factor[1]
        return min_emission - max_cash
    model.min_pareto = pyo.Objective(rule=pareto_rule, sense=pyo.minimize)
    return model

def build_model_PyroCashflow(timeframe, timegap, emission, sequestration,
                             ramping_rate=None, saf_price=2.4, fix_capacity=None,
                             total_target=0, apply_policy=False, saf_target=0, credit_price=0):
    model = pyo.ConcreteModel()
    define_common_components(model, timeframe, timegap, emission, sequestration, ramping_rate=ramping_rate)
    define_cashflow_prob(model, saf_price, fix_capacity=fix_capacity, apply_policy=apply_policy,
                         _credit_price=credit_price, _saf_target=saf_target)
    model.total_constraint = pyo.Constraint(expr=model.total_DLCA == total_target)
    define_max_cashflow_obj(model)
    return model

def build_model_PyroOperation(timeframe, timegap, emission, sequestration,
                              ramping_rate=None, saf_price=2.4, fix_capacity=None,
                              total_target=0, apply_policy=False, saf_target=0, credit_price=0):
    model = pyo.ConcreteModel()
    define_common_components(model, timeframe, timegap, emission, sequestration, ramping_rate=ramping_rate)
    define_cashflow_prob(model, saf_price, fix_capacity=fix_capacity, apply_policy=apply_policy,
                         _credit_price=credit_price, _saf_target=saf_target)
    model.total_constraint = pyo.Constraint(expr=model.total_DLCA == total_target)
    define_max_operation_obj(model)
    return model

def build_model_PyroMinEmission(timeframe, timegap, emission, sequestration,
                                ramping_rate=None, saf_price=2.4, fix_capacity=None,
                                saf_target=0, credit_price=0):
    model = pyo.ConcreteModel()
    define_common_components(model, timeframe, timegap, emission, sequestration, ramping_rate=ramping_rate)
    define_cashflow_prob(model, saf_price, fix_capacity=fix_capacity, apply_policy=True,
                         _credit_price=credit_price, _saf_target=saf_target)
    define_cashflow_equality(model)
    define_min_emission_obj(model)
    return model

def build_model_PyroPareto(timeframe, timegap, emission, sequestration,
                           weight_emission, emission_ub, profit_lb, scale_factor,
                           saf_price=2.4, fix_capacity=None, saf_target=0, credit_price=0):
    model = pyo.ConcreteModel()
    define_common_components(model, timeframe, timegap, emission, sequestration)
    define_cashflow_prob(model, saf_price, fix_capacity=fix_capacity, apply_policy=True,
                         _credit_price=credit_price, _saf_target=saf_target)

    model.emission_ub = pyo.Constraint(expr=model.total_DLCA <= emission_ub)
    model.profit_lb = pyo.Constraint(expr=model.total_cashflow >= profit_lb)

    define_pareto_obj(model, weight_emission, scale_factor)
    return model
