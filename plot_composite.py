"""2x2 composite: (a) GHG-MJSP mesh [Result/pareto_front.xlsx], (b) gray-H2 crossover
[analytic anchors in plot_ammonia_crossover], (c, d) SHAP beeswarms for CCS 60% and
Green NH3 10% + CCS 50% [Result/shap_samples.npz cache]. No TEA re-run."""
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

    # one 2x3 grid (3rd column = colorbar) so constrained_layout aligns each column -> upper
    # boxes take the same width as the lower ones; the top-right colorbar cell stays empty
    fig = plt.figure(figsize=(11, 9), constrained_layout=True)
    gs = fig.add_gridspec(2, 3, width_ratios=[1, 1, 0.04], height_ratios=[1, 1.05])
    ax_p, ax_c = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])
    ax_s = [fig.add_subplot(gs[1, 0])]
    ax_s.append(fig.add_subplot(gs[1, 1], sharex=ax_s[0]))
    cax = fig.add_subplot(gs[1, 2])

    plot_pareto_from_xlsx.draw(ax_p)
    ax_p.text(0.02, 0.02, 'WTWa GHG: Allocation, Korea grid mix', transform=ax_p.transAxes,
              ha='left', va='bottom', fontsize=8, color='#555555')
    plot_ammonia_crossover.draw(ax_c)

    sc = None
    for ax, (name, d) in zip(ax_s, data.items()):
        sc = beeswarm(ax, d['X'], d['sv'], d['order'], f"{name}\n(n={len(d['X'])}, R²={d['r2']:.3f})")
    cb = fig.colorbar(sc, cax=cax)
    cb.set_ticks([0, 1]); cb.set_ticklabels(['low', 'high']); cb.set_label('driver value')

    out = os.path.join('Figure', 'composite_pareto_crossover_shap.png')
    fig.savefig(out, dpi=150)
    print(f'wrote {out}')


if __name__ == '__main__':
    main()
