import pandas as pd

# Reconstructing the data manually (estimated from visuals)
years = list(range(0, 101, 10))

# Estimated net CO2 emissions/sequestration values (arbitrary values)
fig_s5 = [-1.0, -0.85, -0.65, -0.45, -0.25, -0.05, 0.1, 0.15, 0.2, 0.25, 0.3]
fig_s6 = [-1.2, -1.0, -0.8, -0.6, -0.4, -0.2, -0.05, 0.05, 0.1, 0.15, 0.2]
fig_s7 = [-1.5, -1.3, -1.1, -0.85, -0.6, -0.4, -0.25, -0.1, 0.0, 0.05, 0.1]

# Combine into a single DataFrame
df_combined = pd.DataFrame({
    "Year": years,
    "Growth Case 1 (S5)": fig_s5,
    "Growth Case 2 (S6)": fig_s6,
    "Growth Case 3 (S7)": fig_s7
})

def rescale(values, old_min, old_max, new_min, new_max):
    return [((v - old_min) / (old_max - old_min)) * (new_max - new_min) + new_min for v in values]

# Rescale each column using their actual observed ranges
scaled_s5 = rescale(df_combined["Growth Case 1 (S5)"], -1.0, 0.3, -40, 240)
scaled_s6 = rescale(df_combined["Growth Case 2 (S6)"], -1.2, 0.25, -40, 240)
scaled_s7 = rescale(df_combined["Growth Case 3 (S7)"], -1.5, 0.2, -40, 240)

# Construct final DataFrame with real-world units (approximate gCO2e/MJ)
df_scaled = pd.DataFrame({
    "Year": df_combined["Year"],
    "Growth Case 1 (gCO2e/MJ)": scaled_s5,
    "Growth Case 2 (gCO2e/MJ)": scaled_s6,
    "Growth Case 3 (gCO2e/MJ)": scaled_s7
})

import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.plot(df_scaled["Year"], df_scaled["Growth Case 1 (gCO2e/MJ)"], '-o', label="GC1")
ax.plot(df_scaled["Year"], df_scaled["Growth Case 2 (gCO2e/MJ)"], '-d', label="GC2")
ax.plot(df_scaled["Year"], df_scaled["Growth Case 3 (gCO2e/MJ)"], '-x', label="GC3")
ax.legend()
plt.show()
