"""Graphical-abstract strip: Fig 2b (scale-up price models), Fig 3a (GHG-MJSP mesh), Fig 3b
(abatement-cost field) stacked top-to-bottom as square panels, axis labels only (no tick numbers).
Reads Result/scale_up_price_model_mjsp.xlsx and Result/pareto_front.xlsx; no TEA re-run."""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from scipy.interpolate import RegularGridInterpolator
from funs_lca import CORSIA_THRESHOLD
from tea_pareto_front import SA_RC

LINE = {'Base': ('#E5534B', '-', 'Base (gray H$_2$)'),     # colors as in plot_scale_up_from_xlsx
        'Ammonia': ('#F2B701', '--', 'Green NH$_3$'),
        'CCS': ('#3FA34D', ':', 'CCS')}
BAR_GRAYS = ['#d9d9d9', '#a6a6a6', '#707070']   # FR / FR-Log Linear / Fixed Elasticity
E_MJ_PER_L = 31.66   # MJ/L SAF, same as tea_pareto_front abatement


def no_numbers(*axes: plt.Axes) -> None:
    for a in axes:
        a.set_xticks([]); a.set_yticks([])


def draw_scale(ax: plt.Axes) -> None:
    """Fig 2b: biomass-price bars (3 price models) + MJSP mean line / model-range band."""
    sheets = pd.read_excel(os.path.join('Result', 'scale_up_price_model_mjsp.xlsx'),
                           sheet_name=None, index_col=0)
    price = sheets.pop('biomass price').drop(columns='saf production [MMt/yr]')
    x = np.arange(len(price))
    w = 0.26
    for i, (col, c) in enumerate(zip(price.columns, BAR_GRAYS)):
        ax.bar(x + (i - 1) * w, price[col], w, color=c, edgecolor='white', linewidth=0.4,
               label=col.replace(' Linear', '').replace('Elasticity', 'Elast.'))
    ax.set_ylim(0, price.values.max() * 1.05)
    ax.set_xlim(-0.6, len(x) - 0.4)

    ax2 = ax.twinx()
    ax2.spines['right'].set_visible(True)
    for name, df in sheets.items():
        key = name.removeprefix('MJSP ')
        col, ls, lab = LINE[key]
        df = df.drop(columns='saf production [MMt/yr]')
        ax2.fill_between(x, df.min(axis=1), df.max(axis=1), color=col, alpha=0.25, lw=0)
        ax2.plot(x, df.mean(axis=1), color=col, ls=ls, lw=2.2, label=lab)
        if key == 'Base':
            i_min = int(df.mean(axis=1).values.argmin())
            y_min = df.mean(axis=1).iloc[i_min]
            ax2.plot(x[i_min], y_min, 'o', ms=8, mfc='white', mec=col, mew=1.8, zorder=5)
            ax2.annotate('min', (x[i_min], y_min), xytext=(0, -14), textcoords='offset points',
                         ha='center', va='top', fontweight=plt.rcParams['axes.labelweight'],
                         bbox=dict(fc='white', ec='none', pad=1))
    hi = ax2.get_ylim()[1] * 1.25   # headroom for legend
    ax2.set_ylim(-0.25 * hi, hi)   # lift lines above the floor-price bars (no numbers shown)
    ax2.spines['top'].set_visible(False)
    ax2.set_ylabel('MJSP (lines)')
    ax.set_ylabel('Biomass price (bars)')
    ax.set_xlabel('SAF production')
    ax.text(0.04, 0.72, 'economies of scale', transform=ax.transAxes, style='italic')
    ax.text(0.97, 0.72, r'feedstock cost $\uparrow$', transform=ax.transAxes, style='italic', ha='right')
    h1, l1 = ax2.get_legend_handles_labels()
    h2, l2 = ax.get_legend_handles_labels()
    ax2.legend(h1 + h2, l1 + l2, ncol=2, loc='upper left', handlelength=2.2)
    no_numbers(ax, ax2)
    ax2.set_box_aspect(1)


def draw_mesh(ax: plt.Axes) -> None:
    """Fig 3a: GHG-MJSP mesh; color = green-NH3 share, dot size = CCS share."""
    df = pd.read_excel(os.path.join('Result', 'pareto_front.xlsx'))
    gp = df.pivot(index='ammonia_portion', columns='ccs', values='ghg')
    mp = df.pivot(index='ammonia_portion', columns='ccs', values='mjsp')
    for a in gp.index:
        ax.plot(gp.loc[a], mp.loc[a], '-', color='#bbbbbb', lw=0.6, zorder=0)
    for c in gp.columns:
        ax.plot(gp[c], mp[c], '-', color='#bbbbbb', lw=0.6, zorder=0)
    cmap = plt.get_cmap('RdYlBu')
    sc = ax.scatter(df['ghg'], df['mjsp'], s=40 + 260 * df['ccs'], c=df['ammonia_portion'],
                    cmap=cmap, vmin=-0.1, vmax=1.1, edgecolor='black', linewidth=0.6, zorder=3)

    x0, x1 = df['ghg'].min() - 6, df['ghg'].max() + 4
    ax.set_xlim(x0, x1)
    ax.set_ylim(0, df['mjsp'].max() * 1.15)
    ax.axvspan(CORSIA_THRESHOLD, x1, color='#e8e6dc', zorder=-1, lw=0)
    ax.axvline(CORSIA_THRESHOLD, color='#333333', ls='--', lw=1.0, zorder=1)
    ax.text(CORSIA_THRESHOLD + 2, df['mjsp'].max() * 1.1, 'fails\nCORSIA', va='top', color='#555555')

    arrow = dict(arrowstyle='-|>', color='black', lw=1.4)
    ax.annotate('', xy=(0.08, 0.44), xytext=(0.26, 0.30), xycoords='axes fraction', arrowprops=arrow)
    ax.text(0.28, 0.27, r'Green NH$_3$ $\uparrow$', transform=ax.transAxes)
    ax.annotate('', xy=(0.08, 0.31), xytext=(0.26, 0.17), xycoords='axes fraction', arrowprops=arrow)
    ax.text(0.28, 0.13, r'CCS share $\uparrow$ (bigger dot)', transform=ax.transAxes)

    cax = ax.inset_axes([0.74, 0.70, 0.22, 0.03])
    cb = ax.figure.colorbar(sc, cax=cax, orientation='horizontal')
    cb.set_ticks([0, 1]); cb.set_ticklabels(['0%', '100%']); cb.outline.set_visible(False)
    cb.ax.tick_params(length=0, labelsize=8)
    cax.set_title('Green NH$_3$ share', fontsize=9)
    ax.set_xlabel('WTWa GHG-100')
    ax.set_ylabel('MJSP')
    no_numbers(ax)


def draw_abatement(ax: plt.Axes) -> None:
    """Fig 3b: abatement cost vs CCS 50% anchor on a fine (NH3, CCS) grid; bilinear-interpolated
    GHG/MJSP from the 6x5 grid, same formula as tea_pareto_front."""
    df = pd.read_excel(os.path.join('Result', 'pareto_front.xlsx'))
    a_ax = np.sort(df['ammonia_portion'].unique())
    c_ax = np.sort(df['ccs'].unique())
    interp = {k: RegularGridInterpolator((a_ax, c_ax),
                                         df.pivot(index='ammonia_portion', columns='ccs', values=k).values)
              for k in ('ghg', 'mjsp')}
    A, C = np.meshgrid(np.linspace(0, 1, 301), np.linspace(0, 1, 301))
    pts = np.column_stack([A.ravel(), C.ravel()])
    ghg = interp['ghg'](pts).reshape(A.shape)
    mjsp = interp['mjsp'](pts).reshape(A.shape)
    anchor = df[(df['ammonia_portion'] == 0) & (df['ccs'] == 0.5)].iloc[0]
    with np.errstate(divide='ignore', invalid='ignore'):
        abate = (mjsp - anchor['mjsp']) * 1e6 / ((anchor['ghg'] - ghg) * E_MJ_PER_L)
    abate = np.ma.masked_where(ghg >= anchor['ghg'], abate)

    # assumption: color clipped at 3000 $/tCO2 -- the field diverges toward the anchor iso-GHG line
    norm = LogNorm(vmin=abate.min(), vmax=3000, clip=True)
    ax.set_facecolor('#efeee9')   # masked cells = no abatement vs the compliant CCS 50% anchor
    pm = ax.pcolormesh(A, C, abate, cmap='RdYlBu_r', norm=norm, shading='gouraud', rasterized=True)
    ax.contour(A, C, abate, levels=np.geomspace(abate.min() * 1.15, 2500, 5), colors='#333333',
               linewidths=0.5, alpha=0.6)
    ax.contour(A, C, ghg, levels=[anchor['ghg']], colors='black', linewidths=1.6)

    ax.text(0.04, 0.95, 'lowest cost', transform=ax.transAxes, va='top', color='black',
            fontweight=plt.rcParams['axes.labelweight'])
    ax.text(0.97, 0.04, 'highest', transform=ax.transAxes, ha='right', fontweight=plt.rcParams['axes.labelweight'], color='white')
    ax.text(0.05, 0.12, 'does not\nmeet CORSIA', transform=ax.transAxes, color='#555555')
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_xlabel(r'Green NH$_3$ H$_2$ substitution $\rightarrow$')
    ax.set_ylabel(r'CCS portion $\rightarrow$')
    cax = ax.inset_axes([1.04, 0, 0.05, 1])
    cb = ax.figure.colorbar(pm, cax=cax)
    cb.set_ticks([norm.vmin, norm.vmax]); cb.set_ticklabels(['low', 'high'])
    cb.minorticks_off(); cb.set_label('\\$ / t CO$_2$')
    no_numbers(ax)


def main() -> None:
    plt.rcParams.update(SA_RC)
    plt.rcParams['figure.autolayout'] = False
    plt.rcParams.update({'axes.spines.top': False, 'axes.spines.right': False})   # as plot_composite
    # one PNG per panel; Fig 3a (draw_mesh) dropped from the output
    for draw, name in [(draw_scale, 'abstract_fig2b.png'), (draw_abatement, 'abstract_fig3b.png')]:
        fig, ax = plt.subplots(figsize=(4.6, 4.4))
        ax.set_box_aspect(1)
        draw(ax)
        out = os.path.join('Figure', name)
        fig.savefig(out, dpi=200)
        plt.close(fig)
        print(f'wrote {out}')


if __name__ == '__main__':
    main()
