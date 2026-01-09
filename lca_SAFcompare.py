import matplotlib.pyplot as plt

params = {'legend.fontsize': 'x-large',
         'axes.labelsize': 'xx-large',
         'axes.titlesize': 'xx-large',
         'xtick.labelsize':'x-large',
         'ytick.labelsize':'x-large'}
plt.rcParams.update(params)

# Sample data for reproduction (based on the image and approximated values)
# These are dummy data points for visualization purpose
data = {
    'Conventional': [(90, 0.8)],
    'HEFA (1st gen)': [(5, 1.2), (10, 1.0), (15, 0.8), (20, 1.5), (25, 2.3)],
    'HFS (1st gen)': [(20, 5.0), (30, 4.0), (40, 4.5), (50, 5.2)],
    'FT (2nd gen)': [(10, 2.5), (15, 3.0), (20, 1.5), (25, 2.0), (30, 3.0)],
    'ATJ (2nd gen)': [(30, 2.0), (35, 2.2), (40, 1.9), (50, 2.5), (60, 1.8)],
    'Pyrolysis (2nd gen)': [(56.6, 1.99)]  #(144.1, 1.19), (101.5, 2.05), (64.1, 2.7), (59.8, 5.30),
}

price_tot = [t[1] for k, d in data.items() if k != 'Pyrolysis (2nd gen)' for t in d]
price_average = sum(price_tot)/len(price_tot)

#%%
# Markers and colors
marker_style = {
    'FT (2nd gen)': ('o', 'blue'),
    'HEFA (1st gen)': ('s', 'orange'),
    'ATJ (2nd gen)': ('X', 'green'),
    'HFS (1st gen)': ('p', 'purple'),
    'Conventional': ('d', 'black'),
    'Pyrolysis (2nd gen)': ('^', 'red')
}

# Plotting
plt.figure(figsize=(8, 6))
for fuel, points in data.items():
    marker, color = marker_style[fuel]
    x, y = zip(*points)
    plt.scatter(x, y, label=fuel, marker=marker, color=color, s=110)
plt.axvline(x=75.9, color='r', linestyle='-', linewidth=1)
plt.xlabel("Average WTWa GHG Emissions [gCO$_2$eq/MJ]")
plt.ylabel("MJSP [$/L]")
plt.ylim(0, 6)
plt.xlim(0, 100)
plt.legend()
plt.grid(True, alpha=0.7, linestyle='--')
plt.tight_layout()

plt.savefig('Figure/fig_SAF_compare.png')
plt.savefig('Figure/fig_SAF_compare.eps')
plt.show()
