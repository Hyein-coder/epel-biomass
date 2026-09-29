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
