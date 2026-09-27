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

    # CO2 abatement cost vs grey base (x0, CCS0): extra $ per tonne CO2 avoided.
    # abate = dMJSP[$/L] / (dGHG[g/MJ] * E[MJ/L]) * 1e6  (same as tea_scale_up_abatement.py)
    E_MJ_PER_L = 31.66   # MJ/L SAF (report section 3b)
    base = df[(df['amm_scale'] == 0) & (df['ccs'] == 0)].iloc[0]
    d_ghg = (base['ghg'] - df['ghg']) * E_MJ_PER_L        # g/L avoided
    df['abatement'] = (df['mjsp'] - base['mjsp']) * 1e6 / d_ghg   # $/tCO2; base row -> inf/NaN
    df.loc[base.name, 'abatement'] = float('nan')

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

    ax.set_xlabel('WTWa GHG-100 [g CO$_2$e/MJ SAF]')
    ax.set_ylabel('MJSP [$/L SAF]')
    # legend states H2 share from the green-ammonia cracker (= ammonia_portion), not raw scale
    amm_h = [plt.Line2D([], [], marker='o', ls='', color=amm_colors[s], mec='black',
                        label=f'Green NH$_3$ {s / MAIN_SCALE * 100:g}%') for s in AMM_SCALES]
    ccs_h = [plt.Line2D([], [], marker=ccs_markers[c], ls='', color='0.6', mec='black',
                        label=f'CCS {int(c * 100)}%') for c in CCS_RATES]
    ax.legend(handles=amm_h + ccs_h, ncol=2, loc='best')
    ax.set_ylim(0, ax.get_ylim()[1] * 1.2)

    os.makedirs('Figure', exist_ok=True)
    fig.savefig(os.path.join('Figure', 'pareto_front.png'), dpi=150)
    os.makedirs('Result', exist_ok=True)
    df.round(4).to_excel(os.path.join('Result', 'pareto_front.xlsx'), index=False)

    pd.set_option('display.width', 200, 'display.max_rows', 40)
    print(df.round(3).to_string(index=False))
    print('\nPareto front (min MJSP, min GHG) with CO2 abatement cost vs grey base:')
    print(front[['amm_scale', 'ccs', 'ghg', 'mjsp', 'abatement']].round(2).to_string(index=False))

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
