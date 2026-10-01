"""OAT MJSP tornado over the SHAP-range column (report §1) for the two SHAP-analysis
points — CCS 60% and Green NH3 10% + CCS 50% — side by side. Option A: the biomass bar
uses the SHAP supply-curve band (RANGES['Biomass']), not the tornado's ±50% stress.

Reuses the SHAP model verbatim: mjsp_point / RANGES / POINTS from tea_pareto_shap, so
each bar is the one-at-a-time slice of the same inputs the beeswarm samples jointly.
Plot via tea_tornado.tornado. Base = every driver at its nominal (each nominal makes its
mjsp_point term zero, or is the engine default)."""
import os
import sys

import pandas as pd
import matplotlib.pyplot as plt
from funs import TEA
from tea_pareto_front import SA_RC, BIO_PRICE_FR
from tea_pareto_shap import mjsp_point, RANGES, POINTS, mlabel, _H2_COST, _H2_RATE
from tea_tornado import LB2KG, TS_BASE, AMM_P_BASE, tornado

# nominal (unperturbed) driver values. Biomass/Capacity nominals sit at their SHAP-band low
# end (FR floor / 8000 h base above both CF endpoints), so those two bars are one-sided.
NOMINAL = {
    'Biomass':     BIO_PRICE_FR,
    'Gray H₂':    (_H2_COST / _H2_RATE) / LB2KG,   # APEA gray-H2 price, $/kg
    'Ammonia':     AMM_P_BASE,
    'CAPEX':       1.0,
    'CO₂ T&S':    TS_BASE,
    'Electricity': 19.05,
    'Co-product':  1.0,
    'Capacity':    TEA().operation_hr,             # 8000 h base
}


def cell_bars(a: float, c: float, order: list[str]) -> tuple[float, list[tuple[str, float, float]]]:
    """Base MJSP and (label, MJSP@low-input, MJSP@high-input) per driver for one point."""
    base = mjsp_point(a, c, NOMINAL)
    bars = []
    for k in order:
        lo, hi = RANGES[k]
        bars.append((mlabel(k),
                     mjsp_point(a, c, {**NOMINAL, k: lo}),
                     mjsp_point(a, c, {**NOMINAL, k: hi})))
    return base, bars


def main() -> None:
    sys.stdout.reconfigure(encoding='utf-8')
    plt.rcParams.update(SA_RC)   # _PLOTTING_STYLE: no grid, no title, transparent legend, .png
    fig, axes = plt.subplots(1, len(POINTS), figsize=(13, 5.5), sharex=True, squeeze=False)
    axes = axes.ravel()

    records = []
    for ax, (name, (a, c, order)) in zip(axes, POINTS.items()):
        base, bars = cell_bars(a, c, order)
        tornado(ax, base, bars, f'{mlabel(name)}  (base {base:.2f})')
        print(f'\n{name}  base MJSP = {base:.3f} $/L')
        for lab, lo, hi in sorted(bars, key=lambda b: -abs(b[2] - b[1])):
            print(f'   {lab:<24} {min(lo, hi):.3f} … {max(lo, hi):.3f}   (span {abs(hi - lo):.3f})')
            records.append({'point': name, 'variable': lab, 'base': base,
                            'mjsp_low_input': lo, 'mjsp_high_input': hi, 'span': abs(hi - lo)})

    from matplotlib.patches import Patch
    fig.legend(handles=[Patch(color='#4575b4', label='low input'),
                        Patch(color='#d73027', label='high input')],
               loc='upper center', ncol=2, framealpha=0.)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    os.makedirs('Figure', exist_ok=True)
    fig.savefig(os.path.join('Figure', 'tornado_shap_ccs60_vs_nh10ccs50.png'), dpi=150)
    os.makedirs('Result', exist_ok=True)
    pd.DataFrame(records).to_excel(os.path.join('Result', 'tornado_shap_ccs60_vs_nh10ccs50.xlsx'), index=False)

    # self-check: base positive; CAPEX (monotone) must widen MJSP both sides on every point
    df = pd.DataFrame(records)
    assert (df['base'] > 0).all()
    cap = df[df['variable'] == 'CAPEX']
    assert (cap['mjsp_high_input'] > cap['base']).all() and (cap['mjsp_low_input'] < cap['base']).all()
    print('\nOK: self-checks passed; wrote Figure/tornado_shap_ccs60_vs_nh10ccs50.png + Result xlsx')


if __name__ == '__main__':
    main()
