"""CO2 T&S cost across all study scales, CCS scenario (60% capture).

Sweeps co2_ts_usd_per_ton over the literature range and records MJSP per scale.
Same scale list / file naming / CCS portion as tea_scale_up.py.
"""
import os
import pandas as pd
from funs import TEA

case_scale = [1, 2.5, 5, 7.5, 10, 20, 30]
ts_prices = [0., 4., 45.]  # $/tCO2: 0 = no T&S (base CCS), 4-45 = literature range
ccs_portion = 0.60         # scale-up CCS scenario (matches tea_scale_up.py)

fig_folder = os.path.join(os.getcwd(), 'Figure')
os.makedirs(fig_folder, exist_ok=True)


def mjsp_and_saf(n: float, ts: float) -> tuple[float, float]:
    tea = TEA()
    tea.co2_ts_usd_per_ton = ts
    file_stream = f'Process_Data\\Pyrolysis_Jones_572_2MC_{int(n * 10):04d}_Streams.xlsx'
    file_apea = f'Process_Data\\Pyrolysis_Jones_572_2MC_{int(n * 10):04d}_APEAresults.xlsm'
    _, _, annual_prod_saf, _, _, data_all, _ = \
        tea.economic_analysis(file_stream, file_apea, ['Base'], ccs_portion=ccs_portion, ammonia_portion=0.)
    return data_all['cost'][0]['MJSP'], annual_prod_saf


mjsp = pd.DataFrame(index=case_scale, columns=ts_prices, dtype=float)
saf = {}
for n in case_scale:
    for ts in ts_prices:
        m, s = mjsp_and_saf(n, ts)
        mjsp.loc[n, ts] = m
        saf[n] = s

# T&S adder [$/L] = MJSP(ts) - MJSP(0); sequestered CO2 [t/yr] back-out from the $4 case.
adder = mjsp.subtract(mjsp[0.], axis=0)
co2_seq_tpy = adder[4.] / 4. * pd.Series(saf)  # $/L * L/yr / ($/t) = t/yr

summary = pd.DataFrame({
    'MJSP no T&S [$/L]': mjsp[0.],
    'MJSP $4/t [$/L]': mjsp[4.],
    'MJSP $45/t [$/L]': mjsp[45.],
    'T&S adder $4 [$/L]': adder[4.],
    'T&S adder $45 [$/L]': adder[45.],
    'CO2 sequestered [t/yr]': co2_seq_tpy,
    'SAF [L/yr]': pd.Series(saf),
})
summary.index.name = 'scale (x)'
print(summary.round(4).to_string())
summary.to_excel(os.path.join(fig_folder, 'scale_up_co2ts.xlsx'))

# Linear-in-price invariant: adder at $45 must be ~45/4 x adder at $4 for every scale.
ratio = (adder[45.] / adder[4.]).dropna()
assert ((ratio - 45 / 4).abs() < 0.05).all(), ratio
print('OK: linear in $/tCO2 across all scales, ratios =', ratio.round(3).tolist())
