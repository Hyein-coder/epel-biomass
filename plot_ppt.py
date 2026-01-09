# Re-import necessary libraries due to code execution state reset
import matplotlib.pyplot as plt

# Data from the transportation sector slice
labels = [
    "Light \n Duty Vehicles",
    "Medium & Heavy Vehicles\n(Trucks and Buses)",
    "Off Road Vehicles & Equipment",
    "Rail & Maritime",
    # "Maritime",
    "Aviation",
    "Others"  #  \n (Pipeline\n /Military/\n Lubricants)
]
sizes = [49, 21, 10, 2+3, 11, 4]
colors = [
    '#4daf4a',  # Light Duty Vehicles - Green
    '#1b7837',  # Medium & Heavy Vehicles - Dark Green
    '#e39e54',  # Off Road Vehicles - Orange
    '#8c6bb1',  # Rail - Purple
    # '#80b1d3',  # Maritime - Blue
    '#41b6c4',  # Aviation - Cyan
    '#636363'   # Other - Dark Gray
]

# Plotting the pie chart
plt.figure(figsize=(9, 8))
wedges, texts, autotexts = plt.pie(
    sizes,
    labels=labels,
    autopct='%1.0f%%',
    colors=colors,
    startangle=140,
    textprops={'fontsize': 18},
    wedgeprops={'edgecolor': 'white', 'linewidth': 2}  # White borders
)

plt.title("Distribution of Transportation Sector \n GHG Emissions (2019 U.S.)", fontsize=20)
plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
plt.subplots_adjust(left=0.3, right=0.9)  # Adjust plot area to avoid cropping
plt.tight_layout()
plt.show()

#%%
# import matplotlib.pyplot as plt
import numpy as np

# Years and corresponding values from the chart
years = ["2025", "2030", "2032", "2035", "2040", "2045", "2050"]
saf_values = [2, 6, 6, 20, 34, 42, 70]
synthetic_saf_values = [0, 0, 1.2, 5, 10, 15, 35]

# Calculate the actual SAF portion by subtracting synthetic SAF
bio_saf_values = [s - syn for s, syn in zip(saf_values, synthetic_saf_values)]

# Bar width and position
x = np.arange(len(years))
bar_width = 0.6

# Re-plot the bar chart rotated 90 degrees clockwise (horizontal bars)
plt.figure(figsize=(6, 6))
plt.barh(x, synthetic_saf_values, label='Synthetic Sustainable Aviation Fuel', color='#fdbf11')
plt.barh(x, bio_saf_values, left=synthetic_saf_values, label='Sustainable Aviation Fuel', color='#ed6d47')

# Add percentage labels at the end of each bar
for i in range(len(years)):
    total = saf_values[i]
    plt.text(total + 1, x[i], f"{total}%", va='center', fontsize=14)

# Aesthetics
params = {
    # 'legend.fontsize': 'x-large',
    'axes.labelsize': 'xx-large',
    # 'axes.titlesize': 'xx-large',
    'xtick.labelsize': 'x-large',
    'ytick.labelsize': 'x-large'}
plt.rcParams.update(params)
plt.yticks(x, years)
plt.xlim([0, 80])
plt.xlabel("Minimum SAF Proportion (%)")
# plt.title("Mandatory Minimum Proportion of SAF \n in EU Aviation Safety Agency", fontsize=14)
plt.legend(loc="lower right", fontsize=12)
plt.grid(axis='x', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

#%%
# Stack data by material type instead of by source
materials = ['Used Cooking Oil', 'Forest Residue']
domestic = [144, 2843.071]
imported = [96, 0]

x = np.arange(len(materials))

# Plotting
plt.figure(figsize=(6, 6))
plt.bar(x, domestic, label='Domestic', color='#4daf4a')
plt.bar(x, imported, bottom=domestic, label='Import', color='#377eb8')

params = {
    'legend.fontsize': 'x-large',
    'axes.labelsize': 'xx-large',
    # 'axes.titlesize': 'xx-large',
    'xtick.labelsize': 'xx-large',
    'ytick.labelsize': 'xx-large'}
plt.rcParams.update(params)

# Labels and formatting
plt.xticks(x, materials)
plt.ylabel("Supply [kt/yr]")
# plt.title("Biomass Supply by Material and Source")
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.ylim([0, 3000])

plt.tight_layout()
plt.show()

#%%
# Data
categories = ['Forest Residue', 'Forest Logs']
static_gwp = [0.21266, 0.21266]
seq_US = [0.25696, 0.46942]
seq_KR = [0.22907, 0.36198]

x = np.arange(len(categories))
width = 0.25

params = {
    'legend.fontsize': 'xx-large',
    'axes.labelsize': 'xx-large',
    'axes.titlesize': 'xx-large',
    'xtick.labelsize': 'xx-large',
    'ytick.labelsize': 'xx-large'}
plt.rcParams.update(params)

# Plot
fig, ax = plt.subplots(figsize=(8, 6))
bars1 = ax.bar(x - width, static_gwp, width, label='Static GWP', color='steelblue')
bars2 = ax.bar(x, seq_US, width, label='U.S.', color='seagreen')
bars3 = ax.bar(x + width, seq_KR, width, label='Korea', color='peru')

# Add value labels
for bars in [bars1, bars2, bars3]:
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + 0.01, f'{height*1000:.0f}',
                ha='center', va='bottom', fontsize=17)

# Labels and formatting
ax.set_ylabel('Global emission [g CO2e/MJ]')
ax.set_ylim(0, 0.52)
ax.set_xticks(x)
ax.set_xticklabels(categories)
ax.legend()
plt.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.show()

#%%

import matplotlib.pyplot as plt
import pandas as pd

# Data extracted from the image
years = list(range(2024, 2036))
market_size = [13.30, 13.87, 14.93, 16.59, 17.86, 18.54, 19.90, 21.21, 22.78, 24.52, 26.18, 29.67]

# Create a DataFrame
df = pd.DataFrame({
    'Year': years,
    'Market Size (USD Billion)': market_size
})
params = {
    'legend.fontsize': 'x-large',
    'axes.labelsize': 'x-large',
    'axes.titlesize': 'xx-large',
    'xtick.labelsize': 'x-large',
    'ytick.labelsize': 'x-large'}
plt.rcParams.update(params)
# Plot as a line chart
plt.figure(figsize=(8, 5))
plt.plot(df['Year'], df['Market Size (USD Billion)'], marker='o', linestyle='-', color='skyblue', linewidth=2)
plt.title('Green Chemicals Market Size \n (Source: ESOMAR, Vantage Market Research)')
plt.xlabel('Year')
plt.ylabel('Market Size (USD Billion)')
plt.grid(True)
plt.tight_layout()
plt.show()

#%%
"""
https://www.ieabioenergy.com/wp-content/uploads/2024/12/CountryReport2024_Korea_final.pdf
"""
from matplotlib.patches import ConnectionPatch
params = {
    'legend.fontsize': 'x-large',
    'axes.labelsize': 'x-large',
    'axes.titlesize': 'xx-large',
    'xtick.labelsize': 'x-large',
    'ytick.labelsize': 'x-large'}
plt.rcParams.update(params)

# Data for main pie chart (2022 total energy share)
main_labels = ['Other', 'Coal', 'Oil', 'Natural Gas', 'Nuclear', 'Renewables']
main_sizes = [36.5, 24.4, 16.4, 19.1, 1.1, 2.5]
main_colors = ['grey', 'black', 'red', 'darkgrey', 'lightgrey', 'yellowgreen']

# Data for renewable share inset
renew_labels = ['Bioenergy', 'Hydro', 'Wind', 'Solar', 'Geothermal', 'Marine']
renew_sizes = [1.3, 0.1, 0.1, 0.9, 0.1, 0.1]
renew_colors = ['mediumseagreen', 'lightblue', 'cornflowerblue', 'yellow', 'purple', 'lightgrey']

# Replot with second chart as an inset in the upper right corner

fig, ax1 = plt.subplots(figsize=(12, 8))

# Draw main pie chart
main_explode = [0, 0, 0, 0, 0, 0.2]
wedges, texts = ax1.pie(main_sizes, colors=main_colors, startangle=10,
                        explode=main_explode, wedgeprops={'edgecolor': 'white'},
                        textprops={'fontsize': 18})

# Custom label for main chart
for i, txt in enumerate(main_labels):
    if txt:
        texts[i].set_text(f'{txt} {main_sizes[i]}%')
    else:
        texts[i].set_text('')  # Skip Renewables label here
plt.subplots_adjust(left=-0.2)  # Adjust plot area to avoid cropping

# Title for main chart
ax1.set_title('Total Energy Share in Korea (2022)', fontsize=25)

# Add inset axis for the renewable pie chart (position: [left, bottom, width, height])
ax2 = fig.add_axes([0.6, 0.55, 0.35, 0.35])
ax2.pie(renew_sizes,
        labels=[f'{label} {size}%' for label, size in zip(renew_labels, renew_sizes)],
        colors=renew_colors, startangle=150, wedgeprops={'edgecolor': 'white'},
        textprops={'fontsize': 15})
# ax2.set_title('Renewable Energy Share', fontsize=14)

plt.show()

#%%
import matplotlib.pyplot as plt
import numpy as np

categories = ['Demand for SAF', '1st Gen', '2nd Gen \n 2021 Production', '2nd Gen \n Domestic Vol/70 yr']
idx_2nd_gen = 2
labels_supply = ['Log', 'Forest Residue']
data_supply_tonne = {
    '1st Gen': [144000],
    'Log': [3274200, 6409698/0.7],
    'Forest Residue': [2843071, 4655465/0.7]  # No data for the last column
}
labels_demand = [2025, 2030, 2040, 2050]
data_demand_tonne = [330266.44*i for i in [2, 4.8, 24, 35]]

data_supply = {k: [vi/1e6 for vi in v] for k, v in data_supply_tonne.items()}
data_demand = [vi/1e6 for vi in data_demand_tonne]

x = np.arange(len(categories))  # the label locations
width = 0.2  # the width of the bars

fig, ax = plt.subplots(figsize=(8,4))
def autolabel(rects):
    for rect in rects:
        height = rect.get_height()
        if height > 0:
            ax.annotate(f'{height:,.2f}',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')
colors_demand = ['#256675', '#3ba4bc', '#4acdeb', '#92e1f3']
for i, d in enumerate(data_demand):
    rect_i = ax.bar(x[0] - width/2*3 + width*i, d, width, color=colors_demand[i], label=f'{labels_demand[i]} Demand' + r'$^1$')
    autolabel(rect_i)
ax.bar(x[1:idx_2nd_gen], data_supply['1st Gen'], width=0.6, label=r'1st Generation$^2$', color='green')
ax.bar(x[idx_2nd_gen:], data_supply['Forest Residue'], width=0.6, label=r'Forest Residue$^3$', color='#b9d379')
ax.bar(x[idx_2nd_gen:], data_supply['Log'], label=r'Log$^3$', width=0.6, color='goldenrod', bottom=data_supply['Forest Residue'])

# Adding labels on top of bars (optional)
for i, (l, p) in enumerate(zip(data_supply['Forest Residue'], data_supply['Log'])):
    ax.text(x[idx_2nd_gen+i], l / 2, f'{l:.2f}', ha='center', va='center', color='black')
    ax.text(x[idx_2nd_gen+i], l + p / 2, f'{p:.2f}', ha='center', va='center', color='black')
ax.set_ylim([0, max(data_supply['Forest Residue'])+max(data_supply['Log']) + 1])

# Labels and titles
ax.set_ylabel('Mt/year')
ax.set_title('')
ax.set_xticks(x)
ax.set_xticklabels(categories)
ax.grid(axis='y', linestyle='--', alpha=0.7)
ax.legend(loc='upper left', bbox_to_anchor=(1., .95))

fig.tight_layout()
plt.show()

