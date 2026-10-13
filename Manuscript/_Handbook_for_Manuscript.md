# Handbook of Manuscript

## Drafting rules

1. Do not use quotation marks for emphasis. Carry the emphasis in the tone of the sentence, or set the word in *italic*.
2. Do not state scale as a multiple of the base case (no "×" of base). Give the exact SAF production figure instead.
3. Every SI subsection must be referenced in the related part of the main body. If no matching place is found, ask the user.
4. Before generating or editing any `.tex` file, read `Manuscript/main-sc.tex` first. It is the master document, and every `.tex` fragment must follow its class, packages, labels, and `\input` names (see *Manuscript structure* below).

## Manuscript structure (main-sc.tex)

**Template.** Elsevier CAS bundle, single column: `\documentclass[a4paper,fleqn]{cas-sc}`. If the front matter runs past one page, switch to the `longmktitle` option (already present as a commented-out line).

**Packages available to fragments.** `natbib` (`authoryear,longnamesfirst`), `mhchem` v3 (`\ce{}`), `amsmath`, `amssymb`, `booktabs`, `caption`, `threeparttable` (table notes under the table), and `longtable`. `hyperref` and `placeins` are commented out, so fragments must not use `\url`/`\href` or `\FloatBarrier`. Any new package goes into the preamble of `main-sc.tex` and nowhere else.

**Front matter (still template placeholders).** `\shorttitle`, `\shortauthors`, `\title[mode = title]` with `\tnotetext`, two `\author` blocks, each with `\fnmark`, `\ead`, `\credit`, and `\affiliation`, plus `\cortext` for the corresponding author. The abstract still contains the template line `\nocite{*}`, which must be removed. After that come `highlights` (3 items), `keywords` (separated by `\sep`), and `\maketitle`. The graphical abstract is commented out.

**Body.** Each section is a separate fragment pulled in with `\input`. A fragment has no preamble and no `\section{}` of its own, since `main-sc.tex` supplies the heading and label:

| Section | Label | `\input` file | Markdown source |
|---|---|---|---|
| Introduction | `sec:intro` | `1 Introduction.tex` | `1. Introduction.md` |
| Methods | `sec:methods` | `2 Methods.tex` | `2. Methods.md` |
| Results and Discussion | `sec:results` | `3 Results.tex` | `3. Results.md` |
| Conclusion | `sec:conclusion` | `4 Conclusion.tex` | `4. Conclusion.md` |
| Appendix (SI) | `sec:S0`–`sec:S9` | `SI.tex` | `SI. Supporting Information.md` |

The `.tex` file names contain a space and no period after the number (`2 Methods.tex`, not `2. Methods.tex`). Fragments start at `\subsection`.

**Appendix.** `\appendix` is followed by `\input{SI}`. `SI.tex` renumbers its own sections as S0–S9, nests tables within sections, and numbers them `S<n>-<k>` (e.g. Table S9-1). It contains `\section`s of its own, which is the one exception to the no-`\section` rule above. Tables use `table[htbp]` + `\centering` + `\caption`, with labels in the form `tab:<name>`.

**Back matter.** `\printcredits`, bibliography style `cas-model2-names` (author–year), and `\bibliography{main-sc}`, so references go in `main-sc.bib`. This file does not exist yet. Cite with `\cite{key}` (natbib, author–year). The biography is commented out.

**Status (2026-10-03).** Only `SI.tex` exists as a fragment. The four body `.tex` files and `main-sc.bib` are not written yet, so `main-sc.tex` will not compile until they exist.

## Log history

### 2026-10-13 (update 19)

**Discussion**
- The user checked the gasification temperature, which resolves part of the open item in update 18. Our pyrolyzer design is 925 °F (~496 °C), with sand entering at 1,190 °F (~643 °C). Both are below the 870 °C and 1,300 °C gasifier cases in Swanson 2010.

**Open**
- Not yet decided: add "(~500 °C)" to the pyrolysis-temperature clause in the Introduction ¶3.
- Not yet decided: change `SI.tex` line 55 from 1189 °F to 1,190 °F.

### 2026-10-13 (update 18)

**Discussion**
- The user asked for one sentence in the Conclusion saying our SAF is slightly cheaper than earlier work. The comparison uses the update 13 energy-basis values (base `\$25.0/GJ`, CCS 50% `\$28.8/GJ`) against the Introduction range of `\$34.8–91.0/GJ` (CEPCI, 2022 USD).

**Code**
- `4 Conclusion.tex` ¶2: appended a sentence after the CCS 50% lowest-cost sentence, citing `dutta2023model` and `griffin2024opening`.

**Open**
- The `\$/GJ` values depend on E = 31.66 MJ/L (update 13 open item). If 35.2 MJ/L is right, they drop by about 10%, which widens the gap but leaves the claim intact.

### 2026-10-13 (update 18)

**Discussion**
- The user asked for citations for the two uncited clauses added in update 16: pyrolysis runs cooler than gasification, and syngas cleanup adds cost.
- I chose Bridgwater 2012 for the temperature claim. Swanson 2010 is cited with it because it reports gasifiers running at 870 °C and 1,300 °C. For the complexity-and-cost claim I chose Swanson 2010 and Anex 2010.

**Code**
- `main-sc.bib`: appended `bridgwater2012review`, `swanson2010techno` and `anex2010techno`. The metadata comes from Crossref, and a fact-checker agent confirmed it (all 13 Anex authors).
- `1 Introduction.tex`: added `\citep{swanson2010techno, anex2010techno}` after "complexity and cost" in ¶2. Added `\citep{bridgwater2012review, swanson2010techno}` after "lower temperatures than gasification" in ¶3.

**Open**
- The fact-checker rated support as PLAUSIBLE, not CONFIRMED. The Elsevier full texts returned 403, so there are no verbatim quotes for Bridgwater's ~500 °C, Swanson's cleanup cost, or Anex's capital-cost comparison. Check them with institutional access.

### 2026-10-13 (update 17)

**Discussion**
- The user added a sentence to the scale/feedstock paragraph saying that feedstock remains a key factor. I copy-edited it.

**Code**
- `1 Introduction.tex` (line 13): "In other words, the feedstock viability is still playing key-role…" became "In particular, feedstock availability and cost remain key factors in the sustainable production of alternative jet fuels." "In other words" was wrong because the sentence does not restate the one before it. I also fixed the next sentence. It said that a larger plant cuts capital cost *as* sourcing expands, which is not what the comment above the paragraph intends. It now reads "Although increasing plant capacity can reduce unit capital costs, it also raises feedstock costs as sourcing expands…".

**Open**
- Not yet checked whether `chireshe2025cost` supports the rising-feedstock-cost half of the corrected sentence.

### 2026-10-13 (update 16)

**Discussion**
- The user reorganized the Introduction and asked for better conjunctions in the 2nd and 3rd paragraphs (HEFA/FT limits; fast pyrolysis and prior studies), and allowed the 2nd paragraph to be longer.

**Code**
- `1 Introduction.tex`: ¶2 now opens with "However". It adds two consequences (HEFA supply alone cannot keep pace with demand; FT adds complexity and cost) and a bridge sentence leading into pyrolysis. In ¶3, "Meanwhile" became "Fast pyrolysis ... offers such an alternative, because it operates at lower temperatures than gasification". "Moreover" became "In addition", the prior-study sentence now starts with "Accordingly", and "Nevertheless" became "Despite these advances".

**Open**
- The new uncited clauses (pyrolysis runs cooler than gasification; FT cleanup adds cost) are general knowledge. Decide whether they need a citation.

### 2026-10-13 (update 15)

**Discussion**
- The user moved the prior-study sentences from ¶2 to ¶3, because Dutta 2023 and Griffin 2024 are both woody-biomass pyrolysis studies. They now open ¶3 and lead into the existing scale and feedstock-cost argument. The first sentence now says "woody-biomass pyrolysis".

**Code**
- `main-sc.bib`: appended `dutta2023model` and `griffin2024opening`, with metadata from the doi.org BibTeX for each DOI. A. Nolan Wilson is written as `Wilson, A. Nolan`. Correction to update 14: the citations now resolve.
- `1 Introduction.tex`: moved the two sentences to the start of ¶3 and updated the ¶3 comment.

**Open**
- The "more expensive than petroleum jet fuel" claim still has no cited jet-price figure.

### 2026-10-13 (update 14)

**Discussion**
- The user asked for a prior-study context sentence in the Introduction: (1) earlier pyrolysis designs span a wide MSP and GHG range, in 2022 USD on CEPCI; (2) they are still expensive.
- Ranges come from `_Base_Revision.md` §5.2–5.3, CEPCI ×1.506 basis: MSP `\$34.8–91.0/GJ` (Dutta 2023 low end, Griffin 2024 ±10% high end) and GHG 3.9–35.0 g CO₂e/MJ (Dutta Case B to Case C; Griffin 7–13.3 and Jones 2013 28.3–33.3 fall inside).
- Bann 2017, Michailos 2019 and Wang 2022 are left out of the range because they have not been escalated to 2022 USD.

**Code**
- `1 Introduction.tex` ¶2: two sentences appended after the lignin/jet-fraction sentence, citing `dutta2023model` and `griffin2024opening`.

**Open**
- `dutta2023model` and `griffin2024opening` are not in `main-sc.bib` yet, so the citations will show as `?` until entries are added.
- The "more expensive than petroleum jet fuel" claim has no cited jet-price figure.

### 2026-10-13 (update 13)

**Discussion**
- Our SAF energy density is E = 31.66 MJ/L. It is the process volume basis (SAF MJ/hr ÷ L/hr from Aspen), the same litre our MJSP is quoted on (`2 Methods.tex` l.83, `tea_pareto_front.py:198`). The update 10/12 assumption of 34.5 MJ/L is superseded.
- Our MJSP on an energy basis (1Q-2022 USD): `$0.79/L` = `$25.0/GJ`; CCS 50% `$0.913/L` = `$28.8/GJ`; maximum `$3.09/L` = `$97.6/GJ`. Per litre of gasoline equivalent (32.36 MJ/L, the GGE basis of Dutta and Griffin): `$0.81`, `$0.93` and `$3.16/LGE`.
- Compared with the update 12 escalated values: Dutta 2023 is `$27–31/GJ` (CPI) or `$35–40/GJ` (CEPCI); Griffin 2024 is `$53–72/GJ` (CPI) or `$68–91/GJ` (CEPCI). Our base and our CCS 50% case both sit at or below Dutta's lower bound.
- Inconsistency found: SI Table (`SI.tex` l.146–147) lists an LHV of 44.8 MJ/kg and a specific gravity of 786 (it should read 0.786). These imply 35.2 MJ/L, not 31.66. Conversely, 31.66 MJ/L implies 0.707 kg/L at 44.8 MJ/kg (below the Jet A minimum of 0.775) or 40.3 MJ/kg at 0.786.

**Code**
- None.

**Open**
- Reconcile E = 31.66 MJ/L with the SI LHV and specific gravity. One of the Aspen volume basis, the density or the LHV is off. If 35.2 MJ/L is right, MJSP per GJ and the abatement costs (`$/t`) drop by about 10%.
- The specific gravity "786" in `SI.tex` l.147 is missing its decimal point.

### 2026-10-13 (update 12)

**Discussion**
- Our cost basis is 1Q-2022 USD (`2 Methods.tex` l.28; `funs.py:58-59`, `cost_idx_1Q2022 = 3230`, `cost_idx_Jones = 2250` for 2011). The repo does not name this index and has no 2016 value for it. It is not the Nelson–Farrar index (about 2,400 in 2011).
- Dutta 2023 and Griffin 2024 are in 2016 USD and were escalated to 1Q-2022 with two factors that bracket the result:
  - CPI-U: 1Q-2022 average 284.123 / 2016 annual 240.007 = 1.184. Values from BLS series CUUR0000SA0, 2016 annual averaged from the monthly values.
  - CEPCI: 2022 annual 816.0 / 2016 annual 541.7 = 1.506. The 541.7 is confirmed; the 816.0 is from memory (paywalled source).
- Escalated values, in `$/GGE`, `$/LGE` and `$/GJ`:
  - Dutta 2023 Cases A–C: CPI `3.35–3.80`, `0.885–1.004`, `27.4–31.0`; CEPCI `4.26–4.84`, `1.126–1.277`, `34.8–39.5`.
  - Griffin 2024 (±10% band): CPI `6.51–8.76`, `1.72–2.31`, `53.2–71.5`; CEPCI `8.29–11.15`, `2.19–2.95`, `67.6–91.0`.
- A single index applied to the whole MFSP is a simplification: capital, feedstock and operating costs escalate differently. CPI gives the lower bound and CEPCI the upper.

**Code**
- None.

**Open**
- Name and source of the 3230/2250 index; it should be stated in `2 Methods.tex` l.28 and the SI.
- CEPCI 2022 annual (816.0) and the 1Q-2022 monthly CEPCI values are unverified (paywalled).
- Jet LHV behind our `$/GJ` figure: `funs.py:146` gives density from Aspen; the LHV is not checked.

### 2026-10-13 (update 11)

**Discussion**
- The user asked to cite ICAO Doc 05 for the 10% rule in Methods.

**Code**
- `2 Methods.tex` l.103: added `\citep{ICAO2025SustCriteria}` after "10\% reduction in WTWa GHG-100 intensity".

**Open**
- LaTeX not compiled.

### 2026-10-13 (update 10)

**Discussion**
- The user asked for the MSP and GHG ranges and the dollar basis of two NREL catalytic fast pyrolysis (CFP) studies. Values below were read directly from the PDFs.
- Dutta et al. 2023 (CEJ 451, 138485). 2016 USD, 2000 dry MT/d, gasoline and diesel blendstocks (no SAF cut). MFSP `$2.83`/`$3.13`/`$3.21` per GGE for Cases A/B/C (Table 5: `$0.75`/`$0.83`/`$0.85` per LGE). GHG 21.5/3.9/35.0 g CO₂e/MJ (77/96/62% below 93 g/MJ petroleum gasoline).
- Case definitions in Dutta 2023: A = refinery co-hydrotreating with natural-gas SMR H₂ plus acetone and MEK coproducts. B = standalone hydrotreating with H₂ from CFP off-gas plus coproducts. C = co-hydrotreating with natural-gas H₂ and no coproducts.
- Griffin et al. 2024 (Green Chem 26, 9768). 2016 USD, MFSP on the whole fuel pool (gasoline, SAF and heavies). Base `$6.69`/GGE (17-O) and `$6.15`/GGE (20-O); ±10% band `$6.0–7.4` and `$5.5–6.8`/GGE. TCI `$711M`/`$726M`. GHG 7 and 13.3 g/MJ (92% and 85% below 88.7 g/MJ petroleum jet), with H₂ from reformed off-gas.
- Our worst fossil-H₂ case (100.8 g/MJ) is about 3× Dutta Case C (35.0 g/MJ), which also uses fossil H₂. The gap needs a contribution-level explanation in the manuscript.

**Code**
- None.

**Open**
- Griffin 2024 plant scale not stated in the main text (ESI not read).
- The `$/GJ` comparison assumes a jet LHV of about 34.5 MJ/L for our MJSP. Confirm against the density and LHV used in the TEA.

### 2026-10-13 (update 9)

**Discussion**
- The user deleted the section `.md` drafts (Introduction to Conclusion) as outdated. Only `SI. Supporting Information.md` and this handbook remain. Traps 1, 3 and 6 from update 8 are therefore moot.
- Trap 7 (stale commented lines in Results.tex): the user said to leave them.
- Trap 2: CCS 50% is stated as the minimum "on the grid".
- Traps 4 and 8: the user chose the labels "the CCS-only and the ammonia-assisted compliance routes", which replace "two compliant configurations with the lowest MJSP" and "cheapest compliant point of each route".

**Code**
- `3 Results.tex` l.29: "minimum capture rate of 50\%" → "… 50\% on the grid".
- `3 Results.tex` l.65: "two compliant configurations with the lowest MJSP: …" → "the CCS-only and the ammonia-assisted compliance routes: CCS 50\% and Green-ammonia 10\% + CCS 39\%, respectively".
- `SI.tex` and `SI. Supporting Information.md`, Tables S9-6 and S9-7 captions: "at the cheapest compliant point of each route" → "for the CCS-only and the ammonia-assisted compliance routes".

**Open**
- LaTeX not compiled.

### 2026-10-13 (update 8)

**Discussion**
- The user asked for minimal edits in Results and Conclusion. The agent rewrites from updates 3 and 6 were discarded; only numbers that changed are now edited. Correction to updates 3 and 6: Results and Conclusion no longer carry the agents' extra prose, such as the interpolation sentence, the NH₃-route definition and the T&S explanations.
- The NH₃ SHAP value is 0.03147, so it rounds to 0.031, not 0.032 as written in update 6.

**Code**
- `3 Results.tex`, `3. Results.md`, `4 Conclusion.tex`, `4. Conclusion.md`: reset to HEAD (e292c9f), then values only:
  - threshold 75.93 → 80.1
  - CCS 60% → CCS 50%, at 78.99 g/MJ and `$0.913/L`
  - CCS-only crossing ~58% → ~47.5%
  - NH₃ counterpart 10% + CCS 50% → 10% + CCS 39% (`$1.072/L`)
  - abatement: NH₃-only `$3,990` → `$5,647`; CCS 75% `$733` → `$649`; CCS 100% `$742` → `$698`; NH₃ tail `$900–1360` → `$840–1290`; full NH₃ + CCS 100% `$1250` → `$1201`
  - SHAP and T&S values; crossovers 1.59/2.91/4.40/7.21 → 2.51/3.82/5.32/8.13 `$/kg`
  - break-even NH₃ price ~`$450` → ~`$335/t`; T&S crossover shift ~0.45 → ~0.6 `$/kg`
  - compliant-fuel lower bound ~`$1.00` → ~`$0.91/L`
- `SI.tex` and `SI. Supporting Information.md`, Table S9-6: Green NH₃ SHAP changed from 0.032 to 0.031.

**Open**
- Logical traps were reported to the user and not fixed. See the session answer: the Results.md interpolation clause, the "minimum capture rate 50%" wording, the undeclared CCS 39% interpolation, the Methods.md CCS 60% reference, and the commented-out Results.tex lines.

### 2026-10-13 (update 7)

**Discussion**
- The user reverted every Methods edit from updates 3, 5 and 6. The only change kept in Methods is the CORSIA threshold value. Correction to updates 3, 5 and 6: Methods no longer carries the CCS 50% / CCS 39% anchor wording, the counterpart definition, the interpolation note, or the `ICAO2025SustCriteria` citation.

**Code**
- `2 Methods.tex` and `2. Methods.md` reset to HEAD. This also undid two unintended changes: a `\cite`→`\citep` switch and a `han2011well`→`an2011well` key corruption (an earlier edit had dropped the "h").
- `2 Methods.tex` l.103: appended "(89 g CO₂e/MJ \citep{ICAO2025Methodology}), i.e., a threshold of 80.1 g CO₂e/MJ".
- `2. Methods.md` §2.3.3: "0.9 × (conventional-jet WTWa GHG-100) … GREET inventory" → "0.9 × 89 g CO₂e/MJ (ICAO conventional-jet baseline; ICAO Doc 07, 2025) = 80.1 g CO₂e/MJ".

**Open**
- `2. Methods.md` still describes CCS 60% as the reference point (Pareto, abatement and SHAP bullets), which contradicts Results. The user asked for these to stay unchanged.
- `ICAO2025SustCriteria` is in `main-sc.bib` but no longer cited.

### 2026-10-13 (update 6)

**Discussion**
- Ammonia counterpart for SHAP, OAT and crossover (paired against CCS 50%):
  - Was Green NH₃ 10% + CCS 50% (75.18 g/MJ, `$1.098/L`). It was 3.8 g cleaner than CCS 50%, so the comparison was not GHG-matched.
  - The user asked for a counterpart as tight to CORSIA as possible.
  - Proposed NH₃ 10% + CCS 40% (79.55, `$1.074/L`). The user chose **NH₃ 10% + CCS 39%** instead (79.99 g/MJ, 0.11 under the threshold, `$1.072/L`). This is the lowest whole-percent CCS that clears 80.1 with 10% NH₃; the exact minimum is 38.75%.
- Other options not taken: a GHG-matched NH₃ ~29% + CCS 25%, and NH₃-only at the threshold (~54%). Both are off-grid and costlier.
- CCS 39% GHG is interpolated, linear in capture fraction between the CCS025 and CCS050 LCA cases, minus the NH₃ credit (0.1 × 38.1). Its MJSP comes straight from the TEA engine at `ccs_portion = 0.39`.
- New comparison: both routes sit at about 79–80 g/MJ, so the `$0.159/L` gap is the cost of complying via NH₃ instead of more CCS.
- SHAP (NH₃ route): Gray H₂ 0.273, CAPEX 0.101, Co-product 0.086, Electricity 0.057, NH₃ 0.032, Capacity 0.025, T&S 0.017, Biomass 0.001; R² 0.9994.
- OAT CO₂ T&S span is 0.140 (vs 0.165 for CCS 50%).
- Gray-H₂ crossovers: `$2.51`, `$3.82`, `$5.32` and `$8.13/kg` at NH₃ `$270`, `$441`, `$635` and `$1000/t`. Two now fall inside the 1–4 `$/kg` range, and NH₃ below about `$335/t` brings the crossover under `$3/kg`.
- T&S from `$4` to `$45/t` shifts the crossover by about 0.6 `$/kg`, favouring NH₃.
- Co-product crossover: NH₃ wins only below about `$140/t`.

**Code**
- `tea_pareto_shap.py`: NH₃ point changed to `(0.10, 0.39)`. Outputs renamed `*_ccs50_vs_nh10ccs39.*`, and the cache resampled.
- `tea_tornado_shap.py` and `plot_composite.py`: names and outputs follow the same change.
- `plot_ammonia_crossover.py` and `plot_coproduct_crossover.py`: `NH3_BASE_MJSP` changed from 1.098 to 1.072.
- `plot_ammonia_crossover_ts.py`: `TS_SLOPE_NH3` changed to 0.140/41.
- Reran tornado, SHAP, the three crossovers and the composite; all self-checks passed. The composite figure (d, e) now shows CCS 39% and two crossover dots.
- Text:
  - `2 Methods` (.tex/.md): added a sentence defining the counterpart and noting the interpolation.
  - `3 Results` (.tex/.md): SHAP, OAT and crossover narrative updated.
  - `4 Conclusion.tex`: crossover changed to `$2.51–3.82/kg`.
  - `SI` (.tex/.md): Tables S9-5, S9-6 and S9-7 and their captions updated. The S9-4 grid row NH₃ 10% + CCS 50% is kept as a grid fact.

**Open**
- NH₃ SHAP 0.0315 is shown as 0.032 (the boundary case).
- SI caption says "cheapest compliant point of each route", which overstates it for CCS 39%. Consider "ammonia-route counterpart".
- `3 Results.tex` commented lines 56 and 84 still use the CCS 50% NH₃ basis.
- The 0.11 g margin rests on the interpolated GHG; no GREET run exists at CCS 39%.

### 2026-10-13 (update 5)

**Discussion**
- The user pointed to the BibTeX source, `D:\EPEL_biomass\Analysis\Biomass_Ammonia_Elsevier.zip`, and asked to add ICAO Docs 05 and 07.
- Citation split:
  - Doc 05 for the 10% rule (`ICAO2025SustCriteria`).
  - Doc 07 for the 89 g/MJ baseline (`ICAO2025Methodology`).
  - `ICAO2023CORSIA` (LCA Methodology V5) kept only for the ILUC sentence in Methods l.93.

**Code**
- `Manuscript/main-sc.bib`: copied from the zip (81 entries; `cas-refs.bib` is the Elsevier template sample and was not copied). Added `ICAO2025SustCriteria` and `ICAO2025Methodology` after `ICAO2023CORSIA`.
- Baseline citation switched from `ICAO2023CORSIA` to `ICAO2025Methodology` in `2 Methods.tex` l.103, `4 Conclusion.tex` l.5 and `SI.tex` (Table S9-4 caption).
- `2. Methods.md` §2.3.3 now reads "ICAO Doc 07, 2025" and "ICAO Doc 05, 2025".

**Open**
- LaTeX + BibTeX not compiled; `@techreport` `type`/`number` rendering in the Elsevier style is unchecked.

### 2026-10-13 (update 4)

**Discussion**
- A co-author asked for a comparison with the MJSP and GHG ranges of earlier pyrolysis jet/SAF TEA and LCA studies, plus a clearer research-gap sentence. A literature survey was run, then checked by a separate fact-checker agent (DOIs and citation counts from OpenAlex, 2026-10-13).
- Prior pyrolysis jet MJSP: Bann 2017 `$1.52/L` (`$1.02–2.10`, 2015 USD); Michailos & Bridgwater 2019 `$1.98/L` (2017 USD, 100 dry t/h); Wang 2022 `$3.21/L` (rice husk, 600 t/d); Wright 2010 `$0.56–0.82/L` gasoline-equivalent (purchased vs onsite H₂, 2000 t/d, cost year unconfirmed). Our `$0.79/L` falls below the jet-specific TEAs, so any comparison needs the values put on a common dollar year.
- Prior pyrolysis jet GHG: de Jong 2017 reports 54–75% savings vs 87.5 g/MJ (in-situ vs natural-gas SMR H₂); Han 2013 reports 68–76%; Griffin 2024 (catalytic fast pyrolysis) reports 85–92%. All use H₂ from reforming process off-gas, so our grey-H₂ 100.8 g/MJ sits outside this range. The difference comes from purchased SMR H₂.
- Fact-check correction: CCS on pyrolysis-route fuels is prior art (Jafri 2022 10.3389/fenrg.2022.797529; Meerman & Larson 2017 10.1039/c7se00013h; Ahlström 2023 10.1016/j.ijggc.2023.103886). Electrolytic H₂ already appears as a sensitivity case in de Jong 2017. Dropped claims: "first CCS + pyrolysis jet" and "first green H₂". Defensible claims: ammonia-derived H₂ (no study found) and the NH₃ × CCS map with a crossover H₂ price; also a scale-dependent supply curve coupled with train limits for pyrolysis SAF (Wright & Brown 2007 is generic and has no jet or LCA).
- ICAO Doc 06 (8th ed., Nov 2025) lists no pyrolysis or HDCJ default value. This can be stated as part of the gap.

**Code**
- None.

**Open**
- No manuscript text written yet. Waiting for the user to choose the claim direction.
- Unconfirmed: Wright 2010 cost year; de Jong 2015 € year and scale; de Jong 2017 exact 22/41/37 g/MJ (figure only); Rojas Michaga 2022 −121.8 (snippet only). Google Scholar not checked for the ammonia gap.
- Bib entries for the new references not yet added.

### 2026-10-13 (update 3)

**Discussion**
- Reviewer comment: the CORSIA threshold of 75.93 g CO₂e/MJ had no stated basis. It was 0.9 × the GREET conventional-jet WTWa (84.37 g/MJ), not the CORSIA baseline.
- The user chose the ICAO CORSIA baseline of 89 g CO₂e/MJ, which gives a threshold of 0.9 × 89 = 80.1 g CO₂e/MJ. Dropped option: keep 84.37 and rename it "10% below GREET conventional jet". Rejected because the paper claims CORSIA compliance.
- Effect: CCS 50% (78.99 g/MJ, `$0.913/L`) is now compliant and is the cheapest compliant point. It replaces the interpolated CCS 60% anchor (75.14 g/MJ, `$0.977/L`). The CCS-only crossing moves from about 58% to about 47.5% CCS. Green NH₃ 10% + CCS 50% (75.18, `$1.098/L`) stays as the NH₃ comparison route.
- The qualitative conclusion is unchanged: CCS alone is the cheapest compliance route.
- Abatement costs are rebased to CCS 50%: CCS 75% `$649/t`, CCS 100% `$698/t`, and the NH₃ + CCS tail `$840–1290/t`.
- Gray-H₂ crossovers: `$3.13`, `$4.45`, `$5.94` and `$8.75/kg` at NH₃ `$270`, `$441`, `$635` and `$1000/t`. Only `$270/t` falls inside the plotted 1–4 `$/kg` range.
- Both routes now store the same CO₂, so the CO₂ T&S price no longer moves the crossover.
- Sources were checked by two separate agents against the ICAO PDFs:
  - 10% criterion: ICAO Doc 05, *CORSIA Sustainability Criteria for CORSIA Eligible Fuels* (4th ed., June 2025), Criterion 1.1.
  - 89 g/MJ baseline: ICAO Doc 07, 7th ed. (Nov 2025), and the CORSIA LCA Methodology supporting document V8 (Nov 2025, p25).

**Code**
- `funs_lca.py`: new `CORSIA_THRESHOLD = 0.9 * 89.0`.
- `plot_pareto_from_xlsx.py` and `tea_pareto_front.py` now use `CORSIA_THRESHOLD` instead of `0.9 × get_WTWa_conventional`. `lca_SAFcompare.py` line moved from 75.9 to 80.1.
- `tea_pareto_front.py`: abatement anchor is now the CCS 50% grid point (was CCS 60% interpolated), and its self-check asserts the anchor is below `CORSIA_THRESHOLD`.
- `tea_pareto_shap.py` and `tea_tornado_shap.py`: SHAP and OAT point changed from CCS 60% to CCS 50%. Outputs renamed `*_ccs50_vs_nh10ccs50.*`.
- `plot_ammonia_crossover.py`, `plot_ammonia_crossover_ts.py`, `plot_coproduct_crossover.py`: CCS-only base changed to `0.913`. In `plot_ammonia_crossover_ts.py` the T&S slope is now 0.165 (was 0.187) and the strict check was loosened to allow equal slopes.
- Reran: pareto front, pareto xlsx plot, crossovers, SHAP (R² 0.9996 / 0.9993), tornado-SHAP, composite figure.
- Text updated: `2 Methods` (.tex/.md) states the 89 g/MJ basis with citations (`ICAO2025SustCriteria` for the 10% rule, `ICAO2023CORSIA` for the baseline). Also updated: `3 Results`, `4 Conclusion`, `1. Introduction.md`, `SI` (.tex/.md), and SI Tables S9-4 to S9-7.

**Open**
- `main-sc.bib` is not in the repo, so the `ICAO2025SustCriteria` entry has not been added yet. Should `ICAO2023CORSIA` be moved to V8 (Nov 2025)?
- `_Pareto_Front.md` and `_Tornado_Sensitivity.md` still describe CCS 60% and 75.93. They need a dated correction entry.
- `2. Methods.md` line 191: the U.S.-grid example "60% CCS (60.3 g/MJ)" is still there. It is still true, but it is no longer the anchor.
- The LaTeX has not been compiled after these edits.

### 2026-10-13 (update 2)

**Discussion**
- The user asked for the G&A element in the Fig. 2 legend to read "general and admin." instead of "governance and admin.".
- The label is renamed only at plot time. The xlsx is unchanged, so the figure did not need a TEA re-run.
- The user asked to commit only their manual typo and citation edits to the manuscript. The CORSIA-threshold change (80.1, CCS 50%) and the new `main-sc.bib` stay uncommitted, to be handled in another session.

**Code**
- `plot_scale_up_from_xlsx.py`: renames the `governance and admin.` column of `df_base` to `general and admin.` before plotting, then regenerates `Figure/composite_scale_up_mjsp.png`. Cause: legend labels come straight from the column names in `Result/scale_up_base_summary.xlsx`.
- `2 Methods.tex`: the allocation citation `\citep{an2011well}` is corrected to `han2011well`. Cause: the "h" was dropped during a manual edit.
- Commits: `cb435c5` (Fig. 2 legend) and `e292c9f`, which holds only the typo and citation edits: `indsutry`/`feedsotck` in `1 Introduction.tex`, `\cite`→`\citep` in Intro and Methods, a wording fix in the Results T\&S sentence, and `\$` escapes in `4. Conclusion.md`. These were staged from HEAD plus the selected edits, so the working tree still holds the threshold edits.

**Open**
- `tea_scale_up.py` still writes the `governance and admin.` column. Any other figure or table that reads it will still show the old label.

### 2026-10-13

**Discussion**
- Reviewer comment 5: SI S7 supply labels did not match. The reviewer read 3,127,378 t/yr as the residue ceiling and 2.84 as log. That reading is wrong. In the price model (`tea_biomass_price_only.py:7-8`, 783486 / 902296 lb/hr × 8000 h), FR = 2.84 and Log = 3.27 MMt/yr, which matches the 2021 production in `plot_ppt.py`. The labels on the FR–Log Linear and Fixed Elasticity curves were correct; the "ceilings" sentence was the one that was wrong.
- The user chose to write every supply figure in MMt/yr.

**Code**
- `Manuscript/SI.tex` S7 ceilings line and `SI. Supporting Information.md` S8: "FR 3,127,378; log (2,843,071 + 3,274,200) t/yr" changed to "FR 2.84; log 3.27 (combined 6.12) MMt/yr". Cause: in `tea_scale_up_price_models.py` the FR value had been put in the log sum.
- `plot_scale_up_from_xlsx.py`: Fig. 2 (`composite_scale_up_mjsp.png`) panel (b) biomass price changed from \$/lb to \$/t (×2204.62, metric tonne). The FR floor is now 107.3 \$/t; at 1.24 MMt/yr FR–Log Linear is 281.8 and Fixed Elasticity 520.3 \$/t. The xlsx is unchanged and still stores \$/lb.
- Biomass price in the manuscript text moved to \$/t to match Fig. 2. The user considered \$/kg and dropped it: \$0.11 → \$0.12/kg hides the 8.3% step, and SI S7 is already in \$/t.
  - `2 Methods.tex` ¶ feedstock: logs \$0.19/kg → \$192.4/t; residues \$0.11/kg → \$107.3/t.
  - `3 Results.tex` ¶2: floor \$0.11/kg → \$107.3/t; at 0.41 MMt/yr \$0.12/kg → \$116.1/t.
  - `3 Results.tex` SHAP ¶: \$0.11–0.12/kg → \$107.3–116.1/t.
  - `SI.tex` / `SI. Supporting Information.md` Table S8-2: biomass columns \$/lb → \$/t (0.0486 → 107.3, …, 0.2360 → 520.3), computed from the xlsx × 2204.62.
- `tea_scale_up_price_models.py`: deleted the unused `supply_rate_in_tpd`/`supply_rate_in_coverage` (the source of the mislabel, referenced nowhere else).

**Open**
- The source of 3,127,378 t/yr is unknown; it has been in the code since the initial commit.

### 2026-10-11 (update 6)

**Discussion**
- The user asked to bring the MJSP numbers in the synced `.tex` files onto T&S \$10/t, uncommitted, so they can review the edits.
- Method: mapped every old→new scale-up MJSP (HEAD xlsx vs regenerated xlsx) at 2 and 3 decimals and searched all `.tex` files for them. False positives left alone: lignin compound shares and H₂ price in SI, tornado table rows already on \$10/t, and 0.41 MMt/yr scale mentions.
- Re-checked the scale claims in Results ¶1 on the new numbers. All still hold: capital ≈47% of the drop to 0.41 (text: "approximately half"), 88% of the reduction by 0.41 (text: ≈90%), 59% total drop (Conclusion: ≈60%), per-doubling ≈20% below 0.41 and ≈10% above.

**Code**
- `Manuscript/SI.tex`: rows of Tables S8-1–S8-3 (lines 561–614) regenerated from the xlsx; only the numbers changed, 21 rows.
- `Manuscript/3 Results.tex`: ¶1 \$1.64→\$1.65 and \$0.66→\$0.68/L; ¶2 \$0.78→\$0.79 and \$0.84→\$0.85/L.
- `Manuscript/4 Conclusion.tex`: ¶2 \$0.78/L→\$0.79/L (\$3.09/L unchanged; it comes from `pareto_front.xlsx`, already on \$10/t).

**Open**
- Results ¶4 says operating expenditure is ">80% of the gross production cost" at 0.41 MMt/yr. From `scale_up_base_summary.xlsx` it is 72% (gross = all components except co-product sales), and it was 72% under T&S 0 as well. This claim was wrong before today's T&S change.
- `3. Results.md` still has the old values; it is superseded by the `.tex` but has not been synced.

### 2026-10-11 (update 5)

**Discussion**
- The user asked to pull the 1st-draft LaTeX source (`Biomass_Ammonia_Elsevier.zip`, `main` commit `0556baa`) into `Manuscript/`. The zip's `.tex` files (Oct 11) supersede the local copies (Oct 3).
- Skipped `2 Methods_claude.tex` from the zip: it is identical to the old local `2 Methods.tex`.

**Code**
- `Manuscript/`: replaced `1 Introduction.tex`, `2 Methods.tex`, `main-sc.tex`, `SI.tex`, and added `3 Results.tex`, `4 Conclusion.tex` from the zip.

**Open**
- `main-sc.bib`, the Elsevier class/style files and the figure PNGs are in the zip only; `Manuscript/` does not compile on its own.
- `1 Introduction_old.tex` is no longer part of the draft; keep or remove is undecided.

### 2026-10-11 (update 4)

**Discussion**
- The user decided T&S stays on the EGR CO₂ (`622X`): `co2_seq = co2_left·capture + co2_EGR` in `funs.calc_cost_CCS` is intended. Dropped option: charging T&S on `co2_left·capture` only. Update 3 called this charge a modelling error; that was wrong. The \$10/t results (S9-1–S9-4, tornado, SHAP, crossover anchors) stand as they are.

### 2026-10-11 (update 3)

**Discussion**
- The user approved replacing the values in SI S9-1–S9-3 with the T&S \$10/t numbers.
- The user asked what "T&S on EGR CO₂" means. Stream `622X` is 200,000 lb/hr of pure CO₂ split off at `VAL-621` (the same block that releases `623CO2`) and returned as `622XX` into `VAL-610`. It is a recycle loop that sends CO₂ back into the process. `calc_cost_CCS` adds it to `co2_seq`, so T&S is charged on CO₂ that is never shipped or stored: 725,700 t/yr × \$10/t = \$7.26M/yr, or \$0.0128/L at 0.414 MMt/yr. That is the whole S9-4 vs composite gap. The same `co2_seq` also sizes the CCS unit's CAPEX and energy, so the base case (0% capture) carries a CCS unit sized on the recycle flow. That part is common to both runs and is not part of the gap.

**Code**
- `Manuscript/SI. Supporting Information.md`: rewrote the rows of S9-1, S9-2 and S9-3 from the regenerated `scale_up_base_summary.xlsx` and `scale_up_price_model_mjsp.xlsx` (T&S \$10/t). Captions unchanged.

**Open**
- Not decided: whether T&S should apply only to `co2_left·capture` (excluding the recycled `622X`). If so, every \$10/t result (S9-4, S9-5+, tornado, SHAP, crossover anchors) shifts by about −\$0.0128/L.
- Rounding: S9-1 at 0.414 shows 0.793 (sum of unrounded components 0.79251), while S9-4 shows 0.792 (from 0.7925, already rounded to 4 decimals in the xlsx).

### 2026-10-11 (update 2)

**Discussion**
- The user picked T&S \$10/t for the scale-up runs (not a caption note) and asked for a basis check on the other composite figures.
- `composite_pareto_crossover_shap.png` was already on one basis: (a, b) come from `pareto_front.xlsx` (`CO2_TS = 10`); (c, d) from `tea_pareto_shap.py` (`TS_BASE = 10`); (e) uses the `plot_ammonia_crossover.py` anchors 0.977 / 1.098, taken from tornado runs at `TS_BASE = 10`. No re-run was needed.

**Code**
- `tea_scale_up.py`, `tea_scale_up_price_models.py`: added `tea.co2_ts_usd_per_ton = 10.` and re-ran both. `scale_up_base_summary.xlsx` and `scale_up_price_model_mjsp.xlsx` were regenerated, then the composite was redrawn with `plot_scale_up_from_xlsx.py`. Base MJSP at 0.414 MMt/yr is now 0.7925 and full CCS is 1.3337, both equal to S9-4. Each scale shifts by about +\$0.012/L (base and full NH₃, EGR T&S) and about +\$0.068/L (full CCS).
- `tea_scale_up.py` still crashes at line 322 (`KeyError: [18.5]`). An equipment table indexes scale 18.5, which is not in `case_scale`. This bug was already there; the outputs used for the figures are written before line 322.

**Open**
- SI Tables S9-1–S9-3 and `_Scale_Up_Sensitivity.md` still show the T&S-0 numbers and need updating.

### 2026-10-11

**Discussion**
- The user flagged that the 0.414 MMt/yr base MJSP disagrees: SI Table S9-4 (a=0, c=0) gives \$0.792/L and `Figure/composite_scale_up_mjsp.png` gives \$0.780/L.
- Cause: CO₂ T&S basis. `tea_pareto_front.py` sets `co2_ts_usd_per_ton = 10`. `tea_scale_up.py` and `tea_scale_up_price_models.py` keep the default of 0. In `funs.calc_cost_CCS`, `co2_seq = co2_left·capture + co2_EGR`, so the EGR stream `622X` is charged T&S even at 0% capture. That charge, \$0.0128/L, is the whole gap. Re-running the current engine with the Scale0100 551 files gives 0.7797 (T&S 0) and 0.7925 (T&S 10), which match both sources exactly. Engine and input files are unchanged since 2026-09-26, so neither number is stale.
- The scale-up 60% CCS line (T&S 0) and the S9-4 abatement anchor CCS 60% \$0.977/L (T&S 10) have the same basis mismatch.

**Open**
- Not decided: put scale-up on T&S \$10/t (re-run `tea_scale_up.py`, `tea_scale_up_price_models.py`, then redraw the composite and SI S9-1–S9-3), or add a T&S-basis note to S9-4 and the figure caption.
- Not decided: whether the base case (0% capture) should be charged T&S on EGR CO₂ at all.

### 2026-10-03 (update 5)

**Discussion**
- The user revised `2. Methods.md`: dropped the Tornado and NH₃-vs-CCS crossover bullets (sensitivity treatments now three: Pareto front, CO₂ abatement cost, SHAP), moved the driver ranges into the SHAP bullet, removed the results-reminder note, the `ammonia_portion` ≈0.655 optimum, the dynamic-GWP-only clause, and the displacement-bracket sentence.
- The user's edit had stripped every `\$` (e.g. `65.0/MWh`, `/L SAF`) and added bare `$ 635`. All money signs were restored as `\$` before commit.
- The user asked for a Methods `.tex` from the markdown, following `main-sc.tex` (fragment starts at `\subsection`).

**Code**
- `Manuscript/2. Methods.md`: committed with the user's edits plus restored `\$` escapes.
- `Manuscript/2 Methods.tex`: new fragment, §2.1–2.3 as `\subsection`/`\subsubsection` with `sec:methods-*` labels; `§` cross-refs become `\ref`, SI refs point to `sec:S1`–`sec:S8` and `tab:S3-1`, `tab:S9-1`…`tab:S9-7`; MJSP and GHG(a, c) set as equations. Only `jones2013process` is a real key; `rao2002`, `galik`, `katebah2022`, `ijhe2024cracker`, `greet`, `levasseur2010`, `lan2021` are placeholders.

**Open**
- The Pareto bullet still says the band is drawn from the tornado drivers and contrasts with the ±50% tornado range, though the Tornado bullet was removed. Introduction ¶6 also still names a tornado analysis and the crossover.
- `main-sc.bib` is still missing; the fragment has not been compiled (`3 Results.tex`, `4 Conclusion.tex` absent).

### 2026-10-03 (update 4)

**Discussion**
- Discard excel-file citations in `SI.tex` only where the data is already embedded as a table. Scope split: table-caption `source: ...xlsx` clauses (data lives in the table) are removed; upstream-provenance prose (APEA `.xlsm`, GREET `WTWa_LCA.xlsx`, the `Result/` folder umbrella) is kept because no table embeds it.
- Table S9-3 caption: dropped the `scale_up_price_model_mjsp.xlsx` + sheet-name citation but kept the config meaning (full green-NH3 = 100% green-NH3 H2; full CCS = CCS portion 1.0) as plain text.

**Code**
- `Manuscript/SI.tex`: removed 7 excel citations from table captions S3-1, S9-1, S9-2, S9-3, S9-4, S9-6, S9-7. Caption text otherwise unchanged.

**Open**
- None.

### 2026-10-03 (update 3)

**Discussion**
- The user asked for a new Introduction `.tex` that fits the `main-sc.tex` structure. The file holds body text only: `main-sc.tex` supplies `\section{Introduction}\label{sec:intro}`, and the Introduction has no subsections.
- The prose follows the ¶1–¶7 outline in `1. Introduction.md`. Scale figures are left out because §3.1 (0.41 MMt/yr) and the outline's consistency check (0.457 MMt/yr) still disagree.

**Code**
- `Manuscript/1 Introduction.tex`: new fragment with seven paragraphs. Old-manuscript references are placeholder keys `oldref1`–`oldref11`, and claims without a source are marked `\textbf{[cite needed]}`. ¶7 points to `sec:methods`, `sec:results` and `sec:conclusion`.

**Open**
- `main-sc.bib` does not exist yet, so the `oldrefN` keys and every `[cite needed]` still need real BibTeX entries.
- The fragment has not been compiled, because `2 Methods.tex`, `3 Results.tex` and `4 Conclusion.tex` do not exist yet.

### 2026-10-03 (update 2)

**Discussion**
- The user asked the handbook to point to `main-sc.tex` whenever a `.tex` file is generated or edited, and to summarize the manuscript's structure and format.

**Code**
- `Manuscript/_Handbook_for_Manuscript.md`: added Drafting rule 4 (read `main-sc.tex` before any `.tex` work) and a new *Manuscript structure (main-sc.tex)* section, covering the template, packages, front matter, the `\input` map, SI numbering, back matter, and status.

**Open**
- `main-sc.tex` is untracked in git. The four body `.tex` fragments and `main-sc.bib` are missing.
- The front matter is all placeholders, and `\nocite{*}` is still in the abstract.

### 2026-10-03

**Discussion**
- The user asked for Methods to describe the plots newly added to Results. Methods now covers the scale-up breakdown and price-model panels, the Pareto grid, the abatement contour, SHAP, and the NH₃-vs-CCS crossover. The text follows the code (`tea_pareto_front.py`, `tea_pareto_shap.py`, `plot_ammonia_crossover.py`) and the `Result/*.xlsx` sheets, not the old Methods wording.
- Text that conflicted with the code was kept and qualified with appended sentences rather than replaced, per the append-only rule. The abatement base (grey H₂ in the old text, CCS 60% in the code) and the U.S.- vs Korea-grid intensities in §2.3.3 were handled this way.
- New text names no panel letters, because the composite figure was relettered in update 22 and §3 still uses the old letters.

**Code**
- `Manuscript/2. Methods.md` §2.2.1: appended *Scale-up evaluation*, covering the seven scales from 0.041 to 1.243 MMt/yr, the cost-breakdown categories, and the three price models × three configurations (SI Tables S9-1 to S9-3).
- `Manuscript/2. Methods.md` §2.2.4: count of sensitivity treatments changed from three to five. The Pareto bullet gained the 6 × 5 levels, the Korea-grid allocation basis, the additive GHG(a, c) assumption, the supply-curve biomass band (107.3–116.1 \$/t) and the CCS 60% interpolation. The abatement bullet gained the CCS 60% reference and the undefined region. New bullets: *SHAP attribution* (LHS N = 128, gradient-boosted surrogate, R² > 0.99, TreeSHAP; S9-6, S9-7) and *NH₃-vs-CCS crossover* (analytic lines, slopes from OAT spans; S9-5).
- `Manuscript/2. Methods.md` §2.3.3: appended the Korea-grid values used in §3.2 (threshold 75.93, grey base 100.8, CCS 60% 75.14 g CO₂e/MJ).
- Concurrent edit in another session (`3. Results.md`, 23:46 on 2026-10-02): §3.1 Step 1 bullet 2 moved to the 551 basis. It now reads ~20% / ~10% per doubling, 0.41 MMt/yr, and 1.24 MMt/yr. This agrees with the new Methods scales. Commit `671f4e8` (composite abatement panel) also landed during this session.

**Open**
- `2. Methods.md` §2.1.1 says the scale-up reaches 1.23 MMt/yr; the data sheets give 1.243.
- The *Results reminder* blockquote in §2.2.1 is outdated, since §3.1 Step 2 now covers the price models. It has not been removed.
- §3 text and the composite caption still use the pre-update-22 panel letters, with crossover = (b), and the abatement panel (b) has no Results text.
- The new Methods text uses `\$`, but the older Methods text still uses unescaped `$`.

### 2026-10-02 (update 22)

**Discussion**
- The user asked to add the CO₂ abatement-cost plot to the composite Pareto figure as panel (b), move the MJSP crossover to (e), and draw the abatement panel from the datasheet. The datasheet used is the `abatement` column of `Result/pareto_front.xlsx` (CCS 60% base), not `Figure/scale_up_abatement.xlsx`, which is the scale-up series.
- Layout chosen: 3×2 grid, with (a) and (b) on the top row, (c) and (d) SHAP in the middle, and (e) bottom-left. The bottom-right cell is empty.

**Code**
- `plot_pareto_from_xlsx.py`: new `draw_abatement(ax, cax)` reads the recorded `abatement` column and draws the same contour as `pareto_abatement_contour_compliance.png` (no TEA re-run).
- `plot_composite.py`: grid changed to 3×3 (third column holds the colorbars). Panels relabelled a–e. Regenerated `Figure/composite_pareto_crossover_shap.png`.

**Open**
- The 12,511 \$/t cell (NH₃ 75%, CCS 0%) stretches the linear colour scale, so most of panel (b) is one blue band. Log or clipped levels not applied.
- The empty bottom-right cell could hold (e) spanning both columns, or a legend. Not decided.

### 2026-10-02 (update 21)

**Discussion**
- Code review of `tea_scale_up.py` (commit df306cf) used a second model to check the SI. Code and SI Tables S9-1 to S9-3 agree with `Result/scale_up_base_summary.xlsx` and `Result/scale_up_price_model_mjsp.xlsx`. The manuscript text was still on the pre-551, short-ton numbers.
- The user said they had fixed the §3.1 numbers themselves and asked for the Conclusion to be updated. For the rest of §3, they asked only to be pointed to the numbers, not to have them edited.

**Code**
- `Manuscript/4. Conclusion.md` point 1: scale numbers moved to the 551 metric-tonne basis. Crossover 0.457 → 0.414 MMt/yr, range 0.04–1.25 → 0.041–1.243 MMt/yr, "to a third (\$1.46 → \$0.54/L)" → "by ~60% (\$1.64 → \$0.66/L)", "captured by 0.42" → "0.414". The ~90% share is unchanged (88% on S9-1).
- `Manuscript/4. Conclusion.md` point 2: base intensity 87.6 → 100.8 g CO₂e/MJ. 87.6 was the U.S.-grid value; §3.2 and S9-4 use the Korea grid mix.

**Open**
- The §3.1 edits the user mentioned are not on disk in the Revise worktree. `3. Results.md` has no diff and still reads 0.05–1.37 MMt/yr and \$1.48 → \$0.54/L.
- `3. Results.md:26` still says 0.457 MMt/yr; it should be 0.414. The rest of §3.2–§3.3 matches S9-4. The §3.3 SHAP and crossover numbers were checked against the SI text only, not re-run.
- The "exponent ~0.8 to ~1.0" claim in Conclusion point 1 and `3. Results.md:10` comes from the old model; not checked on 551.
- `2. Methods.md:174` still uses 87.6 g CO₂e/MJ (U.S. grid).
- Other review items left open: 2- vs 3-decimal tick labels (`plot_scale_up_from_xlsx.py:37`), unescaped `$69.14 M` (`SI. Supporting Information.md:37`), and the CCS line labelled and coloured 'Mix' (`tea_scale_up.py:126`).

### 2026-10-02 (update 20)

**Discussion**
- The user asked for the CO₂ abatement-cost numbers in §3.2 to be converted from the `\$/L per g CO₂e/MJ` slope form to `\$/t CO₂ avoided`. Converted and reported only; not yet written into the text.

**Code**
- No file changed. Conversion uses the existing project formula (Methods: ΔMJSP·10⁶/(ΔGHG·E), E = 31.66 MJ/L SAF), i.e. slope·10⁶/E.
- Raw-derived values (from ΔMJSP/ΔGHG, not the rounded slopes): Green NH₃ 0.185·10⁶/(3.81·31.66) ≈ \$1,534/t; CCS 0→50% 0.12·10⁶/(21.8·31.66) ≈ \$174/t; CCS 50→100% 0.42·10⁶/(19.0·31.66) ≈ \$698/t.
- Cross-check: ratios 1534/174 = 8.8× and 1534/698 = 2.2× reproduce the text's "~8×" and "~2× cheaper than green NH₃".

**Open**
- §3.2 lines 32–33 still carry the `\$/L per g` slopes; the \$/t swap is proposed, not applied. Awaiting user go-ahead on whether to replace or add alongside.
- Rounded-slope path (0.049/0.006/0.022) gives 1,548/190/695 \$/t — small rounding drift; use the raw-derived figures if the text is edited.

### 2026-10-02 (update 19)

**Discussion**
- The user decided that numbers in the text must match those printed in the figure. Only the numbers in §3.1 were changed. The wording, the derived percentages (~11%, ~3%, ~90%, ~6%), and the x10 phrasing were left as they were.

**Code**
- `Manuscript/3. Results.md` §3.1: SAF production values 0.04, 0.42, 0.457, 0.913, and 1.25 MMt/yr were changed to the figure's axis labels, 0.05, 0.46, 0.46, 0.91, and 1.37 MMt/yr. The smallest-scale MJSP \$1.46 was changed to \$1.48/L, the value printed in panel (a). This closes the update 16 open item.

**Open**
- The axis of panel (a) is labelled with the price-model scales (0.046–1.370 MMt/yr, Table S9-2), but Table S9-1 lists its data at 0.042–1.252 MMt/yr. The text now follows the figure. Table S9-1 and the derived percentages, which were computed on the 0.042 basis, have not been updated.
- §3.2 onward still writes 0.457 MMt/yr (for example in the §3.2 opening sentence), not 0.46 as printed in the figure. This was left alone because the user's instruction covered only §3.1.

### 2026-10-02 (update 18)

**Discussion**
- The user found the panel labels in `composite_pareto_crossover_shap.png` too small, and wanted the labels to come from a script so the figure can be reproduced.

**Code**
- `plot_composite.py`: panel-label font size changed from 12 (rc `axes.labelsize`) to 16, because 12 reads too small on the 12.6-inch-wide figure. The scale-up composite keeps 12. The PNG was regenerated.

### 2026-10-02 (update 17)

**Discussion**
- The user asked for alphabetical panel labels on the composite_* figures. The labels go at the top-left, outside each axes, as (a), (b), and so on.

**Code**
- `plot_composite.py` and `plot_scale_up_from_xlsx.py`: added the panel labels (a–d and a–b). They use the same weight and size as the axis labels. `fontweight='bold'` rendered a hollow outline variant of Helvetica Neue LT Pro, so it was replaced by `axes.labelweight`. Both PNGs were regenerated.

### 2026-10-02 (update 16)

**Discussion**
- The user asked to replace the §3.1 figures with `composite_scale_up_mjsp.png`. The two separate figures (base breakdown and price-model MJSP) became one figure with panels (a) and (b), placed at the top of §3.1.

**Code**
- `Manuscript/3. Results.md`: the first figure link now points to `Figure/composite_scale_up_mjsp.png`, with an (a)/(b) caption. The second figure link (`scale_up_price_model_mjsp.png`) was removed. The text is unchanged.

**Open**
- Panel (a) labels the smallest scale 0.05 MMt/yr with \$1.48/L, but the §3.1 text says 0.04 MMt/yr and \$1.46/L. This has not been reconciled.
- §3.1 Step 2 no longer has a figure of its own. A reference to panel (b) (Figure Xb) should be added to its text, pending the user's approval.

### 2026-10-02 (update 15)

**Discussion**
- The user asked for the data tables behind the Results figures to go into the SI. They went in as a new section, SI §S9, with one table per figure panel plus the one-at-a-time spans cited in §3.3. Scale is given as SAF production, not as a multiple of the base case (Drafting rule 2).

**Code**
- `Manuscript/SI. Supporting Information.md`: appended §S9 with Tables S9-1 to S9-7: base MJSP breakdown, biomass price and MJSP under the three price models (grey H₂, full NH₃, full CCS), the 30-configuration grid with Pareto status, band and abatement cost, the NH₃-vs-CCS crossover points, mean |SHAP|, and the OAT spans. The tables were generated from the `Result/*.xlsx` files and `plot_ammonia_crossover.py` by a scratchpad script; no TEA re-run.
- `Manuscript/3. Results.md`: added six parenthetical SI Table S9-x references (Drafting rule 3). The existing wording is unchanged.

**Open**
- The §3.1 text gives the smallest-scale MJSP as \$1.46/L, but the components in `scale_up_base_summary.xlsx` sum to \$1.479/L (Table S9-1). This has not been reconciled.
- §3.1 Step 1 uses the `scale_up_base_summary` production basis (0.042–1.252 MMt/yr). Step 2 uses the price-model basis (0.046–1.370 MMt/yr). Tables S9-1 and S9-2 therefore list different SAF production values for the same scale.

### 2026-10-02 (update 14)

**Discussion**
- The user asked for all manuscript markdown files on one artifact page, with a home page that links to each. Published privately as https://claude.ai/artifact/Sn7c348D632rDr1KiP7bBp: a home page with one card per file, a tab bar, and a reader view with a section list. The three §3 figures are uploaded alongside it.

**Code**
- Scratchpad `build_site.py` + `site_template.html` (not in the repo): embed the five `Manuscript/*.md` files in one HTML page, rendered in the browser with marked.js. `../Figure/` paths are rewritten to the uploaded `Figure/` copies.

**Open**
- The page is a snapshot. Later edits to the manuscript files need a rebuild and republish. The build scripts sit in the session scratchpad, so they are lost after this session unless moved into the repo.

### 2026-10-02 (update 13)

**Discussion**
- Session opened for the Introduction. The user asked for an overall flow, built from the old introduction (`Biomass_LCA_ACS (2).pdf`, p2–5) and consistent with Results §3.1–3.3, with two arms: scale and biomass supply capacity, and hydrogen economy and sustainability.
- Haulage cost (the focus of old intro ref 8) is reframed as the feedstock supply curve, because §3.1 excludes haulage. SMR+CCS and PEM are dropped as separate pathways; the H₂ options follow the Results grid (grey H₂ vs green-NH₃ share, plus CCS portion).

**Code**
- `Manuscript/1. Introduction.md` (new): paragraph-level outline ¶1–¶7, each with role, kept old-intro content and refs, changes, and the Results section it sets up.

**Open**
- New claims need citations: 0.6-exponent / flat-price TEA practice, biomass supply curves (Galik), single-train limits, Korea NH₃ import strategy.
- The old abstract quotes base-scale numbers (\$2.82/L, \$1.74/L) that conflict with §3.2 at 0.457 MMt/yr; abstract to be rewritten.

### 2026-10-02 (update 12)

**Discussion**
- Updates 9–10 (yellow Total Sum bars at ~0.7 alpha) were committed in `53ee42b` with the user's approval.
- The user then asked to try swapping the Base and Ammonia colors in the lower panel (Base pink, Ammonia yellow), with the upper Total Sum bars in pink. After seeing the trial figure, the user approved it and asked for a commit.

**Code**
- `plot_scale_up_from_xlsx.py`: `line_colors` changed to `['#D57F78', '#D6AE5C', '#85B27C']` (Base / Ammonia / CCS), and `total_color` to `#D57F78B3` (pink, alpha ≈ 0.7). Figure regenerated.

### 2026-10-02 (update 11)

**Discussion**
- The user asked §3.3 to introduce the crossover panel (composite panel b), to argue that green NH₃ price matters more than CO₂ T&S, and to state when the NH₃ route becomes worthwhile: when grey H₂ becomes expensive or the green-NH₃ price falls. The base NH₃ price is 0.288 \$/lb = 635 \$/t, and at the user's request it is now labelled (Base) in the legend.
- Green NH₃ vs CO₂ T&S is argued from the one-at-a-time spans (0.234 vs 0.165–0.187 \$/L) and from how far each moves the crossover: about 5.6 \$/kg H₂ across the ammonia range, against ≤0.45 \$/kg H₂ for the T&S range. The ≤0.45 figure comes from the rejected three-panel T&S variant (`_Tornado_Sensitivity.md` log 2026-10-02), used here only as a number, not as a figure.

**Code**
- `plot_ammonia_crossover.py` `draw()`: the legend label for the line at `AMM_P_BASE` now ends in " (Base)". Re-ran it together with `plot_composite.py`, which regenerated `Figure/ammonia_crossover_mjsp.png` and `Figure/composite_pareto_crossover_shap.png`.
- `Manuscript/3. Results.md` §3.3: added a paragraph, *When green NH₃ beats CCS-only*, with three bullets: the slopes (0.419 vs 0.378), the crossovers at each NH₃ price (1.59 / 2.91 / 4.40 / 7.21 \$/kg H₂), and the conditions under which the NH₃ route wins (expensive grey H₂, or green NH₃ below ~450 \$/t).

**Open**
- The crossover lines are analytic, built from the anchors hard-coded in `plot_ammonia_crossover.py`; no TEA was re-run.
- Figure numbers are still placeholders (Figure Xb).

### 2026-10-02 (update 10)

**Discussion**
- The user asked for the yellow Total Sum bars to be slightly transparent.

**Code**
- `plot_scale_up_from_xlsx.py`: `total_color` is now `#D6AE5CB3`, an 8-digit hex with alpha ≈ 0.7. Only the fill is transparent; the black edge stays opaque. Figure regenerated.

### 2026-10-02 (update 9)

**Discussion**
- The user asked for the upper panel's Total Sum bars to use the lower panel's Base yellow instead of the raw-materials red, so that the base-case total and the Base MJSP line share one color.

**Code**
- `plot_scale_up_from_xlsx.py`: changed `total_color` from `#F0B1AC` to `#D6AE5C` and regenerated `Figure/composite_scale_up_mjsp.png`.

### 2026-10-02 (update 8)

**Discussion**
- The upper panel still looked lighter than the lower one. The user put this down to the segment value labels being too thin and asked for a heavier font.
- The user approved committing the scale-up composite work.

**Code**
- `plotting.py` `plot_stack_bar`: the segment value labels on hatched bars use fontweight 400 instead of 200. Non-hatched callers keep 200.

### 2026-10-02 (update 7)

**Discussion**
- The user asked §3.3 to explain the SHAP beeswarms (composite panels c, d): grey H₂ is the strongest lever, and CO₂ T&S and green NH₃ are named in each case as the factor specific to that route. The numbers come from `_Tornado_Sensitivity.md` §3–4 (mean |SHAP| table).

**Code**
- `Manuscript/3. Results.md` §3.3: added a *SHAP attribution at the two compliance points* paragraph with five bullets. Grey H₂ is the strongest driver (0.310 / 0.274 \$/L). CAPEX, co-product price and electricity come next, and capacity factor and biomass are negligible. CO₂ T&S is 0.025 vs 0.023 (larger at CCS 60% because it captures more CO₂). Green NH₃ (0.031) appears only in the NH₃ case. The closing bullet says the route choice does not change the main driver.

**Open**
- Methods §2.2.4 does not describe the SHAP method (LHS N = 128, surrogate, TreeSHAP); §3.3 states it only briefly.
- Composite panel (b), the NH₃-vs-CCS crossover, still has no text.

### 2026-10-02 (update 6)

**Discussion**
- The user asked for opaque bars in the upper panel. Asked to choose between three options (color fill under the hatch, a stronger red total, or both), they answered "hatch without a fill". This was read as: keep the white fill and change the faded gray hatch and edge lines to black, to match the lower panel. No color fill was added.
- The upper x-axis now uses the lower panel's numbers. The SAF production axes of both panels show at most 2 decimals.

**Code**
- `plotting.py` `plot_stack_bar`: when hatches are used, bar edges and hatch lines are black instead of `#808080`, including the Total Sum bars.
- `plot_scale_up_from_xlsx.py`: the price-model sheet is read before the upper panel is drawn. Its x values (`.2f`) become `df_base.index`, so both panels show 0.05–1.37.

**Open**
- The upper panel's tick labels come from the price-model sheet, but its bar values are still on the metric-tonne basis (0.042–1.252). They line up only if both sheets list the same 7 cases in the same row order.

### 2026-10-02 (update 5)

**Discussion**
- User asked for the combined scale-up figure's file name to start with `composite_`, to match `composite_pareto_crossover_shap.png`.

**Code**
- `plot_scale_up_from_xlsx.py`: the output is now `Figure/composite_scale_up_mjsp.png`, replacing `scale_up_combined_mjsp.png`, which was deleted.

### 2026-10-02 (update 4)

**Discussion**
- User asked for the two §3.1 scale-up figures to be merged into one figure: the base MJSP breakdown on top and the price-model MJSP on the bottom. Both panels are redrawn from their xlsx data sheets.
- In the upper panel, the cost stacks now use hatches instead of fill colors. The Total Sum bars are solid red (`#F0B1AC`, the old raw-materials color).

**Code**
- `plotting.py` `plot_stack_bar`: new `ax`, `hatches` and `total_color` arguments. When `ax` is given, the function draws into that axes and does not save the figure. When hatches are used, segment labels get a white box so they stay readable. Existing callers behave as before.
- `plot_scale_up_from_xlsx.py`: builds a 2×1 figure from `Result/scale_up_base_summary.xlsx` and `Result/scale_up_price_model_mjsp.xlsx` and writes `Figure/scale_up_combined_mjsp.png`. It no longer writes the two separate PNGs.

**Open**
- The two panels use different x-axis values: the upper panel is on a metric-tonne basis (0.042–1.252), the lower one is not (0.046–1.370). `scale_up_price_model_mjsp.xlsx` needs to be regenerated on the metric-tonne basis.

### 2026-10-02 (update 3)

**Discussion**
- User asked for the sensitivity analysis to sit in its own section. §3.2 Step 4 is now §3.3; §3.2 keeps Steps 1–3.

**Code**
- `Manuscript/3. Results.md`: Step 4 became §3.3 *Sensitivity of the trade-off*, with a one-line lead. The text is unchanged, except that "Steps 1–3" now reads "§3.2".

**Open**
- The SHAP panels (c, d) may also belong in §3.3, but they still have no text.

### 2026-10-02 (update 2)

**Discussion**
- Drafted Results §3.2 from `_Pareto_Front.md` (§3 grid, §5 abatement, §6 sensitivity, §7 CCS 60%). Its §4 was not used because it is stale: it still says CCS-only cannot reach CORSIA.
- §3.2 is written around the composite figure (`composite_pareto_crossover_shap.png`), but only panel (a) has text so far.
- Scale is given as 0.457 MMt/yr (drafting rule 2), the same figure §3.1 uses. CCS 60% points to SI §S7 for its interpolated GHG (drafting rule 3).

**Code**
- `Manuscript/3. Results.md`: appended §3.2 *Cost–emission trade-off of hydrogen source and CCS*, written in four steps: lever geometry, CORSIA compliance, abatement vs CCS 60%, and H₂-price sensitivity.

**Open**
- Panels (b–d) of the composite figure (NH₃-vs-CCS crossover, SHAP) are not yet described in §3.2.
- Methods §2.2.4 gives the knee scale as 0.41 MMt/yr; §3.1 and §3.2 use 0.457. Methods also costs abatement against the grey-H₂ base, while §3.2 uses CCS 60%.
- Methods §2.3.3 and SI §S7 quote U.S.-grid intensities (87.6 / 49.5 / 60.3 g CO₂e/MJ), but §3.2 uses the Korea grid mix (100.8 / 62.7 / 75.14).
- The figure number in §3.2 is a placeholder (Figure Xa).

### 2026-10-02

**Discussion**
- §3.1 final two figures unified: `scale_up_wo_price_model_base_summary.png` restyled to match `scale_up_price_model_mjsp.png` (SA_RC fonts, same figure size). Both shortened vertically 4.5 → 3.6 in (now 9 × 3.6 in). Base-summary x labels now 3 decimals like the price-model figure.
- Combined `pareto_front.png` (a), `ammonia_crossover_mjsp.png` (b) and `shap_beeswarm_ccs60_vs_nh10ccs50.png` (c, d) into one 2×2 figure, laid out like the user's mock-up. The panels are redrawn from their data, not pasted in as images.

**Code**
- `plotting.py` `plot_stack_bar`: `fs=None` keeps SA_RC label/tick sizes (value labels sized off `font.size`); other callers unchanged (default `fs=15`). Added type hints.
- `tea_scale_up.py`: base_summary call uses `figsize=(9, 3.6)`, `fs=None`, 3-decimal x labels; `saf_mmt` rounding 2 → 3 decimals.
- `tea_scale_up_price_models.py`: both figures `figsize=(9, 4.5)` → `(9, 3.6)`. Both PNGs regenerated.
- `plot_composite.py` (new): writes `Figure/composite_pareto_crossover_shap.png`. Reads `Result/pareto_front.xlsx` and `Result/shap_samples.npz` (cached LHS samples + SHAP values). No TEA re-run.
- `plot_ammonia_crossover.py` and `plot_pareto_from_xlsx.py`: plotting moved into `draw(ax)` (with a `main()` wrapper) so the composite can reuse it. Standalone output is unchanged.
- `_PLOTTING_STYLE.md`, `tea_pareto_front.py` and `plot_ammonia_crossover.py` (`SA_RC`): `ytick.labelsize` changed 10 → 12, so x and y tick labels are both 12 pt.
- `plot_composite.py`: subfigures replaced with one 2×3 gridspec whose third column holds the colorbar. The upper plot boxes now match the lower ones in width; the top-right cell stays empty.
- §3.1 figures now redrawn from data sheets (user request): `tea_scale_up.py` writes `Result/scale_up_base_summary.xlsx`, `tea_scale_up_price_models.py` writes `Result/scale_up_price_model_mjsp.xlsx` (sheets `biomass price`, `MJSP Base/Ammonia/CCS`). `plot_scale_up_from_xlsx.py` (new) redraws both PNGs with no TEA re-run: shared 9 × 3.6 in canvas, SA_RC with 12 pt ticks. The base-summary legend is now inside the box (`plot_stack_bar` got `legend_kw`, `ytop`; default stays outside for other callers). It had been left outside because `plot_stack_bar` hard-coded the outside legend and the first pass only changed size and fonts.
- `plot_composite.py`: top and right spines dropped, so only the x and y axis lines remain (composite only; `SA_RC` unchanged). Canvas shrunk 13 × 10.5 → 11 × 9 in so the fonts read larger relative to the plots.
- `plot_composite.py`: removed the in-panel text labels (the "WTWa GHG: Allocation, Korea grid mix" note and the beeswarm case labels "CCS 60% …" and "Green NH₃ 10% + CCS 50% …"). The beeswarms no longer say which case they show.
- `plot_ammonia_crossover.py` `draw`: the "base H₂" annotation is replaced by a legend entry on the dotted line, "Base gray H₂ price (1.50 \$/kg)". This also changes the standalone figure.
- `plot_composite.py`: canvas widened 11 × 9 → 14 × 9 in.
- `plot_ammonia_crossover.py` `draw`: thicker lines and bigger markers. CCS line lw 1.4 → 2.2; NH₃ lines lw 0.7 → 1.6; line markers ms 3 → 6; crossover dots 4 → 7; base-H₂ dotted line lw 0.6 → 1.2. This also changes the standalone figure.
- Committed `1d29e71` (composite, crossover, `_PLOTTING_STYLE.md`, PNG); the handbook was left out because it also holds another session's uncommitted entries. A concurrent session had already committed earlier parts of this work in `6fd65a9`.
- `plot_composite.py`: trial canvas at 90%, 14 × 9 → 12.6 × 8.1 in (same aspect). Not committed.
- Legend locations (user): pareto `loc='best'` → `'lower left'` (`plot_pareto_from_xlsx.py`); crossover `'upper left'` → `'lower right'` (`plot_ammonia_crossover.py`). Both are set inside `draw`, so the standalone figures change too.
- Pareto legend split into 2 columns (`ncol=2`), with green NH₃ shares in the first column and CCS rates + CORSIA in the second. This clears the CCS 100% / Green NH₃ 50% point that the single-column legend covered.
- `plot_ammonia_crossover.py` `draw`: the base-H₂ line now uses the CORSIA line style (`#333333`, `--`, lw 1.0; was gray dotted, lw 1.2). Crossover dots shrunk from ms 7 to 4.
- Crossover legend relabeled (user): "CCS-only", "Green NH₃ \$270/t … \$1,000/t" and "Base gray H₂ price". The "(base)" tag and the "NH₃ 10% + CCS 50%" prefix were dropped (`plot_ammonia_crossover.py`).
- Beeswarm driver "Ammonia" is now shown as "Green NH₃", renamed for display only in `plot_composite.py`. The `shap_samples.npz` cache keys keep 'Ammonia', so no re-sample was needed.

**Open**
- x-axis basis mismatch: base_summary uses metric MMt/yr (0.042 … 1.252), price-model figure uses short tons/1e6 (0.046 … 1.370) under the same "MMt/yr" label (`tea_scale_up_price_models.py:130`, no ×0.907185).
- `tea_scale_up.py:319` crashes (`KeyError: [18.5]`) after the figures are saved; pre-existing, not touched.
- Panel (b) has no Excel source. Its lines are analytic, built from the `_Tornado_Sensitivity.md` §5 constants hard-coded in `plot_ammonia_crossover.py`. The beeswarms need the per-sample `shap_samples.npz`; the xlsx holds only mean |SHAP| values.
- The "WTWa GHG: Allocation, Korea grid mix" label was removed from `plot_pareto_from_xlsx.py` during this session by a concurrent edit. `plot_composite.py` re-adds it to panel (a) only.
- Other inline `SA_RC` copies still have `ytick.labelsize: 10`: `tea_scale_up.py`, `tea_scale_up_price_models.py`, `plot_scale_up_mjsp_bar.py` and `plot_coproduct_crossover.py`. The two `tea_scale_up` files were being edited by a concurrent session.

### 2026-09-30

**Discussion**
- Decided to drop the PEM-electrolysis hydrogen pathway from the manuscript. Hydrogen-supply comparison now covers only green-ammonia-cracked H₂ and SMR-with-CCS grey H₂.
- New per-session log target: this file (`Manuscript/_Manuscript_Revision_Log.md`), separate from `_Tornado_Sensitivity.md` and `_Base_Revision.md`.
- Units in Methods switched to annual basis at user request: mass flows → MMt/yr, energy duties → GWh/yr, prices → \$/t and \$/MWh (prices converted too, not just flows). Conversion basis: 8000 h/yr, 1 t = 2204.62 lb, 1 MMBtu = 0.293071 MWh. Kept file's existing unescaped-\$ convention (did not apply the CLAUDE.md \$ escaping, since the manuscript file uses raw \$ throughout).
- **Correction (same day):** first-pass process-flow numbers were wrong — they used the Jones 45.5 basis and mixed short/metric tons. Re-sourced from the 551 sim (`Pyrolysis_551_Scale0010`, verified in `_Base_Revision.md`): the old prose `t/hr` values were **short tons**, and MMt = metric megatonne. Mass basis decided = **metric tonne** (user: the headline scale-up graph already uses metric via ×0.907185).
- Discovered the biomass-price figure (`tea_biomass_price_only.py`) used a **short-ton** x-axis (`unit_MTy = 1/2000/...`) while the headline MJSP figure (`tea_scale_up.py`) uses metric — an inconsistency. Fixed the price figure to metric.
- Located the true source of the unit-train counts: `D:\EPEL_biomass\Scaling_Up_Study_ver551_organized.xlsx` (Sheet2 = per-unit "Number of Replicas" summary; Sheet1 = the sizing metric each count derives from). Replica count = `ceil(total duty / single-train cap)`, cap = max per-replica value.
- **R-110 cap discrepancy found:** this source gives pyrolyzer combustor R-110 **base heat 44.75 MMBtu/hr, single-train cap 447.5 MMBtu/hr** (10× base; reproduces the 1/1/1/1/1/2/3 replica pattern exactly). This contradicts the manuscript / `_Base_Revision.md` figure of base 70 / cap 700 MMBtu/hr. Real cap = 447.5, not 700. The queued p12 edit `50,000,000 → 700,000,000` Btu/hr is wrong; correct target is **447,500,000 Btu/hr**. Not yet applied — awaiting user go.
- Clarified "compressors follow the same numbering-up as pyrolyzer": same *method*, not same *schedule*. Only C-101 and C-401 share R-110's `1/1/1/1/1/2/3`; C-110/C-147 split at 7.5×, MC-610 at 2.5× (→20 units at 30×), expander C-231 needs 2 units even at base (→54 at 30×).
- **Checked the actual cell equations:** the "Number of Replicas" row is **hand-entered integers, not a formula**. Only formula is `per-replica load = Total ÷ n`. So `n` is the denominator and per-replica is the output; the cap is implicit (= the plateaued per-replica value). Verified `n = ceil(Total ÷ cap)` reproduces counts exactly for 7/9 units with these exact caps: C-101 15,807,904.02 cuft/hr; C-110 17,569,960.50; C-147 17,772,607.11; C-401 15,231,525.66; R-110 447,500,000 Btu/hr; E-616 955,358,000 Btu/hr; GT-612 441,072.56 hp. **Two units break the ceil rule (over-provisioned):** MC-610 at 30× (20 vs ceil 15, total/cap=15.0 exactly) and expander C-231 at 2.5×/5× (6 vs 5, 10 vs 9).

**Code**
- `Manuscript/2. Methods.md`: removed PEM-electrolysis from §2.1.1 hydrogen-supply-flexibility bullet and deleted the PEM-alternative sentence (40 kWh/kg, 2000 \$/kW electrolyzer, Korean-PV capacity factor) from §2.2.2.
- `Manuscript/2. Methods.md`: unit conversion across §2.1.1–§2.2.4. Duties (pyrolyzer 1641 / base 164 GWh/yr; cracker ceiling 403 GWh/yr; Rao regen heat 7772 GWh/yr). Prices (grey H₂ 1499 \$/t; NH₃ 635 base / 270–1000 \$/t; feedstock 107.3 / 192.4 \$/t; utilities 65.0 & 49.1 \$/MWh; tornado grey-H₂ 1000–4000 \$/t). FR–Log-Linear supply curve re-derived to `price = supply × 25.08 + 33.30 $/t` (supply in MMt/yr). Supply thresholds 2.84 / 6.12 MMt/yr; demand slope scale × 0.330 MMt/yr (from the price model's nominal 91,014 lb/hr).
- `Manuscript/2. Methods.md` §2.1.1 flows corrected to 551 metric values: biomass feed **0.343** (94,654 lb/hr), bio-oil→HT **0.244** (67,321 lb/hr, 71 wt%), make-up H₂ **0.0238** total (250H2 **0.0212** / 532H2 **0.00268**) MMt/yr. CCS base stream 3.13 MMt/yr (Rao reference, unchanged).
- `tea_biomass_price_only.py:57`: `unit_MTy` short ton → metric tonne (`1/2204.62/1e6*8000`), so the biomass-price figure x-axis is metric MMt/yr. Figures NOT regenerated.
- `Manuscript/SI. Supporting Information.md` §S3: appended **Table S3-1** (per-unit single-train caps + replica counts for C-101/C-110/C-147/C-401/MC-610/C-231/R-110/E-616/GT-612 from `Scaling_Up_Study_ver551_organized.xlsx`), with notes that R-110 447.5 MMBtu/hr supersedes the 700 figure and that MC-610/C-231 are over-provisioned vs `ceil(total/cap)`. Old 700 MMBtu/hr bullet left in place (append-only rule) — flagged for reconciliation.
- `Manuscript/2. Methods.md` scale-up paragraph: added a sentence pointing to SI Table S3-1 and stating that replicated parallel trains capture none of the single-unit economies of scale (mechanism behind the 0.8→1.0 exponent rise).
- **Demand slope resolved** (from `_Base_Revision.md:232-238`): linear slope = 0.330 MMt/yr per scale = 91,014 lb/hr (NC column, linear: 0.826/2.5 = 0.330). The 0.343 MMt/yr / 94,654.5 lb/hr is the x1 *total feed* incl. elevated moisture in `Scale0010` and is non-linear (0.839/2.5 = 0.336). Two different quantities — Methods §2.2.1's 0.330 slope is correct; no edit needed.

**Open**
- PEM references may still exist in code/other docs (`tea_h2pathways.py`, `funs.py`, `SI. Supporting Information.md`, `_Base_Revision.md`). Not touched — confirm whether those should be purged too.
- Engine (`funs.py`, price models) still computes in lb/hr and MMBtu/hr; the Methods prose is now a presentation-layer conversion. Numbers not re-verified against the engine — confirm the re-derived FR–Log-Linear coefficients (25.08, 33.30) and all converted constants match the code before submission.
- Results (`3. Results.md`) and SI still use the old units — not yet converted; confirm whether they should follow.
- **91,014 vs 94,654 lb/hr:** the price model / biomass-price figure use a nominal 91,014 lb/hr demand slope (Methods §2.2.1 → 0.330 MMt/yr per scale), but the actual 551 base feed is 94,654 lb/hr (§2.1.1 → 0.343). Confirm whether the demand slope should be updated to 94,654 (would shift the figure's critical scales).
- Biomass-price figure regeneration pending (ran the `unit_MTy` fix but did not re-plot). Its y-axis is still \$/lb — decide whether to convert to \$/t to match Methods.
- Short-ton `/2e3` and `/2000` still used elsewhere (`funs.py:139` SAF ton, `tea_h2pathways.py:87`, `tea_scale_up_price_models.py:103`); these feed metric conversions downstream (e.g. `tea_scale_up.py` ×0.907185) — left as-is, not audited for consistency.
- **R-110 base/cap:** decide 44.75/447.5 MMBtu/hr (from `Scaling_Up_Study_ver551_organized.xlsx`) vs the 70/700 in manuscript & `_Base_Revision.md`. If the xlsx is authoritative, update `2. Methods.md` (1641/164 GWh/yr → recompute from 447.5/44.75), `SI. Supporting Information.md:47`, `_Base_Revision.md §1.7`, and the p12 edit target (→447,500,000 Btu/hr). Not applied.
- Manuscript SI/Methods state "compressors/turbines/expanders follow the same numbering-up" without per-unit caps; the xlsx now supplies them (C-101 ~2772 HP, C-110 ~9980 HP, C-147 ~7420 HP, C-401 ~192,935 HP, MC-610 ~8.69M cuft/hr, C-231 ~1944 HP, GT-612 ~441,072 hp, E-616 955.36 MMBtu/hr). Decide whether to add a per-unit cap table (Table 5 / SI S3).
