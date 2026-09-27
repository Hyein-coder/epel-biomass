# Sub-Unit Scale Sensitivity — Ammonia Cracker Size vs Main Unit

## 1. Goal & Setup

**Question.** Fix the main pyrolysis-SAF unit at its largest studied size (×30) and
vary **only the ammonia cracker** from ×1 to ×30. How does the CO2 abatement cost
change, and what are the absolute MJSP and CO2-emission levels?

**Why this cut.** Earlier scale work (`_Scale_Up_Sensitivity.md`) scaled the *whole*
plant (main + cracker together). This isolates the cracker: does a small cracker
bolted onto a big plant abate CO2 as cheaply as a full-size one, or does it pay a
size penalty?

**How "cracker ×k" maps to the model.** The cracker is sized by the H2 flow it must
supply. A ×1 cracker supplies 6570.4 lb H2/hr (the ×1 plant's full demand); the ×30
main unit demands ~30× that. So a cracker of size ×k inside the ×30 plant supplies a
fraction **f = k/30** of the plant's H2; grey H2 covers the remaining 1−f. This is
exactly `H2Mix(30).mjsp_with_ammonia(f)` with `f = k/30` — the engine reads the
cracker CAPEX from `NH3_Cracking_130_scale{k}0_APEAresult.xlsx` (piecewise-linear
over the ×1/2.5/5/7.5/10/20/30 APEA files), not the six-tenths rule.

**Assumptions.**
- 551 feedstock files (`Pyrolysis_551_Scale0300`), the manuscript/report basis.
- Main unit fixed ×30; SAF = 1.705 G L/yr, 53.98 PJ/yr; grey-H2 base MJSP 0.664 $/L.
- Cracker sizes = the ammonia APEA data points **×{1, 2.5, 5, 7.5, 10, 20, 30}** (no
  interpolation error).
- H2 supplied by cracker = green ammonia at base price 0.288 $/lb; remainder = grey H2.
  No CCS.
- WTWa GHG is **scale-independent** and linear in ammonia fraction (`ghg_with_ammonia`),
  read from the four `Pyrolysis_551_LCA_*` files. Abatement basis SAF energy density
  **E = 31.66 MJ/L**. $/t CO2 = ΔMJSP[$/L]·1e6 / (ΔGHG[g/MJ]·E).
- **Common "none" reference for all abatement costs (§2 and §3):** the base plant with
  **no ammonia and no CCS** — grey-H2 only, at ×30. MJSP **0.664 $/L**; WTWa GHG **87.57**
  (alloc) / **123.03** (disp) g/MJ. Every Δ in this report (ammonia mix *and* CCS capture)
  is measured against this single point, so the two levers are directly comparable.
- Post-fix six-tenths cost model (HEAD); numbers reproduce `_Scale_Up_Sensitivity.md`
  §3c/§4 endpoints exactly (base 0.664, full ammonia 2.389, GHG 87.57→49.45 alloc /
  123.03→2.27 disp).

## 2. Cracker Size Sweep (×1 → ×30 inside the ×30 main unit)

MJSP $/L SAF. GHG = WTWa GHG-100, 4-method mean [g CO2e/MJ]. abs CO2 = mean GHG ×
annual SAF energy [Mt CO2e/yr]. $/t = abatement vs grey base (US Allocation /
Displacement; KR values within 0.1 % of US — the base→ammonia ΔGHG is the same, 38.1
alloc / 120.8 disp). Full table in `Result/ScaleUp_Subunits_ammonia.xlsx`.
% red = ΔGHG vs the grey base per basis (alloc base 87.57, disp base 123.03 g/MJ),
linear in NH3 fraction — so each %red pairs with the $/t of the same basis.
The lo–hi columns span the green-NH3 **price** range: lo = projected 0.1225, hi = current
0.4535 $/lb (base 0.288 = their average). Price hits only the ammonia feed line
(2.038 $/L at full ammonia, flat across scale), so MJSP moves ±f·1.171 $/L about the base
and each $/t scales with ΔMJSP (GHG, hence %red, is price-independent).
The **CCS** columns answer the same-reduction question: for each row, capture the CCS
portion that removes the *same* WTWa GHG as the ammonia cracker (portion = f·38.12/43.42
= f·0.878; capture is linear in CO2 removed, alloc & disp give the same portion). CCS
MJSP is the **actual six-tenths `economic_analysis` run at that portion — not
interpolated**, and now carries **$10/tCO2 CO2 transport & storage (T&S)** on the whole
sequestered stream (622X EGR CO2 + capture_portion·623CO2); the discrete 25/50/75/100 %
runs reproduce §3 MJSP exactly (0.732/0.786/0.980/1.198). CCS $/t uses the same (matched)
ΔGHG as the ammonia row, so ammonia $/t and
CCS $/t on one row are a like-for-like cost of an identical emission cut.

| Cracker × | NH3 frac | MJSP [$/L] | ΔMJSP | GHG mean [g/MJ] | abs CO2 [Mt/yr] | $/t alloc | $/t disp | %red alloc | %red disp | MJSP lo–hi [$/L] | $/t alloc lo–hi | $/t disp lo–hi | CCS %cap | CCS MJSP [$/L] | CCS $/t alloc | CCS $/t disp |
|----------:|---------:|-----------:|------:|----------------:|----------------:|----------:|---------:|-----------:|----------:|-----------------:|----------------:|---------------:|---------:|--------------:|-------------:|------------:|
| 0 (base)  | 0.000    | 0.664      | —     | 109.02          | 5.885           | —         | —        | —          | —         | —                | —               | —              | —        | 0.664         | —            | —           |
| 1         | 0.033    | 0.725      | 0.061 | 106.37          | 5.742           | 1528      | 482      | 1.4        | 3.2       | 0.686–0.764      | 550–2506        | 174–790        | 2.9      | 0.683         | 485          | 153         |
| 2.5       | 0.083    | 0.813      | 0.149 | 102.40          | 5.528           | 1484      | 469      | 3.6        | 8.2       | 0.715–0.911      | 512–2456        | 162–776        | 7.3      | 0.693         | 293          | 93          |
| 5         | 0.167    | 0.959      | 0.295 | 95.78           | 5.170           | 1470      | 464      | 7.3        | 16.4      | 0.764–1.154      | 497–2443        | 157–771        | 14.6     | 0.710         | 228          | 72          |
| 7.5       | 0.250    | 1.105      | 0.441 | 89.16           | 4.813           | 1462      | 462      | 10.9       | 24.5      | 0.812–1.398      | 492–2433        | 155–769        | 21.9     | 0.726         | 205          | 65          |
| 10        | 0.333    | 1.248      | 0.584 | 82.54           | 4.455           | 1451      | 458      | 14.5       | 32.7      | 0.858–1.638      | 481–2421        | 152–764        | 29.3     | 0.742         | 194          | 61          |
| 20        | 0.667    | 1.817      | 1.153 | 56.05           | 3.026           | 1433      | 452      | 29.0       | 65.5      | 1.036–2.598      | 463–2403        | 146–758        | 58.5     | 0.835         | 213          | 67          |
| 30        | 1.000    | 2.389      | 1.725 | 29.57           | 1.596           | 1429      | 451      | 43.5       | 98.2      | 1.218–3.560      | 459–2399        | 145–757        | 87.8     | 1.092         | 355          | 112         |

**Findings.**

1. **Abatement cost is set by the cracker's own size, not the main-unit size.** The
   ×1-cracker slice of a ×30 plant abates at 1528 $/t (alloc) / 482 (disp) — *identical*
   to a stand-alone ×1 full-ammonia plant (`_Scale_Up_Sensitivity.md` §3c). The ×30
   cracker gives 1429 / 451. So the ammonia $/t depends only on the cracker's absolute
   scale; the size of the main unit it feeds is irrelevant to the abatement price.

2. **Scaling the cracker is a weak lever: ×1→×30 cuts $/t only ~6.5 %** (1528→1429
   alloc; 482→451 disp). Reason: the ammonia route's cost is dominated by the NH3 feed
   purchase (~2.0 $/L, flat per unit H2 and per unit CO2 avoided); only the cracker
   CAPEX-per-unit-H2 improves with size, and it is a minor share. Cracker economies of
   scale barely move the abatement price.

3. **A small cracker buys a small, expensive emission cut.** At ×1 the MJSP penalty is
   tiny (+0.061 $/L) but so is the CO2 cut (109→106 g/MJ; 5.89→5.74 Mt/yr). MJSP rises
   almost linearly with cracker size to 2.389 $/L at ×30, where emissions reach 29.6
   g/MJ mean (49.5 alloc / 2.3 disp) — near-zero under displacement.

4. **Method dominates the level, size does not.** Displacement (fertilizer co-product
   credit) is ~3× cheaper per ton than allocation at every cracker size (~460 vs ~1470
   $/t). Sizing the cracker never closes that gap.

5. **Ammonia's marginal abatement price is flat across the reduction fraction.** The
   new %red columns span 1.4→43.5 % (alloc) / 3.2→98.2 % (disp) as the cracker grows,
   yet $/t stays ~1430–1528 (alloc) / 451–482 (disp) throughout. So each extra fraction
   of GHG cut costs about the same — a linear reduction curve at a constant price. This
   is the opposite of CCS (§3), whose $/t *rises* with capture depth (167→389 alloc);
   ammonia buys deep reduction at a flat but high unit price, CCS buys shallow reduction
   cheaply that gets dearer with depth.

6. **The green-NH3 price dwarfs cracker size as the economic lever.** Across the price
   range the abatement $/t swings ~4.5× (e.g. ×30 alloc 459→2399, vs the ~6.5 % that
   *sizing* the cracker moves it). Even the low (projected 0.1225 $/lb) end — 459 alloc /
   145 disp at ×30 — stays above CCS's dearest 100 % point (389 alloc / 123 disp, §3);
   at the current 0.4535 $/lb ammonia is ~6–14× CCS. And MJSP never beats grey (0.664):
   the ×30 low-price MJSP is still 1.218 $/L. So price sets whether ammonia is merely
   expensive or prohibitive; cracker size is second-order either way.

7. **At an identical GHG cut, CCS is ~3–7.5× cheaper per ton than the ammonia cracker.**
   Matching each row's reduction with the CCS portion that removes the same WTWa GHG
   (2.9 % capture for the ×1 slice up to 87.8 % for full-ammonia's cut), the *actual*
   six-tenths CCS MJSP (incl. $10/tCO2 T&S) runs 0.683→1.092 $/L vs ammonia 0.725→2.389,
   and CCS $/t is 194–485 (alloc) / 61–153 (disp) vs ammonia 1429–1528 / 451–482 — same
   reduction, still lower cost. Charging T&S on the *whole* sequestered stream (the
   always-captured 622X EGR CO2 plus capture_portion·623CO2) makes the shallowest matched
   cut the dearest per ton: at ×1 the 2.9 % capture pays T&S on the fixed EGR CO2 against a
   tiny ~1.3 g/MJ credit, so its $/t is highest (485 alloc). $/t falls to a minimum near
   ×10 (29 % capture, 194 alloc), then rises again past the ~54 % waste-heat kink (×20 →
   58.5 % → 213; ×30 → 87.8 % → 355). CCS still wins on $/t at every reduction depth the
   ammonia cracker can reach.

**Answer.** Growing the ammonia cracker inside a fixed ×30 plant lowers the CO2
abatement cost only marginally — 1528→1429 $/t (allocation) / 482→451 (displacement),
≈−6.5 % across the full ×1→×30 range — because the price is feed-driven, not
CAPEX-driven. The abatement $/t tracks the cracker's absolute size and is independent
of the main unit. Absolute MJSP runs 0.725 (×1 slice) → 2.389 $/L (×30, full ammonia);
WTWa emissions 106 → 29.6 g/MJ mean (5.74 → 1.60 Mt CO2e/yr). All endpoints reproduce
the manuscript/Sensitivity report, confirming the engine.

## 3. Comparison with CCS (same ×30 main unit)

CCS is the other sub-unit lever. Its "size" is the **capture portion** (scales the CCS
unit off the sequestered-CO2 flow), so the analog of the cracker sweep is capture
0→100 % inside the same ×30 plant. Same E, same abatement formula, same grey base
(0.664 $/L). MJSP now includes **$10/tCO2 CO2 T&S** on the sequestered stream (622X EGR
CO2 + capture_portion·623CO2); the grey base carries no CCS unit and no T&S. GHG read
from the actual `CCS025/050/075/100` LCA sheets (nonlinear in
portion — waste heat covers capture free up to ~54 %); 60 % interpolated (flagged).
US Allocation / Displacement only (no KR sheets for CCS). Data in
`Result/ScaleUp_Subunits_ccs.xlsx`.

| Capture % | MJSP [$/L] | ΔMJSP | GHG alloc [g/MJ] | GHG disp | $/t alloc | $/t disp |
|----------:|-----------:|------:|-----------------:|---------:|----------:|---------:|
| 25        | 0.732      | 0.069 | 76.01            | 86.44    | 188       | 59       |
| 50        | 0.786      | 0.122 | 64.44            | 49.76    | 167       | 53       |
| 60*       | 0.848      | 0.184 | 60.33*           | 36.75*   | 214       | 68       |
| 75        | 0.980      | 0.316 | 54.18            | 17.23    | 299       | 94       |
| 100       | 1.198      | 0.535 | 44.15            | −14.57   | 389       | 123      |

*60 % GHG interpolated between the 50 % and 75 % sheets (the nonlinear waste-heat
region); MJSP is direct. `_Scale_Up_Sensitivity.md` §3c/§4 stays T&S-free (CCS-60 % ×30 ≈
168/53 $/t); on that T&S-free basis this row is 161/51 (matches to interpolation
tolerance), and the 214/68 above is the same run plus $10/tCO2 T&S.

**Verdict — not comparable: CCS is ~4–9× cheaper per ton of CO2 than the ammonia
cracker at the ×30 plant, even with $10/tCO2 T&S loaded onto CCS.**

- Allocation: CCS 167–389 $/t vs ammonia 1429–1528. Even the *most expensive* CCS
  (100 % capture, 389) is ~3.7× below the *cheapest* ammonia (×30, 1429).
- Displacement: CCS 53–123 $/t vs ammonia 451–482. Same ranking — ammonia's cheapest
  (451) is ~3.7× the dearest CCS (123) and ~8.5× the cheap sub-50 % CCS (~53).
- CCS also costs less in absolute MJSP: 100 % capture (1.198 $/L) is below even a ×10
  cracker (1.248). And CCS is cheapest per ton **below the ~54 % waste-heat kink**
  (25–50 % ≈ 167–188 alloc / 53–59 disp), where the reboiler runs on free process heat.

**So:** sizing the ammonia cracker never makes it cost-competitive with CCS as a CO2
abatement lever. Ammonia's value is *depth* — full ammonia reaches ~2.3 g/MJ
(displacement), near-zero, deeper than partial CCS on grey can go — not $/t. This
confirms `_Scale_Up_Sensitivity.md` §3b's ranking, now on the identical ×30 sub-unit
axis.

## Log history

### 2026-09-27

**Discussion**
- **CO2 T&S re-costed at $10/tCO2 (was $0) — CCS numbers only.** Decision: the CCS unit in
  this report now carries $10/tCO2 transport & storage; the grey base (no CCS unit) carries
  none. Applied *locally* (analytically, as in `tea_scale_up_abatement.py`) — `funs.py`
  default `co2_ts_usd_per_ton = 0.` left untouched so other reports stay T&S-free. T&S is a
  cost, not an emission: all GHG intensities, ΔGHG, %cap and every ammonia-only number are
  unchanged. Updated §2 matched-CCS (MJSP + $/t alloc/disp) and §3 (MJSP, ΔMJSP, $/t). Key
  consequence: T&S is charged on the *whole* sequestered stream `co2_seq = 622X EGR CO2 +
  capture_portion·623CO2` (funs.py:504/513), and the always-captured EGR term is portion-
  independent — so a shallow matched-CCS cut pays T&S on the full EGR CO2 against a tiny net
  credit. This inverts the old "flat & cheapest below the kink" shape of finding #7: matched-
  CCS $/t is now highest at ×1 (2.9 % cap, 485 alloc), dips to a minimum near ×10 (194), then
  rises past the kink to 355 at ×30. CCS-vs-ammonia advantage narrows from 5–12× to ~3–7.5×
  (§2) / ~4–13× to ~4–9× (§3), but CCS still wins on $/t at every depth. §3 60 %: 161/51 on
  the T&S-free basis (still matches `_Scale_Up_Sensitivity.md` 168/53), 214/68 with T&S.
- **Validation pass — independent engine re-run (report-only, no numbers changed).** Re-ran
  the engine from repo root and re-derived every column against §2/§3. Engine columns (MJSP,
  4-method GHG, mean GHG, abs CO2, $/t alloc/disp for the ammonia sweep; §3 CCS sweep; §2
  matched-CCS %cap/MJSP/$/t) reproduce to the last printed digit — ammonia $/t 1528→1429 alloc
  / 482→451 disp, §3 CCS 115–340 / 36–107, matched-CCS 127→304 / 40→96. Derived-only columns
  (price lo–hi, %red) recomputed from the exact (unrounded) MJSP match within rounding: %red ≤0.1
  (×1 disp 3.3 vs 3.2, ×20 disp 65.4 vs 65.5), and the price-range $/t within ~1 % at ×1 (558 vs
  550) because the report derived those from the rounded 3-dp MJSP lo–hi rather than full precision
  — a presentation choice, not an error. Anchors all pass: base 0.664, full NH3 2.389, GHG
  87.57→49.45 (alloc) / 123.03→2.27 (disp), CCS discrete 0.706/0.746/0.926/1.131, E=31.66 (script
  assert), and the ×1-slice $/t 1528/482 equals a re-run stand-alone ×1 full-NH3 plant (finding #1
  confirmed: abatement price is set by cracker absolute size, not main-unit size).
- Added **same-reduction CCS** columns to §2 (CCS %cap, CCS MJSP, CCS $/t alloc/disp) at
  the request "run CCS to the same GHG reduction, no linear interpolation." Method: for
  each ammonia row set ccs_portion = f·(38.12/43.42) = f·0.878 (capture linear in CO2
  removed; alloc & disp give the same portion), then run the *actual* six-tenths
  `economic_analysis(['Base'], ccs_portion=p)` at x30 — no cost interpolation. Self-check:
  base 0.664 and the discrete 25/50/75/100 % runs reproduce §3 MJSP exactly. CCS $/t uses
  the matched (=ammonia) ΔGHG so the two levers are compared at an identical cut. New
  finding #7: CCS 5–12× cheaper per ton at the same reduction (CCS $/t 122–304 alloc /
  39–96 disp vs ammonia 1429–1528 / 451–482); the ~54 % waste-heat kink shows as a step
  between ×10 (29 % cap, 122 alloc) and ×20 (58.5 % cap, 157). Consistent with §3's
  "CCS ~4–13× cheaper" verdict, now row-matched on GHG.
- Added green-NH3 **price-range** columns to §2 (MJSP lo–hi, $/t alloc lo–hi, $/t disp
  lo–hi) at the request "range of economics following the ammonia price range". Range =
  projected 0.1225 (lo) / current 0.4535 (hi) $/lb, base 0.288 = their average. Reused the
  established feed = 2.038 $/L flat-across-scale constant (`_Scale_Up_Sensitivity.md` §5;
  validated here by the exact ×1-slice identity 1528/482 shared between the two reports) →
  no re-run needed; MJSP moves ±f·1.171, $/t scales with ΔMJSP (GHG price-independent).
  New finding #6: price swings $/t ~4.5×, dwarfing the ~6.5 % size effect; even the lo end
  stays above the dearest CCS. Assumption logged: feed 2.038 taken as basis-independent
  (551 vs 572) on the strength of the reproduced endpoints, not re-derived from 551 APEA.
- Added per-basis **%red alloc / %red disp** columns to §2 to compare abatement $/t
  *by* the fraction of GHG reduced. Chose per-basis (ΔGHG/base: alloc 87.57, disp 123.03)
  over a single 4-method-mean %red so each %red pairs with the $/t of the same basis;
  linear in NH3 fraction. Endpoints ×30 = 43.5 % (alloc) / 98.2 % (disp). New finding #5:
  ammonia's marginal price is flat across %red (~1430–1528 alloc), opposite CCS whose $/t
  rises with capture depth.
- Confirmed both levers' abatement $/t are measured from the same **"none" plant** (no
  ammonia, no CCS; grey-H2 ×30: MJSP 0.664, GHG 87.57 alloc / 123.03 disp). §2 (ammonia)
  and §3 (CCS) already used this identical zero reference; added an explicit shared-baseline
  note to §1 so the two are unambiguously comparable. No numbers changed.
- New report created at user request: isolate the ammonia cracker's size effect (×1→×30)
  inside a fixed ×30 main unit, distinct from the whole-plant scaling in
  `_Scale_Up_Sensitivity.md`. Log target for this session = this file (confirmed at start).
- Modeling decision: "cracker ×k in ×30 plant" ≡ ammonia fraction f = k/30 via
  `H2Mix(30).mjsp_with_ammonia(f)`; the cracker CAPEX is read per scale from the
  `NH3_Cracking_130_scale####` APEA files (piecewise-linear, not six-tenths). Grey H2
  covers 1−f. Cracker sizes chosen = the ammonia data points {1,2.5,5,7.5,10,20,30} to
  avoid interpolation error.
- Key result: ammonia abatement $/t is governed by the cracker's *absolute* size, not the
  main-unit size — the ×1-cracker slice of a ×30 plant equals a stand-alone ×1 plant
  (1528 alloc / 482 disp). Scaling the cracker ×1→×30 cuts $/t only ~6.5 % (feed-cost
  dominated, ~2.0 $/L flat). Consistent with the Sensitivity report's "ammonia weakly
  falls with scale (−6.5 %)".
- Double-checks all pass: base ×30 MJSP 0.664, full ammonia 2.389, GHG endpoints
  87.57→49.45 (alloc) / 123.03→2.27 (disp) — match manuscript / `_Scale_Up_Sensitivity.md`
  §3/§4. E-density self-check (SAF PJ/yr ÷ L/yr = 31.66 MJ/L) asserted in the script.

- CCS comparison added (§3) at user's "is it comparable to CCS" question. Result: **not
  comparable — CCS ~4–13× cheaper per ton** at the same ×30 plant (alloc 112–340 vs
  ammonia 1429–1528; disp 35–107 vs 451–482). Ammonia's edge is depth (near-zero via
  displacement), not $/t. Confirms `_Scale_Up_Sensitivity.md` §3b on the identical axis.
  CCS GHG read from the true `CCS025/050/075/100` sheets (nonlinear, waste-heat kink ~54 %);
  60 % interpolated.

**Code**
- `scratchpad/subunit_ccs_ts.py` (not committed): reproduces §2 matched-CCS and §3 CCS at
  fixed ×30 via `TEA.economic_analysis(['Base'], ccs_portion=p)`, adds T&S analytically
  `dMJSP = co2_seq/2204.62·8000·ts/saf` (co2_seq from 622X+623CO2, same as funs.calc_cost_CCS).
  Asserts E=31.66 (saf·E=53.98 PJ/yr), base 0.664, and §3 T&S=0 MJSP anchors
  0.706/0.746/0.926/1.131 before re-running at ts=$10/t. All asserts green.
- Validation re-run (session scratchpad, not committed): copies of `subunit_sweep.py`,
  `ccs_sweep.py`, `ccs_match_ammonia.py` plus `arith_audit.py` (price lo–hi / %red). Run with
  `PYTHONPATH`=repo root, Excel output redirected to scratchpad so repo `Result/` stayed untouched.
  All engine anchors asserted green.
- `scratchpad/subunit_sweep.py` (not committed): sweeps cracker ×{1..30} at fixed ×30 main
  via `H2Mix(30)`; grey base MJSP + SAF energy from `TEA.economic_analysis(['Base'])`;
  abatement = ΔMJSP·1e6/(ΔGHG·E). Writes `Result/ScaleUp_Subunits_ammonia.xlsx`.
- `scratchpad/ccs_sweep.py` (not committed): CCS capture-portion sweep {25,50,60,75,100}%
  at ×30, GHG from actual CCS sheets. Writes `Result/ScaleUp_Subunits_ccs.xlsx`. Feeds §3.

**Open**
- With $10/t T&S this report's §3 CCS $/t diverges from the T&S-free `_Scale_Up_Sensitivity.md`
  (60 % ×30: 214/68 here vs 168/53 there); the two only reconcile at the T&S-free basis
  (161/51). Deliberate — the sister report must stay T&S-free per the modeling scope.
- T&S charged on the always-captured 622X EGR CO2 (portion-independent) is the sanctioned
  convention (funs.calc_cost_CCS + `tea_scale_up_abatement.py`); if EGR CO2 should be exempt
  from T&S the shallow matched-CCS $/t (esp. ×1 = 485 alloc) would fall — not revisited here.
- CCS §3 has no KR-allocation numbers (LCA files carry no CCS KR sheets); ammonia §2 KR
  ≈ US. So a strict KR-basis ammonia-vs-CCS $/t is not tabulated.
- CCS 60 % GHG is interpolated (no sheet); the 50→75 % span is the nonlinear waste-heat
  region, so treat the 60 % $/t (161/51) as approximate.
- KR-allocation $/t reported as ≈US (ΔGHG coincidentally equal, 38.1); not separately
  tabulated as a distinct binding number.
- Absolute CO2 [Mt/yr] is the 4-method WTWa mean; allocation vs displacement spread is
  wide at high ammonia fraction (49.5 vs 2.3 g/MJ at ×30) — the mean smears them.
- CCS not included in this cut (ammonia-cracker-only, per the request).
