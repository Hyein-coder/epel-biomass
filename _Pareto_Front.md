# Pareto Front — MJSP vs GHG (ammonia cracker × CCS scale)

Two-objective trade-off (minimize MJSP, minimize WTWa GHG) for the SAF pyrolysis
process, main unit fixed at scale **x10** (MJSP economies-of-scale knee), sweeping
ammonia-cracker scale and CCS portion. 551 basis, Allocation LCA.

Script: `tea_pareto_front.py` → `Figure/pareto_front.png`, `Result/pareto_front.xlsx`.

## 1. Objective & Grid Design

- **Objectives** (both minimized): MJSP [$/L SAF]; WTWa GHG-100 [g CO₂e/MJ SAF].
- **Fixed**: main SAF process unit at x10 (knee point of the MJSP scale-up curve).
- **Grid (6 × 5 = 30)**:
  - Ammonia cracker scale: x0, x1, x2.5, x5, x7.5, x10 — where **x0 = full grey-H₂** (no cracker).
  - CCS portion: 0%, 25%, 50%, 75%, 100%.
- **Ammonia scale → H₂ share**: at an x10 plant a cracker of scale x_a supplies x_a/10 of
  the H₂ demand, so `ammonia_portion = x_a / 10` (x0 → 0, x10 → full ammonia). This makes
  the cracker-scale axis a partial-substitution axis, not an oversizing axis.

## 2. Method

- **MJSP** — `funs.TEA.economic_analysis` at `Scale0100`. For x0, the grey `Base` row; for
  x1–x10, the `Mix` row (partial grey/ammonia H₂ **with CCS applied at the same portion**).
  No engine change. CO₂ T&S = **$10/tCO₂** (current basis, commit 95db93c).
- **GHG** — `funs_lca.get_WTWa_pyrolysis`, GHG-100, Allocation. CCS uses the per-portion LCA
  sheets (`Base`, `CCS025/050/075/100` — no interpolation). The ammonia lever is applied as an
  additive delta from base:
  `GHG(a,c) = ghg_ccs[c] − a·(ghg_base − ghg_ammonia)`.
  - **Assumption**: ammonia-H₂ abatement (removing upstream grey-H₂/SMR emissions) is
    independent of, and additive to, CCS process-CO₂ capture — they act on largely different
    emission sources. Cross-terms not modelled (no combined ammonia+CCS LCA case exists).
- **Pareto front**: non-dominated set minimizing both objectives (12 of 30 points).

## 3. Results

![Pareto front](Figure/pareto_front.png)

Colour = ammonia scale; marker = CCS portion; line = Pareto front.

**Pareto-optimal points** (grey-end cheap → ammonia-end clean):

| NH₃ scale | CCS | GHG [g CO₂e/MJ] | MJSP [$/L] |
|-----------|-----|-----------------|------------|
| x0  | 0%   | 87.57 | 0.793 |
| x0  | 25%  | 76.01 | 0.855 |
| x0  | 50%  | 64.44 | 0.913 |
| x0  | 75%  | 54.18 | 1.111 |
| x1  | 50%  | 60.63 | 1.098 |
| x1  | 75%  | 50.36 | 1.296 |
| x0  | 100% | 44.15 | 1.334 |
| x1  | 100% | 40.34 | 1.518 |
| x2.5| 100% | 34.62 | 1.782 |
| x5  | 100% | 25.09 | 2.221 |
| x7.5| 100% | 15.56 | 2.657 |
| x10 | 100% |  6.03 | 3.085 |

Full 30-point grid in `Result/pareto_front.xlsx`.

## 4. Reading the trade-off

- **Front spans 0.79 → 3.09 $/L for 87.6 → 6.0 g CO₂e/MJ** — a ~14× GHG cut costs ~3.9× MJSP.
- **CCS is the efficient near-term lever.** From grey-no-CCS, ramping CCS 0→100% (all at x0
  ammonia) stays on or near the front down to 44 g at 1.33 $/L. Ammonia at low CCS is
  dominated — every x2.5–x10 point at CCS <100% sits above the front.
- **Ammonia only pays below ~44 g CO₂e/MJ.** Grey+CCS100 bottoms out at 44 g; going deeper
  requires displacing grey H₂, so the whole deep-decarbonization tail of the front is
  **CCS100 + rising ammonia scale**. Ammonia never appears on the front without CCS100.
- **Knee of the front** is around the x0/CCS100 → x1/CCS100 region (44 g, 1.33 $/L): the last
  cheap GHG reductions before ammonia's steep cost tail.
- This is a first scatter at base green-ammonia price ($0.288/lb) and $10/tCO₂ T&S; both move
  the ammonia and CCS tails respectively (see `_Tornado_Sensitivity.md` ranges).

## 5. CO₂ abatement cost

Marginal abatement cost of each option vs the grey base (x0, CCS0 — cheapest, dirtiest):
`abatement = ΔMJSP / (ΔGHG · E) · 10⁶` [$/tCO₂], `E = 31.66 MJ/L SAF` (§3b). Same formula as
`tea_scale_up_abatement.py`. Full grid in `Result/pareto_front.xlsx` (`abatement` column).

**Pareto-front points** (grey base = reference, no abatement):

| Green NH₃ | CCS | GHG [g/MJ] | MJSP [$/L] | Abatement [$/tCO₂] |
|-----------|-----|------------|------------|--------------------|
| 0%   | 25%  | 76.01 | 0.855 | 170 |
| 0%   | 50%  | 64.44 | 0.913 | 165 |
| 0%   | 75%  | 54.18 | 1.111 | 301 |
| 10%  | 50%  | 60.63 | 1.098 | 358 |
| 0%   | 100% | 44.15 | 1.334 | 394 |
| 10%  | 75%  | 50.36 | 1.296 | 427 |
| 10%  | 100% | 40.34 | 1.518 | 485 |
| 25%  | 100% | 34.62 | 1.782 | 590 |
| 50%  | 100% | 25.09 | 2.221 | 722 |
| 75%  | 100% | 15.56 | 2.657 | 818 |
| 100% | 100% |  6.03 | 3.085 | 888 |

- **Cheapest CO₂ removal ≈ 165–170 $/tCO₂** — grey H₂ + CCS 25–50%. Abatement cost *rises* as CCS
  deepens (75%→100% grey = 301→394 $/t): the last increments of capture cost more per tonne.
- **Green ammonia is the expensive tail: 485 → 888 $/tCO₂** (10%→100% share, all at CCS100). It is
  only worth buying once CCS100 is exhausted at 44 g/MJ and deeper cuts are still needed.
- Whole-grid minimum abatement cost is the grey+CCS50 point (165 $/t); the maximum useful option
  (full green NH₃ + CCS100) reaches 6 g/MJ at 888 $/t.

## Log history

### 2026-09-28 (update 2)

**Discussion**
- Legend relabelled `Green NH₃ ##%` (## = H₂ share supplied by the cracker = ammonia_portion),
  replacing raw cracker-scale `×N`. Cosmetic; grid values unchanged.
- Added CO₂ abatement cost (§5) vs the grey base, reusing the `tea_scale_up_abatement.py`
  formula (E = 31.66 MJ/L). Reference = x0/CCS0.

**Code**
- `tea_pareto_front.py` — added `abatement` column ($/tCO₂ vs grey base), printed for the front,
  written to `Result/pareto_front.xlsx`; legend labels changed to `Green NH₃ ##%`.

**Open**
- Abatement cost is single point-estimate (base NH₃ price, $10/t T&S), Allocation only — same
  caveats as MJSP/GHG.

### 2026-09-28

**Discussion**
- New two-objective study requested: Pareto front of MJSP vs WTWa GHG, main SAF unit fixed at
  x10 (declared MJSP knee), grid = ammonia cracker {x0,x1,x2.5,x5,x7.5,x10} × CCS {0,25,50,75,100%}.
  x0 defined as full grey-H₂. First deliverable = scatter of the 30 combinations. Log target =
  this file (`_Pareto_Front.md`), per user naming the new report.
- Ammonia cracker scale mapped to H₂ substitution share `ammonia_portion = x_a/10` at the x10
  plant (chosen over treating cracker scale as standalone oversizing — the cracker only needs to
  cover plant H₂ demand).
- GHG for combined ammonia+CCS taken as additive-delta superposition (no combined LCA case
  exists); flagged as an assumption in-script and in §2.

**Code**
- `tea_pareto_front.py` — 6×5 grid; MJSP via `economic_analysis` Mix row (CCS+ammonia in one
  call), GHG via `funs_lca.get_WTWa_pyrolysis` (Allocation, per-portion CCS sheets + additive
  ammonia delta); scatter (colour=NH₃ scale, marker=CCS) + Pareto line; writes
  `Figure/pareto_front.png`, `Result/pareto_front.xlsx`. Self-checks: base MJSP>0, GHG base≈87.57,
  CCS/ammonia monotone GHG reduction, front non-empty & monotone. All passed.

**Open**
- Single point-estimate scatter only: green-ammonia price and CO₂ T&S held at base ($0.288/lb,
  $10/t). Price-band envelope on the front not yet drawn.
- Only Allocation LCA method shown; Displacement / KRmix fronts not generated.
