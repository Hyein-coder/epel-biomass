import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import os


def plot_stack_bar(df: pd.DataFrame, ylabel: str, colors: list | None = None, label_lim: float = 0.1,
                   save_name: str | None = None, fs: float | None = 15,
                   figsize: tuple = (8,5), xlabel: str | None = None, tot_sum: bool = True,
                   legend_kw: dict | None = None, ytop: float = 1.1, ax: plt.Axes | None = None,
                   hatches: list | None = None, total_color: str = '#C5C5C5'):
    # ax given: draw into it (no tight_layout/save/show); hatches given: white fill + hatch per column
    # fs=None: keep rcParams (SA_RC) label/tick sizes; value labels sized off font.size
    fs_txt = plt.rcParams['font.size'] + 2 if fs is None else fs
    # df = df.copy().fillna(0.)
    df = df.copy().dropna(how='all', axis=1)
    # Stack the values
    if tot_sum:
        bar_width = 0.4
        offset = bar_width * 1.2
    else:
        bar_width = 0.6
        offset = 0.
    x = np.arange(len(df.index))

    own_fig = ax is None
    fig, ax = plt.subplots(figsize=figsize) if own_fig else (ax.figure, ax)
    bottom_positive = np.zeros(len(df.index))
    bottom_negative = np.zeros(len(df.index))

    # Plot stacked bars
    if colors is None:
        # Generate colors from colormap
        colormap = matplotlib.cm.get_cmap('Set2', len(df.columns))
        colors = [matplotlib.colors.to_hex(colormap(i)) for i in range(len(df.columns))]
    if hatches is not None:
        colors = ['white'] * len(df.columns)
    hatch_list = hatches or [None] * len(df.columns)
    edge = '#808080' if hatches is None else 'black'   # gray hatch reads as faded; match lower-panel black
    bars_list = []
    for i, (column, color, hatch) in enumerate(zip(df.columns, colors, hatch_list)):
        val = df[column].values
        pos_mask = val > 0
        neg_mask = val < 0

        bars_positive = ax.bar(x, val * pos_mask, bar_width, bottom=bottom_positive, label=column, color=color,
                               edgecolor=edge, linewidth=0.5, hatch=hatch)
        bars_negative = ax.bar(x, val * neg_mask, bar_width, bottom=bottom_negative, color=color,
                               edgecolor=edge, linewidth=0.5, hatch=hatch)

        bars_list.append(bars_positive)
        bars_list.append(bars_negative)

        bottom_positive += val * pos_mask
        bottom_negative += val * neg_mask
    ax.axhline(0, color='black', linewidth=0.8)

    # hatched bars: white box behind segment labels so the hatch doesn't swallow the text
    lbl_box = dict(boxstyle='square,pad=0.1', fc='white', ec='none') if hatches is not None else None
    seg_fw = 200 if hatches is None else 400
    for i in range(len(df.index)):
        cumulative_height_pos = 0
        cumulative_height_neg = 0
        for column in df.columns:
            val = df[column].iloc[i]
            pos_mask = val > 0
            neg_mask = val < 0

            cumulative_height_pos += val * pos_mask
            cumulative_height_neg += val * neg_mask
            if val > label_lim:
                ax.text(x[i], cumulative_height_pos - val * pos_mask / 2, f'{val:.2f}',
                        ha='center', va='center', fontsize=fs_txt-5, fontweight=seg_fw, color='black', bbox=lbl_box)
            elif val < -label_lim:
                ax.text(x[i], cumulative_height_neg - val * neg_mask / 2, f'{val:.2f}',
                        ha='center', va='center', fontsize=fs_txt-5, fontweight=seg_fw, color='black', bbox=lbl_box)

    if tot_sum:
        total_sums = df.sum(axis=1)
        total_bars = ax.bar(np.arange(len(df.index)) + offset, total_sums, color=total_color, width=bar_width,
                            edgecolor=edge, linewidth=0.5,
                            label='Total Sum')

    # Adding labels correctly for each stack
    # for i in range(len(df.index)):
    #     total_height = sum(df.iloc[i].map(lambda x: x * (x > 0)))
    #     ax.text(x[i], total_height + 0.1, f'{total_height:.2f}', ha='center', va='bottom',
    #             fontsize=10, fontweight='bold', color='black')
        for bar in total_bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, height / 2, f'{height:.2f}', ha='center', va='center',
                    fontsize=fs_txt-2, fontweight=400, color='black')

    # Legend
    ax.legend(**(legend_kw or dict(loc='upper left', bbox_to_anchor=(1, 1))))

    # Labels and formatting
    ax.set_xticks(x + offset/2)
    ax.set_xticklabels(df.index)
    ax.set_ylim((min(bottom_negative) * 1.1, max(bottom_positive) * ytop))
    ax.set_ylabel(ylabel, fontsize=None if fs is None else fs+3)
    if xlabel is not None:
        ax.set_xlabel(xlabel, fontsize=None if fs is None else fs+3)
    if fs is not None:
        ax.tick_params(axis='both', which='major', labelsize=fs)
    if not own_fig:
        return fig, ax
    plt.tight_layout()

    # _PLOTTING_STYLE.md: no grid, save .png only
    if save_name is None:
        save_name = os.path.join(os.getcwd(), 'stack_bar')
    plt.savefig(save_name + '.png')
    plt.show()
    return fig, ax

def autopct_format(pct):
    # Function to determine label position
    return ('%1.1f%%' % pct) if pct >= 5 else ''  # Hide labels below 1%

def plot_pie_chart(df, title, lgd_anchor=(.97, .8), save_name=None, fs=15, fix_order=False):
    df = df.fillna(0.)
    if not fix_order:
        df = df.loc[:, df.iloc[0].sort_values(ascending=False).index]

    # Define colors for each category
    colors = [
                 '#2f6ea5',  # Brighter Deep Blue
                 '#c0c0c0',  # Brighter Gray
                 '#ffbf50',  # Brighter Golden Yellow
                 '#80d6d6',  # Brighter Muted Cyan
                 '#e0e0e0',  # Brighter Light Gray
                 '#f5d6a0',  # Brighter Warm Beige
                 '#c2a2e0',  # Muted Pastel Lavender (Toned Down)
                 '#B6C9ED',
                 '#f09040',  # Brighter Burnt Orange
                 '#00bfbf',  # Brighter Teal
                 '#6eacf2',  # Brighter Steel Blue
                 '#CFDBFA',     # Light Grey Lavender
                 '#D2E1C0',  #
                 '#008f8f',  # Brighter Dark Green
                 '#DAADA0',    # Brighter Dead Rose
                 # '#ffa500',   # Classical Orange
                 # '#ffcc80',   # Soft Yellow-Orange (New)
                 # '#80bf88',  # Muted Green
                 '#F0EEE8'  # White Grey
             ][:len(df.columns)]

    # colormap = matplotlib.cm.get_cmap('summer', len(df.columns))
    # colors = [matplotlib.colors.to_hex(colormap(i)) for i in range(len(df.columns))]

    # Create pie charts
    fig, axes = plt.subplots(1, len(df.index), figsize=(15, 5))

    # Ensure axes is iterable in case there's only one subplot
    if len(df.index) == 1:
        axes = [axes]

    for i, category in enumerate(df.index):
        wedges, _, autotexts = axes[i].pie(df.loc[category], labels=None,
                                           autopct=lambda pct: autopct_format(pct),
                                           colors=colors, startangle=140, textprops={'fontsize': fs},
                                           pctdistance=0.8)
        axes[i].set_title(category, fontsize=fs+3)  # , fontsize=14, fontweight='bold'

        # Rotate percentage labels clockwise
        # for autotext in autotexts:
        #      autotext.set_rotation(autotext.get_rotation() - 45)
        total = sum(df.loc[category])
        for i, autotext in enumerate(autotexts):
            pct = 100 * df.loc[category][i] / total
            if pct < 6:
                fontsize = fs-1
                autotext.set_fontsize(fontsize)
                autotext.set_rotation(autotext.get_rotation() - 45)

    # Create legend
    legend = fig.legend(df.columns, loc='upper right', bbox_to_anchor=lgd_anchor, title=title, prop={'size': fs-3})

    # Adjust layout and show plot
    # fig.suptitle(title, fontweight='bold', fontsize=24)
    plt.tight_layout()
    plt.subplots_adjust(right=0.8)  # Leave space for legend on the right

    if save_name is None:
        save_name = os.path.join(os.getcwd(), 'pie_chart')
    plt.savefig(save_name + '.png')
    plt.savefig(save_name + '.eps')
    plt.show()

