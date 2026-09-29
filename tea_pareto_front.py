"""Pareto front (min MJSP, min GHG) over a 6x5 grid of ammonia-cracker scale x
CCS portion, main SAF process unit fixed at x10 (MJSP knee point). 551 basis.

Reuses funs.TEA.economic_analysis (Mix row = partial grey/ammonia H2 WITH CCS)
and funs_lca.get_WTWa_pyrolysis (WTWa GHG-100, Allocation).

Axes (both minimized):
  MJSP  [$/L SAF]        <- economic_analysis at Scale0100, ccs_portion, ammonia_portion
  GHG   [g CO2e/MJ SAF]  <- WTWa GHG-100, Allocation

Ammonia cracker scale x_a at an x10 plant supplies x_a/10 of the H2 demand, so
ammonia_portion = x_a / 10  (x0 = full grey, x10 = full ammonia).
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
from funs import TEA
from funs_lca import get_WTWa_pyrolysis

# _PLOTTING_STYLE.md (SA_RC lives only in the notebook; inlined here)
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

MAIN_SCALE = 10                 # main SAF unit fixed at knee-point x10
AMM_SCALES = [0, 1, 2.5, 5, 7.5, 10]   # ammonia cracker scale
CCS_RATES = [0.0, 0.25, 0.50, 0.75, 1.00]
CO2_TS = 10.0                   # $/tCO2 T&S basis (current, commit 95db93c)
LCA_METHOD = 'Allocation'       # report primary; GHG-100

# Biomass price-model span at the x10 plant (0.457 MMt/yr SAF), from
# tea_scale_up_price_models.py / tea_biomass_price_only.py: FR-price floor and galik
# supply-curve estimate. Sets the §6 biomass sensitivity range (one-sided up).
BIO_PRICE_FR = 0.04865          # $/lb, FR-price model (base/floor)
BIO_PRICE_HI = 0.05268          # $/lb, galik supply-curve at x10 demand

FS = f'Process_Data\\Pyrolysis_551_Scale{MAIN_SCALE * 10:04d}_Streams.xlsx'
FA = f'Process_Data\\Pyrolysis_551_Scale{MAIN_SCALE * 10:04d}_APEA.xlsm'
FILE_LCA = f'Process_Data\\Pyrolysis_551_LCA_{LCA_METHOD}.xlsx'
FILE_WTWA = 'Process_Data\\WTWa_LCA.xlsx'


def ghg(case: str) -> float:
    return get_WTWa_pyrolysis(case, FILE_LCA, FILE_WTWA)['WTWa']['GHG-100']


def mjsp(tea: TEA, a: float, c: float) -> float:
    """MJSP [$/L] at ammonia_portion a, ccs_portion c. a=0 -> grey Base row."""
    if a == 0:
        _, _, _, _, _, da, _ = tea.economic_analysis(FS, FA, ['Base'], ccs_portion=c)
        return da['cost'][0]['MJSP']
    _, _, _, _, _, da, _ = tea.economic_analysis(FS, FA, ['Base'], ccs_portion=c, ammonia_portion=a)
    return da['cost'][-1]['MJSP']   # 'Mix' row


# Tornado sensitivity conditions (_Tornado_Sensitivity.md §1) reused as the single
# source of truth; adapted here to Mix frontier points (partial grey + partial ammonia).
from tea_tornado import (H2_RANGE, ELEC_F, COPROD_F, CAPEX_PM,
                         CF_HOURS, TS_RANGE, TS_BASE, AMM_FEED_USD_L, AMM_P_BASE,
                         AMM_PRICE, LB2KG, raw_costs, tornado)


def mix_row(tea: TEA, a: float, c: float) -> tuple[float, pd.Series, float]:
    """(MJSP, df_mjsp row, annual SAF) for a Mix point; a=0 -> grey Base row."""
    if a == 0:
        dfm, _, saf, _, _, da, _ = tea.economic_analysis(FS, FA, ['Base'], ccs_portion=c)
        return da['cost'][0]['MJSP'], dfm.iloc[0], saf
    dfm, _, saf, _, _, da, _ = tea.economic_analysis(FS, FA, ['Base'], ccs_portion=c, ammonia_portion=a)
    return da['cost'][-1]['MJSP'], dfm.iloc[-1], saf


def rerun_mix(a: float, c: float, **knobs) -> float:
    """Mix MJSP with scalar knob(s) on a fresh TEA (T&S basis kept at $10/t)."""
    t = TEA()
    t.co2_ts_usd_per_ton = TS_BASE
    for k, v in knobs.items():
        setattr(t, k, v)
    if 'elec_price_usd_per_mmbtu' in knobs:
        t.product_price_work['ELC-'] = t.elec_price_usd_per_mmbtu
    return mix_row(t, a, c)[0]


def mix_bars(tea: TEA, a: float, c: float, h2_cost: float, h2_rate: float,
             bio_cost: float, op: float) -> tuple[float, list[tuple[str, float, float]]]:
    """(base, per-driver tornado bars) for a Mix point. Bars = [(label, MJSP@low, MJSP@high)];
    grey-H2 scales with (1-a), ammonia with a, T&S/electricity/co-product/capacity re-run,
    biomass/CAPEX linear. Single source for both the frontier band and the tornado panels."""
    base, row, saf = mix_row(tea, a, c)
    bars: list[tuple[str, float, float]] = []
    # Biomass price range = supply-curve price-model span at this x10 plant (0.457 MMt/yr
    # SAF): FR-price floor 0.04865 $/lb (base) up to the galik supply-curve 0.05268 $/lb
    # (+8.3%). One-sided (FR is the floor); replaces the generic +-50% swing.
    d_bio = (BIO_PRICE_HI / BIO_PRICE_FR - 1.) * bio_cost * op / saf
    bars.append(('Biomass +8.3%', base, base + d_bio))
    if a < 1:                                                    # gray H2 on the grey share
        p_kg = (h2_cost / h2_rate) / LB2KG
        h2_term = h2_cost * (1 - a) * op / saf
        lo, hi = H2_RANGE
        bars.append(('Gray H₂ 1–4 $/kg', base + (lo / p_kg - 1.) * h2_term, base + (hi / p_kg - 1.) * h2_term))
    if a > 0:                                                    # ammonia price on the ammonia share
        lo, hi = AMM_PRICE
        bars.append(('Ammonia 0.12–0.45 $/lb', base + a * AMM_FEED_USD_L * (lo / AMM_P_BASE - 1.),
                     base + a * AMM_FEED_USD_L * (hi / AMM_P_BASE - 1.)))
    bars.append(('CAPEX ±30%', base - CAPEX_PM * row['capital investment'],   # Mix cap inv, incl CCS
                 base + CAPEX_PM * row['capital investment']))
    if c > 0:                                                    # CO2 T&S 4-45 $/t (CCS only)
        lo, hi = TS_RANGE
        bars.append(('CO₂ T&S 4–45 $/t', rerun_mix(a, c, co2_ts_usd_per_ton=lo), rerun_mix(a, c, co2_ts_usd_per_ton=hi)))
    e_lo, e_hi = ELEC_F                                          # electricity +-30%
    bars.append(('Electricity ±30%', rerun_mix(a, c, elec_price_usd_per_mmbtu=19.05 * e_lo),
                 rerun_mix(a, c, elec_price_usd_per_mmbtu=19.05 * e_hi)))
    c_lo, c_hi = COPROD_F                                        # co-product +-20%
    bars.append(('Co-product ±20%',
                 rerun_mix(a, c, product_price_stream={'316GAS': 0.75757 * c_lo, '326SAF': 0, '336DIES': 0.6 * c_lo}),
                 rerun_mix(a, c, product_price_stream={'316GAS': 0.75757 * c_hi, '326SAF': 0, '336DIES': 0.6 * c_hi})))
    h85, h91 = CF_HOURS                                          # capacity 85% / 91%
    bars.append(('Capacity 85% / 91%', rerun_mix(a, c, operation_hr=h85), rerun_mix(a, c, operation_hr=h91)))
    return base, bars


def mjsp_error(tea: TEA, a: float, c: float, h2_cost: float, h2_rate: float,
               bio_cost: float, op: float) -> tuple[float, float, float]:
    """(base, min, max) MJSP envelope over the tornado drivers of a Mix point."""
    base, bars = mix_bars(tea, a, c, h2_cost, h2_rate, bio_cost, op)
    ends = [base] + [v for _, lo, hi in bars for v in (lo, hi)]
    return base, min(ends), max(ends)


def tornado_compare(tea: TEA, h2_cost: float, h2_rate: float, bio_cost: float, op: float) -> None:
    """Two-panel MJSP tornado: the two ~25%-decarbonization frontier points reviewers weigh
    against each other -- grey-H2 + CCS 25% (a=0, c=0.25) vs Green NH3 25% (a=0.25, c=0)."""
    cases = [(0.0, 0.25, 'Grey H₂ + CCS 25%'), (0.25, 0.0, 'Green NH₃ 25%')]
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharex=True)   # shared x -> spans comparable
    for ax, (a, c, name) in zip(axes, cases):
        base, bars = mix_bars(tea, a, c, h2_cost, h2_rate, bio_cost, op)
        assert base > 0 and bars, name
        tornado(ax, base, bars, f'{name}  (base {base:.2f})')
    from matplotlib.patches import Patch
    fig.legend(handles=[Patch(color='#4575b4', label='low input'),
                        Patch(color='#d73027', label='high input')],
               loc='upper center', ncol=2, framealpha=0.)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(os.path.join('Figure', 'tornado_ccs25_vs_nh325.png'), dpi=150)


def pareto_mask(pts: pd.DataFrame) -> pd.Series:
    """Non-dominated set minimizing both ghg and mjsp (O(n^2), n=30)."""
    dominated = pd.Series(False, index=pts.index)
    for i in pts.index:
        for j in pts.index:
            if (pts.loc[j, 'ghg'] <= pts.loc[i, 'ghg'] and pts.loc[j, 'mjsp'] <= pts.loc[i, 'mjsp']
                    and (pts.loc[j, 'ghg'] < pts.loc[i, 'ghg'] or pts.loc[j, 'mjsp'] < pts.loc[i, 'mjsp'])):
                dominated[i] = True
                break
    return ~dominated


def main() -> None:
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    tea = TEA()
    tea.co2_ts_usd_per_ton = CO2_TS

    # GHG levers: CCS by portion (own sheet), ammonia additive delta from base.
    # assumption: ammonia H2 abatement (upstream grey-H2) is independent of / additive to
    # CCS process-CO2 capture -> GHG(a,c) = ghg_ccs[c] - a*(ghg_base - ghg_ammonia).
    ghg_base = ghg('Base')
    amm_delta = ghg_base - ghg('Ammonia')
    ghg_ccs = {0.0: ghg_base,
               **{c: ghg(f'CCS{int(c * 100):03d}') for c in CCS_RATES if c > 0}}

    rows = []
    for s in AMM_SCALES:
        a = s / MAIN_SCALE
        for c in CCS_RATES:
            rows.append({'amm_scale': s, 'ammonia_portion': a, 'ccs': c,
                         'mjsp': mjsp(tea, a, c),
                         'ghg': ghg_ccs[c] - a * amm_delta})
    df = pd.DataFrame(rows)
    df['pareto'] = pareto_mask(df)

    # CO2 abatement cost vs the compliance floor (converted from the old grey-base reference).
    # A producer is forced only to the cheapest CORSIA-compliant point; abatement = extra $/tCO2 to
    # decarbonize *below* it. Anchor = grey-H2 + CCS25 (no ammonia): the CCS25 GREET sample is the
    # nearest real run to the 0.9x-conventional line (76.0 g/MJ ~ 75.9 threshold; no interpolation,
    # user choice) and is the cheapest compliant point on the front (every NH3-bearing compliant
    # point costs more). Same formula as tea_scale_up_abatement.py: dMJSP / (dGHG * E) * 1e6.
    E_MJ_PER_L = 31.66   # MJ/L SAF (report section 3b)
    anchor = df[(df['amm_scale'] == 0) & (df['ccs'] == 0.25)].iloc[0]
    d_ghg = (anchor['ghg'] - df['ghg']) * E_MJ_PER_L        # g/L avoided vs the floor
    df['abatement'] = (df['mjsp'] - anchor['mjsp']) * 1e6 / d_ghg   # $/tCO2
    df.loc[df['ghg'] > anchor['ghg'], 'abatement'] = float('nan')   # strictly above the floor (dirtier): n/a
    df.loc[anchor.name, 'abatement'] = 0.0                          # the floor itself = 0 $/tCO2 reference (colored on contour)

    # scatter: color by ammonia scale, marker by CCS -----------------------
    plt.rcParams.update(SA_RC)
    import numpy as np
    cmap = plt.get_cmap('RdYlBu')
    amm_colors = {s: cmap(x) for s, x in zip(AMM_SCALES, np.linspace(0.1, 0.9, len(AMM_SCALES)))}
    ccs_markers = dict(zip(CCS_RATES, ['o', 's', '^', 'D', 'P']))

    fig, ax = plt.subplots(figsize=(7, 6))
    for _, r in df.iterrows():
        ax.scatter(r['ghg'], r['mjsp'], s=70, color=amm_colors[r['amm_scale']],
                   marker=ccs_markers[r['ccs']], edgecolor='black', linewidth=0.6, zorder=3)
    front = df[df['pareto']].sort_values('ghg')
    ax.plot(front['ghg'], front['mjsp'], '-', color='#333333', lw=1.2, zorder=2, label='Pareto front')

    # MJSP tornado-driver envelope as a shaded band along the frontier --------
    h2_cost, h2_rate, bio_cost = raw_costs(tea, FA)
    op = tea.operation_hr
    err = [mjsp_error(tea, r['ammonia_portion'], r['ccs'], h2_cost, h2_rate, bio_cost, op)
           for _, r in front.iterrows()]
    lo = [e[1] for e in err]
    hi = [e[2] for e in err]
    # front is sorted by ghg, so fill_between reads left->right along the frontier
    ax.fill_between(front['ghg'], lo, hi, color='#999999', alpha=0.25, lw=0,
                    zorder=1, label='MJSP sensitivity (§4.7)')
    front = front.assign(mjsp_lo=lo, mjsp_hi=hi)

    ax.set_xlabel('WTWa GHG-100 [g CO$_2$e/MJ SAF]')
    ax.set_ylabel('MJSP [$/L SAF]')
    # legend states H2 share from the green-ammonia cracker (= ammonia_portion), not raw scale
    amm_h = [plt.Line2D([], [], marker='o', ls='', color=amm_colors[s], mec='black',
                        label=f'Green NH$_3$ {s / MAIN_SCALE * 100:g}%') for s in AMM_SCALES]
    ccs_h = [plt.Line2D([], [], marker=ccs_markers[c], ls='', color='0.6', mec='black',
                        label=f'CCS {int(c * 100)}%') for c in CCS_RATES]
    front_h = plt.Line2D([], [], color='#333333', lw=1.2, label='Pareto front')
    err_h = plt.matplotlib.patches.Patch(facecolor='#999999', alpha=0.25, edgecolor='none',
                                         label='MJSP sensitivity (§4.7)')
    ax.legend(handles=amm_h + ccs_h + [front_h, err_h], ncol=2, loc='best')
    # GHG basis stated on-plot to remove ambiguity (US grid mix, Allocation)
    ax.text(0.02, 0.02, 'WTWa GHG: Allocation, US grid mix', transform=ax.transAxes,
            ha='left', va='bottom', fontsize=8, color='#555555')
    ax.set_ylim(0, 4)  # fix y-axis top at $4/L SAF

    os.makedirs('Figure', exist_ok=True)
    fig.savefig(os.path.join('Figure', 'pareto_front.png'), dpi=150)
    os.makedirs('Result', exist_ok=True)
    df.round(4).to_excel(os.path.join('Result', 'pareto_front.xlsx'), index=False)

    # abatement-cost contour vs the compliance floor: x = NH3 substitution ratio, y = CCS portion.
    # Cells at/above the floor (GHG >= anchor) are n/a (NaN) -> blank; only the decarbonize-below-
    # compliance region carries a cost. New filename keeps the old grey-base contour + report section 5.
    piv = df.pivot(index='ccs', columns='ammonia_portion', values='abatement')
    X, Y = np.meshgrid(piv.columns.values, piv.index.values)
    fig2, ax2 = plt.subplots(figsize=(7, 6))
    cf = ax2.contourf(X, Y, piv.values, levels=12, cmap='RdYlBu_r')
    cs = ax2.contour(X, Y, piv.values, levels=cf.levels, colors='k', linewidths=0.4)
    ax2.clabel(cs, inline=True, fmt='%.0f', fontsize=7)
    ax2.scatter(X, Y, c='k', s=8, zorder=3)   # the 30 sampled combinations
    fig2.colorbar(cf, ax=ax2, label='CO$_2$ abatement cost [\\$/tCO$_2$]')  # escape $ so mathtext keeps the currency sign
    ax2.set_xlabel('Green NH$_3$ H$_2$ substitution ratio')
    ax2.set_ylabel('CCS portion')
    fig2.savefig(os.path.join('Figure', 'pareto_abatement_contour_compliance.png'), dpi=150)

    pd.set_option('display.width', 200, 'display.max_rows', 40)
    print(df.round(3).to_string(index=False))
    print('\nPareto front with CO2 abatement cost + MJSP sensitivity range (§4.7):')
    print(front[['amm_scale', 'ccs', 'ghg', 'mjsp', 'mjsp_lo', 'mjsp_hi', 'abatement']].round(2).to_string(index=False))
    front.round(4).to_excel(os.path.join('Result', 'pareto_front_sensitivity.xlsx'), index=False)

    tornado_compare(tea, h2_cost, h2_rate, bio_cost, op)   # CCS 25% vs Green NH3 25% panels

    # self-checks: base positive; GHG base matches report ~87.57; more CCS lowers GHG at fixed NH3;
    # more NH3 lowers GHG at fixed CCS; front is non-empty and trades off (ghg up <-> mjsp down).
    assert (df['mjsp'] > 0).all()
    assert abs(ghg_base - 87.57) < 1.0, ghg_base
    g = df.pivot(index='amm_scale', columns='ccs', values='ghg')
    assert (g[1.0] < g[0.0]).all() and (g.loc[10] < g.loc[0]).all()
    assert len(front) >= 2 and front['mjsp'].is_monotonic_decreasing
    print('\nOK: self-checks passed; wrote Figure/pareto_front.png + Result/pareto_front.xlsx')


if __name__ == '__main__':
    main()
