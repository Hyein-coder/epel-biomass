# Supporting Information

Detail extracted from the analysis scripts (`funs.py`, `funs_lca.py`, `Dynamic_LCA/`,
and the `tea_*` / `lca_*` drivers) that supports the Methods but is too granular for the
main text. Constants are quoted as implemented in code.

## S1. Cost basis and financial parameters

- Cost-year indices: `cost_idx_1Q2022 = 3230`, `cost_idx_Jones = 2250`; Jones-era source
  costs escalated ×(3230/2250) to 1Q-2022 USD. Katebah SMR uses its own index 2340.
- The standalone Jones base-case validation script (`tea_base_JonesBaseCaseScale.py`)
  instead deflates 1Q-2022 → 2011 by `bi_22to11 = 2250/3230 ≈ 0.697`; this factor is
  **not** applied in the production engine `funs.py`, which works in 1Q-2022 USD.
- Financial: economic period 30 yr; IRR/discount 10%; tax 35%; salvage 0; straight-line
  depreciation; 8000 operating hours/yr (≈91.3% capacity factor).
- MJSP (annuity form): `annuity = (1+irr)⁻¹·(1−(1+irr)⁻ⁿ)/(1−(1+irr)⁻¹)`;
  `capital investment/yr = (CAPEX − annuity·tax·depreciation)/annuity/(1−tax)`;
  `MJSP = (min revenue − co-product sales)/annual SAF volume`.
- SAF annual volume = stream 326SAF volumetric flow × 8000 h × 28.3168 L/cuft.
- Product/utility prices: 326SAF = 0 (the priced product); 316GAS (naphtha) 0.75757 $/lb;
  336DIES (diesel) 0.6 $/lb; electricity 19.05 $/MMBtu; natural gas / fuel 14.38 $/MMBtu.
- LHV is read per stream ("LHV at 15 °C [Btu/lb]") and corrected to 25 °C via
  `lhv_25C = lhv_15C + heat_capacity·ΔT`, ΔT = (25−15)·5/9 °F. The 44.8 MJ/kg SAF LHV in
  the main text is a reporting basis, not a hardcoded engine constant.

## S2. Sub-unit cost interpolation

All five bolt-on sub-units use `unit_cost_interpolation` with the same law
(`r = stream/base_stream`): **CAPEX × r⁰·⁶** (six-tenths), **OPEX × r⁰·⁷**, stream and
utility rates linear (× r). Literature base cases:

| Sub-unit | Reference | Base stream | Base CAPEX | Notes |
|---|---|---:|---:|---|
| CCS (amine) | Rao & Rubin 2002 | 862,853 lb/hr CO₂ | $297.93 M | heat 3,315 MMBtu/hr; elec = 14% of heat |
| PSA H₂ recovery | Byun 2020 | 700 m³/hr | $780,993 | OPEX $5,078/yr; ~68% of OPEX = adsorbent/reactant |
| R-510 hydrocracking | Jones 2013 | 9,600 lb/hr | $5.27 M | driven by recycle stream 340 |
| Off-gas reformer | Jones 2013 | (8846+995)/0.91 lb H₂ | $69.14 M (2011) | escalated ×3230/2250 |
| SMR (+CCS) | Katebah 2022 | 45,922 | $424 M / OPEX $147 M | idx 2340; NG feed 156,136; CO₂ 55,107 |

Hydrotreating catalyst charging (`calc_cost_HTcat`): R-202/R-220 ruthenium LHSV 0.5,
price 60 × 2.2 $/kg; R-225 molybdenum LHSV 0.22, price 15.5 × 2.2 $/kg (× cost index).

## S3. Scale-up and single-train limits

- Scale set: [1, 2.5, 5, 7.5, 10, 20, 30]×; main plant read from per-scale APEA files
  `Pyrolysis_551_Scale0010…1000_APEA.xlsm`.
- Pyrolyzer (R-110) single-train cap 700 MMBtu/hr = 10× base duty (70 MMBtu/hr at
  45.5 t/hr biomass); train count = ceil(base duty × scale / cap) → 1/1/1/1/1/2/3 across
  the scale set. Gas turbines, compressors, and expanders follow the same numbering-up.
- Ammonia-cracker reactor single-train cap 172 MMBtu/hr (distinct unit).
- Compressor optimization (`opt_compressor.py`): inlet 50 bar → 365 bar target;
  gas-turbine firing-temperature sweep 1900–2400 °F (`opt_GT_temperature.py`).

**Table S3-1. Per-unit single-train caps and replica counts** (source:
`Scaling_Up_Study_ver551_organized.xlsx`). Number of parallel trains follows
`n = ceil(total duty / cap)`; the cap equals the saturated per-replica load.

| Unit | Service | Sizing metric | Single-train cap | Replicas [1, 2.5, 5, 7.5, 10, 20, 30]× |
| ---- | ------- | ------------- | ---------------- | -------------------------------------- |
| C-101 | Compressor | Volumetric flow | 15.81×10⁶ cuft/hr (2772 HP) | 1 / 1 / 1 / 1 / 1 / 2 / 3 |
| C-110 | Compressor | Volumetric flow | 17.57×10⁶ cuft/hr | 1 / 1 / 1 / 2 / 2 / 3 / 5 |
| C-147 | Compressor | Volumetric flow | 17.77×10⁶ cuft/hr | 1 / 1 / 1 / 2 / 2 / 4 / 6 |
| C-401 | Compressor | Volumetric flow | 15.23×10⁶ cuft/hr (192,935 HP) | 1 / 1 / 1 / 1 / 1 / 2 / 3 |
| MC-610 | Compressor | Volumetric flow | 17.38×10⁶ cuft/hr | 1 / 2 / 3 / 4 / 5 / 10 / 20 † |
| C-231 | Expander | Volumetric flow | 24,981 cuft/hr (1944 HP) | 2 / 6 / 10 / 14 / 18 / 36 / 54 † |
| R-110 | Combustion chamber (pyrolyzer) | Heat absorbed | 447.5 MMBtu/hr (base 44.75) | 1 / 1 / 1 / 1 / 1 / 2 / 3 |
| E-616 | Heat exchanger | Heat duty | 955.4 MMBtu/hr | 1 / 1 / 1 / 1 / 1 / 2 / 3 |
| GT-612 | Gas turbine | Power output | 441,073 hp | 1 / 1 / 2 / 2 / 2 / 4 / 6 |

- The R-110 cap of 447.5 MMBtu/hr (10× the 44.75 MMBtu/hr base) supersedes the
  700 MMBtu/hr figure listed above; `ceil(scale × 44.75 / 447.5)` reproduces its
  1/1/1/1/1/2/3 pattern exactly.
- † MC-610 and C-231 are **over-provisioned** relative to the strict `ceil(total/cap)`
  rule: MC-610 carries 20 trains at 30× where the rule gives 15 (total/cap = 15.0 exactly),
  and C-231 carries 6 and 10 trains at 2.5× and 5× where the rule gives 5 and 9. Every
  other unit matches the rule exactly.

## S4. Ammonia cracker detail

- Cracker scale index `n = main_h2_demand / 6570.40 lb/hr`; non-grid `n` linearly
  interpolated between bracketing APEA runs `NH3_Cracking_130_scale{NNNN}_APEAresult.xlsm`.
- Base cost structure from `NH3_Cracking_126_FinalComp_APEAresult.xlsm`.
- Utilities = electricity; raw material = ammonia; fertilizer credited from the Product
  Summary sheet. Conversion / H₂-recovery ratios live inside the Aspen model (APEA export
  gives NH₃-in vs H₂-out); GHSV/kinetics source: `ghsv_IJHE_2024.py` (Int. J. Hydrogen
  Energy 2024).
- Grey-H₂ benchmark 0.68 $/lb H₂. SMR calc uses NG price 0.092306 $/lb (US), escalated.
- PEM alternative: 40 kWh/kg H₂, 70% efficiency, 2000 $/kW (DOE 2024, 2022 USD),
  0.5 capacity factor (Korean PV).

## S5. CCS detail

- Sequestered mass `co2_seq = co2_left(623CO2)·ccs_portion + co2_EGR(622X)`; 622X captured
  at 100%, 623CO2 at `ccs_portion`.
- Capture OPEX: `Fuel = max(heat − plant heat_gen, 0)·14.38·8000`;
  `Electricity = elec·19.05·8000`; `T&S = co2_seq/2204.62·8000·co2_ts_usd_per_ton`.
- CO₂ T&S price: default 0 (off) in base runs; literature range 4–45 $/t; manuscript basis
  10 $/t (`tea_tornado.py`, `tea_pareto_front.py`). T&S adder verified linear in price
  (`test_co2_ts.py`, `tea_scale_up_co2ts.py`).
- ccs_portion sweeps: {0, 0.25, 0.5, 0.75, 1.0} (`tea_ccs.py`); 0–0.9 in 0.1 steps
  (`tea_co2_portion.py`); scale-up scenario fixed at 0.60.
- **Open caveat (from `_Base_Revision.md`).** The Rao & Rubin base case implies a specific
  reboiler duty of ~8.9 GJ/t CO₂ (3315 MMBtu/hr ÷ 862,853 lb/hr), roughly 2× the
  conventional 30 wt% MEA benchmark of 3.5–4.2 GJ/t. The absolute duty and base CO₂ stream
  are not traceable to the ES&T 2002 letter's own tables. Flagged for correction; not yet
  resolved.

## S6. Dynamic LCA (Bern model)

Used only for the dynamic-GWP illustration (`Dynamic_LCA/`), not the headline intensities.

- Bern impulse-response function (Levasseur 2010; IPCC 2007, 378 ppm background):
  `a0=0.217, a1=0.259, a2=0.338, a3=0.186`; `τ1=172.9, τ2=18.51, τ3=1.186 yr`;
  `τ_CH4=12 yr`, `τ_N2O=114 yr`.
- Radiative efficiencies: CO₂ 1.759e-15, CH₄ 7.54e-14, N₂O 3.7e-13.
- Time-varying characterization factor `dGWP_density_X(t) = aGWP_X(T−t)/aGWP_X(T)`.
- Sequestration entered as negative flux over its duration; net trajectory = emission +
  sequestration (+ construction). CCS trajectory in the green-CCS illustration uses a
  10-yr capture window. Sequestration profile data: `Dynamic_LCA/Sequestration_Traj/`
  (Lan 2021).

## S7. LCA inventories, allocation, and SAF criterion

- Numeric LCA results are read from GREET-derived Excel workbooks
  (`Process_Data/WTWa_LCA.xlsx`, `Process_Data/Pyrolysis_551_LCA_<method>.xlsx`); the
  Python only orchestrates, thresholds, averages, and plots. The energy/mass/market
  allocation basis itself is implemented inside GREET/the workbooks, one sheet per method.
- Four LCA method variants computed: Allocation, Displacement, Allocation_KRmix,
  Displacement_KRmix (U.S. vs Korea grid mix). Reported central value = Allocation; spread
  = (Allocation, Displacement) range, per config.
- WTWa = WTP + PTWa; PTWa (combustion) for every pyrolysis case taken from the FT-jet
  reference. `wBio` toggle selects the with-/without-biogenic combustion sheet
  (`WTWa_ftjet` vs `WTWa_ftjet_woBio`), driven by the `woBiogenic` case name.
- SAF threshold = 0.9 × conventional-jet WTWa GHG-100 (CORSIA −10%); conventional baseline
  read from the `WTWa_conventional` sheet, not hardcoded. The SAF-comparison figure draws a
  75.9 g CO₂e/MJ CORSIA line; its scatter points are flagged in code as visualization
  dummies.
- 60% CCS intensity is a linear interpolation between the simulated CCS-50% and CCS-75%
  WTWa points (`lca_ccs.py`); base and full-ammonia intensities are read directly.
- Abatement-cost energy density E = 31.66 MJ/L SAF.

## S8. Supply-availability context

Domestic feedstock ceilings used to convert plant scale to a share of aviation-fuel demand
(`tea_scale_up_price_models.py`): forest residue 3,127,378 t/yr; log (2,843,071 + 3,274,200)
t/yr. Critical scale multiples where each supply tier is exhausted: forest residue ≈8.6×,
forest residue + log ≈18.5×.

## S9. Data tables for the Results figures

Numeric values behind the main-text Results figures, read from the `Result/` workbooks. MJSP in \$/L SAF (1Q-2022 USD); GHG in g CO₂e/MJ (WTWa GHG-100, Allocation, Korea grid mix).

**Table S9-1. Base-case (grey H₂, flat forest-residue price) MJSP breakdown vs SAF production** (§3.1, base-case breakdown figure; source: `Result/scale_up_base_summary.xlsx`). Components in \$/L SAF; MJSP = sum of components.

| SAF production [MMt/yr] | Capital investment | Raw materials | Utilities | Operating labor | Maintenance | Operating charges | Plant overhead | G&A | Co-product sales | MJSP |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.041 | 1.152 | 1.284 | 0.664 | 0.036 | 0.110 | 0.009 | 0.073 | 0.172 | -1.860 | 1.638 |
| 0.104 | 0.936 | 1.269 | 0.590 | 0.014 | 0.093 | 0.004 | 0.054 | 0.160 | -1.860 | 1.258 |
| 0.207 | 0.857 | 1.263 | 0.467 | 0.007 | 0.086 | 0.002 | 0.046 | 0.147 | -1.860 | 1.015 |
| 0.311 | 0.801 | 1.262 | 0.406 | 0.005 | 0.083 | 0.001 | 0.044 | 0.142 | -1.860 | 0.884 |
| 0.414 | 0.750 | 1.261 | 0.368 | 0.004 | 0.078 | 0.001 | 0.041 | 0.138 | -1.860 | 0.780 |
| 0.828 | 0.719 | 1.260 | 0.327 | 0.003 | 0.077 | 0.001 | 0.040 | 0.134 | -1.860 | 0.701 |
| 1.243 | 0.700 | 1.259 | 0.311 | 0.002 | 0.079 | 0.000 | 0.040 | 0.133 | -1.860 | 0.664 |

**Table S9-2. Biomass price and grey-H₂ base MJSP under three biomass price models** (§3.1, price-model figure; source: `Result/scale_up_price_model_mjsp.xlsx`). MJSP in \$/L SAF.

| SAF production [MMt/yr] | Biomass, FR Price [\$/lb] | Biomass, FR-Log Linear [\$/lb] | Biomass, Fixed Elasticity [\$/lb] | MJSP grey H₂, FR Price | MJSP grey H₂, FR-Log Linear | MJSP grey H₂, Fixed Elasticity |
|---|---:|---:|---:|---:|---:|---:|
| 0.041 | 0.0486 | 0.0486 | 0.0486 | 1.638 | 1.638 | 1.638 |
| 0.104 | 0.0486 | 0.0486 | 0.0486 | 1.258 | 1.258 | 1.258 |
| 0.207 | 0.0486 | 0.0486 | 0.0486 | 1.015 | 1.015 | 1.015 |
| 0.311 | 0.0486 | 0.0486 | 0.0486 | 0.884 | 0.884 | 0.884 |
| 0.414 | 0.0486 | 0.0527 | 0.0527 | 0.780 | 0.836 | 0.836 |
| 0.828 | 0.0486 | 0.0903 | 0.1064 | 0.701 | 1.278 | 1.502 |
| 1.243 | 0.0486 | 0.1278 | 0.2360 | 0.664 | 1.761 | 3.259 |

**Table S9-3. MJSP of the full green-NH₃ and full-CCS configurations under three biomass price models** (§3.1, price-model figure; source: `Result/scale_up_price_model_mjsp.xlsx`, sheets `MJSP Ammonia` = 100% green-NH₃ hydrogen, `MJSP CCS` = CCS portion 1.0). MJSP in \$/L SAF.

| SAF production [MMt/yr] | MJSP full green NH₃, FR Price | MJSP full green NH₃, FR-Log Linear | MJSP full green NH₃, Fixed Elasticity | MJSP full CCS, FR Price | MJSP full CCS, FR-Log Linear | MJSP full CCS, Fixed Elasticity |
|---|---:|---:|---:|---:|---:|---:|
| 0.041 | 3.483 | 3.483 | 3.483 | 2.207 | 2.207 | 2.207 |
| 0.104 | 3.049 | 3.049 | 3.049 | 1.785 | 1.785 | 1.785 |
| 0.207 | 2.789 | 2.789 | 2.789 | 1.519 | 1.519 | 1.519 |
| 0.311 | 2.649 | 2.649 | 2.649 | 1.377 | 1.377 | 1.377 |
| 0.414 | 2.531 | 2.587 | 2.587 | 1.266 | 1.322 | 1.322 |
| 0.828 | 2.431 | 3.007 | 3.231 | 1.174 | 1.751 | 1.975 |
| 1.243 | 2.389 | 3.486 | 4.984 | 1.131 | 2.228 | 3.726 |

**Table S9-4. MJSP, GHG, Pareto status, sensitivity band, and abatement cost of the 30 green-NH₃ share × CCS portion configurations at 0.414 MMt/yr SAF** (§3.2, Figure Xa; sources: `Result/pareto_front.xlsx`, `Result/pareto_front_sensitivity.xlsx`). MJSP low/high = tornado-driver band (§2.2.4), computed for Pareto points only (§3.3). Abatement cost = ΔMJSP·10⁶/(ΔGHG·E), E = 31.66 MJ/L, relative to CCS 60% (75.14 g CO₂e/MJ, \$0.977/L); – where GHG is not below CCS 60%.

| Green NH₃ share [%] | CCS portion [%] | MJSP [\$/L] | GHG [g CO₂e/MJ] | Pareto | MJSP low [\$/L] | MJSP high [\$/L] | Abatement cost [\$/t CO₂] |
|---|---:|---:|---:|---:|---:|---:|---:|
| 0 | 0 | 0.792 | 100.83 | yes | 0.546 | 1.841 | – |
| 0 | 25 | 0.855 | 89.93 | yes | 0.608 | 1.903 | – |
| 0 | 50 | 0.913 | 78.99 | yes | 0.666 | 1.962 | – |
| 0 | 75 | 1.111 | 69.36 | yes | 0.864 | 2.160 | 733 |
| 0 | 100 | 1.334 | 59.96 | yes | 1.087 | 2.382 | 742 |
| 10 | 0 | 0.977 | 97.02 | no | – | – | – |
| 10 | 25 | 1.039 | 86.12 | no | – | – | – |
| 10 | 50 | 1.098 | 75.18 | yes | 0.851 | 2.042 | – |
| 10 | 75 | 1.296 | 65.55 | yes | 1.049 | 2.240 | 1,049 |
| 10 | 100 | 1.518 | 56.15 | yes | 1.271 | 2.462 | 900 |
| 25 | 0 | 1.240 | 91.31 | no | – | – | – |
| 25 | 25 | 1.302 | 80.40 | no | – | – | – |
| 25 | 50 | 1.361 | 69.46 | no | – | – | 2,138 |
| 25 | 75 | 1.559 | 59.83 | no | – | – | 1,201 |
| 25 | 100 | 1.782 | 50.44 | yes | 1.489 | 2.568 | 1,029 |
| 50 | 0 | 1.680 | 81.78 | no | – | – | – |
| 50 | 25 | 1.742 | 70.88 | no | – | – | 5,671 |
| 50 | 50 | 1.800 | 59.94 | no | – | – | 1,711 |
| 50 | 75 | 1.998 | 50.31 | yes | 1.413 | 2.584 | 1,299 |
| 50 | 100 | 2.221 | 40.91 | yes | 1.635 | 2.806 | 1,148 |
| 75 | 0 | 2.116 | 72.26 | no | – | – | 12,511 |
| 75 | 25 | 2.178 | 61.35 | no | – | – | 2,752 |
| 75 | 50 | 2.236 | 50.41 | no | – | – | 1,609 |
| 75 | 75 | 2.434 | 40.78 | yes | 1.556 | 3.313 | 1,340 |
| 75 | 100 | 2.657 | 31.39 | yes | 1.779 | 3.535 | 1,213 |
| 100 | 0 | 2.544 | 62.74 | no | – | – | 3,991 |
| 100 | 25 | 2.606 | 51.83 | no | – | – | 2,207 |
| 100 | 50 | 2.665 | 40.89 | no | – | – | 1,556 |
| 100 | 75 | 2.862 | 31.26 | yes | 1.691 | 4.034 | 1,357 |
| 100 | 100 | 3.085 | 21.86 | yes | 1.914 | 4.256 | 1,250 |

**Table S9-5. Grey-H₂ price at which Green NH₃ 10% + CCS 50% matches CCS 60%** (§3.3, Figure Xb; source: `plot_ammonia_crossover.py`). Both routes are linear in grey-H₂ price h [\$/kg]: CCS 60% = 0.977 + 0.419·(h − 1.50) \$/L; Green NH₃ 10% + CCS 50% = 1.098 + 0.378·(h − 1.50) + 0.2038·(p_NH₃/635 − 1) \$/L. Slopes are the one-at-a-time grey-H₂ spans (Table S9-7) divided by the 3 \$/kg range width.

| Green NH₃ price [\$/t] | Crossover grey-H₂ price [\$/kg] | MJSP at crossover [\$/L] | Inside 1–4 \$/kg range |
|---|---:|---:|---:|
| 270 | 1.59 | 1.016 | yes |
| 441 | 2.91 | 1.568 | yes |
| 635 (base) | 4.40 | 2.195 | no |
| 1,000 | 7.21 | 3.373 | no |

**Table S9-6. Mean |SHAP| of MJSP drivers at the two cheapest compliant points** (§3.3, Figure Xc, d; source: `Result/shap_ccs60_vs_nh10ccs50.xlsx`). \$/L SAF; 128 Latin-hypercube TEA runs per point, gradient-boosted surrogate (R² > 0.999); – = driver not sampled.

| Driver | CCS 60% | Green NH₃ 10% + CCS 50% |
|---|---:|---:|
| Grey H₂ | 0.310 | 0.274 |
| CAPEX | 0.103 | 0.102 |
| Co-product | 0.097 | 0.083 |
| Electricity | 0.052 | 0.055 |
| Green NH₃ | – | 0.031 |
| CO₂ T&S | 0.025 | 0.023 |
| Capacity | 0.019 | 0.028 |
| Biomass | 0.003 | 0.002 |

**Table S9-7. One-at-a-time MJSP spans at the two cheapest compliant points** (§3.3; source: `Result/tornado_shap_ccs60_vs_nh10ccs50.xlsx`). \$/L SAF; input ranges as in §2.2.4.

| Point | Driver | Base MJSP | MJSP at low input | MJSP at high input | Span |
|---|---|---:|---:|---:|---:|
| CCS 60% | Grey H₂ | 0.977 | 0.767 | 2.026 | 1.258 |
| CCS 60% | Co-product | 0.977 | 1.224 | 0.730 | 0.494 |
| CCS 60% | CAPEX | 0.977 | 0.741 | 1.213 | 0.472 |
| CCS 60% | Electricity | 0.977 | 1.134 | 0.820 | 0.313 |
| CCS 60% | Capacity | 0.977 | 1.174 | 0.987 | 0.188 |
| CCS 60% | CO₂ T&S | 0.977 | 0.950 | 1.137 | 0.187 |
| CCS 60% | Biomass | 0.977 | 0.977 | 1.029 | 0.052 |
| Green NH₃ 10% + CCS 50% | Grey H₂ | 1.098 | 0.909 | 2.042 | 1.133 |
| Green NH₃ 10% + CCS 50% | Co-product | 1.098 | 1.344 | 0.851 | 0.494 |
| Green NH₃ 10% + CCS 50% | CAPEX | 1.098 | 0.858 | 1.337 | 0.480 |
| Green NH₃ 10% + CCS 50% | Electricity | 1.098 | 1.258 | 0.937 | 0.321 |
| Green NH₃ 10% + CCS 50% | Green NH₃ | 1.098 | 0.980 | 1.215 | 0.234 |
| Green NH₃ 10% + CCS 50% | Capacity | 1.098 | 1.313 | 1.108 | 0.205 |
| Green NH₃ 10% + CCS 50% | CO₂ T&S | 1.098 | 1.073 | 1.238 | 0.165 |
| Green NH₃ 10% + CCS 50% | Biomass | 1.098 | 1.098 | 1.149 | 0.052 |
