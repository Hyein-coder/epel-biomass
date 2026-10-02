"""Redraw Figure/pareto_front.png from the already-recorded Result/pareto_front.xlsx
(no TEA re-run). Same scatter/legend as tea_pareto_front.main; shade band dropped,
smaller canvas. Use after the grid is computed once; edit here for figure-only tweaks."""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from funs_lca import get_WTWa_conventional
from tea_pareto_front import SA_RC, AMM_SCALES, CCS_RATES, MAIN_SCALE, FILE_WTWA


def draw(ax: plt.Axes) -> pd.DataFrame:
    """Draw the GHG-MJSP mesh panel on ax (shared with plot_composite.py); returns the grid."""
    df = pd.read_excel(os.path.join('Result', 'pareto_front.xlsx'))
    cmap = plt.get_cmap('RdYlBu')
    amm_colors = {s: cmap(x) for s, x in zip(AMM_SCALES, np.linspace(0.1, 0.9, len(AMM_SCALES)))}
    ccs_markers = dict(zip(CCS_RATES, ['o', 's', '^', 'D', 'P']))

    # mesh: connect the 6x5 (NH3 x CCS) sampling into iso-NH3 and iso-CCS lines so the
    # deformed grid is visible in the (GHG, MJSP) plane. Under the markers (zorder 0).
    gp = df.pivot(index='amm_scale', columns='ccs', values='ghg')
    mp = df.pivot(index='amm_scale', columns='ccs', values='mjsp')
    for a in gp.index:                          # iso-NH3 (walk CCS)
        ax.plot(gp.loc[a], mp.loc[a], '-', color='#bbbbbb', lw=0.6, zorder=0)
    for c in gp.columns:                        # iso-CCS (walk NH3)
        ax.plot(gp[c], mp[c], '-', color='#bbbbbb', lw=0.6, zorder=0)
    for _, r in df.iterrows():
        ax.scatter(r['ghg'], r['mjsp'], s=70, color=amm_colors[r['amm_scale']],
                   marker=ccs_markers[r['ccs']], edgecolor='black', linewidth=0.6, zorder=3)

    # SAF regulation standard: CORSIA -10% line (0.9x conventional jet WTWa GHG-100).
    corsia = 0.9 * get_WTWa_conventional(FILE_WTWA)['WTWa']['GHG-100']
    ax.axvline(corsia, color='#333333', ls='--', lw=1.0, zorder=1, label='CORSIA Standard')

    ax.set_xlabel('WTWa GHG-100 [g CO$_2$e/MJ SAF]')
    ax.set_ylabel('MJSP [$/L SAF]')
    amm_h = [plt.Line2D([], [], marker='o', ls='', color=amm_colors[s], mec='black',
                        label=f'Green NH$_3$ {s / MAIN_SCALE * 100:g}%') for s in AMM_SCALES]
    ccs_h = [plt.Line2D([], [], marker=ccs_markers[c], ls='', color='0.6', mec='black',
                        label=f'CCS {int(c * 100)}%') for c in CCS_RATES]
    corsia_h = plt.Line2D([], [], color='#333333', ls='--', lw=1.0, label='CORSIA Standard')
    ax.legend(handles=amm_h + ccs_h + [corsia_h], ncol=1, loc='best', markerscale=1.8)
    ax.set_ylim(0, 4)
    # SA_RC sets ytick 10 vs xtick 12; both axes are numeric here, so match y to x
    ax.tick_params(axis='y', labelsize=plt.rcParams['xtick.labelsize'])
    return df


def main() -> None:
    plt.rcParams.update(SA_RC)
    fig, ax = plt.subplots(figsize=(5.5, 5))   # smaller canvas -> legend reads larger relative to axes
    df = draw(ax)
    front = df[df['pareto']]
    os.makedirs('Figure', exist_ok=True)
    fig.savefig(os.path.join('Figure', 'pareto_front.png'), dpi=150)
    print('wrote Figure/pareto_front.png from Result/pareto_front.xlsx (%d points, %d on front)'
          % (len(df), len(front)))


if __name__ == '__main__':
    main()
