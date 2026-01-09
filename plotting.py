import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import os


def plot_stack_bar(df, ylabel, colors=None, label_lim=0.1, save_name=None, fs=15,
                   figsize=(8,5), xlabel=None, tot_sum=True):
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

    fig, ax = plt.subplots(figsize=figsize)
    bottom_positive = np.zeros(len(df.index))
    bottom_negative = np.zeros(len(df.index))

    # Plot stacked bars
    if colors is None:
        # Generate colors from colormap
        colormap = matplotlib.cm.get_cmap('Set2', len(df.columns))
        colors = [matplotlib.colors.to_hex(colormap(i)) for i in range(len(df.columns))]
    bars_list = []
    for i, (column, color) in enumerate(zip(df.columns, colors)):
        val = df[column].values
        pos_mask = val > 0
        neg_mask = val < 0

        bars_positive = ax.bar(x, val * pos_mask, bar_width, bottom=bottom_positive, label=column, color=color,
                               edgecolor='#808080', linewidth=0.5)
        bars_negative = ax.bar(x, val * neg_mask, bar_width, bottom=bottom_negative, color=color,
                               edgecolor='#808080', linewidth=0.5)

        bars_list.append(bars_positive)
        bars_list.append(bars_negative)

        bottom_positive += val * pos_mask
        bottom_negative += val * neg_mask
    ax.axhline(0, color='black', linewidth=0.8)

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
                        ha='center', va='center', fontsize=fs-5, color='black')
            elif val < -label_lim:
                ax.text(x[i], cumulative_height_neg - val * neg_mask / 2, f'{val:.2f}',
                        ha='center', va='center', fontsize=fs-5, color='black')

    if tot_sum:
        total_sums = df.sum(axis=1)
        total_bars = ax.bar(np.arange(len(df.index)) + offset, total_sums, color='#C5C5C5', width=bar_width,
                            edgecolor='#808080', linewidth=0.5,
                            label='Total Sum')

    # Adding labels correctly for each stack
    # for i in range(len(df.index)):
    #     total_height = sum(df.iloc[i].map(lambda x: x * (x > 0)))
    #     ax.text(x[i], total_height + 0.1, f'{total_height:.2f}', ha='center', va='bottom',
    #             fontsize=10, fontweight='bold', color='black')
        for bar in total_bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, height / 2, f'{height:.2f}', ha='center', va='center',
                    fontsize=fs-2, fontweight='bold', color='black')

    # Legend
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1))

    # Labels and formatting
    ax.set_xticks(x + offset/2)
    ax.set_xticklabels(df.index)
    ax.set_ylim((min(bottom_negative) * 1.1, max(bottom_positive) * 1.1))
    plt.ylabel(ylabel, fontsize=fs+3)
    if xlabel is not None:
        plt.xlabel(xlabel, fontsize=fs+3)
    ax.tick_params(axis='both', which='major', labelsize=fs)
    plt.tight_layout()

    # Add horizontal grid
    ax.yaxis.grid(True, linestyle=':', alpha=0.7)
    if save_name is None:
        save_name = os.path.join(os.getcwd(), 'stack_bar')
    plt.savefig(save_name + '.png')
    plt.savefig(save_name + '.eps')
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

