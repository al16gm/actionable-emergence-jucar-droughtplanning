# Canonical Forecast Archive

## File

```text
AE_forecast_scenarios_ALL.csv
```

## Purpose

This file is the fixed analytical forecast archive used as input to the Actionable Emergence analysis.

It is a derived model-output dataset, not a collection of raw hydrological or meteorological observations.

## Integrity

Expected number of rows:

```text
33,720
```

Expected SHA-256:

```text
e4e08302fd160ed26d603f93ba2af0cb2978f55e6e8b294753b1c4bc228dc011
```

Verify on Linux:

```bash
sha256sum AE_forecast_scenarios_ALL.csv
```

Verify on macOS:

```bash
shasum -a 256 AE_forecast_scenarios_ALL.csv
```

## Temporal coverage

- First target month: `2024-01-01`
- Last target month: `2030-12-01`
- Number of target months: `84`
- Forecast leads: `1–84 months`
- Temporal resolution: monthly

## Components

The `input_kind` field identifies the analytical component:

- `Aquifer`
- `Reservoir`
- `River`

## Scenarios

The `scenario` field identifies the forcing pathway:

- `Base`
- `Favorable`
- `Unfavorable`

Scenario names describe forcing narratives. They do not impose a required monotonic ordering on the modelled hydrological response.

## Model families

The `model_family` field identifies:

- `ENDO`: forecasts based on endogenous hydrological memory and seasonality.
- `EXOG`: forecasts incorporating exogenous climate and water-demand drivers.

Only EXOG trajectories provide aligned Base, Favorable, and Unfavorable scenario forecasts and are therefore used for AE2 and AE3 scenario comparisons.

## Column dictionary

| Column | Description |
|---|---|
| `target_date` | Monthly forecast target date. |
| `lead_months` | Forecast lead in months, ranging from 1 to 84. |
| `point_id` | Stable identifier of the hydrological control point. |
| `series_id` | Source-series identifier retained for traceability. |
| `input_kind` | Hydrological component: Aquifer, Reservoir, or River. |
| `scenario` | Scenario label: Base, Favorable, or Unfavorable. |
| `model_family` | Forecast family: ENDO or EXOG. |
| `model` | Selected statistical or machine-learning model. |
| `feature_set` | Feature configuration used by the selected model. |
| `y_hat` | Reconstructed forecast level. This is the forecast variable used by the AE analysis. |
| `dy_hat` | Predicted forecast increment. Retained for provenance but not used in AE2 or AE3. |

## Analytical populations

The archive includes more trajectories than the final complete-case AE populations.

AE2 and AE3 retain only control points with aligned Base, Favorable, and Unfavorable trajectories for every target month.

Final complete-case populations:

| Component | Eligible control points | AE1 inference horizon |
|---|---:|---:|
| Aquifer | 22 | 48 months |
| Reservoir | 24 | 36 months |
| River | 54 | 24 months |

The same point population is used for both non-Base scenarios within each component.

## Use in the analysis

The canonical notebook performs the following checks before analysis:

- expected SHA-256;
- required columns;
- target-date and lead consistency;
- duplicate analytical keys;
- exact scenario alignment;
- component and scenario counts;
- complete-case control-point trajectories;
- use of reconstructed forecast levels only.

Forecasts beyond the inherited AE1 horizon remain in the archive for context but do not contribute to statistical inference, pooled utility summaries, persistence windows, or Full Actionable Emergence classification.

## Original source data

The observations and forcing data used to produce this archive are not redistributed here.

Original data access:

- Júcar River Basin District: https://www.chj.es
- AEMET OpenData: https://opendata.aemet.es

Reuse of original observations remains subject to the respective provider conditions.
