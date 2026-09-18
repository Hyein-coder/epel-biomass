# Workframe — TEA Scripts

Reference for writing/editing/analyzing TEA code and results.

## Version lineage (process design iterations, not sequential order)

| Series | Scripts | Engine | Status |
|--------|---------|--------|--------|
| **541** | `tea_base_JonesBaseCaseScale.py` | inline funcs from `funs` | ancestor, monolithic |
| **572** | `tea_scale_up.py`, `tea_h2pathways.py`, `tea_ammonia_mix.py`, `tea_scale_up_ammonia.py`, ... | `TEA` class | mid-gen, `Pyrolysis_Jones_572_2MC_*` data |
| **551** | `tea_ccs.py`, `tea_co2_portion.py`, `tea_scale_up_price_models.py` | `TEA` class | **current**, `Pyrolysis_551_Scale*` data |

Latest = 551 trio. `tea_co2_portion.py` is newest.

- `tea_co2_portion.py` — CCS portion sweep 0→90%, TEA cost joined with WTWa LCA (`funs_lca`). Writes `Result/CO2_ver551_0##.xlsx`. Scale 30.
- `tea_ccs.py` — CCS portion sweep 0/25/50/75/100%, MJSP stack bar + util/raw material breakdown + `TEA_summary_CCS.xlsx`. Scale 1.
- `tea_scale_up_price_models.py` — 3 biomass price models (FR Price / FR-Log Linear / Fixed Elasticity) × 7 scales, Base/Ammonia/CCS. Biomass price vs MJSP figure.

## Calculation procedure

All 551/572 scripts route through `TEA.economic_analysis` (`funs.py:789`).

```
1. Read Aspen streams (Material/Heat/Work sheets)
2. Products    -> hourly_revenue, energy_production, annual SAF
3. Sub-units by cost interpolation from literature base cases:
     CCS (Rao 2022) · PSA H2 recovery (Byun 2020) · R-510 hydrocracking (Jones 2013)
     · hydrotreat catalysts (Ru/Mo charging)   <- ccs_portion scales the CCS unit
4. Main process CAPEX/OPEX  <- APEA xlsm (Project Summary sheet)
5. resume_cost_summary  -> combine main + sub-units
6. cal_MJSP  -> MJSP [$/L SAF]  (annual OPEX / annual SAF production)
7. H2-source swap: strip grey-H2 cost from main, add SMR/Ammonia/PEM/Mix LCOH
8. return df_mjsp (rows = H2 source, cols = cost category)
```

Key knobs:
- `ccs_portion` — fraction of CO2 captured (scales CCS unit cost).
- `ammonia_portion` — adds a "Mix" H2 case (partial grey + ammonia-cracked H2).

Cost basis: all costs shifted 1Q-2022 → 2011 base via `bi_22to11 = 2250/3230`.

## What changed 541 → 551

- **541 monolith → TEA class**: inline procedure extracted into `funs.TEA` methods, reused by all newer scripts. 541 hardcodes Base + SMR-CCS only.
- **Data version**: 541 → 572 → 551 process files. 551 scripts still carry commented-out 572 paths (mid-migration leftovers).
- **New in 551**: LCA coupling (`funs_lca`, WTWa GHG), biomass price models, CCS portion sweeps. 572-era `tea_scale_up.py` had scale-up + H2 pathways but no price models / LCA integration.
