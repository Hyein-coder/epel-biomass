"""CO2 transport & storage knob: MJSP rises linearly with $/tCO2 on captured CO2."""
from funs import TEA

file_stream = 'Process_Data\\Pyrolysis_551_Scale0010_Streams.xlsx'
file_apea = 'Process_Data\\Pyrolysis_551_Scale0010_APEA.xlsm'


def mjsp_at(ts_price: float, ccs_portion: float = 1.) -> float:
    tea = TEA()
    tea.co2_ts_usd_per_ton = ts_price
    df_mjsp, *_ = tea.economic_analysis(file_stream, file_apea, ['Base'], ccs_portion=ccs_portion)
    return df_mjsp.loc['Base'].sum()


base = mjsp_at(0.)
low = mjsp_at(4.)
high = mjsp_at(45.)

print(f'MJSP [$/L]  T&S=0: {base:.4f}  T&S=$4: {low:.4f}  T&S=$45: {high:.4f}')

# T&S off must not change base case; cost must be monotonic and linear in price.
assert abs(mjsp_at(0.) - base) < 1e-9
assert high > low > base
ratio = (high - base) / (low - base)
assert abs(ratio - 45 / 4) < 0.05, ratio  # linear: delta scales with price
print('OK: linear in $/tCO2, ratio =', round(ratio, 3))
