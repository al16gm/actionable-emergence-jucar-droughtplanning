# Online Resources

This directory contains the three curated workbooks supporting the manuscript.

The workbooks are intended to provide reviewer- and reader-facing result tables. They are not substitutes for the canonical code or the fixed forecast archive.

## Online Resource 1

Online_Resource_1_AE1_AE2.xlsx

Title: Data support, inherited AE1 reliability gates, and AE2 forecast-relative scenario-separation results.

Main content:

analytical population;
forecast-panel validation;
inherited component-specific AE1 horizons;
Base-reference diagnostics;
empirical-rank and tie diagnostics;
monthly AE2 effects;
pointwise bootstrap intervals;
joint component-wise simultaneous bands;
practical threshold and persistence sensitivity;
leave-one-control-point-out influence diagnostics.

Interpretation:

The drought-rank score is a forecast-relative empirical rank.
It is not a calibrated probability or an official drought indicator.
Joint AE2 evidence is used in the final Full AE intersection.


## Online Resource 2

Online_Resource_2_AE3_Decision_Value.xlsx

Title: Cross-validated AE3 decision-value analysis under policy reselection.

Main content:

monthly Scenario-Conditioning Value;
policy value relative to no action;
Base-policy and perfect-information regret;
pooled Relative Utility Value;
pooled denominator diagnostics;
selected-action frequencies;
Base-to-scenario policy transitions;
decision-loss parameter sensitivity;
fixed-contribution and policy-reselection bootstrap comparison.

Interpretation:

Scenario-Conditioning Value measures incremental value relative to a Base-conditioned policy.
Policy value relative to no action is a separate quantity.
Loss and value quantities are dimensionless.
The primary inference reselects policies inside every bootstrap replicate.
Pooled RUV is a descriptive effect size, not a significance criterion or economic return.


## Online Resource 3

Online_Resource_3_Integrated_AE.xlsx

Title: Integrated AE1–AE2–AE3 synthesis and persistence results.

Main content:

monthly AE1–AE2–AE3 gate intersection;
exploratory and confirmatory evidence flags;
magnitude-based and direction-consistent classifications;
persistence calculations;
persistent Full Actionable Emergence windows;
hierarchical evidence summaries;
source tables supporting the integrated manuscript synthesis.

Definitions:

Exploratory Full AE = AE1 + joint AE2 + pointwise-positive AE3.
Confirmatory Full AE = AE1 + joint AE2 + joint-positive AE3.
Persistence is applied after constructing the monthly gate intersection.
Magnitude and direction are classified separately.
Workbook structure

Each workbook begins with a worksheet named:

README

The worksheet documents:

scientific scope;
sheet inventory;
variable definitions;
units;
key identifiers;
manuscript links;
interpretation limits;
canonical analysis version.

---

# 4. `requirements.txt`

```text
numpy>=1.26,<3.0
pandas>=2.2,<3.0
scipy>=1.12,<2.0
matplotlib>=3.8,<4.0
openpyxl>=3.1,<4.0
XlsxWriter>=3.2,<4.0
jupyterlab>=4.2,<5.0
ipykernel>=6.29,<7.0

Cuando la ejecución canónica esté cerrada, se puede generar además un entorno completamente congelado:

pip freeze > requirements-lock.txt
