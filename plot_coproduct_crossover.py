"""Variant of plot_ammonia_crossover: co-product price on the x-axis.

Asked for as a "try" alongside the gray-H2 version. CAVEAT baked into the figure:
the §5 OAT co-product span is the SAME for both routes (0.494 $/L — they share the
co-product streams and SAF output), so both lines have the SAME slope in co-product
price. The CCS 60% line and every NH3 line are therefore PARALLEL and never cross;
whether an NH3 line sits below CCS 60% depends only on its ammonia price (the fixed
0.121 $/L base gap -> ammonia < ~258 $/t), not on co-product price. Still linear.

Anchors from _Tornado_Sensitivity.md §5 (base MJSPs + recorded co-product/ammonia
OAT spans); co-product enters as a revenue credit so MJSP falls as its price rises.
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
    'xtick.labelsize': 12, 'xtick.color': 'black', 'ytick.labelsize': 10, 'ytick.color': 'black',
    'font.family': 'sans-serif',
    'font.sans-serif': ['Helvetica Neue LT Pro', 'Helvetica Neue', 'Arial', 'DejaVu Sans'],
    'font.size': 10, 'font.weight': '300', 'text.color': 'black',
    'patch.edgecolor': 'black', 'patch.linewidth': 0.7, 'patch.force_edgecolor': True,
    'legend.fontsize': 8, 'legend.title_fontsize': 9, 'legend.framealpha': 0.0,
    'legend.edgecolor': '#444444', 'lines.linewidth': 0.7, 'lines.markersize': 3,
    'savefig.dpi': 150, 'savefig.bbox': 'tight', 'savefig.facecolor': 'white',
}
plt.rcParams.update(SA_RC)

# Anchors (_Tornado_Sensitivity §5: base MJSPs + recorded OAT spans)
NH3_BASE_MJSP: float = 1.098    # Green NH3 10% + CCS 50% MJSP at base drivers, $/L
CCS_BASE_MJSP: float = 0.977    # CCS 60% (CCS-only) MJSP at base drivers, $/L
COPROD_SPAN: float = 0.494      # §5 co-product OAT span, $/L (same for both routes)
COPROD_F: tuple[float, float] = (0.80, 1.20)   # §4.7 co-product price band (× base)
AMM_P_BASE: float = 0.288       # base ammonia price, $/lb
AMM_RANGE_LBS: tuple[float, float] = (0.1225, 0.4535)  # reviewer §4.5 range, $/lb
AMM_FEED_USD_L: float = 2.038   # full-ammonia MJSP offset per (p/base-1), $/L
SHARE: float = 0.10             # NH3 share of the compliant point (10%)
LB_TO_T: float = 2204.62        # $/lb -> $/t NH3 for readable labels

# co-product is a revenue credit -> MJSP DECREASES as its price rises (negative slope).
# slope = -span / band-width, same for both routes (shared co-product streams).
SLOPE_CP: float = -COPROD_SPAN / (COPROD_F[1] - COPROD_F[0])  # $/L per unit multiplier
AMM_COEFF: float = AMM_FEED_USD_L * SHARE                      # $/L per (p_amm/base - 1)

mjsp_ccs = lambda m: CCS_BASE_MJSP + SLOPE_CP * (m - 1.0)      # m = co-product price × base
mjsp_nh3 = lambda m, pa: (NH3_BASE_MJSP + SLOPE_CP * (m - 1.0)
                          + AMM_COEFF * (pa / AMM_P_BASE - 1.0))

# ammonia prices to draw one NH3 line each; $/lb
AMM_LINES: tuple[float, ...] = (AMM_RANGE_LBS[0], 0.20, AMM_P_BASE, AMM_RANGE_LBS[1])

# sweep a bit beyond the reviewer ±20% band to show the (parallel) trend
m = np.linspace(0.6, 1.4, 200)

fig, ax = plt.subplots(figsize=(7.5, 5))
ax.plot(m, mjsp_ccs(m), color='#ed7d31', lw=1.4, label='CCS 60% (CCS-only)')

greens = plt.cm.Greens(np.linspace(0.45, 0.9, len(AMM_LINES)))
for pa, col in zip(AMM_LINES, greens):
    tag = ' (base)' if abs(pa - AMM_P_BASE) < 1e-9 else ''
    ax.plot(m, mjsp_nh3(m, pa), color=col,
            label=f'NH$_3$ 10% + CCS 50%, {pa * LB_TO_T:.0f} \\$/t{tag}')

# reviewer ±20% band + base marker
ax.axvspan(COPROD_F[0], COPROD_F[1], color='#bbbbbb', alpha=0.12)
ax.axvline(1.0, color='#888888', lw=0.6, ls=':')
ax.annotate('base', (1.0, ax.get_ylim()[0]),
            textcoords='offset points', xytext=(3, 6), fontsize=8, color='#888888')

ax.set_xlabel('Co-product price [× base]')
ax.set_ylabel('MJSP [\\$/L SAF]')
ax.set_xlim(m[0], m[-1])
ax.legend(loc='upper right')

out = os.path.join('Figure', 'coproduct_crossover_mjsp.png')
fig.savefig(out, dpi=150)
print(f'saved {out}  |  co-product slope = {SLOPE_CP:.3f} $/L per × (same both routes)')

# check: both routes share one slope -> lines are parallel -> the NH3-vs-CCS ordering
# for each ammonia price is the same at both ends of the sweep (no crossover in co-product).
for pa in AMM_LINES:
    lo = mjsp_nh3(m[0], pa) - mjsp_ccs(m[0])
    hi = mjsp_nh3(m[-1], pa) - mjsp_ccs(m[-1])
    assert np.sign(lo) == np.sign(hi), pa
    print(f'  ammonia {pa * LB_TO_T:5.0f} $/t -> NH3 {"below" if lo < 0 else "above"} CCS 60% everywhere')
