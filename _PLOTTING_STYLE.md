# Plotting Style (`SA_RC`)

All figures use a shared `SA_RC` rcParams dict, defined in `plot_conventional.ipynb` and  
applied in analysis scripts via `plt.rcParams.update(SA_RC)`.

```python
SA_RC = {
    # Figure
    'figure.dpi': 150,
    'figure.facecolor': 'white',
    'figure.autolayout': True,
    # Axes
    'axes.facecolor': 'white',
    'axes.edgecolor': '#444444',
    'axes.linewidth': 0.8,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'axes.labelsize': 12,
    'axes.labelcolor': 'black',
    'axes.labelweight': '500',
    'axes.titlelocation': 'center',
    'axes.grid': False,
    # Ticks
    'xtick.labelsize': 12,
    'xtick.color': 'black',
    'xtick.direction': 'out',
    'ytick.labelsize': 12,
    'ytick.color': 'black',
    'ytick.direction': 'out',
    # Font
    'font.family': 'sans-serif',
    'font.sans-serif': ['Helvetica Neue LT Pro', 'Helvetica Neue', 'Arial', 'DejaVu Sans'],
    'font.size': 10,
    'font.weight': '300',
    'text.color': 'black',
    # Patches (bars, legend swatches)
    'patch.edgecolor': 'black',
    'patch.linewidth': 0.7,
    'patch.force_edgecolor': True,
    # Legend
    'legend.fontsize': 8,
    'legend.title_fontsize': 9,
    'legend.framealpha': 0.0,
    'legend.edgecolor': '#444444',
    # Lines
    'lines.linewidth': 0.7,
    'lines.markersize': 3,
    # Saving
    'savefig.dpi': 150,
    'savefig.bbox': 'tight',
    'savefig.facecolor': 'white',
}
```

## Key conventions

- **Colormap**: `RdYlBu` with `np.linspace(0.1, 0.9, n_features)` for feature color assignments
- **No grid** — `axes.grid: False`; never call `ax.grid(...)`
- **Transparent legend** — `legend.framealpha: 0.0`; no explicit `fontsize=` overrides
- **Y headroom** — `ax.set_ylim(0, ax.get_ylim()[1] * 1.2)` after plotting
- **No explicit fontsize** on axis labels or titles — let `SA_RC` handle all sizes
- **Save formats** — save `.png` **only** (150 dpi). Do not emit `.svg`/`.eps` copies; the  
triple-format output cluttered the analysis folder. Regenerate a vector copy on demand only  
when a specific figure needs one for publication.
- **No titles**


## Frame and layout

- **Axis lines only, no box** — `axes.spines.top/right: False`. A twin y-axis re-enables its own
right spine: `ax2.spines['right'].set_visible(True)`.
- **Multi-panel figures** — one `gridspec`, `constrained_layout=True`, and set
`plt.rcParams['figure.autolayout'] = False` (autolayout fights constrained_layout). Colorbar gets
its own narrow grid column (`width_ratios=[..., 0.04]`) so the data panels keep equal widths.
- **No in-panel case titles**; panel identity goes in the caption.

## Lines and markers

- **Background mesh / guide lines**: `color='#bbbbbb', lw=0.6, zorder=0`.
- **Main data lines**: `lw` 1.6–2.2, `markersize` 5–6, `markevery` on dense curves.
- **Colour-independent series** — every series gets a distinct marker (`o s ^ D v P`) and/or
line style (`- -- :`), so it reads in grayscale.
- **Range band** around a line: `fill_between(..., alpha=0.25, linewidth=0)`, same colour as the line.
- **Scatter**: `s=70, edgecolor='black', linewidth=0.6`.

## Colour

- **Ordered sweep** (one line per parameter level): sequential map sliced away from the white end,
e.g. `plt.cm.Blues(np.linspace(0.45, 0.9, n))`; light = low, dark = high.
- **Value-coded scatter**: `RdYlBu_r` (blue low → red high), `vmin=0, vmax=1` on normalised values;
colorbar ticks `[0, 1]` labelled `low` / `high`.
- **Semi-transparent fill, solid edge** — put alpha in the fill hex (`'#RRGGBBCC'` ≈ 0.8) rather
than `alpha=`, so edges stay fully black.

## Bars

- Bar `width=0.7`; stacked-segment edge `linewidth=0.5`.

## Labels and legends

- **Units in square brackets**: `Quantity [unit]`.
- **mathtext**: escape dollar as `\$` in labels; sub/superscripts via `$_2$`, `$^{-1}$`.
- **Legend proxies** — build `plt.Line2D([], [], ...)` handles when markers and colours encode
separate dimensions; `markerscale=1.8` keeps small markers legible. Merge twin-axis handles into one
legend.
- **Equal tick sizes** when both axes are numeric:
`ax.tick_params(axis='y', labelsize=plt.rcParams['xtick.labelsize'])`.
