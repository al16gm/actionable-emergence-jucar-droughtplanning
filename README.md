# Actionable Emergence of Scenario-Conditioned Hydrological Forecasts for Drought Planning in Regulated Mediterranean Basins
 
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.PENDING.svg)](https://doi.org/10.5281/zenodo.PENDING)
 
**Authors:** A. Garcia-Monteagudo¹, M. Arnaldos², M.A. Pardo¹  
**Affiliations:** ¹University of Alicante | ²Cetaqua, Water Technology Centre  
**Contact:** alejandro.garciam@ua.es
 
## About This Repository
 
This repository contains the results data, analysis scripts, and supplementary materials for:
 
> Garcia-Monteagudo A, Arnaldos M, Pardo MA (2026) Actionable emergence of
> scenario-conditioned hydrological forecasts for drought planning in regulated
> Mediterranean basins. *Stochastic Environmental Research and Risk Assessment*.
> [DOI pending]
 
This is the **third paper** in a series on data-driven hydrological modelling for the
Júcar Hydrographic Confederation (JHC, eastern Spain):
- **Paper 1 (2025):** Explanatory modelling framework. https://doi.org/10.2139/ssrn.5364304
- **Paper 2 (2026):** Multi-horizon scenario-conditioned forecasting. [DOI pending]
- **Paper 3 (this repo):** Actionable Emergence (AE) framework for drought planning.
 
## Repository Structure
 
| Folder/File | Description |
|-------------|-------------|
| `results/` | Output CSV files from the AE1, AE2, and AE3 analyses |
| `scripts/` | Python scripts used to generate the results |
| `data/` | Instructions for accessing the original data sources |
 
## Key Results Files
 
| File | Content |
|------|---------|
| `AE1_reliability_horizon.csv` | Trustworthy horizons by component (River/Reservoir/Aquifer) |
| `AE2_bootstrap_delta_ci.csv` | Bootstrap 95% CIs for scenario separation Δp(pp) |
| `AE2_bootstrap_ci_fixed.csv` | Bootstrap CIs for drought probability by scenario |
| `AE2_emergence_metrics.csv` | Full AE2 emergence metrics across lead times |
| `AE3_value_ruv_fixed.csv` | RUV and VoI metrics for drought-trigger policy evaluation |
| `AE_forecast_scenarios_ALL.csv` | Hindcast skill by scenario, typology, and lead time |
| `Table_AE2_actionable_summary.csv` | Actionability summary table (AE2 gate per component) |
 
## How to Cite
 
If you use this code or data, please cite:
 
```bibtex
@article{GarciaMonteagudo2026ae,
  author  = {Garcia-Monteagudo, A. and Arnaldos, M. and Pardo, M.A.},
  title   = {Actionable emergence of scenario-conditioned hydrological forecasts
             for drought planning in regulated Mediterranean basins},
  journal = {Stochastic Environmental Research and Risk Assessment},
  year    = {2026},
  doi     = {PENDING}
}
```
 
## Data Sources
- **CHJ-SIA (hydrological data):** https://www.chj.es
- **AEMET (meteorological data):** https://opendata.aemet.es
 
Data are not redistributed in this repository due to licensing restrictions.
See `data/README.md` for download instructions.
 
## Requirements
```
pip install -r requirements.txt
```
 
## License
MIT — see [LICENSE](LICENSE)
