# Workframe — TEA Scripts

Reference for writing/editing/analyzing TEA code and results.

## Version lineage (process design iterations, not sequential order)


| Series  | Scripts                                                                                      | Engine                   | Status                                                         |
| ------- | -------------------------------------------------------------------------------------------- | ------------------------ | -------------------------------------------------------------- |
| **541** | `tea_base_JonesBaseCaseScale.py`                                                             | inline funcs from `funs` | ancestor, monolithic                                           |
| **572** | `tea_scale_up.py`, `tea_h2pathways.py`, `tea_ammonia_mix.py`, `tea_scale_up_ammonia.py`, ... | `TEA` class              | mid-gen, `Pyrolysis_Jones_572_2MC_*` data                      |
| **551** | `tea_ccs.py`, `tea_co2_portion.py`, `tea_scale_up_price_models.py`                           | `TEA` class              | **current (Biomass_LCA_ACS.pdf)**, `Pyrolysis_551_Scale*` data |


Latest = 551 trio. `tea_co2_portion.py` is newest.

- `tea_co2_portion.py` — CCS portion sweep 0→90%, TEA cost joined with WTWa LCA (`funs_lca`). Writes `Result/CO2_ver551_0##.xlsx`. Scale 30.
- `tea_ccs.py` — CCS portion sweep 0/25/50/75/100%, MJSP stack bar + util/raw material breakdown + `TEA_summary_CCS.xlsx`. Scale 1.
- `tea_scale_up_price_models.py` — 3 biomass price models (FR Price / FR-Log Linear / Fixed Elasticity) × 7 scales, Base/Ammonia/CCS. Biomass price vs MJSP figure.
- `tea_h2pathways.py` — 551-applicable (active data `Pyrolysis_551_Scale0010`, labeled "Journal Paper"; 572 path commented "Thesis"). CCS-free (`ccs_portion=0`). H2-source compare Base/SMR/Ammonia/PEM + Mix (`ammonia_portion=.5`), scale 1. Figures only (`mjsp`, `equipment`, `opex`), no `Result` xlsx. Also emits subunit LCOH (SMR/Ammonia/PEM), emission lb/MJ, util+raw-material rate table (tons/hr). Natural host for H2 / green-ammonia price dynamics.

## Calculation procedure

All 551/572 scripts route through `TEA.economic_analysis` (`funs.py:789`).

```
1. Read Aspen streams (Material/Heat/Work sheets)
2. Products    -> hourly_revenue, energy_production, annual SAF
3. Sub-units by cost interpolation from literature base cases:
     CCS (Rao 2022) · PSA H2 recovery (Byun 2020) · R-510 hydrocracking (Jones 2013)
     · hydrotreat catalysts (Ru/Mo charging)   <- ccs_portion scales the CCS unit
4. Main process CAPEX/OPEX  <- APEA xlsm (Project Summary sheet)
5. resume_cost_summary  -> combine main + sub-units
6. cal_MJSP  -> MJSP [$/L SAF]  (annual OPEX / annual SAF production)
7. H2-source swap: strip grey-H2 cost from main, add SMR/Ammonia/PEM/Mix LCOH
8. return df_mjsp (rows = H2 source, cols = cost category)
```

Key knobs:

- `ccs_portion` — fraction of CO2 captured (scales CCS unit cost).
- `ammonia_portion` — adds a "Mix" H2 case (partial grey + ammonia-cracked H2).

Cost basis: all costs shifted 1Q-2022 → 2011 base via `bi_22to11 = 2250/3230`.

## What changed 541 → 551

- **541 monolith → TEA class**: inline procedure extracted into `funs.TEA` methods, reused by all newer scripts. 541 hardcodes Base + SMR-CCS only.
- **Data version**: 541 → 572 → 551 process files. 551 scripts still carry commented-out 572 paths (mid-migration leftovers).
- **New in 551**: LCA coupling (`funs_lca`, WTWa GHG), biomass price models, CCS portion sweeps. 572-era `tea_scale_up.py` had scale-up + H2 pathways but no price models / LCA integration.

## Python environment

- Scripts run on Miniconda base (`C:\Users\user\miniconda3`, Python 3.13.5). No project env file existed before 2026-10-15.
- `requirements.txt` (repo root): `pip list --format=freeze` of that base env, 176 pins. Rebuild: `pip install -r requirements.txt` on Python 3.13.
- Full backup of all 23 Miniconda envs: `D:\conda_env_backup\` (`packed/` conda-pack archives, `yml/`, `pip/`, `RESTORE.txt`).
- `opt_delete_cache.py:35` hardcodes `C:\Users\Hyein\anaconda3\envs\Analysis\...` (old machine), stale.

- Update 2026-10-15 (supersedes the 176-pin line above): `requirements.txt` now holds only the 8 packages the code imports (numpy 2.1.3, pandas 2.2.3, openpyxl 3.1.5, matplotlib 3.10.6, scipy 1.15.3, scikit-learn 1.7.2, shap 0.52.0, pywin32 311), pinned to the base env versions. Full base freeze kept at `D:\conda_env_backup\pip\base_full_freeze_requirements.txt`.
- pip-only setup (no conda): `py -3.13 -m venv .venv` then `.venv\Scripts\python -m pip install -r requirements.txt` (python.org 3.13.5). `.venv/` is gitignored. Reproduces base MJSP and WTWa bit-for-bit vs Miniconda.
- Not in `requirements.txt`: `GPyOpt`, `pyomo`, `pyautogui` (imported by `opt_*.py` but absent from base env too, so those scripts were never run from base).

## Log history

### 2026-10-15

**Discussion**
- User is uninstalling Anaconda/Miniconda. Confirmed project depends on Miniconda base env (not full Anaconda; no `anaconda3` on this machine).
- User asked for package lists plus real package-file backups of every env. Backup put on D: (1.7 TB free) instead of C: to keep it away from the uninstall.

**Code**
- `requirements.txt`: new, base env pins via `pip list --format=freeze` (plain `pip freeze` emits conda `@ file:///` paths that break off-machine).
- `D:\conda_env_backup\`: for each of 23 envs, `conda env export` yml, `conda list --explicit`, pip freeze list, and `conda-pack` archive (`--ignore-editable-packages --ignore-missing-files`). 16 GB total; all 23 archives pass `gzip -t`. `conda-pack` pip-installed into base to do this.

**Open**
- Archives not test-restored (unpack + import) yet.
- Editable pip installs (if any) are excluded from archives; their source dirs must be kept separately.
- `opt_delete_cache.py:35` stale anaconda3 path not fixed.

**Code (later same day)**
- `requirements.txt` trimmed to 8 import-level pins. The full base freeze listed conda internals (`conda`, `libmambapy`, `menuinst`, ...) that pip cannot install.
- `.venv` built with pip only on python.org Python 3.13.5; `.gitignore` gets `.venv/`.
- Reproduction check (scratch script, no repo writes; inputs as `tea_h2pathways.py` + `tea_co2_portion.py`): conda and venv outputs identical to 10 decimals. Base 551 scale-1 MJSP [\$/L]: Base 1.638, SMR 2.758, Ammonia 3.483, PEM 5.751, Mix(50%) 2.604. WTWa GHG-100 [g/MJ] US-grid Allocation: Base 87.57, SMR 67.13, Ammonia 49.45, PEM 47.12 (Conventional 84.37); KR-mix: Base 100.83, SMR 80.42, Ammonia 62.74, PEM 60.40. Matches `_Scale_Up_Sensitivity.md` (1.638, 3.483) and `_Pareto_Front.md` (87.57 / 100.83).

**Open (later same day)**
- Figure-producing scripts (`tea_h2pathways.py` etc.) not run in the venv; only the calculation path was checked.
- `plot_composite.py` run in `.venv`: `Figure/composite_pareto_crossover_shap.png` pixel-identical to the conda render and to the committed file (1907×1847, max pixel diff 0). PNG bytes differ (pip-wheel zlib vs conda build), so the committed file was restored to avoid a no-op git diff. Note: it reads cached `Result/pareto_front.xlsx` + `Result/shap_samples.npz`; SHAP/Pareto regeneration (`tea_pareto_shap.py`, `tea_pareto_front.py`) not exercised.
