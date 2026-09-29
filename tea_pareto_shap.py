"""Exact KernelSHAP attribution of MJSP across the §4.7 drivers, for the two
~25%-decarbonization frontier points: grey-H2 + CCS 25% (a=0, c=0.25) and
Green NH3 25% (a=0.25, c=0). Interaction-aware complement to tea_tornado.

MJSP model is the SAME one the whole pareto analysis uses (mix_row engine re-run
for T&S/electricity/co-product/capacity + linear cost terms for biomass/H2/
ammonia/CAPEX). Each point has <=7 drivers, so KernelSHAP with nsamples=2**M and
l1_reg=0 enumerates every coalition -> values are exact Shapley (sum == f(hi)-f(lo)).
"""
import os
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import shap
from funs import TEA

# reuse the analysis' single source of truth for files, style, MJSP model, ranges
from tea_pareto_front import FS, FA, SA_RC, mix_row, BIO_PRICE_FR
from tea_tornado import (H2_RANGE, ELEC_F, COPROD_F, CAPEX_PM, CF_HOURS, TS_RANGE,
                         TS_BASE, AMM_FEED_USD_L, AMM_P_BASE, AMM_PRICE, LB2KG, raw_costs)

# driver -> (low input value, high input value); low is the cheaper-input end
RANGES = {
    'Biomass':     (BIO_PRICE_FR, 0.05268),               # $/lb, FR floor -> galik supply-curve
    'Gray H₂': H2_RANGE,                              # $/kg
    'Ammonia':     AMM_PRICE,                              # $/lb
    'CAPEX':       (1 - CAPEX_PM, 1 + CAPEX_PM),           # multiplier
    'CO₂ T&S': TS_RANGE,                              # $/tCO2
    'Electricity': (19.05 * ELEC_F[0], 19.05 * ELEC_F[1]),  # $/MMBtu
    'Co-product':  COPROD_F,                              # multiplier
    'Capacity':    CF_HOURS,                              # operation hours/yr
}

# per point: (ammonia_portion a, ccs_portion c, driver order). Gray H2 present when a<1,
# ammonia when a>0, CO2 T&S when c>0 -> exactly the bars tea_tornado draws for each point.
POINTS = {
    'Grey H₂ + CCS 25%': (0.0, 0.25,
        ['Biomass', 'Gray H₂', 'CAPEX', 'CO₂ T&S', 'Electricity', 'Co-product', 'Capacity']),
    'Green NH₃ 25%': (0.25, 0.0,
        ['Biomass', 'Gray H₂', 'Ammonia', 'CAPEX', 'Electricity', 'Co-product', 'Capacity']),
}

# raw-material rates come from the APEA and do not depend on the perturbed knobs -> read once
_H2_COST, _H2_RATE, _BIO_COST = raw_costs(TEA(), FA)


def mjsp_point(a: float, c: float, v: dict[str, float]) -> float:
    """MJSP [$/L] for point (a,c) with all drivers set to the values in v. Engine knobs
    (T&S/electricity/co-product/capacity) applied together on one TEA; biomass/H2/ammonia/
    CAPEX added as the same linear cost terms used elsewhere, from this run's quantities."""
    t = TEA()
    t.co2_ts_usd_per_ton = v.get('CO₂ T&S', TS_BASE)
    t.elec_price_usd_per_mmbtu = v['Electricity']
    t.product_price_work['ELC-'] = v['Electricity']       # sales reference copied at __init__
    cf = v['Co-product']
    t.product_price_stream = {'316GAS': 0.75757 * cf, '326SAF': 0, '336DIES': 0.6 * cf}
    t.operation_hr = v['Capacity']
    base, row, saf = mix_row(t, a, c)
    op = t.operation_hr
    mjsp = base + (v['Biomass'] / BIO_PRICE_FR - 1.) * _BIO_COST * op / saf
    if a < 1:                                             # gray H2 on the grey share
        p_base = (_H2_COST / _H2_RATE) / LB2KG
        mjsp += (v['Gray H₂'] / p_base - 1.) * _H2_COST * (1 - a) * op / saf
    if a > 0:                                             # ammonia price on the ammonia share
        mjsp += a * AMM_FEED_USD_L * (v['Ammonia'] / AMM_P_BASE - 1.)
    mjsp += (v['CAPEX'] - 1.) * row['capital investment']  # CAPEX multiplier on cap inv (incl CCS)
    return mjsp


def shap_point(a: float, c: float, order: list[str]) -> tuple[float, np.ndarray, float]:
    """(base = MJSP at all-low inputs, exact Shapley values, MJSP at all-high inputs)."""
    def f(X: np.ndarray) -> np.ndarray:
        return np.array([mjsp_point(a, c, dict(zip(order, row))) for row in np.atleast_2d(X)])

    x_lo = np.array([[RANGES[k][0] for k in order]])
    x_hi = np.array([[RANGES[k][1] for k in order]])
    expl = shap.KernelExplainer(f, x_lo)                  # background = cheaper-input corner
    # nsamples=2**M enumerates all coalitions; l1_reg=0 keeps every feature -> exact Shapley
    sv = np.asarray(expl.shap_values(x_hi, nsamples=2 ** len(order), l1_reg=0)).ravel()
    return float(expl.expected_value), sv, float(f(x_hi)[0])


def panel(ax, name: str, order: list[str], base: float, sv: np.ndarray) -> None:
    """Signed Shapley contribution per driver, largest on top, bars from the base MJSP."""
    idx = np.argsort(np.abs(sv))                          # ascending -> largest on top
    y = range(len(order))
    for i, j in enumerate(idx):
        ax.barh(i, sv[j], left=base, color='#d73027' if sv[j] >= 0 else '#4575b4', edgecolor='white')
    ax.axvline(base, color='k', lw=1)
    ax.set_yticks(list(y))
    ax.set_yticklabels([order[j] for j in idx])
    ax.set_xlabel('MJSP [$/L SAF]')
    ax.text(0.98, 0.04, f'{name}\n(base {base:.2f} -> {base + sv.sum():.2f})',
            transform=ax.transAxes, ha='right', va='bottom', fontsize='large')


def main() -> None:
    sys.stdout.reconfigure(encoding='utf-8')
    plt.rcParams.update(SA_RC)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharex=True)
    records = []
    for ax, (name, (a, c, order)) in zip(axes, POINTS.items()):
        base, sv, hi = shap_point(a, c, order)
        assert abs(base + sv.sum() - hi) < 1e-6, name    # exactness: contributions sum to the swing
        panel(ax, name, order, base, sv)
        print(f'\n{name}: base(all-low) MJSP = {base:.3f} $/L -> all-high = {hi:.3f}')
        for k, s in sorted(zip(order, sv), key=lambda t: -abs(t[1])):
            print(f'   {k:<12} {s:+.4f}')
            records.append({'point': name, 'driver': k, 'shap_usd_per_L': s,
                            'base_mjsp': base, 'high_mjsp': hi})

    from matplotlib.patches import Patch
    fig.legend(handles=[Patch(color='#d73027', label='raises MJSP'),
                        Patch(color='#4575b4', label='lowers MJSP')],
               loc='upper center', ncol=2, framealpha=0.)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    os.makedirs('Figure', exist_ok=True)
    fig.savefig(os.path.join('Figure', 'shap_ccs25_vs_nh325.png'), dpi=150)
    os.makedirs('Result', exist_ok=True)
    pd.DataFrame(records).round(4).to_excel(os.path.join('Result', 'shap_ccs25_vs_nh325.xlsx'), index=False)
    print('\nOK: exact-Shapley self-checks passed; wrote Figure/shap_ccs25_vs_nh325.png + Result xlsx')


if __name__ == '__main__':
    main()
