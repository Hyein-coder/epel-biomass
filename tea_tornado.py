"""Reviewer §4.7 tornado sensitivity: MJSP driver ranges for Base / Full-Ammonia
/ Full-CCS at scale x1 and x30, on the 551 basis. Reuses funs.TEA (no engine
change); mirrors the call pattern and ammonia constants of tea_scale_up_abatement.py.

Two mechanisms per bar (see _Tornado_Sensitivity.md §1):
  linear = input enters OPEX/CAPEX linearly -> exact post-scale of the base run.
  re-run = set the scalar knob on a fresh TEA(), recompute (net or non-linear).
"""
import os
import sys

import pandas as pd
import matplotlib.pyplot as plt
from funs import TEA

LB2KG = 0.453592
SCALES = [1, 30]

# Reviewer §4.7 ranges
BIOMASS_PM = 0.50          # biomass price +-50%
H2_RANGE = (1.0, 4.0)      # gray H2 price, $/kg
ELEC_F = (0.70, 1.30)      # electricity price +-30%
COPROD_F = (0.80, 1.20)    # co-product price +-20%
CAPEX_PM = 0.30            # CAPEX +-30%
CF_HOURS = (0.85 * 8760, 0.91 * 8760)   # capacity factor 85% / 91% (base 8000 h = 91.3%)
TS_RANGE = (4, 45)         # CO2 transport & storage sweep, $/tCO2 (Full-CCS only)
TS_BASE = 10               # CO2 T&S basis baked into the CCS unit, $/tCO2
# Ammonia price: same source of truth as tea_scale_up_abatement.py:20-23
AMM_FEED_USD_L, AMM_P_BASE = 2.038, 0.288
AMM_PRICE = (0.1225, 0.4535)   # $/lb, low (projected) / high (current)

# config -> (h2 source list, ccs_portion, row index into df_mjsp / data_all, has gray-H2, has ammonia)
SPEC = {
    'Base':         dict(names=['Base'],           ccs=0.0, idx=0, h2=True,  amm=False),
    'Full-Ammonia': dict(names=['Base', 'Ammonia'], ccs=0.0, idx=1, h2=False, amm=True),
    'Full-CCS':     dict(names=['Base'],           ccs=1.0, idx=0, h2=True,  amm=False),
}


def run_mjsp(tea: TEA, fs: str, fa: str, cfg: str) -> tuple[float, pd.Series, float]:
    """One economic_analysis call for a config; return (MJSP, df_mjsp row, annual SAF)."""
    s = SPEC[cfg]
    df_mjsp, _, saf, _, _, da, _ = tea.economic_analysis(fs, fa, s['names'], ccs_portion=s['ccs'])
    return da['cost'][s['idx']]['MJSP'], df_mjsp.iloc[s['idx']], saf


def raw_costs(tea: TEA, fa: str) -> tuple[float, float, float]:
    """Base hourly costs read straight from the APEA: (H2 $/hr, H2 lb/hr, biomass $/hr)."""
    df = pd.read_excel(fa, sheet_name='RawMaterial Summary', header=2).dropna(how='all')
    df['Description'] = df['Description'].astype(str)
    h2 = df[df['Description'].isin(tea.hydrogen_feed_stream)]
    bio = tea.get_biomass_info(fa)
    return h2['Cost per Hour'].sum(), h2['Rate per Hour'].sum(), bio['Cost [$/hr]']


def rerun_knob(fs: str, fa: str, cfg: str, **knobs) -> float:
    """MJSP with scalar knob(s) overridden on a fresh TEA (used for the non-linear bars)."""
    t = TEA()
    if SPEC[cfg]['ccs']:
        t.co2_ts_usd_per_ton = TS_BASE          # $10/t basis; an explicit knob below overrides it
    for k, v in knobs.items():
        setattr(t, k, v)
    # electricity sales reference is a copied float at __init__ -> keep it in sync
    if 'elec_price_usd_per_mmbtu' in knobs:
        t.product_price_work['ELC-'] = t.elec_price_usd_per_mmbtu
    return run_mjsp(t, fs, fa, cfg)[0]


def cell_bars(fs: str, fa: str, cfg: str) -> tuple[float, list[tuple[str, float, float]]]:
    """Base MJSP and the list of (label, MJSP@low-input, MJSP@high-input) bars for one cell."""
    s = SPEC[cfg]
    tea = TEA()
    if s['ccs']:
        tea.co2_ts_usd_per_ton = TS_BASE          # $10/t CO2 T&S baked into the CCS base
    base, row, saf = run_mjsp(tea, fs, fa, cfg)
    h2_cost, h2_rate, bio_cost = raw_costs(tea, fa)
    op = tea.operation_hr

    bars: list[tuple[str, float, float]] = []

    # linear bars ----------------------------------------------------------
    d_bio = BIOMASS_PM * bio_cost * op / saf
    bars.append(('Biomass ±50%', base - d_bio, base + d_bio))

    if s['h2']:
        p_kg = (h2_cost / h2_rate) / LB2KG            # base gray-H2 price, $/kg
        h2_term = h2_cost * op / saf                  # full-cost $/L; scales with price ratio
        lo, hi = H2_RANGE
        bars.append(('Gray H₂ 1–4 $/kg',
                     base + (lo / p_kg - 1.) * h2_term,
                     base + (hi / p_kg - 1.) * h2_term))

    if s['amm']:
        lo, hi = AMM_PRICE
        bars.append(('Ammonia 0.12–0.45 $/lb',
                     base + AMM_FEED_USD_L * (lo / AMM_P_BASE - 1.),
                     base + AMM_FEED_USD_L * (hi / AMM_P_BASE - 1.)))

    cap_inv = row['capital investment']               # $/L, config-specific (incl. CCS for Full-CCS)
    bars.append(('CAPEX ±30%', base - CAPEX_PM * cap_inv, base + CAPEX_PM * cap_inv))

    if s['ccs']:
        # CO2 T&S sweep around the $10/t basis; engine applies it on sequestered CO2 (calc_cost_CCS).
        lo, hi = TS_RANGE
        bars.append(('CO₂ T&S 4–45 $/t',
                     rerun_knob(fs, fa, cfg, co2_ts_usd_per_ton=lo),
                     rerun_knob(fs, fa, cfg, co2_ts_usd_per_ton=hi)))

    # re-run bars ----------------------------------------------------------
    e_lo, e_hi = ELEC_F
    bars.append(('Electricity ±30%',
                 rerun_knob(fs, fa, cfg, elec_price_usd_per_mmbtu=19.05 * e_lo),
                 rerun_knob(fs, fa, cfg, elec_price_usd_per_mmbtu=19.05 * e_hi)))

    c_lo, c_hi = COPROD_F
    bars.append(('Co-product ±20%',
                 rerun_knob(fs, fa, cfg, product_price_stream={'316GAS': 0.75757 * c_lo, '326SAF': 0, '336DIES': 0.6 * c_lo}),
                 rerun_knob(fs, fa, cfg, product_price_stream={'316GAS': 0.75757 * c_hi, '326SAF': 0, '336DIES': 0.6 * c_hi})))

    h85, h91 = CF_HOURS
    bars.append(('Capacity 85% / 91%',
                 rerun_knob(fs, fa, cfg, operation_hr=h85),
                 rerun_knob(fs, fa, cfg, operation_hr=h91)))

    return base, bars


def tornado(ax, base: float, bars: list[tuple[str, float, float]], title: str) -> None:
    """One tornado subplot: bars sorted by span, each drawn from base to both input ends."""
    bars = sorted(bars, key=lambda b: abs(b[2] - b[1]))   # ascending -> largest on top
    y = range(len(bars))
    c_lo, c_hi = '#4575b4', '#d73027'                     # RdYlBu ends: low / high input
    for i, (_, v_lo, v_hi) in enumerate(bars):
        # draw the longer arm first so the shorter is not hidden when both fall one side
        for v, c in sorted([(v_lo, c_lo), (v_hi, c_hi)], key=lambda t: -abs(t[0] - base)):
            ax.barh(i, v - base, left=base, color=c, edgecolor='white')
    ax.axvline(base, color='k', lw=1)
    ax.set_yticks(list(y))
    ax.set_yticklabels([b[0] for b in bars])
    ax.set_xlabel('MJSP [$/L SAF]')
    ax.text(0.98, 0.04, title, transform=ax.transAxes, ha='right', va='bottom', fontsize='large')


def main() -> None:
    sys.stdout.reconfigure(encoding='utf-8')   # console prints contain –, …, ₂
    params = {'legend.fontsize': 'large', 'axes.labelsize': 'x-large',
              'xtick.labelsize': 'large', 'ytick.labelsize': 'large'}
    plt.rcParams.update(params)   # _PLOTTING_STYLE: no grid, no title, transparent legend, .png only

    # shared x-axis across all panels so spans are directly comparable
    fig, axes = plt.subplots(len(SPEC), len(SCALES), figsize=(15, 12), sharex=True)
    records = []
    for r, cfg in enumerate(SPEC):
        for c, n in enumerate(SCALES):
            fs = f'Process_Data\\Pyrolysis_551_Scale{int(n * 10):04d}_Streams.xlsx'
            fa = f'Process_Data\\Pyrolysis_551_Scale{int(n * 10):04d}_APEA.xlsm'
            base, bars = cell_bars(fs, fa, cfg)
            tornado(axes[r][c], base, bars, f'{cfg}  ×{n}  (base {base:.2f})')
            print(f'\n{cfg} ×{n}  base MJSP = {base:.3f} $/L')
            for lab, lo, hi in sorted(bars, key=lambda b: -abs(b[2] - b[1])):
                print(f'   {lab:<22} {min(lo, hi):.3f} … {max(lo, hi):.3f}   (span {abs(hi - lo):.3f})')
                records.append({'scale': n, 'config': cfg, 'variable': lab, 'base': base,
                                'mjsp_low_input': lo, 'mjsp_high_input': hi, 'span': abs(hi - lo)})

    from matplotlib.patches import Patch
    fig.legend(handles=[Patch(color='#4575b4', label='low input'),
                        Patch(color='#d73027', label='high input')],
               loc='upper center', ncol=2, framealpha=0.)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    os.makedirs('Figure', exist_ok=True)
    fig.savefig(os.path.join('Figure', 'tornado.png'), dpi=150)

    pd.DataFrame(records).to_excel(os.path.join('Figure', 'tornado_sensitivity.xlsx'), index=False)

    # self-check: cost inputs must widen MJSP, base positive, re-run bars must actually move
    df = pd.DataFrame(records)
    assert (df['base'] > 0).all()
    for v in ('Biomass ±50%', 'CAPEX ±30%'):
        sub = df[df['variable'] == v]
        assert (sub['mjsp_high_input'] > sub['base']).all() and (sub['mjsp_low_input'] < sub['base']).all(), v
    assert (df[df['variable'] == 'Capacity 85% / 91%']['span'] > 0).all()
    print('\nOK: self-checks passed; wrote Figure/tornado.png + tornado_sensitivity.xlsx')


if __name__ == '__main__':
    main()
