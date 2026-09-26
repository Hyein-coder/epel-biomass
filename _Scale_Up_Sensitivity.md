# Scale-Up Sensitivity — Grey-H2, Full-Ammonia, CCS

## 1. Scale Effect: Grey-H2 / Full-Ammonia / CCS

**Question.** Does scaling the plant make the grey-hydrogen (Base) or the CCS
configuration more cost-effective?

**Setup.** 551 data, FR Price folder (`Process_Data`, **fixed** biomass price
0.0486 $/lb — so the sweep isolates pure economies of scale, no feedstock-price
confounding). Full-ammonia case = all grey H2 replaced by ammonia-cracked H2
(`ammonia_portion=None`, `'Ammonia'` entry — not the 65.5 % Mix). CCS = 60 %
capture on the grey-H2 base. Engine: `TEA.economic_analysis` (`funs.py:789`).

| Scale (×) | SAF [kt/yr] | Base MJSP | Ammonia MJSP | CCS MJSP | Base CAPEX [M$] | CCS-unit CAPEX [M$] |
|----------:|------------:|----------:|-------------:|---------:|----------------:|--------------------:|
| 1         | 45.7        | 1.582     | 3.426        | 1.743    | 429             | 24.7                |
| 2.5       | 114.1       | 1.231     | 3.022        | 1.392    | 888             | 61.7                |
| 5         | 228.3       | 1.004     | 2.778        | 1.165    | 1 654           | 123.5               |
| 7.5       | 342.4       | 0.881     | 2.645        | 1.041    | 2 338           | 185.2               |
| 10        | 456.6       | 0.781     | 2.532        | 0.941    | 2 936           | 246.9               |
| 20        | 913.1       | 0.711     | 2.441        | 0.872    | 5 706           | 493.9               |
| 30        | 1 369.7     | 0.678     | 2.403        | 0.839    | 8 378           | 740.8               |

MJSP in $/L SAF. Full table + per-unit CAPEX + per-raw-material OPEX in
`Result/ScaleUp_Sensitivity_table.xlsx`.

**Findings.**

1. **Whole-plant scale-up is very effective, but only up to ~10×.** Base MJSP
   falls 1.582 → 0.678 $/L (−57 %) over 1→30×, but 1.582 → 0.781 (−51 %) is
   already reached by 10×. Past that the curve flattens: the gain from 10→30× is
   just −0.10 $/L. Driver is CAPEX dilution.

2. **Grey-H2 Base plateaus at a variable-cost floor.** At scale 10 the dominant
   OPEX lines are Hydrogen gas 357.6 M$ ≈ Biomass 355.6 M$ (Electricity 203.3 M$),
   all linear in throughput. Scale cannot dilute them, so Base asymptotes toward
   ~0.68 $/L. Buying grey H2 caps how far scale-up can go.

3. **CCS does NOT get cheaper with scale — the penalty is scale-invariant.** The
   CCS-unit CAPEX is *exactly linear* in scale (24.69 M$ × n), giving a **flat
   +0.161 $/L** CCS premium over Base at every scale (1× through 30×, identical to
   4 decimals). CCS total MJSP falls only because it rides the Base curve down;
   scaling the plant does nothing to reduce the marginal cost of capture. The
   capture-cost model (Rao 2022 interpolation, `calc_cost_CCS`) is proportional to
   captured CO2, which is proportional to plant size — hence no economy of scale on
   the capture step itself.

4. **Full ammonia is not competitive at these prices.** MJSP 3.43 → 2.40 $/L; a
   +1.72–1.84 $/L premium over Base that barely shrinks with scale. Ammonia-cracked
   H2 cost dominates; scale-up does not close the gap.

**Answer.** Scaling up is worth it for the plant as a whole (target the ~10×
knee), and it lowers the *absolute* MJSP of both the grey-H2 and CCS cases. But it
does **not** improve the *relative* economics of either add-on: grey H2 sets a
hard variable-cost floor, and the CCS penalty is a fixed +0.16 $/L independent of
scale. So "scale to make CCS cheaper" does not hold under the current linear
capture-cost model — CCS is cheaper only in absolute terms, never relative to
base. (This corrects the initial a-priori expectation that CCS, being
capital-heavy, would benefit disproportionately from scale.)

**Validation.** Sub-unit CAPEX (Main/CCS/PSA/Catalysts/R-510) reconciles to case
total CAPEX at every scale (hard assert passed); per-raw-material + utility OPEX
recorded per case in the workbook for line-by-line audit.

## 2. Cross-Check Against Manuscript

Source: `Downloads/Biomass_LCA_ACS (2).pdf` (newest; no "(3)" exists). Same TEA
engine + 551 data as the manuscript, so base-scale numbers reproduce to 3 digits.

**Base scale (×1 = 1 % coverage):**

| Quantity | Manuscript | This run | Source |
|---|--:|--:|---|
| Base MJSP [$/L] | 1.58 | 1.582 | Table 9 / Fig 7 (0 %) |
| Base total CAPEX [M$] | 428.7 | 428.7 | Table 9 |
| Ammonia (full) MJSP | 3.43 | 3.426 | Table 9 |
| Ammonia (full) CAPEX [M$] | 501.3 | 501.3 | Table 9 |
| CCS 60 % MJSP | 1.74–1.75 | 1.743 | Fig 7 (60 %) / abstract |
| CCS 60 % premium over Base | 0.16 | 0.161 | Fig 7 |

Table 7 raw-material prices also match the run inputs (FR biomass 0.0487, grey H2
0.68, ammonia 0.288 $/lb, electricity 0.065 $/kWh).

**Two manuscript facts to keep straight (labeling / axis, not number gaps):**

1. **CCS is nonlinear in *capture portion*** (Fig 7): premium 0/25/50/75/100 % =
   0.05 / 0.10 / 0.29 / 0.51 $/L, kink at ~54 %. Reason (p26): process waste heat
   (254.5 MMBtu/hr) covers 53.8 % of off-gas CO2 capture *for free*; beyond that,
   purchased energy drives cost up. The "flat +0.161 $/L" in §1 is the premium vs
   **scale at fixed 60 % portion** — a different axis. Both hold: at fixed portion,
   waste heat and CO2 scale together, so the 60 % premium is scale-invariant. The
   $0.51/L incremental figure in the manuscript is the **100 %** capture premium.

2. **Manuscript Fig 8 (scalability) "Ammonia" line = the 65.5 % Mix (base 2.82),
   NOT full ammonia (3.43).** The scalability configs are (i) ammonia cracking with
   34.5 % grey H2 = Mix, (ii) 60 % CCS. §1's Ammonia column here is the **full**
   ammonia (Table 9 basis, 3.43) per the session's stated choice. So §1 Base + CCS
   scale lines correspond to Fig 8; the §1 Ammonia line does not (it is Table 9's
   full case). A Fig-8 match would require rerunning the Mix.

**Scale trend (constant feedstock, FR Price):** manuscript — economies of scale
"halve production cost", ~$0.92/L at 10 % coverage. This run — Base 1.58→0.78
(10 %)→0.68 (30 %, −57 %); CCS 1.74→0.94→0.84. Manuscript $0.92 ≈ CCS@10 % (0.94).
Consistent.

**Verdict.** The scale run reproduces the manuscript. All differences are labeling
(Fig 8 Ammonia = Mix) or axis (portion-nonlinearity vs scale-invariance), not
numeric disagreement.

## 3. Ammonia CO2 Abatement Cost and Sweet Spot

**Question.** Cost of reducing 1 ton CO2 via the ammonia route, and the mix-ratio
sweet spot. Base scale (1 % coverage), via `H2Mix` (`funs_lca.py`) = the paper's
551 TEA+LCA coupling. SAF energy density E = **31.66 MJ/L** (process basis).
Conversion: $/t CO2 = ΔMJSP[$/L] · 1e6 / (ΔGHG[g/MJ] · E). ΔMJSP anchored to the
paper's reported MJSP (Base 1.58, Mix-65.5 % 2.82, full Ammonia 3.43); `H2Mix`
reproduces the ammonia line (2.820 @ 0.655, 3.426 @ 1.0) but its p=0 endpoint is a
1.67 code-path artifact, so Base is taken as the paper's 1.58.

**WTWa GHG-100 [g CO2e/MJ SAF] (base scale):**

| LCA method | Base (grey) | Full ammonia |
|---|--:|--:|
| Allocation (US) | 87.57 | 49.45 |
| Displacement (US) | 123.03 | 2.27 |
| Allocation (KR mix) | 100.83 | 62.74 |
| Displacement (KR mix) | 124.63 | 3.83 |
| Mean | 109.02 | 29.57 |

CORSIA threshold = 0.9 × conventional = **75.93 g CO2e/MJ**.

**Abatement cost — $/t CO2 (ammonia vs grey base).** Both MJSP and GHG are linear
in ammonia fraction, so $/t is **constant along the mix** (not a curve with a
minimum):

| Method | $/t CO2 |
|---|--:|
| Allocation (US) | ~1 530 |
| Allocation (KR) | ~1 530 |
| Displacement (US) | ~484 |
| Displacement (KR) | ~484 |
| Mean | ~735 |

Method dominates: displacement credits the ammonium-sulfate fertilizer co-product
(ammonia WTWa → near zero), roughly **3× cheaper** abatement than allocation.

**Sweet spot = min ammonia fraction meeting the threshold** (max cheap grey H2
while compliant). Because $/t is flat, the optimum is compliance, not a cost
minimum — any extra ammonia beyond the threshold is over-abatement you pay for and
do not need.

| Method | grey fraction allowed | ammonia needed |
|---|--:|--:|
| Allocation (US) | 69.5 % | 30.5 % |
| Displacement (US) | 61.0 % | 39.0 % |
| **Allocation (KR)** | **34.6 %** | **65.4 %** |
| Displacement (KR) | 59.7 % | 40.3 % |

**Binding case = Korea allocation → 34.6 % grey, i.e. the manuscript's 34.5 % grey
mix.** So the paper's mix ratio is set by the strictest LCA method (KR allocation);
under US allocation only ~30 % ammonia would be required.

**Answer.** Reducing CO2 through ammonia costs ~735 $/t on average (~1 530 under
allocation, ~484 under displacement). The sweet spot is the minimum ammonia that
clears CORSIA — 65.4 % ammonia (34.6 % grey), governed by KR allocation — matching
the manuscript.

### 3b. CCS abatement cost (comparison lever)

CCS WTWa emissions per capture portion exist in `Pyrolysis_551_LCA_Allocation.xlsx`
/ `_Displacement.xlsx` (sheets `CCS025/050/075/100`) — the earlier "cannot compute"
was wrong (the `tea_co2_portion.py:30` `데이터가 없음` TODO is stale). Base-scale
MJSP matches Fig 7 exactly (0/25/50/60/75/100 % = 1.582 / 1.632 / 1.682 / 1.743 /
1.873 / 2.090 $/L). Same E = 31.66 MJ/L.

| Capture | GHG alloc | $/t alloc | GHG disp | $/t disp |
|--:|--:|--:|--:|--:|
| 0 % | 87.57 | — | 123.03 | — |
| 25 % | 76.01 | 136 | 86.44 | 43 |
| 50 % | 64.44 | 136 | 49.76 | 43 |
| 75 % | 54.17 | 275 | 17.23 | 87 |
| 100 % | 44.15 | 369 | −14.57 | 117 |

**CCS is ~4–11× cheaper per ton than ammonia** (136–369 vs ~1530 allocation;
43–117 vs ~484 displacement). Marginal CCS cost is flat and cheap ≤50 % capture
(process waste heat covers the reboiler), then jumps past the ~54 % waste-heat
threshold — the same kink as Fig 7. Displacement 100 % = −14.6 g/MJ is net-negative
(BECCS: captured biogenic CO2 credited as removal).

**Sweet spot / CORSIA compliance:** under US allocation ~25 % capture already meets
the 75.93 threshold (GHG 76.01); the manuscript's "60 % capture" is the **Korea
allocation** binding case — the same strictest-method logic that fixes ammonia's
34.5 % grey. So both levers' design points are set by KR allocation.

**Lever verdict.** For meeting CORSIA at least cost, **CCS dominates ammonia on
$/t CO2**. Ammonia's value is as a low-carbon H2 pathway (and deeper cuts /
net-negative via displacement), not as the cheapest abatement.

### 3c. Abatement cost vs production scale

GHG intensity [g/MJ] is scale-independent (same LCA per MJ SAF); only MJSP moves
with scale. So $/t = ΔMJSP(scale) · 1e6 / (ΔGHG · E), ΔGHG and E fixed. ΔMJSP per
scale from `ScaleUp_Sensitivity_table.xlsx` (full ammonia, CCS 60 %). ΔGHG: NH3
38.12 (alloc) / 120.76 (disp); CCS-60 % 26.05 / 82.56 (linear-interp of CCS sheets).

| Scale × | NH3 alloc | NH3 disp | CCS alloc | CCS disp |
|--:|--:|--:|--:|--:|
| 1 | 1528 | 482 | 195 | 62 |
| 2.5 | 1484 | 469 | 195 | 62 |
| 5 | 1470 | 464 | 195 | 62 |
| 7.5 | 1462 | 462 | 195 | 62 |
| 10 | 1451 | 458 | 195 | 62 |
| 20 | 1433 | 452 | 195 | 62 |
| 30 | 1429 | 451 | 195 | 62 |

- **CCS: flat across scale** (195 / 62 $/t). CCS MJSP premium is scale-invariant
  (§1) and GHG intensity is fixed, so abatement $/t does not move.
- **Ammonia: weakly decreasing** (1528 → 1429 alloc, −6.5 % over 1→30×) — H2-subunit
  economies of scale trim the premium slightly.
- **Scale does not change the ranking:** CCS is ~7–23× cheaper per ton at every
  scale. Neither lever's cost-effectiveness is materially unlocked by scaling.

> **CAVEAT (2026-09-26): the flat CCS-vs-scale behavior above is a BUG artifact.**
> `unit_cost_interpolation` (`funs.py:157`) branches on the dict *value* `v`
> (`if not isinstance(v, str) ... elif 'CAPEX' in v`) instead of the *key* `k`.
> All cost values are numbers, so the six-tenths (`r_scale**0.6`) and OPEX-0.7
> branches never run — every sub-unit cost (CCS, PSA, R-510) scales strictly
> linearly. Fixing it (`'CAPEX' in k` / `'OPEX' in k`) makes CCS CAPEX ~3× higher at
> base scale (~24.7→~68 M$) and −31 % at scale 30 (~741→~512 M$): the base-scale CCS
> MJSP would exceed the manuscript's 1.74, and the premium would *shrink* with scale.
> §1/§3c CCS scale conclusions hold only under the (buggy) linear model the
> manuscript used. Fix pending user decision — it rewrites all CCS results.

## Log history

### 2026-09-26

**Discussion**
- Correction to 2026-09-25 "cannot compute CCS abatement". The CCS-portion WTWa
  emissions **do exist** — `Pyrolysis_551_LCA_Allocation.xlsx` /
  `_Displacement.xlsx` carry sheets `CCS025/050/075/100`. The `데이터가 없음`
  ("no data") TODO in `tea_co2_portion.py:30` is stale. User flagged that the CCS
  results already existed; correct.
- Result: **CCS abatement is ~4–11× cheaper per ton than ammonia** (§3b). CCS
  136–369 $/t (allocation) / 43–117 (displacement) vs ammonia ~1530 / ~484.
- Both design points (ammonia 34.5 % grey, CCS 60 % capture) are set by the
  **Korea-allocation** binding case; under US allocation CCS needs only ~25 %.
- The `CO2_ver551_0##.xlsx` files store only the cost breakdown (scale 30), not
  emissions — emissions come from the LCA sheets, not those files.
- Abatement $/t vs scale (§3c): CCS flat (195/62), ammonia weakly falling
  (1528→1429 alloc). Scale does not change the CCS-over-ammonia ranking. GHG
  intensity held scale-independent per the user's instruction (same LCA per MJ).
- **BUG found (user prompted "is it really linear?"):** `unit_cost_interpolation`
  (`funs.py:157`) tests the dict *value* not the *key*, so the six-tenths CAPEX rule
  and 0.7 OPEX rule are dead code — CCS/PSA/R-510 sub-units scale linearly. This is
  the root cause of the "flat CCS premium" (§1) and "flat CCS abatement" (§3c). Patch
  = branch on `k` (`'CAPEX' in k` / `'OPEX' in k`). Consequential: base-scale CCS
  CAPEX ~24.7→~68 M$ (base MJSP would break the 1.74 manuscript match), scale-30
  741→512 M$ (premium then shrinks with scale). Manuscript CCS numbers were all
  generated under the linear bug. NOT applied — awaiting user decision.

**Code**
- No production code changed. Bug identified in `funs.py:157`
  (`unit_cost_interpolation`); patch proposed, not applied (rewrites manuscript CCS
  results).
- `scratchpad/abatement.py`: CCS branch computes MJSP via
  `economic_analysis(ccs_portion=p)` (base scale) and GHG via
  `get_WTWa_pyrolysis('CCS0pp', ...)`; abatement = ΔMJSP·1e6/(ΔGHG·E).

**Open**
- KR-allocation CCS $/t not tabulated (only US alloc + disp); needed to state the
  KR binding number precisely rather than by inference.
- `tea_co2_portion.py` still reads `ghg_withCCS` from a hardcoded sheet with a
  stale TODO and interpolates linearly instead of reading `CCS025/050/075` directly
  — the script's in-memory GHG path is unreliable even though the sheet data exists.

### 2026-09-25

**Discussion**
- Session goal: quantify the scale effect on process economics for grey-H2 (Base),
  CCS, and full-ammonia H2, and judge whether scale-up is effective.
- A-priori guess (CCS benefits more from scale because it is capital-heavy) was
  **rejected by the data**: CCS-unit CAPEX is linear in scale, premium is flat.
  Kept here so it is not re-raised.
- Chose FR Price (fixed-price) data folder to isolate pure economies of scale;
  the 3-price-model sweep (`tea_scale_up_price_models.py`) was not needed for a
  numbers-only answer (dropped to avoid confounding MJSP with rising biomass price).
- Full ammonia = `'Ammonia'` source entry with `ammonia_portion=None`, NOT
  `ammonia_portion=0`. Verified in `funs.py:789-862`: `ammonia_portion` only
  spawns the separate 65.5 % `Mix` row; the `'Ammonia'` entry (from
  `name_h2_source[1:]` off `main_wo_h2`) is already full ammonia. The existing
  `tea_scale_up_price_models.py` mislabels its Mix as "Ammonia".
- Cross-checked the run against `Biomass_LCA_ACS (2).pdf` (§2). Base/full-Ammonia/
  CCS base-scale MJSP + CAPEX reproduce Table 9 / Fig 7 to 3 digits → engine and
  551 data are the manuscript's. Confirmed the manuscript's scalability "Ammonia"
  (Fig 8) is the 65.5 % Mix (base 2.82), whereas this run's Ammonia is the full
  case (Table 9, 3.43). The $0.51/L CCS figure in the manuscript is the 100 %-capture
  premium; CCS is nonlinear in capture *portion* (waste heat covers 53.8 % free)
  but scale-invariant at fixed 60 % portion.

- Reframed "ammonia sweet spot" as CO2 abatement cost ($/t CO2), §3. Retrieved
  WTWa GHG from the 551 LCA files via `H2Mix`; abatement $/t is flat along the mix
  (both MJSP and GHG linear in ammonia fraction), so the sweet spot is the
  compliance point, not a cost minimum. Confirmed the paper's 34.5 % grey mix is
  set by the KR-allocation constraint (the strictest method). Method choice swings
  abatement ~3× (allocation ~1530 vs displacement ~484 $/t) via the fertilizer
  co-product credit.

**Code**
- `scratchpad/abatement.py` (not committed): `H2Mix`-based; prints per-method WTWa
  GHG (Base/ammonia), MJSP endpoints, abatement $/t, and per-method sweet-spot
  ammonia fraction. E = 31.66 MJ/L from process (SAF MJ/hr ÷ L/hr).
- `scratchpad/scale_table.py` (not committed): runs the 7-scale sweep via
  `TEA.economic_analysis`, two calls per scale (Base+Ammonia, then CCS at
  `ccs_portion=0.6`). Emits summary MJSP/CAPEX/OPEX table + per-unit CAPEX +
  per-raw-material OPEX to `Result/ScaleUp_Sensitivity_table.xlsx`. Hard assert:
  sub-unit CAPEX sums to total; soft warn on MJSP ordering; assert Base CAPEX/ton
  monotonically decreasing. All passed, no warnings.

**Open**
- Result is conditional on the linear CCS cost model (`calc_cost_CCS`). If capture
  were modeled with a <1 scaling exponent, the flat-premium conclusion could
  change — not tested.
- Only FR Price (fixed feedstock) run. Under rising-with-scale biomass price models
  the Base plateau would turn upward at large scale; not quantified here.
- Fig-8 scale line for the **Mix** (65.5 %) case not reproduced — this run carries
  full ammonia instead. Rerun with `ammonia_portion=0.655` reading `index('Mix')`
  if a direct Fig-8 Ammonia-line match is needed.
- Manuscript text "$0.92/L at 10 %" vs this run's CCS@10 % = 0.94: 2 % gap,
  likely rounding / chart-read; not chased.
- **CCS abatement $/t not computed.** CCS captures mostly *biogenic* stack CO2
  (0.229 lb/MJ physical at 60 %), which under CORSIA becomes a net removal
  (net-negative at 100 %); the WTWa reduction is not the raw captured flow and needs
  the biogenic-carbon accounting from `lca_ccs.py`/Fig 6. Deferred to avoid a wrong
  $/t. Needed for the ammonia-vs-CCS lever comparison.
- Abatement uses E = 31.66 MJ/L (process volume basis); slightly below the ~34 MJ/L
  generic jet LHV — confirm the paper's SAF energy/volume basis before quoting $/t
  externally.
