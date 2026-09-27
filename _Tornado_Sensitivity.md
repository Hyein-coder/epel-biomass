# Tornado Sensitivity Analysis (Reviewer §4.7)

Addresses Critical Review §4.7 ("No sensitivity analysis"), reinforced by §4.5
(ammonia price range) and §8. One-at-a-time MJSP sensitivity over the reviewer's
seven parameters, on the 551 basis, for Base / Full-Ammonia / Full-CCS at scale
×1 and ×30. Driver: `tea_tornado.py` (reuses `funs.TEA`, no engine change).

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
| CO₂ T&S | 4–45 $/tCO₂ | Full-CCS | linear — seq. CO₂ (623CO2 + 622X) × price / SAF; base = 0 |

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
| Full-CCS | 2.21 | 1.13 |

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
- **CO₂ T&S (4–45 $/tCO₂, Full-CCS)** adds up to ~0.28 $/L (scale-invariant),
  below CAPEX and biomass — transport & storage price is not a dominant risk.

Conclusion: MJSP uncertainty is governed by the hydrogen source price (gray H₂ or
ammonia); at commercial scale, feedstock prices outweigh CAPEX. The Full-Ammonia
ranking is contingent on the assumed ammonia price.

## Log history

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
  Full-CCS; now included as a linear bar ($4–45/tCO₂, base 0).

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

**Open**
- Electricity bar does not re-price APEA-embedded main-plant electricity (fixed $);
  fertilizer co-product not covered by the co-product bar. Documented as scope, not
  yet quantified.
