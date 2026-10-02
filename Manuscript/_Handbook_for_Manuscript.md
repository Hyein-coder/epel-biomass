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
