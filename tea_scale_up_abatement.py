"""Post-fix (six-tenths) + T&S numbers for the restructured scale-up report.

Base / full-Ammonia / CCS-by-rate MJSP per scale on the 551 basis, plus CO2
abatement cost ($/tCO2, allocation & displacement). GHG intensities are
scale-independent (LCA per MJ SAF), taken from report sections 3b/3c. T&S is a
flat $/t on sequestered CO2, added to MJSP analytically (linear in price).
"""
import os
import pandas as pd
from funs import TEA

scales = [1, 2.5, 5, 7.5, 10, 20, 30]
rates = [0.25, 0.50, 0.75, 1.00]
ts_prices = [4, 45]  # $/tCO2 range
E = 31.66            # MJ/L SAF (section 3b)

# GHG intensity [g CO2e/MJ], scale-independent (sections 3b/3c)
BASE_GHG = {'alloc': 87.57, 'disp': 123.03}
AMM_dGHG = {'alloc': 38.12, 'disp': 120.76}  # base - full ammonia
# Green-ammonia price range (§3): feed contributes a flat 2.038 $/L across scale (§5/§3c),
# base price 0.288 $/lb; low=projected 0.1225, high=current 0.4535.
AMM_FEED_USD_L, AMM_P_BASE = 2.038, 0.288
AMM_PRICE = {'low': 0.1225, 'high': 0.4535}
CCS_GHG = {0.25: {'alloc': 76.01, 'disp': 86.44},
           0.50: {'alloc': 64.44, 'disp': 49.76},
           0.75: {'alloc': 54.17, 'disp': 17.23},
           1.00: {'alloc': 44.15, 'disp': -14.57}}
# Korea grid-mix method (funs_lca on Pyrolysis_551_LCA_*_KRmix); heavier grid -> smaller net dGHG for CCS
KR = {'base_alloc': 100.83, 'amm_alloc': 62.74, 'ccs100_alloc': 59.96,
      'base_disp': 124.63, 'amm_disp': 3.83, 'ccs100_disp': -4.97}
KR_dAMM = {'alloc': KR['base_alloc'] - KR['amm_alloc'], 'disp': KR['base_disp'] - KR['amm_disp']}
KR_dCCS100 = {'alloc': KR['base_alloc'] - KR['ccs100_alloc'], 'disp': KR['base_disp'] - KR['ccs100_disp']}

tea = TEA()


def abate(dmjsp: float, dghg: float) -> float:
    return dmjsp * 1e6 / (dghg * E)  # $/tCO2


rows = []
for n in scales:
    fs = f'Process_Data\\Pyrolysis_551_Scale{int(n * 10):04d}_Streams.xlsx'
    fa = f'Process_Data\\Pyrolysis_551_Scale{int(n * 10):04d}_APEA.xlsm'

    # Sequestered-CO2 streams (lb/hr), same definition as calc_cost_CCS
    df = pd.read_excel(fs, sheet_name='Material', header=3)
    idx = tea.get_idx_material(df)
    co2_EGR = df['622X'][idx['mass flow [lb/hr]']]
    co2_left = df['623CO2'][idx['mass flow [lb/hr]']]

    _, _, saf, _, _, da, _ = tea.economic_analysis(fs, fa, ['Base', 'Ammonia'], ccs_portion=0.)
    base, amm = da['cost'][0]['MJSP'], da['cost'][1]['MJSP']
    rec = {'scale': n, 'Base': base, 'Ammonia': amm,
           'Amm_abate_alloc': abate(amm - base, AMM_dGHG['alloc']),
           'Amm_abate_disp': abate(amm - base, AMM_dGHG['disp'])}
    # Ammonia abatement range vs green-NH3 price (lowest/highest); MJSP offset = feed $/L * (p/base - 1)
    for lab, p in AMM_PRICE.items():
        amm_p = amm + AMM_FEED_USD_L * (p / AMM_P_BASE - 1.)
        rec[f'Amm_abate_alloc_{lab}'] = abate(amm_p - base, AMM_dGHG['alloc'])
        rec[f'Amm_abate_disp_{lab}'] = abate(amm_p - base, AMM_dGHG['disp'])

    for r in rates:
        _, _, _, _, _, dac, _ = tea.economic_analysis(fs, fa, ['Base'], ccs_portion=r)
        ccs = dac['cost'][0]['MJSP']
        seq_tpy = (co2_left * r + co2_EGR) / 2204.62 * 8000.  # t/yr
        tag = int(r * 100)
        rec[f'CCS{tag}'] = ccs
        for p in ts_prices:
            mjsp_ts = ccs + seq_tpy * p / saf
            rec[f'CCS{tag}_ts{p}'] = mjsp_ts
            rec[f'CCS{tag}_abate_alloc_ts{p}'] = abate(mjsp_ts - base, BASE_GHG['alloc'] - CCS_GHG[r]['alloc'])
            rec[f'CCS{tag}_abate_disp_ts{p}'] = abate(mjsp_ts - base, BASE_GHG['disp'] - CCS_GHG[r]['disp'])
        rec[f'CCS{tag}_abate_alloc_ts0'] = abate(ccs - base, BASE_GHG['alloc'] - CCS_GHG[r]['alloc'])
        rec[f'CCS{tag}_abate_disp_ts0'] = abate(ccs - base, BASE_GHG['disp'] - CCS_GHG[r]['disp'])

    # Korea-mix abatement for the full options (§4): ammonia (base price) + full-CCS at T&S range
    rec['Amm_KRalloc'] = abate(amm - base, KR_dAMM['alloc'])
    rec['Amm_KRdisp'] = abate(amm - base, KR_dAMM['disp'])
    ccs100 = rec['CCS100']
    seq100 = (co2_left * 1.0 + co2_EGR) / 2204.62 * 8000.
    for p in ts_prices:
        m = ccs100 + seq100 * p / saf
        rec[f'CCS100_KRalloc_ts{p}'] = abate(m - base, KR_dCCS100['alloc'])
        rec[f'CCS100_KRdisp_ts{p}'] = abate(m - base, KR_dCCS100['disp'])
    rows.append(rec)

df_all = pd.DataFrame(rows).set_index('scale').round(3)
pd.set_option('display.width', 240, 'display.max_columns', 60)
print('=== MJSP [$/L] ===')
print(df_all[['Base', 'Ammonia', 'CCS100', 'CCS100_ts4', 'CCS100_ts45']].to_string())
print('\n=== Full-option abatement [$/tCO2] (alloc | disp), CCS100 at T&S 0/4/45 ===')
print(df_all[['Amm_abate_alloc', 'Amm_abate_disp',
              'CCS100_abate_alloc_ts0', 'CCS100_abate_alloc_ts4', 'CCS100_abate_alloc_ts45',
              'CCS100_abate_disp_ts0', 'CCS100_abate_disp_ts45']].to_string())
print('\n=== Ammonia abatement price range [$/tCO2] (low 0.1225 - high 0.4535 $/lb) ===')
print(df_all[['Amm_abate_alloc_low', 'Amm_abate_alloc_high',
              'Amm_abate_disp_low', 'Amm_abate_disp_high']].to_string())
print('\n=== Korea-mix full-option abatement [$/tCO2] ===')
print(df_all[['Amm_KRalloc', 'Amm_KRdisp',
              'CCS100_KRalloc_ts4', 'CCS100_KRalloc_ts45',
              'CCS100_KRdisp_ts4', 'CCS100_KRdisp_ts45']].round(0).to_string())
print('\n=== Abatement vs CCS rate at base scale x1 [$/tCO2] ===')
base_row = df_all.loc[1]
for r in rates:
    tag = int(r * 100)
    print(f'  {tag:>3}%  alloc ts0/4/45 = {base_row[f"CCS{tag}_abate_alloc_ts0"]:.0f}/'
          f'{base_row[f"CCS{tag}_abate_alloc_ts4"]:.0f}/{base_row[f"CCS{tag}_abate_alloc_ts45"]:.0f}'
          f'   disp ts0/45 = {base_row[f"CCS{tag}_abate_disp_ts0"]:.0f}/{base_row[f"CCS{tag}_abate_disp_ts45"]:.0f}')

df_all.to_excel(os.path.join('Figure', 'scale_up_abatement.xlsx'))

# Cross-check: base-scale CCS100 no-T&S alloc abatement must match section 4 (~414).
assert abs(df_all.loc[1, 'CCS100_abate_alloc_ts0'] - 414) < 6, df_all.loc[1, 'CCS100_abate_alloc_ts0']
print('\nOK: base-scale CCS100 alloc abatement =', round(df_all.loc[1, 'CCS100_abate_alloc_ts0']), '(section 4 = 414)')
