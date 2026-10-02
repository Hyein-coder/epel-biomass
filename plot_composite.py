"""5-panel composite: (a) GHG-MJSP mesh and (b) CO2 abatement-cost contour [both from
Result/pareto_front.xlsx], (c, d) SHAP beeswarms for CCS 60% and Green NH3 10% + CCS 50%
[Result/shap_samples.npz cache], (e) gray-H2 crossover [analytic anchors in
plot_ammonia_crossover]. No TEA re-run."""
import os
import numpy as np
import matplotlib.pyplot as plt
import plot_pareto_from_xlsx
import plot_ammonia_crossover
from tea_pareto_shap import SA_RC, POINTS, beeswarm


def main() -> None:
    plt.rcParams.update(SA_RC)
    plt.rcParams['figure.autolayout'] = False   # constrained_layout places the colorbar
    plt.rcParams.update({'axes.spines.top': False, 'axes.spines.right': False})  # axis lines only, no box
    data = np.load(os.path.join('Result', 'shap_samples.npz'), allow_pickle=True)['data'].item()
    assert set(data) == set(POINTS), 'stale SHAP cache: rerun tea_pareto_shap.py'

    # one 3x3 grid (3rd column = colorbars) so constrained_layout aligns each column -> all
    # boxes take the same width; (e) sits bottom-left, its right and colorbar cells stay empty
    fig = plt.figure(figsize=(12.6, 12.2), constrained_layout=True)
    gs = fig.add_gridspec(3, 3, width_ratios=[1, 1, 0.04], height_ratios=[1, 1.05, 1])
    ax_p, ax_a = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])
    ax_s = [fig.add_subplot(gs[1, 0])]
    ax_s.append(fig.add_subplot(gs[1, 1], sharex=ax_s[0]))
    cax = fig.add_subplot(gs[1, 2])
    ax_c = fig.add_subplot(gs[2, 0])

    plot_pareto_from_xlsx.draw(ax_p)
    plot_pareto_from_xlsx.draw_abatement(ax_a, fig.add_subplot(gs[0, 2]))
    plot_ammonia_crossover.draw(ax_c)

    sc = None
    for ax, d in zip(ax_s, data.values()):
        order = [k.replace('Ammonia', 'Green NH₃') for k in d['order']]   # display name only; cache keeps 'Ammonia'
        sc = beeswarm(ax, d['X'], d['sv'], order, '')   # in-panel case label dropped
    cb = fig.colorbar(sc, cax=cax)
    cb.set_ticks([0, 1]); cb.set_ticklabels(['low', 'high']); cb.set_label('driver value')
    for ax, lab in zip([ax_p, ax_a, *ax_s, ax_c], 'abcde'):
        ax.text(-0.1, 1.02, f'({lab})', transform=ax.transAxes, va='bottom',
                fontweight=plt.rcParams['axes.labelweight'], fontsize=16)   # 12.6-in-wide figure: rc 12 reads too small

    out = os.path.join('Figure', 'composite_pareto_crossover_shap.png')
    fig.savefig(out, dpi=150)
    print(f'wrote {out}')


if __name__ == '__main__':
    main()
