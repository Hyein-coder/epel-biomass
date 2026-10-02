# Handbook of Manuscript

## Drafting rules

1. Do not use quotation marks for emphasis. Carry the emphasis in the tone of the sentence, or set the word in *italic*.
2. Do not state scale as a multiple of the base case (no "×" of base). Give the exact SAF production figure instead.
3. Every SI subsection must be referenced in the related part of the main body. If no matching place is found, ask the user.

## Log history

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
