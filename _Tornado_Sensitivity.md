# Tornado Sensitivity Analysis (Reviewer §4.7)

Addresses Critical Review §4.7 ("No sensitivity analysis"), reinforced by §4.5
(ammonia price range) and §8. One-at-a-time MJSP sensitivity over the reviewer's
seven parameters, on the 551 basis, for Base / Full-Ammonia / Full-CCS at scale
×1 and ×30. Driver: `tea_tornado.py` (reuses `funs.TEA`, no engine change).
CO₂ T&S in the CCS unit is costed at a **$10/tCO₂ basis** (Full-CCS); the T&S bar
sweeps 4–45 $/tCO₂ around it.

## 1. Method

Each bar perturbs one parameter to the reviewer's low/high end, holding the rest
at base, and records MJSP. Two mechanisms:

- **linear** — the input enters OPEX/CAPEX linearly, so MJSP is post-scaled from
  the single base run (exact; no re-run).
- **re-run** — a scalar knob is set on a fresh `TEA()` and `economic_analysis`
  recomputed (net or non-linear response).

| Parameter | Range | Configs | Mechanism (knob / line) |
|---|---|---|---|
| Biomass price | ±50% | all | linear — APEA `90BIO` cost (`get_biomass_info`) |
| Gray H₂ price | 1.0–4.0 $/kg | Base, CCS | linear — APEA H₂ raw-material cost (`hydrogen_feed_stream`) |
| Ammonia price | 0.1225–0.4535 $/lb | Full-Ammonia | linear — feed offset 2.038 $/L × (p/0.288 − 1) |
| Electricity | ±30% | all | re-run — `elec_price_usd_per_mmbtu` (+ `product_price_work['ELC-']`) |
| Co-product | ±20% | all | re-run — `product_price_stream` (316GAS, 336DIES) |
| CAPEX | ±30% | all | linear — `df_mjsp['capital investment']` |
| Capacity factor | 85% / 91% | all | re-run — `operation_hr` (0.85/0.91 × 8760) |
| CO₂ T&S | 4–45 $/tCO₂ | Full-CCS | re-run — `co2_ts_usd_per_ton`; **basis $10/tCO₂** in CCS |

Configs map to `economic_analysis` as: Base = `['Base'], ccs=0`; Full-Ammonia =
`['Base','Ammonia'], ccs=0` (Ammonia row); Full-CCS = `['Base'], ccs=1.0` (its
`capital investment` already carries CCS CAPEX).

Scope notes (assumptions):
- **Electricity ±30%** rescales the net electricity export revenue (ELC- work
  product) and CCS electricity only; the main-plant purchased-electricity cost
  embedded in the APEA utility sheet is a fixed $ and is not re-priced.
- **Co-product ±20%** covers the fuel co-products (gasoline, diesel); fertilizer
  co-product (Full-Ammonia, read from the NH₃ APEA) is not re-priced by this bar.
- **Capacity factor**: base is 8000 h = 91.3%; both reviewer endpoints (85%, 91%)
  are below base, so the bar is one-sided (fewer hours → higher MJSP), matching
  the §4.9 concern that 8000 h is optimistic.

## 2. Tornado results

Base MJSP ($/L SAF):

| Config | ×1 | ×30 |
|---|---|---|
| Base | 1.64 | 0.66 |
| Full-Ammonia | 3.48 | 2.39 |
| Full-CCS | 2.28 | 1.20 |

Ranked drivers (figure: `Figure/tornado.png`; table: `Figure/tornado_sensitivity.xlsx`):

- **Feedstock hydrogen dominates every case.** Gray H₂ price (1–4 $/kg) is the
  single largest driver for Base and Full-CCS (span ≈ 1.26 $/L, scale-independent);
  ammonia price (0.12–0.45 $/lb) dominates Full-Ammonia even more strongly (span
  ≈ 2.34 $/L), confirming §4.5 that the ammonia-price assumption drives the ranking.
- **CAPEX sensitivity collapses with scale.** CAPEX ±30% is the #2 driver at ×1
  (0.69–0.80 $/L) but drops to ~0.42–0.49 $/L at ×30 (six-tenths scaling), falling
  below biomass. Biomass ±50% is scale-robust (~0.62–0.65 $/L).
- **Electricity and capacity factor are minor** (spans ≤ 0.36 $/L), so the
  optimistic 8000 h assumption is not a material MJSP risk on its own.
- **CO₂ T&S** sits at a $10/tCO₂ basis (raising Full-CCS base MJSP by ~0.07 $/L
  vs. no T&S); sweeping 4–45 $/tCO₂ moves MJSP within ~0.28 $/L (scale-invariant),
  below CAPEX and biomass — transport & storage price is not a dominant risk.

Conclusion: MJSP uncertainty is governed by the hydrogen source price (gray H₂ or
ammonia); at commercial scale, feedstock prices outweigh CAPEX. The Full-Ammonia
ranking is contingent on the assumed ammonia price.

## Log history

### 2026-09-29

**Discussion**
- Log target for this and future sessions moved here (`_Tornado_Sensitivity.md`) from
  `_Pareto_Front.md`. Earlier 2026-09-29 SHAP work is logged there (updates 4–6); summarized
  below for future reference.

**SHAP summary (past work, source: `_Pareto_Front.md` updates 4–6)**
- Goal: MJSP driver attribution for the two ~25%-decarbonization frontier points —
  grey-H₂ + CCS 25% (a=0, c=0.25) vs Green NH₃ 25% (a=0.25, c=0), same §4.7 driver ranges
  and MJSP model as the tornado (`mix_row` engine re-run + linear cost terms).
- Method evolved across the session:
  1. Two-panel MJSP **tornado** comparison of the two points (`Figure/tornado_ccs25_vs_nh325.png`).
  2. **Exact KernelSHAP** on the TEA function, single instance per point (all-low → all-high
     corner, 2⁷ coalitions enumerated, contributions sum to the swing). Bar + scatter figures.
  3. Reviewer wanted >100 sampled points → switched to **Latin-hypercube (N=128/point) +
     gradient-boosted surrogate + TreeSHAP beeswarm** (`tea_pareto_shap.py`). 128 real TEA calls
     per point; SHAP exact on the surrogate, guarded by `assert R²>0.99` (TEA is near-additive).
- Key finding: **feedstock H₂ price dominates both routes.** Grey+CCS25 — Gray H₂ \$+1.26/L ≫
  CAPEX \$+0.48, Co-product \$−0.49; CO₂ T&S only \$+0.11 (minor lever). Green NH₃ 25% — H₂ bill
  splits Gray H₂ \$+0.94 + Ammonia \$+0.59, sitting on a higher MJSP floor (worst-case
  \$2.19/L vs \$1.87/L for CCS25). (Single-instance exact numbers; beeswarm means in
  `Result/shap_ccs25_vs_nh325.xlsx`.)
- Artifacts: `tea_pareto_shap.py`; `Figure/shap_beeswarm_ccs25_vs_nh325.png` (current);
  `Figure/shap_ccs25_vs_nh325.png` + `shap_scatter_ccs25_vs_nh325.png` (earlier exact bar/scatter,
  now superseded). Added deps: `shap`, and reuses `scipy.stats.qmc` + `sklearn`.

**Code**
- Beeswarm run completed: surrogate R²=0.9995 (CCS25) / 0.9993 (NH₃25). Importance (mean|SHAP|,
  \$/L): CCS25 — Gray H₂ 0.312 ≫ CAPEX 0.103, Co-product 0.095, Electricity 0.058, Capacity 0.020,
  CO₂ T&S 0.010, Biomass 0.004. NH₃25 — Gray H₂ 0.226, Ammonia 0.125, CAPEX 0.100, Co-product 0.093,
  Electricity 0.057, Capacity 0.026, Biomass 0.004. Mean SHAP ≈ 0 for all (symmetric ranges).
  Directionality sanity: high H₂ price (red) → +SHAP → raises MJSP.

**Code**
- Colorbar overlap fixed: root cause was `SA_RC`'s `figure.autolayout=True` fighting `fig.colorbar`;
  switched the beeswarm figure to `constrained_layout=True` (autolayout off for this fig) and moved
  panel titles bottom-left. Added an npz sample cache (`Result/shap_samples.npz`) so cosmetic replots
  skip the ~13-min resample (delete the npz to refresh).
- Beeswarm figsize reduced 14×6 → 9×4.5 (fonts too small at the larger size).

**Open**
- Colorbar overlapped the right-panel title text (cosmetic) — RESOLVED (see Code above). Subscript
  ₂/₃ still render as tofu boxes (SA_RC font). SHAP code changes uncommitted as of this entry.

### 2026-09-27

**Discussion**
- New session for the §4.7 sensitivity request. User chose: log to a **new** file
  (this one, not `_Base_Revision.md`/`_Scale_Up_Sensitivity.md`); cover **Base,
  Full-Ammonia, Full-CCS** at scale **×1 and ×30** (6 tornados).
- Configuration set to Base/Full-Ammonia/Full-CCS rather than the Mix case; the
  Mix option was offered (only case with both grey H₂ and ammonia) but not chosen.
- Optional CO₂ T&S bar on Full-CCS left out by default to match the reviewer's
  seven-item list.
- Update (same session): user then requested the CO₂ T&S bar be added to
  Full-CCS; first added as a $0-base bar ($4–45/tCO₂).
- Update (same session): user set a **$10/tCO₂ basis** for CO₂ T&S in the CCS
  unit. T&S now baked into the Full-CCS base run (via `co2_ts_usd_per_ton=10`);
  Full-CCS base MJSP 2.21→2.28 (×1), 1.13→1.20 (×30). Sensitivity report
  `_Scale_Up_Sensitivity.md` explicitly excludes T&S; `_Scale_Up_Subunits.md`
  numbers updated to the same $10/t basis.

**Code**
- `tea_tornado.py` — new driver; per (config, scale) computes base MJSP and the
  §4.7 bars (seven; Full-CCS also gets an eighth CO₂ T&S bar), writes
  `Figure/tornado.png` (3×2 grid, shared x-axis) and `Figure/tornado_sensitivity.xlsx`. Reuses `funs.TEA.economic_analysis`;
  ammonia-price constants copied from `tea_scale_up_abatement.py` (single source
  of truth). Linear bars derived from the base run; electricity/co-product/capacity
  re-run on a fresh `TEA()` with the knob set.
- Verified engine before wiring: `main_h2_demand` is lb/hr and H₂ cost is not
  returned, so the driver reads the APEA `RawMaterial Summary` directly (same query
  as `get_main_wo_h2`) to get the base gray-H₂ price; `product_price_work['ELC-']`
  is a copied float at `__init__`, so the electricity re-run sets it explicitly
  alongside `elec_price_usd_per_mmbtu`.
- Bug: console `UnicodeEncodeError` (cp949 can't encode `–`/`…`/`₂` in the printed
  labels). Cause: Windows default console codec. Fix: `sys.stdout.reconfigure(encoding='utf-8')`.
- Self-check (in `__main__`): base MJSP > 0, biomass/CAPEX bars straddle base, and
  capacity re-run moves MJSP — all pass.
- CO₂ T&S: `TS_BASE=10` set on the CCS base run and on every Full-CCS re-run
  (`rerun_knob` applies it before knobs); the T&S bar re-runs at 4/45 $/tCO₂.
  Engine `calc_cost_CCS` applies it on `co2_seq` — matches the abatement-script def.

**Open**
- Electricity bar does not re-price APEA-embedded main-plant electricity (fixed $);
  fertilizer co-product not covered by the co-product bar. Documented as scope, not
  yet quantified.
