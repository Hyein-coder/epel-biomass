"""SHAP attribution of MJSP across the §4.7 drivers, for the cheapest CORSIA-compliant
point on the updated (KR-mix) pareto front: Green NH3 10% + CCS 50% (a=0.10, c=0.50).
Distribution-based complement to tea_tornado (beeswarm over sampled inputs).

MJSP model is the SAME one the whole pareto analysis uses (mix_row engine re-run
for T&S/electricity/co-product/capacity + linear cost terms for biomass/H2/ammonia/
CAPEX). Method: Latin-hypercube sample N points over each point's driver ranges
(N TEA calls), fit a gradient-boosted surrogate, TreeSHAP on the surrogate (no
further TEA calls). SHAP is exact on the surrogate; the surrogate is the only
approximation, and TEA is near-additive so in-sample R2 ~ 1 (asserted).
"""
import os
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import shap
from scipy.stats import qmc
from sklearn.ensemble import GradientBoostingRegressor
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
# Single case = the cheapest CORSIA-compliant point on the updated (KR-mix) pareto front:
# Green NH3 10% (a=0.10) + CCS 50% (c=0.50). Has all three feedstock/CCS drivers active -> 8 drivers.
POINTS = {
    'Green NH₃ 10% + CCS 50%': (0.10, 0.50,
        ['Biomass', 'Gray H₂', 'Ammonia', 'CAPEX', 'CO₂ T&S', 'Electricity', 'Co-product', 'Capacity']),
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


N_SAMPLES = 128   # LHS points per frontier point over its 7 driver ranges (>100, user request)


def shap_sample(a: float, c: float, order: list[str], n: int = N_SAMPLES,
                seed: int = 0) -> tuple[np.ndarray, np.ndarray, float]:
    """LHS-sample n points over the point's driver ranges (n TEA calls), fit a surrogate,
    return (X, per-sample TreeSHAP values, surrogate in-sample R2)."""
    lo = np.array([RANGES[k][0] for k in order])
    hi = np.array([RANGES[k][1] for k in order])
    X = qmc.scale(qmc.LatinHypercube(d=len(order), seed=seed).random(n), lo, hi)
    y = np.array([mjsp_point(a, c, dict(zip(order, row))) for row in X])   # the n TEA calls
    surr = GradientBoostingRegressor(random_state=seed).fit(X, y)
    sv = np.asarray(shap.TreeExplainer(surr).shap_values(X))
    return X, sv, float(surr.score(X, y))


def mlabel(s: str) -> str:
    """Render unicode subscripts via mathtext ($_2$) so fonts without the ₂/₃ glyphs don't tofu."""
    return s.replace('₂', r'$_2$').replace('₃', r'$_3$')


def beeswarm(ax, X: np.ndarray, sv: np.ndarray, order: list[str], title: str, seed: int = 0):
    """SHAP beeswarm: one row of n dots per driver, x = SHAP value, colour = driver value
    (blue low -> red high). Drivers ordered by mean|SHAP|, largest on top."""
    rank = np.argsort(np.abs(sv).mean(0))                 # ascending -> largest ends on top
    rng = np.random.default_rng(seed)
    sc = None
    for row, j in enumerate(rank):
        f = X[:, j]
        span = f.max() - f.min()
        fn = (f - f.min()) / span if span else np.zeros_like(f)   # normalise value to 0..1 for colour
        jit = (rng.random(len(f)) - 0.5) * 0.7            # vertical jitter so dots don't stack
        sc = ax.scatter(sv[:, j], row + jit, c=fn, cmap='RdYlBu_r', s=10,
                        edgecolor='none', alpha=0.8, vmin=0, vmax=1)
    ax.axvline(0, color='k', lw=1)
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([mlabel(order[j]) for j in rank])
    ax.set_xlabel('SHAP value [$/L SAF]')
    # title bottom-left: bottom-right collides with the right-side colorbar
    ax.text(0.02, 0.04, mlabel(title), transform=ax.transAxes, ha='left', va='bottom', fontsize='large')
    return sc


def main() -> None:
    sys.stdout.reconfigure(encoding='utf-8')
    plt.rcParams.update(SA_RC)
    plt.rcParams['figure.autolayout'] = False   # let constrained_layout place the colorbar (autolayout fights it)
    os.makedirs('Result', exist_ok=True)
    # cache the LHS samples + SHAP so cosmetic replots skip the ~13-min resample; delete the npz
    # (or change POINTS) to force a fresh sample. Keys must match POINTS or the cache is stale.
    cache = os.path.join('Result', 'shap_samples.npz')
    data = None
    if os.path.exists(cache):
        cached = np.load(cache, allow_pickle=True)['data'].item()
        if set(cached) == set(POINTS):
            data = cached
    if data is None:
        data = {}
        for name, (a, c, order) in POINTS.items():
            X, sv, r2 = shap_sample(a, c, order)
            data[name] = {'X': X, 'sv': sv, 'r2': r2, 'order': order}
        np.savez(cache, data=np.array(data, dtype=object))

    n = len(POINTS)
    # single panel needs a landscape aspect (near-square looks cramped); multi-panel scales by count
    fig, axes = plt.subplots(1, n, figsize=(7 if n == 1 else 5.5 * n, 4.5), sharex=True,
                             constrained_layout=True, squeeze=False)
    axes = axes.ravel()
    records, sc = [], None
    for ax, (name, d) in zip(axes, data.items()):
        X, sv, r2, order = d['X'], d['sv'], d['r2'], d['order']
        assert r2 > 0.99, (name, r2)                     # surrogate must track the near-additive TEA
        sc = beeswarm(ax, X, sv, order, f'{name}\n(n={len(X)}, R²={r2:.3f})')
        print(f'\n{name}: n={len(X)} LHS points, surrogate R²={r2:.4f}')
        for k, m, s in sorted(zip(order, np.abs(sv).mean(0), sv.mean(0)), key=lambda t: -t[1]):
            print(f'   {k:<12} mean|SHAP| {m:.4f}   mean {s:+.4f}')
            records.append({'point': name, 'driver': k, 'mean_abs_shap': m, 'mean_shap': s})

    cb = fig.colorbar(sc, ax=list(axes), fraction=0.03, pad=0.02)
    cb.set_ticks([0, 1]); cb.set_ticklabels(['low', 'high']); cb.set_label('driver value')
    os.makedirs('Figure', exist_ok=True)
    fig.savefig(os.path.join('Figure', 'shap_beeswarm_nh10_ccs50.png'), dpi=150)
    os.makedirs('Result', exist_ok=True)
    pd.DataFrame(records).round(4).to_excel(os.path.join('Result', 'shap_nh10_ccs50.xlsx'), index=False)
    print('\nOK: surrogate R²>0.99; wrote Figure/shap_beeswarm_nh10_ccs50.png + Result xlsx')


if __name__ == '__main__':
    main()
