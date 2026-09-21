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



## Log history

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

