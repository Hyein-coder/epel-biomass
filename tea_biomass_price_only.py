import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

price_forest_residue = 0.048649  # $/lb
price_log = 0.087275    # $/lb
supply_forest_residue = 783486  # lb/hr
supply_log = 902296     # lb/hr

critical_scales = [supply_forest_residue / 91014, (supply_log + supply_forest_residue) / 91014]

def first_model(supply):
    """
    :param supply: lb/hr
    :return: price [$/lb]
    """
    supply_critical = 522324    # arbitrary (1/1.5)
    basis = 1.8
    exponent = 0.5

    ratio = (supply - supply_critical) / (supply_forest_residue - supply_critical)
    if supply < supply_critical:
        price = price_forest_residue * np.power(basis, ratio)
    else:
        price = price_forest_residue * basis * np.power(ratio, exponent)

    return price


def galik_naive(supply):
    if supply < supply_forest_residue:
        price = price_forest_residue
    else:
        price = (supply * 0.04128 + 15107) / 1e6    # $/lb
    return price


def galik_elasticity_fixed(supply, elasticity=0.3):
    if supply < supply_log + supply_forest_residue:
        price = galik_naive(supply)
    else:
        s1 = supply_forest_residue + supply_log
        p1 = price_log
        v = -0.5

        p2 = p1 * (1+v)
        s2 = s1 * (2 + v + v * elasticity) / (2 + v - v * elasticity)

        slope = (p1-p2)/(s1-s2)
        b = slope * (-s1) + p1
        price = slope * supply + b
    return price

scale = [1, 2.5, 5, 7.5, 8.6, 10, 18.5, 20, 30]
biomass_demand = [s * 91014 for s in scale]

unit_MTy = 1/2000/1e6*8000

price = {
    "scale": scale,
    "bio_demand_ktpd": [b*unit_MTy for b in biomass_demand],
    "constant": [price_forest_residue for d in biomass_demand],
    "first": [first_model(d) for d in biomass_demand],
    "galik_naive": [galik_naive(d) for d in biomass_demand],
    "galik_elasticity_fixed": [galik_elasticity_fixed(d) for d in biomass_demand]
}

price_names = ['constant', 'galik_naive', 'galik_elasticity_fixed']
pretty_name = ['FR price', 'FR-Log Linear', r'Fixed Elasticity$^4$']
price_colors = plt.cm.viridis(np.linspace(0, 1, 4))
price_markers = ["x", "o", "^"]

params = {'legend.fontsize': 'large',
          # 'figure.figsize': (15, 5),
         'axes.labelsize': 'xx-large',
         'axes.titlesize':'xx-large',
         'xtick.labelsize':'x-large',
         'ytick.labelsize':'x-large'}
plt.rcParams.update(params)

fig, ax = plt.subplots()
for idx, name in enumerate(price_names):
    ax.plot(price["bio_demand_ktpd"], price[name], label=pretty_name[idx],
            color=price_colors[idx], marker=price_markers[idx], linewidth=2, markersize=9)
ax.axvline(supply_forest_residue*unit_MTy, color='r', linewidth=.8, label=r'FR & Log Production$^3$')
ax.axvline((supply_log + supply_forest_residue)*unit_MTy, color='r', linewidth=.8)
ax.grid(True, alpha=0.7)
ax.set_ylabel('Biomass Price [$/lb]')
ax.set_xlabel('Biomass Supply [Mt/year]')
plt.legend()
plt.tight_layout()
plt.show()
df_price = pd.DataFrame(price)

