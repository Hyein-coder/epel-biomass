# Base Revision

Subject: `"D:\EPEL_biomass\Biomass_LCA_ACS (3).pdf"` 

Plan: `"D:\ObsidianVault\KAN\VibeCoding\Projects\SAF_SNU\Critical_[Review.md](http://Review.md)"`

Base simulation: `"D:\EPEL_biomass\Aspen\Pyrolysis_Jones_551_into_571_forQuality_TSOL2_retune.apw"`

## 1. Numerical errors and internal contracdictions

### 1.1. Aromatic content of SAF product

Base simulation, stream `326SAF`, total mass flow 114,139 lb/hr. 

Source: `"D:\EPEL_biomass\Analysis\Process_Data\Pyrolysis_Jones_551_ASW_Recovered_Notes.xlsx"`

### 1.2. PEM energy → Already correct

### 1.3. Ammonia cracking mass balance

Ammonia cracker: resolved 

Ammonia scrubber: yet-resolved (reference 70% efficiency vs. simulation 99% efficiency, needs recycle loop or more recent reference)

### 1.4. MEA reboiler duty — yet-resolved

Reviewer (Critical_Review §1.4) flagged the MEA reboiler duty as a likely unit error:
8.9 GJ/t vs a conventional 30 wt% MEA benchmark of 3.5–4.2 GJ/t. Confirmed and traced to
its origin in the script.

**Cited source.** Code comment reads "Rao, 2022"; this is a year typo. The intended
reference is **Rao, A. B.; Rubin, E. S. (2002)**, *A Technical, Economic, and
Environmental Assessment of Amine-Based CO₂ Capture Technology for Power Plant Greenhouse
Gas Control*, Environ. Sci. Technol. 36(20), 4467–4475, DOI 10.1021/es0158861. Citation
verified via Crossref + OpenAlex (year, journal, vol/issue/pages all confirmed).

**Numbers hardcoded in the script** (`funs.py` `ccs_base_case`, duplicated in
`tea_base_JonesBaseCaseScale.py`):


| Field                     | Value in script                                 | In Rao &amp; Rubin 2002?                 |
| ------------------------- | ----------------------------------------------- | ---------------------------------------- |
| `base stream` (CO₂ basis) | 862,853 lb/hr (≈ 391 t/hr)                      | **No** — not in source                   |
| `heat consumption`        | 3315 mmBTU/hr                                   | **No** — not in source                   |
| `electricity`             | 3315 × 0.14 = 464 mmBTU/hr                      | **Yes** — 14% factor stated in the paper |
| Implied specific duty     | 3315e6 / 862,853 = 3,842 Btu/lb = **8.94 GJ/t** | **No** — ~2.2× IECM documentation*       |


***What the documentation shows** (checked against Rao &amp; Rubin's IECM MEA model *documentation*,
not the ES&amp;T 2002 letter's own tables — see caveat below):

- Regeneration energy is given only as a *specific* quantity, not an absolute duty:
**~1900 kJ/kg CO₂** theoretical heat of reaction, and a **literature range of
3800–4000 kJ/kg (3.8–4.0 GJ/t)** quoted as "the majority of sources report" — i.e. a
consensus range the documentation cites, **not verified as Rao &amp; Rubin's own reference
value**.
- Reboiler heat computed as **Q = (Q/L)·L** (L = sorbent molar flow), with a simulated
duty range of **95–664 GJ/hr** (max ≈ 629 mmBTU/hr — 3315 is ~5× above this range).
- No populated reference-case flowsheet: neither 3315 mmBTU/hr nor 862,853 lb/hr appears.

Defensible claim: the model's **8.94 GJ/t is ~2× any MEA regeneration figure in that
source**, and its two absolute inputs do not appear in it. Whether 3.8–4.0 GJ/t is
literally the 2002 letter's reference duty is **not confirmed** — the letter's tables were
not read.

- **Electricity = 14% of reboiler heat is a paper value** (the `0.14` factor in the
script is taken from Rao &amp; Rubin 2002, not invented).

So the **14% electricity factor is paper-supported**, but the absolute **3315 mmBTU/hr is
not** a verbatim paper figure and **not** a clean specific-energy × flow product — it is
an undocumented absolute inserted downstream.

**How the script uses these numbers** (`calc_cost_CCS`, `unit_cost_interpolation`):

- Reboiler duty and electricity scale **linearly** with CO₂ sequestered:
`r_scale = co2_seq / 862,853`, `heat = 3315 × r_scale`. No solvent/loading model.
- Electricity fixed at **14%** of heat duty (`3315 × 0.14`).
- Duty first offset by plant waste heat (`heat_gen` = Σ `-Q` stream QCALC); only the
shortfall is bought as Fuel. At the correct ~4 GJ/t, waste heat covers nearly all capture
duty and the CCS MJSP penalty largely disappears — strengthening the best-case result.

**Action.** Re-derive `ccs_base_case` from a defensible MEA regen figure (the 3.8–4.0
GJ/t literature range; provisional: `heat consumption = 4.0 GJ/t × co2_seq`), or document
the true origin of 3315 mmBTU/hr if it comes from another source. Before publishing a
"per Rao &amp; Rubin" value, read the ES&amp;T 2002 letter's own tables to fix the exact number.

### 1.5. LCA electricity — net treatment confirmed, no double-count

Plant is a near-neutral cogenerator: generates ~68,375 KW (`ELC-` turbine streams) and
consumes 68,533 KW (APEA utilities); net ≈ −158 KW, no grid line in RawMaterial Summary.
`funs.py` `get_work_products` already sums all `ELC-` streams to net, so co-product credit
and OPEX charge cancel — effectively net. LCA GHG is GREET output (`funs_lca.py` reads the
`Emissions` block only); the large petroleum-displacement credits are the gas + diesel
co-products, not electricity. No double-count, no action.

### 1.6. Table 7 electricity unit — reviewer correct, paper typo only

Reviewer (Critical_Review §1.6): Table 7 lists electricity as `$0.065/MMBtu`, which is
`$0.00022/kWh` — physically meaningless. The actual model input is **0.065/kWh**
(≈ 19/MMBtu, KEPCO industrial band). Confirmed against the APEA result sheets: every
electricity utility line back-solves to 0.065 USD/kWh (Cost/Hour ÷ Rate), e.g.
`Pyrolysis_551_Scale0100_APEA.xlsm` Utility Resource Summary 23,536.56 USD/h ÷ 362,100.9 KW
= 0.06500 USD/kWh. Matches the `0.065` $/kWh hardcode in `funs.TEA.__init__`. The wrong
unit is a manuscript typo in Table 7 only — no model/code error. **Action:** correct the
Table 7 column header `/MMBtu` → `/kWh`; no code change.

### 1.7. Table 5 pyrolyzer scaling cap — resolved (700 MMBtu/hr)

Reviewer (Critical_Review §1.7) flagged the "rigid upper bound" single-train pyrolyzer
cap as contradicting Table 5. Traced the number in the manuscript and re-derived it.

**Where the number lives.** The "rigid upper bounds" phrasing is on p11 (Methods →
Process Scale-up); the value is on p12: *"pyrolyzers were limited to a heat release of
50,000,000 Btu·hr⁻¹"* (= 50 MMBtu/hr). Justified only by "heat transfer physics" /
"industrial availability" — **no citation, no derivation**. (The 172 MMBtu/hr on p12 is
the ammonia-cracker reactor, a different unit — not the pyrolyzer.)

**Why 50 is wrong.** Table 5 R-110 count is `1 1 1 1 1 2 3` across scales 1 / 2.5 / 5 /
7.5 / 10 / 20 / 30. Unit count follows `n = ceil(D_base·scale / C)`; reproducing that
pattern forces the cap `C = 10–15 × D_base` (R-110 first splits between 10× and 20×). For
the 50 cap to fit, base duty would have to be 3.3–5.0 MMBtu/hr — nonphysical for a
45.5 ton/hr pyrolyzer. The stated cap is ~14× too small.

**Base duty.** A 45.5 ton/hr pyrolyzer's heat release is ≈70 MMBtu/hr (≈2 MJ/kg to heat

- pyrolyze the biomass). This is the correct reading of "70 MMBtu/hr" — the base-scale
duty, not the cap.

**Cap consistent with Table 5 = 700 MMBtu/hr** (= 10 × base duty):


| Scale | Biomass [ton/hr] | Pyrolyzer duty [MMBtu/hr] | duty / 700 | Units (ceil) | Table 5 |
| ----- | ---------------- | ------------------------- | ---------- | ------------ | ------- |
| 1×    | 45.5             | 70                        | 0.10       | 1            | 1       |
| 2.5×  | 114              | 175                       | 0.25       | 1            | 1       |
| 5×    | 228              | 350                       | 0.50       | 1            | 1       |
| 7.5×  | 341              | 525                       | 0.75       | 1            | 1       |
| 10×   | 455              | 700                       | 1.00       | 1            | 1       |
| 20×   | 910              | 1,400                     | 2.00       | 2            | 2       |
| 30×   | 1,365            | 2,100                     | 3.00       | 3            | 3       |


Exact match; scale-10 sits on the cap (700/700 = 1.0), the last single-unit scale.

**Decision.** Single-train pyrolyzer cap = **700 MMBtu/hr**. Fix manuscript p12:
`50,000,000 Btu·hr⁻¹` → `700,000,000 Btu·hr⁻¹`. Caveat: the 70 MMBtu/hr base duty is a
2 MJ/kg estimate, not read from the Aspen block — confirm against the `.apw` R-110 /
combustor duty before the number goes in the manuscript.

### 1.8. Table 1 moisture/ash basis label — resolved (drop "dry basis")

Reviewer (Critical_Review §1.8): Table 1 header reads "dry basis", yet the table lists
biomass moisture 10 wt% and char moisture 0.4 wt% — a moisture entry on a dry basis is
self-contradictory. Reviewer also flagged an ultimate-vs-proximate ash mismatch (biomass
0 vs 1; char 7.67 vs 3.5).

**Decision.** Omit the "dry basis" label from the Table 1 header. Removing the label
resolves the label↔moisture contradiction without recomputing any values; with moisture
rows present the table is read as-received implicitly, so no explicit "as-received"
relabel is needed. **Action:** delete "dry basis" from the Table 1 header; no data change.

The ash ultimate-vs-proximate mismatch is a separate inconsistency not fixed by dropping
the label — see Open.

### 1.9. Hydrogen demand — inconsistent numbers reconciled (anchor 3.3 t/hr)

Reviewer (Critical_Review §1.9): hydrogen demand appears as several inconsistent figures
across the manuscript. Reviewer's set:


| Source               | Value                                         | Disposition                                                                                 |
| -------------------- | --------------------------------------------- | ------------------------------------------------------------------------------------------- |
| Introduction         | ~35 wt% of dry oil feed                       | **Dropped** — cited reference figure, not this model's value; not an internal contradiction |
| Methods text         | 2.9 t/hr to hydroprocess 75 t/hr (3.9 wt%)    | **Fix 2.9 → 3.3 t/hr** (Table 8 is reliable)                                                |
| Methods text         | 12.2 wt% H2 consumption                       | Confusing (combined across hydrotreaters) — replace with absolute per-unit H2 below         |
| Table 8              | 3.3 t/hr H2                                   | **Anchor** — reliable                                                                       |
| Implied from Table 2 | 64 wt% bio-oil × 47.3 t/hr ≈ 30 t/hr (not 75) | Flags the 75 t/hr feed as the error                                                         |


**Anchor: 3.3 t/hr (Table 8).** Table 8 is emitted by `tea_h2pathways.py` (rate table at
line 42 via `tea.get_util_and_rawmaterial_sum`, `funs.py:285`), reading `RawMaterial Summary`
from `Pyrolysis_551_Scale0010_APEA.xlsm` (551 "Journal Paper", scale 1). The "Hydrogen gas"
row = the two fresh-H2 makeup streams (`funs.py:31`, `hydrogen_feed_stream=['250H2','532H2']`),
merged because the extractor strips the leading stream number (`funs.py:280–282`) before
`groupby.sum()`:


| Makeup stream | lb/hr       | t/hr            | Process area (`unit_category`, `funs.py:92`)    |
| ------------- | ----------- | --------------- | ----------------------------------------------- |
| `250H2`       | 5,831.5     | **2.92**        | Hydrotreating (area 200: R-202 / R-220 / R-225) |
| `532H2`       | 739.0       | **0.37**        | Hydrocracking (area 500: R-510)                 |
| **Σ H2**      | **6,570.5** | **3.285 ≈ 3.3** | = Table 8 "Hydrogen gas"                        |


Traces cleanly to the APEA sheet, no manual adjustment.

**Fixes.**

- **Methods `2.9 t/hr` → `3.3 t/hr`.** The 2.9 t/hr hydroprocessing H2 in the Methods text
is superseded by the reliable Table 8 value; correct it to 3.3 t/hr throughout.
- **Replace the combined `12.2 wt%`** (H2 per feed, summed over hydrotreaters — the source of
confusion) **with absolute per-unit H2**: hydrotreating **2.92 t/hr**, hydrocracking
**0.37 t/hr**, total **3.3 t/hr**. Absolute amounts remove the wt%-basis ambiguity.
- **75 t/hr hydroprocessing feed** is inconsistent with Table 2 (64 wt% bio-oil × biomass ≈
30 t/hr). Settle the feed basis separately (see §1.9 caveats / Open).

**Caveats.**

- The 2.92 t/hr is the area-200 makeup shared by *both* hydrotreater stages (R-202 first,
R-220/R-225 second); the export sheets cannot split it stage-by-stage. A large H2 recycle
(~22,000–25,000 lb/hr, streams 227/239/402/599) circulates, so a per-reactor reaction-H2
split needs the `.apw` reactor in/out balance, not the Material/APEA exports.
- Confirm Table 2 bio-oil = 64 wt% and settle biomass feed 45.5 vs 47.3 t/hr before the
75 → ~30 t/hr feed correction goes in the manuscript.

**Verification — pyrolysis oil feed rate (NOT hydrogen demand).** Checked the base 551 scale-1
case (`Pyrolysis_551_Scale0010_Streams.xlsx`, Material sheet): bio-oil into hydrotreating
(`200`/`201`) = 67,320.8 lb/hr = 33.7 short-ton/hr (30.5 metric t/hr), ~71 wt% of biomass, so the
manuscript's 75 t/hr is unsupported (~2.5× high); manuscript feed set to **33.7 short-ton/hr**
(mass basis = short ton, 2,000 lb, throughout). The biomass feed itself is revised from the
45.5 short-ton/hr NC-substream (dry-solid) component to the overall `90BIO` stream flow
(NC + moisture), read per scale from the 551 exports (see §1.15):


Flow rates reported as **MMt/yr** (million metric tonne per year), metric-tonne basis =
stream rate × `operation_hr` (8000 h/yr, `funs.py:12`, ~91% on-stream) ÷ 1e6. SAF is stream
`326SAF`, read from the same 551 exports as the biomass feed.


| Scale | `90BIO` lb/hr | Biomass feed [MMt/yr] | Biomass NC [MMt/yr] | SAF `326SAF` [MMt/yr] |
| ----- | ------------- | --------------------- | ------------------- | --------------------- |
| x1.0  | 94,654.5      | 0.343                 | 0.330               | 0.041                 |
| x2.5  | 231,175.5     | 0.839                 | 0.826               | 0.104                 |
| x5.0  | 458,710.5     | 1.665                 | 1.651               | 0.207                 |
| x7.5  | 686,245.5     | 2.490                 | 2.477               | 0.311                 |
| x10   | 913,780.5     | 3.316                 | 3.302               | 0.414                 |
| x20   | 1,823,920.5   | 6.618                 | 6.604               | 0.828                 |
| x30   | 2,734,060.5   | 9.921                 | 9.906               | 1.243                 |


Overall-flow per-unit is not constant (47.33 at x1 down to 45.57 at x30) because `90BIO` carries
moisture over the ~45.5 short-ton/hr dry-solid NC component; only `Scale0010` shows the elevated
47.33. Revising Table 5 to the overall `90BIO` feed total makes the moisture explicit, closing the
NC-vs-total basis gap.

### 1.10. Abstract numerical inconsistency — resolved

Reviewer (Critical_Review §1.10): a number in the abstract disagreed with the value in the
body. **Decision.** User corrected the abstract number to match the body; abstract and body
now agree. Manuscript abstract fix only, no code/data change.

### 1.11. Conclusion MJSP inconsistency — resolved

Reviewer (Critical_Review §1.11): the MJSP figure in the conclusion paragraph disagreed
with the results. **Decision.** User reconciled the conclusion MJSP number to the reported
result. Manuscript conclusion fix only, no code/data change.

### 1.12. Table 11 HMWB formula — resolved (C21H26O8)

Reviewer (Critical_Review §1.12): the HMWB pseudo-component in Table 11 carried a wrong
molecular formula. **Decision.** User set the Table 11 HMWB formula to **C21H26O8**.
Manuscript Table 11 fix only.

### 1.13. Co-product revenue units typo — resolved (added "M")

Reviewer (Critical_Review §1.13): the co-product revenue value was missing its **M**
(million) magnitude marker. **Decision.** User added the "M" to the co-product revenue
figure. Manuscript typo fix only.

### 1.14. Sand temperature — resolved

Reviewer (Critical_Review §1.14): sand heated to **1,189 °F** in the combustor enters the
pyrolyzer at **1,128 °F** — explain or correct the 61 °F drop.

Traced the sand loop (~1.32 M lb/hr `SAND`) in the 551 stream export
`Pyrolysis_Jones_551_into572_Streams.xlsx` (cross-checked `Pyrolysis_551_Scale0100`):


| Loop point                          | Stream   | Temp (551 base) |
| ----------------------------------- | -------- | --------------- |
| Combustor block R-124 outlet        | COMB-SOL | 1,201 °F        |
| Hot sand → pyrolyzer valve VAL-125A | 125XX    | 1,190 °F        |
| Sand **entering pyrolyzer** R-110   | 101      | **936 °F**      |
| Sand leaving pyrolyzer              | 111      | 814 °F          |


- **1,189 °F is real** — it matches the hot-sand delivery stream (125XX = 1,190 °F; the
combustor block itself runs 1,201 °F).
- **1,128 °F is unsupported** — no stream in sim #551 sits near it. The sand actually
entering the pyrolyzer (stream 101) is **936 °F**.
- **The 61 °F drop is a false premise.** The real combustor→pyrolyzer-feed drop is
1,190 → 936 ≈ **254 °F**, and it is not a sand cooldown: at VAL-125A the hot sand mixes
with cold recycle stream 100 (150 °F, from COL-101), so 936 °F is a blend temperature.

**Status: resolved (pure sand stream temperature 1,190°F).**

## 2. Fuel specification

Addresses Critical_Review §2 (fuel specification table). Base simulation:
`"D:\EPEL_biomass\Aspen\Pyrolysis_Jones_551_into_571_forQuality_TSOL2_retune.apw"`.

### 2.1. Flash point — criterion dropped

Reviewer flags the "max" label as wrong (flash point is a minimum, &gt;38 °C) and the
reported 101 °C as implausibly high for C8–C16 kerosene. Rather than recompute via
correlation, the flash-point row is removed from the spec table.

**Status: dropped.**

### 2.2. Specific gravity — unit fixed

Specific gravity is a ratio, so "(kg/m³)" was density mislabelled. Unit corrected to
dimensionless; density in kg/m³ reported separately.

**Status: resolved.**

### 2.3. LHV — verified from simulation

LHV (44.8 MJ/kg) confirmed against the base simulation.

**Status: resolved.**

### 2.4. Aromatic content — verified from simulation

Aromatic content confirmed from the base simulation (stream `326SAF`, see §1.1).

**Status: resolved.**

### 2.5. Sulfur content — verified from simulation

Sulfur content confirmed from the base simulation, replacing the "NA" entry.

**Status: resolved.**

## 4. TEA issues

### 4.11. CO2 transport &amp; storage cost on the CCS unit

The CCS unit previously carried only capture cost (CAPEX + Fuel/Electricity OPEX); CO2
transport &amp; storage (T&amp;S) was not charged. Added an optional T&amp;S cost applied to the
sequestered CO2 stream (`co2_seq`), controlled by `TEA.co2_ts_usd_per_ton` ($/tCO2),
default `0` so the base case is unchanged.

Sensitivity at CCS 100% (`Scale0010`, `Base` H2 source), T&amp;S over the literature range
$4–45/tCO2:


| T&amp;S price | MJSP [$/L] | Δ vs. no T&amp;S |
| ------------- | ---------- | ---------------- |
| $0/tCO2       | 2.207      | —                |
| $4/tCO2       | 2.234      | +0.027           |
| $45/tCO2      | 2.511      | +0.304           |


MJSP rises linearly with the T&amp;S price (Δ ratio 11.25 ≈ 45/4), i.e. ~$0.0068/L per$1/tCO2 at full capture. At the high end ($45/tCO2) T&amp;S adds ~14% to MJSP.

T&amp;S price-range reference: Smith et al., *The cost of CO2 transport and storage in
global integrated assessment modeling*, IJGGC 2021
(`D:\ObsidianVault\KAN\VibeCoding\References\biomass\IJGGC_2021_Smith_The cost of CO2 transport and storage in global integrated assessment modeling.pdf`).

## Log history

### 2026-09-30

**Discussion**

- Session log target: `_Base_Revision.md`.
- §1.9 biomass scale table converted from t/hr to **tpd**. User chose the **design basis
  (×24 h/day**, nameplate stream flow) over TEA-effective (×8000/365 = ×21.92). Reason: a
  stream flow rate is the instantaneous design value; the engine's `operation_hr = 8000` h/yr
  (`funs.py:12`) only applies when annualizing (SAF/yr, feed/yr, OPEX/yr), not to a stream rate.
- SAF production added to the **same** table as columns (chosen over a separate table).
- **Correction (same session):** dropped tpd(×24); switched the table to **MMt/yr**
  (million metric tonne per year), metric-tonne basis, annual = × `operation_hr` 8000 h/yr
  ÷ 1e6. Reason: annual MMt/yr is the preferred plant-capacity reporting unit; uses the
  engine's own annualization (`funs.py:12`) rather than a nameplate ×24. Short-ton/day
  columns removed with it.

**Code**

- `_Base_Revision.md` §1.9 scale table: now **MMt/yr** (metric) columns — biomass feed,
  biomass NC, SAF `326SAF` — replacing the short-ton/day + metric t/day (×24) version;
  basis note updated. Superseded intermediate: ton/hr → tpd (×24).
  SAF per scale read from `Pyrolysis_551_Scale00XX_Streams.xlsx` (Material sheet, `Mass Flows`
  row, ×24/2000), same source as the biomass feed.

**Findings**

- `326SAF` per scale (short-ton/day, ×24): x1 137.0, x2.5 342.4, x5 684.8, x7.5 1,027.2,
  x10 1,369.7, x20 2,739.3, x30 4,109.0. x1 = 11,413.9 lb/hr.
- **Discrepancy:** §1.1 base `326SAF` = 114,139 lb/hr is the **×10** (Scale0100) case, not
  x1 (Scale0010 = 11,413.9 lb/hr). §1.1 "base simulation" ≠ the scale-1 row. Not reconciled here.

**Open**

- §1.1 vs §1.9 base-scale mismatch: is the manuscript "base" the ×10 plant (114,139 lb/hr SAF)
  or scale-1 (11,414 lb/hr)? Needs a decision before §1.1/§1.9 are cited together.

### 2026-09-30

**Discussion**

- Session log target: `_Base_Revision.md`.
- GHG anatomy of base SAF (grey H2, no green NH3, no post-CCS) requested. Confirmed the
  `Base` sheet in `Pyrolysis_551_LCA_*.xlsx` already is this case (green NH3 = `Ammonia`
  sheet, CCS = `CCS0xx` sheets, both excluded).
- No unit-operation GHG split possible: GREET WTP result is aggregate, not per-block. Anatomy
  reported by stage (WTP/PTWa), species (CO2/CH4/N2O), and fossil-vs-biogenic only.

**Code**

- No file changes. Read-only analysis via `funs_lca.get_WTWa_pyrolysis` / `get_WTWa_ftjet`.

**Findings (base, gCO2e/MJ, GHG-100)**

- Stage: WTP 87.34 (99.7%), PTWa 0.23 (0.3%) — combustion biogenic-neutral.
- WTP species (Allocation): gross fossil CO2 +143.0, biogenic credit -62.4, net CO2 80.64
  (92.3%), CH4 6.23 (7.1%), N2O 0.46 (0.5%).
- Fossil driver: upstream Natural Gas 926.7 Btu/MJ + Coal 219.3 (grey-H2 SMR + grid);
  Biomass 1152.5 Btu/MJ is the biogenic credit side.
- Method spread WTWa: Allocation 87.57, Allocation_KRmix 100.83, Displacement 123.03,
  Displacement_KRmix 124.63; mean 109.02 (= `ghg_with_ammonia(0)` center).

**Open**

- None for this task.

### 2026-09-28

**Discussion**

- Session log target chosen: `_Base_Revision.md`.
- Wrote manuscript Methods as a new file, framed into three subsections (process design /
  TEA / LCA) per user request, plus a separate Supporting Information note for script-level
  detail kept out of the main text. Methods content sourced from the engine scripts, not
  re-derived. CCS reference stated correctly as Rao & Rubin 2002 (engine comment's "Rao 2022"
  is a year typo, per §1.4).

**Code**

- `Manuscript/2. Methods.md` (new): §2.1 process design (main unit changes vs Jones 2013,
  ammonia cracker, CCS), §2.2 TEA (feedstock price models, green ammonia/H2 supply, CCS cost,
  sensitivity), §2.3 LCA (biogenic carbon, allocation rationale, CORSIA SAF criterion).
- `Manuscript/SI. Supporting Information.md` (new): cost basis/financials, sub-unit
  interpolation table, single-train limits, cracker/CCS/Bern-dynamic-LCA/allocation detail,
  supply-availability context.

**Open**

- Feedstock price-model cases (FR Price / FR–Log Linear / Fixed Elasticity) still not added
  as explicit scenarios in the Results section — flagged inline in §2.2.1 and to the user.
- Methods citations are author-year placeholders (Byun 2020, Katebah 2022, Levasseur 2010,
  Lan 2021, DOE 2024, IJHE 2024); need full reference entries + fact-check before submission.

### 2026-09-25

**Open**

- **TODO (future): NC component vs overall `90BIO` flow across scales.** To settle the
47.3 (`Scale0010`) vs 45.6 (scaled) base-feed gap, compare the biomass **NC-substream
(dry-solid) component flow** against the **overall `90BIO` mass flow** per scale
(`Scale0010`/`0100`/`0300`). Hypothesis: the gap is a moisture / NC-vs-total-mass basis
difference; the NC dry-solid per-unit may be constant even where overall flow is not.
`funs.get_atomic_flow_idx` already locates the `NC Substream` block. Recorded as a TODO
in §1.9; not yet executed.

### 2026-09-26

**Discussion**

- **CO2 T&amp;S cost added as an option (→ §4.11).** User asked to charge CO2 transport &amp; storage
on the CCS unit, tested over $4–45/tCO2. Applied to the sequestered CO2 (`co2_seq`), default
off. Chose to lump T&amp;S into the CCS unit's `utilities` line rather than a new OPEX category:
the MJSP breakdown pulls only the fixed APEA-derived `opex_names`, so a new key would be
counted in the MJSP total but dropped from the stack-bar. Break out separately only if the
figure needs T&amp;S shown apart from Fuel/Electricity.
- **Table 5 biomass feedstock revised (→ §1.15).** User decision: replace the 45.5 short-ton/hr ×
scale biomass row (the `90BIO` NC-substream dry-solid component) with the **overall `90BIO` stream
mass flow** per scale. Read from the 551 stream exports (Material sheet, `Mass Flows`): x1 47.33,
x2.5 115.59, x5 229.36, x7.5 343.12, x10 456.89, x20 911.96, x30 1,367.03 short-ton/hr. Overall
flow per-unit is not constant (47.33→45.57) because `90BIO` includes moisture over the ~45.5 dry
NC solid; only `Scale0010` carries the elevated 47.33. Executes the §1.9 TODO (NC vs overall basis).
- §1.9 **closed**: appended a resolution paragraph at end of §1.9 summarizing the pyrolysis oil feed
claim (33.7 short-ton/hr; 75 t/hr unsupported) and folding in the §1.15 finding (47.3-vs-45.5 gap =
moisture basis). The 2026-09-25 NC-vs-overall TODO is now executed.
- §2 fuel spec: **dropped the missing-ASTM-specs action** (distillation curve, naphthalenes,
viscosity, D7566 caveat). Reason: the entire fuel-spec section is moving to SI later, so the
full ASTM D1655/D7566 buildout no longer matters here. Literal aromatic vol% / sulfur value
still pending — will come from the modified-version manuscript.

**Code**

- `funs.py`: added `TEA.co2_ts_usd_per_ton` knob (default 0) and, in `calc_cost_CCS`, a
`ccs_now['CO2 T&S'] = co2_seq/2204.62 * operation_hr * co2_ts_usd_per_ton` term folded into
`annual OPEX` and `utilities`.
- `test_co2_ts.py`: runs CCS 100% at T&amp;S {0, 4, 45}/tCO2; asserts base unchanged and MJSP
linear in price. Result: 2.207 / 2.234 / 2.511 $/L, Δ ratio 11.25.

### 2026-09-24

**Discussion**

- Review **§2 fuel specification** worked. User decisions: **flash point criterion dropped**
(mislabelled "max"; 101 °C implausible for C8–C16 kerosene — removed rather than recomputed);
**specific gravity unit fixed to dimensionless** (the "(kg/m³)" was density mislabelled);
**LHV 44.8 MJ/kg, aromatic content, and sulfur content all verified from the base simulation**
(sulfur replaces the old "NA"). Aromatic value ties to §1.1 (stream `326SAF`). Report §2 written
with per-item status.
- Review item **1.9 pyrolysis-oil feed rate verified** (the last §1.9 table row, *not* a
hydrogen-demand issue). Checked the base sim `Pyrolysis_551_Scale0010_Streams.xlsx`
(Material sheet, Mass Flows): biomass `90BIO` = 94,654.5 lb/hr (47.33 short-ton/hr); bio-oil
into hydrotreating `200`/`201` (liquid, ρ≈66 lb/cuft, area 200) = 67,320.8 lb/hr =
**30.5 metric t/hr (33.66 short-ton/hr)**, i.e. 71 wt% of biomass. Confirms the actual
hydroprocessing feed is ~30 t/hr and the manuscript's **75 t/hr is unsupported (~2.5× high)**.
Appended a verification note + stream table to §1.9 flagging it as a pyrolysis-oil-feed
issue distinct from H2 demand. Feed-basis reconciliation (64 vs 71 wt%, 45.5 vs 47.3 t/hr
biomass) still open before the manuscript correction.
**Decision:** manuscript will use **33.7 t/hr** for the pyrolysis oil feed, and declare
**short ton (2,000 lb)** as the material mass-unit basis throughout (so manuscript "t/hr"
= short-ton/hr; the same stream is 30.5 metric t/hr). Dropped stating the metric value to
avoid a mixed-unit basis.
- **Scale-up biomass feed checked** (`90BIO` across 551 scales). User premise: 47.3 base →
x30 = 1,416 ton/hr. Sim disagrees: x1 (`Scale0010`) = 47.33, x10 (`Scale0100`) = 456.89,
x30 (`Scale0300`) = **1,367.03 short-ton/hr** (2,734,060.5 lb/hr). Scaled cases run off a
**~45.5–45.6 base**, not 47.33 — so x30 is **1,367, not 1,416/1,419**. Only `Scale0010`
carries 47.3; same 45.5-vs-47.3 split still open. Appended scale table to §1.9.
- Review item **1.14 resolved** (user decision, manuscript fixed). User set the manuscript's
pyrolyzer sand-inlet temperature to the **pure sand stream value 1,190 °F** (stream 125XX,
the combustor-side hot-sand delivery), replacing the old **1,128 °F**. Now combustor
1,189 ≈ pyrolyzer-inlet 1,190, so the reviewer's 61 °F drop disappears. Dropped the
alternative of reporting the mixed pyrolyzer feed (**936 °F**, stream 101) — that value is
a blend of hot sand with cold recycle stream 100 (150 °F) and would present a larger
apparent drop. Manuscript-only fix (no code/data change); report §1.14 title → "resolved".
Origin of the paper's old 1,128 °F never identified — moot now.
- Review item **1.14** (sand temperature → Critical_Review §1.14). Reviewer: sand heated
to 1,189 °F in combustor, entering pyrolyzer at 1,128 °F — explain or correct the 61 °F
drop. Traced the 551 sand loop (~1.32 M lb/hr `SAND`) in
`Pyrolysis_Jones_551_into572_Streams.xlsx` (xref `Pyrolysis_551_Scale0100`): combustor
block R-124 = 1,201 °F; hot sand stream to the pyrolyzer valve (125XX) = **1,190 °F**
(≈ the paper's 1,189); sand **entering pyrolyzer** R-110 (stream 101) = **936 °F**;
pyrolyzer outlet (111) = 814 °F. **The 1,128 °F value matches no stream in sim #551.**
Real combustor→pyrolyzer-feed drop = 1,190 → 936 ≈ 254 °F, caused by the hot sand mixing
with cold recycle stream 100 (150 °F, from COL-101) at VAL-125A — a blend temperature,
not a 61 °F sand cooldown. So the reviewer's 61 °F premise rests on a paper number (1,128)
absent from the model; likely Jones design-basis carryover, an older model version, or a
typo. No manuscript-correction decision made yet (see Open).
- Review item **1.9** (Table 8 H2 consumption rate — section still a gap between §1.8 and
§1.10, reserved for this). User holds **3.3 t/hr** (Base column, scale 1) as the reliable
Table 8 hydrogen figure. Traced the generator and verified against source: Table 8 =
util &amp; raw-material consumption-rate table, built by `tea_h2pathways.py:42` via
`funs.get_util_and_rawmaterial_sum` (`funs.py:285`), reading APEA sheets
`RawMaterial Summary` / `Utility Summary` from `Pyrolysis_551_Scale0010_APEA.xlsm`
(551 "Journal Paper" data). The "Hydrogen gas" row = sum of two APEA H2 streams —
250H2 (5831.4 lb/hr = 2.92 t/H) + 532H2 (739.0 lb/hr = 0.37 t/H) = 6570.4 lb/hr =
**3.285 ≈ 3.3 t/hr**. They merge because the extractor strips the leading stream number
(`funs.py:280-282`, `250H2`/`532H2` → `H2`) before `groupby.sum()`. Confirms 3.3 t/hr
traces cleanly to APEA; §1.9 not yet drafted in the report body (see Open).
- Review item **1.9** reconciled to the full 5-number H2 set (Critical_Review §1.9 is
"Hydrogen demand — inconsistent numbers", not a lone Table-8 check). User decisions:
(a) **drop** the Introduction ~35 wt% row — cited reference figure, not a model
contradiction; (b) **fix Methods 2.9 → 3.3 t/hr** (Table 8 is the reliable anchor);
(c) the Methods **12.2 wt%** combines hydrotreater H2 and confuses — replace with
**absolute per-unit H2**. Split by makeup stream: `250H2` 5,831.5 lb/hr = **2.92 t/hr**
(Hydrotreating, area 200), `532H2` 739.0 lb/hr = **0.37 t/hr** (Hydrocracking, area 500),
Σ = **3.3 t/hr** = Table 8. Stage-split of first vs second hydrotreater (R-202 vs
R-220/R-225) not derivable from export sheets — they share the area-200 makeup and a
~22–25 klb/hr H2 recycle circulates; needs `.apw` reactor balance. Also flagged the
75 t/hr hydroprocessing feed as inconsistent with Table 2 (64 wt% bio-oil × biomass ≈
30 t/hr) — feed basis unsettled (Open). §1.9 body rewritten from "confirm 3.3" to the
reconciled set.
- Review items **1.10–1.13** (manuscript numeric/typo fixes → §1.10–1.13). User applied
all four manuscript edits directly: **1.10** abstract number corrected to match body;
**1.11** conclusion-paragraph MJSP number reconciled to the reported result; **1.12**
Table 11 HMWB pseudo-component formula set to **C21H26O8**; **1.13** co-product revenue
figure given its missing **M** (million) marker. All four are manuscript-only fixes (no
code/data change); report sections added recording resolved state. Exact corrected values
not captured in the report body — held by user in the manuscript (see Open).
- Review item **1.8** (Table 1 basis label → §1.8). Reviewer: header "dry basis"
contradicts moisture entries (biomass 10 wt%, char 0.4 wt%). Options: (a) relabel
"as-received", (b) reconcile to one basis, (c) drop the label. User chose **drop
"dry basis"** — removes the contradiction with no value change; moisture rows make
as-received implicit, so an explicit relabel is redundant. Dropped (b) reconcile-to-basis
as unnecessary work for a header-only fix. Ash ultimate-vs-proximate mismatch left open
(not addressed by the label change).
- Review item **1.7** (Table 5 pyrolyzer cap → §1.7). Located the "50 MMBtu/hr rigid
upper bound" in the manuscript: "rigid upper bounds" phrase p11, value p12
(`50,000,000 Btu·hr⁻¹`) — stated with no citation, only "heat transfer physics" /
"industrial availability". Showed it contradicts Table 5: R-110 counts `1 1 1 1 1 2 3`
force cap `C = 10–15 × D_base`, so a 50 cap needs an impossible 3.3–5.0 MMBtu/hr base
duty. User initially proposed cap = 70; corrected — 70 is the **base-scale duty**
(≈2 MJ/kg × 45.5 ton/hr), not the cap. Cap that reproduces Table 5 = **700 MMBtu/hr**
(10× base; scale-10 lands exactly on cap). Dropped option "cap = 70 literally" because it
would force recomputing Table 5 to 1/3/5/8/10/20/30 units (30 pyrolyzers at 30×).
Decision: cap = 700 MMBtu/hr; manuscript p12 fix `50,000,000` → `700,000,000` Btu/hr.
- Review item **1.6** (Table 7 electricity unit → §1.6). Reviewer flagged `$0.065/MMBtu`
as meaningless. Checked the APEA result sheets directly: electricity unit price is
**0.065/kWh** (Cost/Hour ÷ Rate = 0.06500 on every line, e.g. `Pyrolysis_551_Scale0100`
Utility Resource Summary 23,536.56 USD/h ÷ 362,100.9 KW). So the model input was always
/kWh; the paper's `/MMBtu` is a Table 7 typo. Decision: manuscript header fix only, no
code change.
- Log target for this session: `_Base_Revision.md`. Section numbering follows the review
comment file `Critical_Review.md` (obsidian: VibeCoding/Projects/SAF_SNU) — this finding
maps to review item **1.4 MEA reboiler duty**.
- Citation verified (Crossref + OpenAlex): the source is **Rao &amp; Rubin, 2002**, Environ.
Sci. Technol. 36(20) 4467–4475, DOI 10.1021/es0158861. Code comment "Rao, 2022" is a
year typo.
- Traced `ccs_base_case`'s 3315 mmBTU/hr / 862,853 lb/hr against the source (agent read
of Rao &amp; Rubin IECM MEA model documentation). **Neither number appears in the source**;
it gives only specific regen energy (~1900 kJ/kg theoretical; a literature range of
3.8–4.0 GJ/t quoted as "majority of sources") and Q = (Q/L)·L, with simulated duty
95–664 GJ/hr. The model's 8.94 GJ/t is ~2× any figure in that source and not a clean
specific-energy × flow product. Conclusion: 3315 is an undocumented absolute, unsupported
by its cited reference. Caveat: checked the IECM model documentation, not the ES&amp;T 2002
letter's own tables — so 3.8–4.0 GJ/t is not confirmed as the letter's reference value.
- LCA electricity treatment (→ §1.5). Asked whether generated + consumed electricity is
double-counted or netted. Traced Aspen/APEA: plant generates ~68,375 KW (`ELC-` turbine
streams) and consumes 68,533 KW — net ≈ −158 KW (self-supplying, no grid line in
RawMaterial Summary). `funs.py` `get_work_products` already sums all `ELC-` streams to a
net figure. Big negative resources in the Displacement sheet (Crude Oil, Petroleum Fuel)
attributed by user to the **gas + diesel co-products** displacing petroleum, not
electricity — so no electricity double-count. Decision: leave as-is, no code change.
- §1.4 status downgraded (user edit): title "unit-error origin confirmed" → "yet-resolved".
Table/heading relabeled to make the caveat explicit — the 8.94 GJ/t is ~2× the range in
Rao &amp; Rubin's **IECM model documentation**, not the ES&amp;T 2002 letter (still unread).
- §1.3 ammonia (user edit): cracker **resolved**; scrubber **unresolved** — reference
70% capture efficiency vs simulation 99%. Closing the gap needs an unreacted-NH₃ recycle
loop or a more recent scrubber reference.

**Code**

- No script added. One-off `openpyxl` read of `Pyrolysis_551_Scale{0010,0025,0050,0075,0100,0200,0300}_Streams.xlsx`
Material sheet (`90BIO` column, `Mass Flows` row) to pull the overall `90BIO` mass flow per scale
for the §1.15 Table 5 biomass revision.
- No script added. Report §2 "Fuel specification" written in `_Base_Revision.md` (2.1 flash
point dropped, 2.2 specific gravity unit fixed, 2.3 LHV / 2.4 aromatic / 2.5 sulfur verified).
- No script added. One-off `openpyxl` read of `Pyrolysis_Jones_551_into572_Streams.xlsx`
Material sheet (`SAND` mass-flow row + Temperature row) to trace the sand loop
combustor R-124 → pyrolyzer R-110 → combustor and locate the 1,128 °F claim (not present).
- No script added. One-off `PyMuPDF` text extraction of the manuscript PDF to locate the
50 MMBtu/hr cap (p11–12) and Table 5 R-110 counts; `openpyxl` read of base-scale `Heat`
sheet confirmed R-110 duty is not a stream export (heat carried by circulating sand).
- No script added. One-off `openpyxl` read of APEA `Utility Summary` / `Utility Resource Summary` sheets to back-solve the electricity unit price (Cost/Hour ÷ Rate = 0.065 USD/kWh).
- No script added. Read-only trace of CCS energy path in `funs.py`
(`calc_cost_CCS`, `unit_cost_interpolation`, `ccs_base_case`). Reboiler duty is not
computed from first principles — single base case scaled linearly by CO₂ sequestered.
Origin ratio: 3315 mmBTU/hr ÷ 862,853 lb/hr = 3,842 Btu/lb = 8.94 GJ/t.
- No script added. Read-only trace of electricity path: `funs.py` `get_work_products`
(sums `ELC-` work streams), APEA Utility Resource Summary (68,533 KW consumed),
RawMaterial Summary (no grid import), `funs_lca.py` `get_WTWa_pyrolysis` (LCA reads
GREET `Emissions` block only). Generation ≈ consumption; net export ≈ 0.

**Open**

- §2 records LHV/aromatic/sulfur as "verified from simulation" without the literal numeric
values in the body (LHV 44.8 MJ/kg is the only figure written). Aromatic vol% and sulfur value
to be filled from the modified-version manuscript when available.
- §1.14 sand temperature — **closed** this session. Manuscript pyrolyzer-inlet set to the
pure sand stream 1,190 °F; report §1.14 written and marked resolved. Residual (non-blocking):
source of the paper's old 1,128 °F never traced.
- §1.10–1.13 exact corrected values (abstract number, conclusion MJSP figure) not recorded
in the report body — only the fact of resolution is logged. Fill in if the report needs
the literal before/after values.
- §1.8 ash ultimate-vs-proximate mismatch (biomass 0 vs 1; char 7.67 vs 3.5) unresolved —
dropping the "dry basis" label does not fix it. Needs a single reconciled ash figure.
- §1.7 base pyrolyzer duty (70 MMBtu/hr) is a 2 MJ/kg estimate, not read from the Aspen
`.apw` R-110 / combustor block. The 700 MMBtu/hr cap follows from it (10× base) and from
Table 5 counts; confirm the base duty against the model before the manuscript number is
finalized. If real base duty is ~150, the consistent cap shifts to ~1,500.
- §1.3 ammonia scrubber efficiency mismatch: reference 70% vs simulation 99% — unresolved.
Needs unreacted-NH₃ recycle loop or a more recent reference.
- True origin of 3315 mmBTU/hr unknown — not in Rao &amp; Rubin. Whether it came from another
worked case, a different CO₂ basis, or an error is unresolved. Re-derive from 3.8–4.0
GJ/t or document the real source before revising `ccs_base_case`.
- ES&amp;T 2002 letter's own tables not read line-by-line (checked the IECM model
documentation report instead); low risk since that letter is a normalized 500 MWe study
with no 862,853 lb/hr basis, but not visually confirmed.
- Electricity = 14% of reboiler heat: `0.14` factor confirmed as a Rao &amp; Rubin 2002 value
(per author). Not a source of error.
- LCA electricity closed. Net treatment adequate; residual −158 KW net import unmodeled
(negligible). No open item.

### 2026-09-21

**Discussion**

- GHSV for KIER ammonia cracker (IJHE 2024, Cho et al.): catalyst bed volume = 30% of
cracking-tube volume (3:7 catalyst:non-catalyst), bulk-bed basis (no porosity). STP feed
= 163.6 L/hr from NH3 mass flow 3.45e-5 kg/s. Cha et al. 2,827 h⁻¹ identified as TOF, not
GHSV — flagged for manuscript correction. Final dims/value entered by user in §1.
- Log target for this session: new report file `_SAF_COMPOSITION.md` (user chose "New
report file" over the existing H2 price doc).
- "Base simulation" resolved to `Pyrolysis_551_Scale0100_Streams.xlsx` (scale factor 1.0),
matching the base scale used by `tea_ccs.py` / `tea_h2pathways.py`.
- Aromatic grouping decision: reported hydrocarbon aromatics (mono + indanes/indenes +
di/poly) as the headline; phenolics reported separately as oxygenated aromatics because
jet-fuel aromatic specs exclude oxygenates.
- Report renamed `_SAF_COMPOSITION.md` → `_Base_Revision.md` and restructured (user edit):
added Subject / Plan / Base-simulation references at top.
- Correction to the base-simulation resolution above: base sim is the Aspen case
`Pyrolysis_Jones_551_into_571_forQuality_TSOL2_retune.apw`, not `Scale0100_Streams.xlsx`.
- Volumetric % source found: `Pyrolysis_Jones_551_ASW_Recovered_Notes.xlsx` — supersedes
the density-assumption estimate for vol-basis aromatics.

**Code**

- `ghsv_IJHE_2024.py` — GHSV [1/h] from NH3 mass flow + cracking-tube inner diameter and
packed height; asserts STP numerator = 163.6 L/hr.
- No script added. One-off read of the Material sheet, summed the aromatic component
lumps of stream `326SAF` against total mass flow (114,139 lb/hr).

**Open**

- GHSV sensitive to cracking-tube inner dims vs overall reactor shell (200 mm × 575 mm is
the shell + combustion zone, not the tube). Verify dims entered in §1 are tube inner.
- Volume-basis aromatic % only estimated (~24 vol% HC, ~21 vol% mono) — stream export
has no per-component density. Assumed densities miss reported stream volume by 8.6%, so
estimate uncertain. Exact value needs Aspen model densities or a re-export with
Standard-Liquid-Volume-Flow per component.
- Base-invariance across scales not verified (assumed composition is scale-independent).

## Left-over action points

- Volume-basis aromatic % not yet extracted from `Pyrolysis_Jones_551_ASW_Recovered_Notes.xlsx` and reconciled against mass-basis numbers. `_Base_Revision.md` §1.
- Scale-invariance of composition not checked against other `Pyrolysis_551_Scale*` files. `Process_Data/`.
- MEA reboiler duty: 3315 mmBTU/hr / 862,853 lb/hr (= 8.94 GJ/t) shown absent from Rao &amp; Rubin's model docs and ~2× its regen range. Re-derive `ccs_base_case` from 3.8–4.0 GJ/t or document 3315's true origin. `funs.py` `ccs_base_case`, `tea_base_JonesBaseCaseScale.py`. `_Base_Revision.md` §1.4.
- Read ES&amp;T 2002 letter's own tables to fix the exact Rao &amp; Rubin reference reboiler duty before quoting a "per Rao &amp; Rubin" value. `_Base_Revision.md` §1.4.
- Code comment typo `# Rao, 2022` → `Rao & Rubin, 2002` not yet applied (report already corrected). `funs.py:37`.
- §1.3 ammonia scrubber: reference 70% vs simulation 99% efficiency unresolved — add unreacted-NH₃ recycle loop or a more recent reference. `_Base_Revision.md` §1.3.
- §1.7 pyrolyzer cap: apply manuscript edit p12 `50,000,000` → `700,000,000` Btu/hr. Manuscript p12. `_Base_Revision.md` §1.7.
- §1.7 confirm 70 MMBtu/hr base pyrolyzer duty against Aspen `.apw` R-110 / combustor block (cap = 10× base). `Pyrolysis_Jones_551_into_571_forQuality_TSOL2_retune.apw`. `_Base_Revision.md` §1.7.
- §1.8 apply manuscript edit: delete "dry basis" from Table 1 header. Manuscript Table 1. `_Base_Revision.md` §1.8.
- §1.8 ash ultimate-vs-proximate mismatch (biomass 0 vs 1; char 7.67 vs 3.5) still unresolved — reconcile to one ash figure. `_Base_Revision.md` §1.8.

