"""Crossover plot: gray-H2 price vs MJSP for the two CORSIA-compliant routes.

x = gray-H2 price (1-4 $/kg, the dominant driver); y = MJSP. CCS 60% (CCS-only,
100% grey H2) is one steeper reference line; the Green NH3 10% + CCS 50% route
(90% grey H2) is drawn as one line per green-ammonia price. Where an NH3 line
dips below CCS 60% the ammonia route wins -> shows that as ammonia price falls
its crossover moves into the plotted H2 range. All MJSP terms are linear in
their driver, so anchors come straight from _Tornado_Sensitivity.md §5 (no re-run):
base MJSPs + the recorded Gray-H2 / Ammonia OAT spans give the slopes.
"""
import os
import numpy as np
import matplotlib.pyplot as plt

# _PLOTTING_STYLE.md (SA_RC lives only in the notebook; inlined here)
SA_RC = {
    'figure.dpi': 150, 'figure.facecolor': 'white', 'figure.autolayout': True,
    'axes.facecolor': 'white', 'axes.edgecolor': '#444444', 'axes.linewidth': 0.8,
    'axes.spines.top': True, 'axes.spines.right': True, 'axes.labelsize': 12,
    'axes.labelcolor': 'black', 'axes.labelweight': '500', 'axes.grid': False,
    'xtick.labelsize': 12, 'xtick.color': 'black', 'ytick.labelsize': 12, 'ytick.color': 'black',
    'font.family': 'sans-serif',
    'font.sans-serif': ['Helvetica Neue LT Pro', 'Helvetica Neue', 'Arial', 'DejaVu Sans'],
    'font.size': 10, 'font.weight': '300', 'text.color': 'black',
    'patch.edgecolor': 'black', 'patch.linewidth': 0.7, 'patch.force_edgecolor': True,
    'legend.fontsize': 8, 'legend.title_fontsize': 9, 'legend.framealpha': 0.0,
    'legend.edgecolor': '#444444', 'lines.linewidth': 0.7, 'lines.markersize': 3,
    'savefig.dpi': 150, 'savefig.bbox': 'tight', 'savefig.facecolor': 'white',
}
plt.rcParams.update(SA_RC)

# Anchors (_Tornado_Sensitivity §5: base MJSPs + recorded OAT spans over the §1 ranges)
NH3_BASE_MJSP: float = 1.098    # Green NH3 10% + CCS 50% MJSP at base drivers, $/L
CCS_BASE_MJSP: float = 0.977    # CCS 60% (CCS-only) MJSP at base drivers, $/L
H2_BASE: float = 1.4997         # base gray-H2 price (APEA raw-material cost), $/kg
H2_RANGE: tuple[float, float] = (1.0, 4.0)   # §1 gray-H2 range, $/kg
AMM_P_BASE: float = 0.288       # base ammonia price, $/lb
AMM_RANGE_LBS: tuple[float, float] = (0.1225, 0.4535)  # reviewer §4.5 range, $/lb
AMM_FEED_USD_L: float = 2.038   # full-ammonia MJSP offset per (p/base-1), $/L
SHARE: float = 0.10             # NH3 share of the compliant point (10%)
LB_TO_T: float = 2204.62        # $/lb -> $/t NH3 for readable labels

# slope of each route's MJSP in gray-H2 price: recorded OAT span / the 1-4 $/kg width.
# CCS 60% is steeper (100% grey) than the NH3 route (90% grey).
SLOPE_CCS: float = 1.258 / (H2_RANGE[1] - H2_RANGE[0])  # $/L per $/kg
SLOPE_NH3: float = 1.133 / (H2_RANGE[1] - H2_RANGE[0])  # $/L per $/kg
AMM_COEFF: float = AMM_FEED_USD_L * SHARE               # $/L per (p_amm/base - 1)

mjsp_ccs = lambda h: CCS_BASE_MJSP + SLOPE_CCS * (h - H2_BASE)  # h in $/kg
# NH3 route MJSP: grey-H2 term + ammonia-price offset (both linear, superposed)
mjsp_nh3 = lambda h, pa: (NH3_BASE_MJSP + SLOPE_NH3 * (h - H2_BASE)
                          + AMM_COEFF * (pa / AMM_P_BASE - 1.0))
# H2 price where an NH3 line (ammonia pa) meets the CCS-only line
h_cross = lambda pa: H2_BASE + (mjsp_nh3(H2_BASE, pa) - CCS_BASE_MJSP) / (SLOPE_CCS - SLOPE_NH3)

# ammonia prices to draw one NH3 line each: range ends, base, and a cheap mid; $/lb
AMM_LINES: tuple[float, ...] = (AMM_RANGE_LBS[0], 0.20, AMM_P_BASE, AMM_RANGE_LBS[1])

h = np.linspace(H2_RANGE[0], H2_RANGE[1], 200)


def draw(ax: plt.Axes) -> None:
    """Draw the crossover panel on ax (shared by this script and plot_composite.py)."""
    # CCS-only reference line (no ammonia; steeper in grey H2)
    ax.plot(h, mjsp_ccs(h), color='#ed7d31', lw=2.2, marker='s', ms=6, markevery=25,
            label='CCS 60% (CCS-only)')

    # one NH3 line per ammonia price; green shades go light (cheap) -> dark (dear),
    # a distinct marker shape per line so series read apart from colour alone
    greens = plt.cm.Greens(np.linspace(0.45, 0.9, len(AMM_LINES)))
    nh3_markers = ('o', '^', 'D', 'v')   # one per AMM_LINES entry
    for pa, col, mk in zip(AMM_LINES, greens, nh3_markers):
        tag = ' (base)' if abs(pa - AMM_P_BASE) < 1e-9 else ''
        ax.plot(h, mjsp_nh3(h, pa), color=col, lw=1.6, marker=mk, ms=6, markevery=25,
                label=f'NH$_3$ 10% + CCS 50%, {pa * LB_TO_T:.0f} \\$/t{tag}')
        # mark the crossover with CCS 60% when it falls inside the plotted H2 range
        hc = h_cross(pa)
        if H2_RANGE[0] <= hc <= H2_RANGE[1]:
            ax.plot(hc, mjsp_ccs(hc), 'o', color='#444444', markersize=7)

    ax.axvline(H2_BASE, color='#888888', lw=1.2, ls=':',
               label=f'Base gray H$_2$ price ({H2_BASE:.2f} \\$/kg)')

    ax.set_xlabel('Gray hydrogen price [\\$/kg H$_2$]')
    ax.set_ylabel('MJSP [\\$/L SAF]')
    ax.set_xlim(h[0], h[-1])
    ax.legend(loc='upper left')


def main() -> None:
    fig, ax = plt.subplots(figsize=(7.5, 5))
    draw(ax)
    out = os.path.join('Figure', 'ammonia_crossover_mjsp.png')
    fig.savefig(out, dpi=150)
    print(f'saved {out}  |  slopes: CCS {SLOPE_CCS:.3f}, NH3 {SLOPE_NH3:.3f} $/L per $/kg')
    for pa in AMM_LINES:
        print(f'  ammonia {pa * LB_TO_T:5.0f} $/t -> crossover H2 = {h_cross(pa):.3f} $/kg')

    # check: CCS steeper than NH3 route, and cheaper ammonia pulls the crossover to lower H2 price
    assert SLOPE_CCS > SLOPE_NH3
    assert h_cross(AMM_RANGE_LBS[0]) < h_cross(AMM_P_BASE)


if __name__ == '__main__':
    main()
