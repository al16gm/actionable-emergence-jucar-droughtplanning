# =========================================
# CELL AE2 — Emergence E(t)
# Inputs:
#   - /content/ae_exports/AE_forecast_with_sigma.csv  (or EXOG + sigma)
# Outputs:
#   - /content/ae_results/AE2_emergence_metrics.csv
# =========================================

import os
import numpy as np
import pandas as pd
from math import erf, sqrt

IN_FC = "/content/ae_exports/AE_forecast_with_sigma.csv"
OUT_DIR = "/content/ae_results"
os.makedirs(OUT_DIR, exist_ok=True)

fc = pd.read_csv(IN_FC)
fc["target_date"] = pd.to_datetime(fc["target_date"], errors="coerce")
fc["month"] = fc["target_date"].dt.month.astype(int)

# Work with EXOG only for scenarios (recommended)
fc = fc[fc["model_family"].astype(str).str.upper().eq("EXOG")].copy()

# Basic sanity
for col in ["input_kind","point_id","scenario","lead_months","y_hat","sigma_hat","month"]:
    if col not in fc.columns:
        raise ValueError(f"Missing required column: {col}")

# --- Define drought threshold tau_q by (input_kind, month) from Base scenario (seasonal threshold) ---
TAU_Q = 0.20  # drought threshold percentile
base = fc[fc["scenario"].astype(str).str.lower().eq("base")].copy()
tau = (
    base.groupby(["input_kind","month"])["y_hat"]
        .quantile(TAU_Q)
        .reset_index()
        .rename(columns={"y_hat":"tau"})
)

fc = fc.merge(tau, on=["input_kind","month"], how="left")

# --- Normal CDF without scipy (for speed + no extra deps) ---
def norm_cdf(x):
    # standard normal CDF using erf
    return 0.5 * (1.0 + erf(x / sqrt(2.0)))

# Probability below tau for each row (point-level)
# Guard sigma
eps = 1e-9
z = (fc["tau"].to_numpy(dtype=float) - fc["y_hat"].to_numpy(dtype=float)) / np.maximum(fc["sigma_hat"].to_numpy(dtype=float), eps)
fc["p_below_tau"] = np.vectorize(norm_cdf)(z)

# --- Aggregate per (input_kind, lead_months, scenario) ---
agg = (
    fc.groupby(["input_kind","lead_months","scenario"], dropna=False)
      .agg(
          target_date=("target_date","first"),
          month=("month","first"),
          n_points=("point_id","nunique"),
          mean_y=("y_hat","mean"),
          median_y=("y_hat","median"),
          mean_sigma=("sigma_hat","mean"),
          p_below_tau=("p_below_tau","mean"),
      )
      .reset_index()
)

# --- Compute deltas vs Base for each input_kind & lead ---
base_agg = agg[agg["scenario"].astype(str).str.lower().eq("base")][
    ["input_kind","lead_months","mean_y","p_below_tau"]
].rename(columns={"mean_y":"mean_y_base","p_below_tau":"p_below_tau_base"})

AE2 = agg.merge(base_agg, on=["input_kind","lead_months"], how="left")
AE2["delta_mean"] = AE2["mean_y"] - AE2["mean_y_base"]
AE2["delta_p_below_tau"] = AE2["p_below_tau"] - AE2["p_below_tau_base"]

# --- Distributional distance W1 between scenario and Base for each lead (across points) ---
# W1 for equal weights: mean absolute difference between sorted samples (requires same n; we match by min n)
def w1_distance(a, b):
    a = np.sort(np.asarray(a, dtype=float))
    b = np.sort(np.asarray(b, dtype=float))
    n = min(len(a), len(b))
    if n == 0:
        return np.nan
    a = a[:n]
    b = b[:n]
    return float(np.mean(np.abs(a - b)))

w1_rows = []
for (ik, lead), g in fc.groupby(["input_kind","lead_months"]):
    gb = g[g["scenario"].astype(str).str.lower().eq("base")]
    if gb.empty:
        continue
    yb = gb["y_hat"].to_numpy(dtype=float)
    for scen, gs in g.groupby("scenario"):
        ys = gs["y_hat"].to_numpy(dtype=float)
        w1 = w1_distance(ys, yb)
        w1_rows.append({"input_kind":ik, "lead_months":int(lead), "scenario":scen, "W1_yhat_vs_base":w1})
w1_df = pd.DataFrame(w1_rows)

AE2 = AE2.merge(w1_df, on=["input_kind","lead_months","scenario"], how="left")

# --- Emergence flag E(t): conservative combined criterion (tunable) ---
# E=1 when BOTH:
#   |ΔP| >= 0.10  (10 percentage points change in drought probability)
#   AND W1 >= 1 * mean_sigma  (distribution shift comparable to typical uncertainty)
DP_THR = 0.10
SIG_MULT = 1.0
AE2["E_flag"] = (AE2["scenario"].astype(str).str.lower().ne("base")) & \
                (AE2["delta_p_below_tau"].abs() >= DP_THR) & \
                (AE2["W1_yhat_vs_base"] >= (SIG_MULT * AE2["mean_sigma"]))

AE2 = AE2.sort_values(["input_kind","lead_months","scenario"]).reset_index(drop=True)

# --- Export ---
AE2.to_csv(f"{OUT_DIR}/AE2_emergence_metrics.csv", index=False)
print("Saved:", f"{OUT_DIR}/AE2_emergence_metrics.csv")
display(AE2.head(20))
