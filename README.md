# Actionable Emergence of Scenario-Conditioned Hydrological Forecasts for Drought Planning in Regulated Mediterranean Basins
 
[![DOI](https://zenodo.org/badge/1170836933.svg)](https://doi.org/10.5281/zenodo.19188723)
 
**Authors:** A. Garcia-Monteagudo¹, M. Arnaldos², M.A. Pardo¹  
**Affiliations:** ¹University of Alicante | ²Cetaqua, Water Technology Centre  
**Contact:** alejandro.garciam@ua.es
 
## About This Repository
 
This repository contains the results data, analysis scripts, and supplementary materials for:
 
> Garcia-Monteagudo A, Arnaldos M, Pardo MA (2026) Actionable emergence of
> scenario-conditioned hydrological forecasts for drought planning in regulated
> Mediterranean basins. *Stochastic Environmental Research and Risk Assessment*.
> [DOI 10.5281/zenodo.19188724]
 
This is the **third paper** in a series on data-driven hydrological modelling for the
Júcar Hydrographic Confederation (JHC, eastern Spain):
- **Paper 1 (2026):** Explanatory modelling framework. https://doi.org/10.1007/s40899-026-01362-4
- **Paper 2 (2026):** Multi-horizon scenario-conditioned forecasting. [DOI pending]
- **Paper 3 (this repo):** Actionable Emergence (AE) framework for drought planning.
  
## Overview

This repository contains the fixed forecast archive, analysis code, and curated Online Resources supporting the Actionable Emergence (AE) framework applied to the Júcar River Basin District, Spain.

The framework evaluates three conditions independently and intersects them at monthly resolution:

- **AE1 — Reliability gate:** restricts inference to inherited component-specific trustworthy forecast horizons.
- **AE2 — Scenario-separation gate:** evaluates forecast-relative scenario separation using an empirical drought-rank score, complete-control-point trajectory bootstrap, practical effect thresholds, and simultaneous inference.
- **AE3 — Decision-value gate:** evaluates cross-validated Scenario-Conditioning Value under policy reselection inside each bootstrap replicate.

The final monthly intersection distinguishes:

- **Exploratory Full AE:** AE1 + joint AE2 evidence + pointwise-positive AE3 evidence.
- **Confirmatory Full AE:** AE1 + joint AE2 evidence + joint-simultaneous AE3 evidence.

Magnitude and scenario-consistent direction are reported separately. Persistence is applied only after constructing the complete monthly gate intersection.

## Repository contents

```text
.
├── data/
│   ├── README.md
│   └── AE_forecast_scenarios_ALL.csv
├── code/
│   └── AE_canonical_analysis.ipynb
├── online_resources/
│   ├── README.md
│   ├── Online_Resource_1_AE1_AE2.xlsx
│   ├── Online_Resource_2_AE3_Decision_Value.xlsx
│   └── Online_Resource_3_Integrated_AE.xlsx
├── README.md
├── LICENSE
├── CITATION.cff
├── requirements.txt
├── .gitignore
└── SHA256SUMS
```

## Analytical input

The canonical analytical input is:

```text
data/AE_forecast_scenarios_ALL.csv
```

This file contains the fixed monthly multi-horizon forecast archive used by the AE analysis.

Key properties:

- 33,720 rows.
- Monthly target dates from January 2024 to December 2030.
- Forecast leads from 1 to 84 months.
- Components: Aquifer, Reservoir, and River.
- Scenarios: Base, Favorable, and Unfavorable.
- Model families: ENDO and EXOG.
- Scenario comparisons use the EXOG trajectories.
- Downstream AE calculations use the reconstructed forecast level `y_hat`.
- `dy_hat` is retained for provenance but is not used in AE2 or AE3.

Canonical SHA-256:

```text
e4e08302fd160ed26d603f93ba2af0cb2978f55e6e8b294753b1c4bc228dc011
```

The archive is a derived forecast product and should not be described as raw hydrological observations.

## Complete analytical population

After requiring aligned Base, Favorable, and Unfavorable trajectories for all target months, the retained control-point populations are:

| Component | Control points | Inherited AE1 horizon |
|---|---:|---:|
| Aquifer | 22 | 48 months |
| Reservoir | 24 | 36 months |
| River | 54 | 24 months |

AE1 horizons are inherited from the companion multi-horizon forecasting study and are not re-estimated in this repository.

## Reproducibility

### 1. Clone the repository

```bash
git clone https://github.com/al16gm/actionable-emergence-jucar-droughtplanning.git
cd actionable-emergence-jucar-droughtplanning
```

### 2. Create a Python environment

Linux or macOS:

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Run the canonical notebook

```bash
jupyter lab code/AE_canonical_analysis.ipynb
```

When running in Google Colab, clone or upload the complete repository and set the project root in the first configuration cell. The notebook should use repository-relative paths rather than machine-specific `/content` or Google Drive paths.

The full analysis uses 5,000 bootstrap replicates for the primary AE2 and AE3 inference. Runtime depends on the available hardware and has not been formally benchmarked.

## Primary configuration

### AE1

| Component | Trustworthy horizon |
|---|---:|
| Aquifer | 48 months |
| Reservoir | 36 months |
| River | 24 months |

### AE2

- Primary practical threshold: `delta = 1.0 pp`.
- Sensitivity thresholds: `0.5, 1.0, and 1.5 pp`.
- Primary persistence requirement: `r = 3 months`.
- Sensitivity persistence requirements: `1, 3, and 6 months`.
- Bootstrap replicates: `5,000`.
- Confidence level: `95%`.
- Resampling unit: complete control-point trajectory.
- Joint inference: maximum standardised deviation across both scenarios and all eligible months within each component.

### AE3

- Action set: `{0, 0.05, 0.10, 0.20}`.
- Default drought-pressure tolerance: `pi = 0.70`.
- Default action effectiveness: `eta = 1`.
- Default action penalty: `gamma = 1`.
- Sensitivity values:
  - `pi = {0.60, 0.70, 0.80}`
  - `gamma = {0.5, 1.0, 2.0}`
- Policy evaluation: leave-one-control-point-out.
- Base and scenario policies are reselected inside every bootstrap replicate.
- Bootstrap replicates: `5,000`.

## Expected validation results

A successful canonical execution should reproduce the following high-level checks:

- Forecast archive rows: `33,720`.
- Complete control points:
  - Aquifer: `22`
  - Reservoir: `24`
  - River: `54`
- Inherited AE1 horizons:
  - Aquifer: `48 months`
  - Reservoir: `36 months`
  - River: `24 months`
- Reservoir joint-positive AE2 months:
  - Favorable: `9`
  - Unfavorable: `9`
- Reservoir pointwise-positive AE3 months:
  - Favorable: `7`
  - Unfavorable: `7`
- Joint-positive AE3 months: `0` for all component–scenario combinations.
- Persistent exploratory Full AE windows: `4`, all in Reservoir.
- Persistent windows:
  - June–August 2025, Favorable
  - June–August 2025, Unfavorable
  - June–August 2026, Favorable
  - June–August 2026, Unfavorable
- Confirmatory Full AE windows: `0`.
- Reservoir pooled Scenario-Conditioning RUV: approximately `0.54–0.55`.

Small differences in the final decimal places may occur across software or hardware environments, but classifications and counts should remain unchanged.

## Online Resources

### Online Resource 1

```text
online_resources/Online_Resource_1_AE1_AE2.xlsx
```

Contains the analytical population, forecast-panel validation, inherited AE1 horizons, Base-reference diagnostics, monthly AE2 results, pointwise intervals, joint simultaneous bands, threshold–persistence sensitivity, and influence diagnostics.

### Online Resource 2

```text
online_resources/Online_Resource_2_AE3_Decision_Value.xlsx
```

Contains monthly Scenario-Conditioning Value, policy value relative to no action, regret diagnostics, pooled Relative Utility Value, selected actions, policy transitions, loss-parameter sensitivity, and bootstrap comparisons.

### Online Resource 3

```text
online_resources/Online_Resource_3_Integrated_AE.xlsx
```

Contains the monthly AE1–AE2–AE3 gate intersection, exploratory and confirmatory evidence flags, persistence calculations, persistent Full AE windows, and the integrated evidence hierarchy.

Each workbook begins with a `README` worksheet describing its contents, variables, units, identifiers, interpretation constraints, and links to the manuscript.

## Source observations

Original hydrological and meteorological observations are not redistributed in this repository.

They remain available from their original public providers:

- Júcar River Basin District water information system: https://www.chj.es
- AEMET OpenData: https://opendata.aemet.es

Use and redistribution of third-party observations remain subject to the corresponding provider terms.

## Interpretation limits

The drought-rank score is a forecast-relative empirical rank and is not:

- a calibrated drought probability;
- an observed drought frequency;
- an official drought-status indicator.

The AE3 loss function is dimensionless and stylised. Scenario-Conditioning Value and pooled RUV do not represent monetary savings, avoided water volumes, or operational performance of an implemented drought rule.

The reported emergence windows are ex ante, model-conditioned evidence for enhanced monitoring and prospective policy review. They are not automatic intervention dates.

## Versioning

Release `v2.0.0` supports the revised empirical drought-rank and policy-reselection analysis.

Earlier releases are retained only as historical records and do not reproduce the current manuscript.

## Citation

Please cite the archived Zenodo release identified in `CITATION.cff`. When the associated journal article is published, please cite both the article and the software archive.

## License

The source code is released under the MIT License. See `LICENSE`.

The MIT License applies to the software code. Third-party source data remain governed by their original provider terms. Licensing and reuse conditions for the derived forecast archive and workbook outputs should be interpreted together with the accompanying documentation and citation requirements.

## Contact

A. Garcia-Monteagudo  
Department of Civil Engineering, University of Alicante  
Email: alejandro.garciam@ua.es
