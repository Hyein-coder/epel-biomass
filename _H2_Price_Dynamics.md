# H2 Price Dynamics

Raw-material cost breakdown (CCS-free, scale ×1). Top-3 items by $/L SAF.


| Item                | Base $/L | Ammonia $/L |
| ------------------- | -------- | ----------- |
| Ammonia (NH3)       | —        | 2.038       |
| Biomass             | 0.648    | 0.648       |
| Hydrogen gas (grey) | 0.629    | 0           |


## 1. Raw-material Unit Prices

Feedstock unit prices read from `Pyrolysis_551_Scale0010_APEA.xlsm` 


| Item                | Unit    | Unit price |
| ------------------- | ------- | ---------- |
| Ammonia (NH3)       | $/lb    | 0.288      |
| Biomass             | $/lb    | 0.04865    |
| Hydrogen gas (grey) | $/lb    | 0.68027    |
| Natural Gas / Fuel  | $/MMBTU | 14.38      |
| Electricity         | $/kWh   | 0.065      |


Natural Gas / Fuel and Electricity are hardcoded in `funs.TEA.__init__`
(`fuel_price_usd_per_mmbtu = 14.38`, elec 19.05 $/MMBTU = 0.065$/kWh); the rest are
read from the APEA RawMaterial Summary sheet.

## Log history

### 2026-09-18

- **Code** — user trimmed §1 intro to a single source line and pruned the unit-price
  table to Ammonia / Biomass / Hydrogen / Natural Gas / Electricity (dropped Sulfiding
  agent, Sand, Water/BFW rows).
- **Discussion** — "Update unit cost of raw-materials" clarified: record raw feedstock
unit prices ($/lb,$/MMBTU) read from funs.py/data, not the pre-existing $/L SAF
contribution table. Log target chosen = this file. Dropped: rerunning `tea_h2pathways.py`
and editing$/L values (user wanted input-side unit prices instead).
- **Code** — no code change; prices pulled by running existing
`TEA.calc_util_and_rawmaterial_price` on `Pyrolysis_551_Scale0010_APEA.xlsm`.
- **Open** — none.

