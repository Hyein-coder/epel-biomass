"""Variant of plot_ammonia_crossover: one panel per CO2 T&S price (4 / 10 / 45 $/tCO2).

Base anchors (_Tornado_Sensitivity §5) sit at the $10/tCO2 T&S basis. T&S enters MJSP
linearly (funs.py: co2_seq * co2_ts_usd_per_ton), so each route shifts by its recorded
§5 CO2 T&S OAT span / the 4-45 $/t width. CCS 60% stores more CO2 -> larger shift than
NH3 10% + CCS 50%, so dearer T&S pulls every crossover to a lower H2 price.
"""
import os
import numpy as np
import matplotlib.pyplot as plt
from plot_ammonia_crossover import (h, H2_RANGE, H2_BASE, AMM_LINES, LB_TO_T,
                                    SLOPE_CCS, SLOPE_NH3, mjsp_ccs, mjsp_nh3)

TS_BASE: float = 10.0                      # T&S basis behind the §5 anchors, $/tCO2
TS_RANGE: tuple[float, float] = (4.0, 45.0)
TS_CASES: tuple[float, ...] = (TS_RANGE[0], TS_BASE, TS_RANGE[1])
# $/L per $/tCO2 = §5 CO2 T&S span / range width
TS_SLOPE_CCS: float = 0.187 / (TS_RANGE[1] - TS_RANGE[0])
TS_SLOPE_NH3: float = 0.165 / (TS_RANGE[1] - TS_RANGE[0])

ccs_ts = lambda hh, ts: mjsp_ccs(hh) + TS_SLOPE_CCS * (ts - TS_BASE)
nh3_ts = lambda hh, pa, ts: mjsp_nh3(hh, pa) + TS_SLOPE_NH3 * (ts - TS_BASE)
h_cross_ts = lambda pa, ts: H2_BASE + (nh3_ts(H2_BASE, pa, ts) - ccs_ts(H2_BASE, ts)) / (SLOPE_CCS - SLOPE_NH3)


def draw(ax: plt.Axes, ts: float, legend: bool) -> None:
    """Same marks as plot_ammonia_crossover.draw, both routes shifted to T&S = ts."""
    ax.plot(h, ccs_ts(h, ts), color='#ed7d31', lw=2.2, marker='s', ms=6, markevery=25,
            label='CCS-only')
    blues = plt.cm.Blues(np.linspace(0.45, 0.9, len(AMM_LINES)))
    for pa, col, mk in zip(AMM_LINES, blues, ('o', '^', 'D', 'v')):
        ax.plot(h, nh3_ts(h, pa, ts), color=col, lw=1.6, marker=mk, ms=6, markevery=25,
                label=f'Green NH$_3$ \\${pa * LB_TO_T:,.0f}/t')
        hc = h_cross_ts(pa, ts)
        if H2_RANGE[0] <= hc <= H2_RANGE[1]:
            ax.plot(hc, ccs_ts(hc, ts), 'o', color='#444444', markersize=4)
    ax.axvline(H2_BASE, color='#333333', lw=1.0, ls='--', label='Base gray H$_2$ price')
    # panel tag in place of a title (style: no titles)
    ax.text(0.03, 0.97, f'CO$_2$ T&S \\${ts:.0f}/tCO$_2$', transform=ax.transAxes,
            va='top', fontsize=10)
    ax.set_xlabel('Gray hydrogen price [\\$/kg H$_2$]')
    ax.set_xlim(h[0], h[-1])
    if legend:
        ax.legend(loc='lower right')


def main() -> None:
    fig, axes = plt.subplots(1, len(TS_CASES), figsize=(15, 5), sharey=True)
    for i, (ax, ts) in enumerate(zip(axes, TS_CASES)):
        draw(ax, ts, legend=(i == len(TS_CASES) - 1))
    axes[0].set_ylabel('MJSP [\\$/L SAF]')
    out = os.path.join('Figure', 'ammonia_crossover_ts_mjsp.png')
    fig.savefig(out, dpi=150)
    print(f'saved {out}')
    for ts in TS_CASES:
        print(f'  T&S {ts:4.0f} $/t: ' + ', '.join(
            f'{pa * LB_TO_T:.0f}->{h_cross_ts(pa, ts):.2f}' for pa in AMM_LINES) + ' $/kg')

    # check: base panel reproduces the original figure; dearer T&S lowers every crossover
    assert np.allclose(ccs_ts(h, TS_BASE), mjsp_ccs(h))
    assert all(h_cross_ts(pa, TS_RANGE[1]) < h_cross_ts(pa, TS_RANGE[0]) for pa in AMM_LINES)


if __name__ == '__main__':
    main()
