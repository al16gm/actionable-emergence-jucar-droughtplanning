# =========================================
# CELL AE1 — Reliability horizon R(t)
# Inputs:
#   - /content/ae_exports/AE_skill_by_lead.csv
# Outputs:
#   - /content/ae_results/AE1_reliability_by_lead.csv
#   - /content/ae_results/AE1_reliability_horizon.csv
# =========================================

import os
import numpy as np
import pandas as pd

IN_SKILL = "/content/ae_exports/AE_skill_by_lead.csv"
OUT_DIR = "/content/ae_results"
os.makedirs(OUT_DIR, exist_ok=True)

sk = pd.read_csv(IN_SKILL)

# --- Choose which skill columns to use (prefer KGE_y_mean etc if present) ---
kge_col = "KGE_y_mean" if "KGE_y_mean" in sk.columns else ("KGE_mean" if "KGE_mean" in sk.columns else None)
nse_col = "NSE_y_mean" if "NSE_y_mean" in sk.columns else ("NSE_mean" if "NSE_mean" in sk.columns else None)

if kge_col is None:
    raise ValueError("No KGE column found in AE_skill_by_lead.csv")

# --- Define reliability rule (tunable) ---
# Conservative defaults for Q1-friendly "trustworthy horizon":
KGE_THR = 0.30          # typical "acceptable" threshold
NSE_THR = 0.30          # optional; used if available
MIN_SERIES = 10         # guard: ensure enough series behind metrics

sk["lead_months"] = pd.to_numeric(sk["lead_months"], errors="coerce").astype(int)
sk["n_series"] = pd.to_numeric(sk["n_series"], errors="coerce") if "n_series" in sk.columns else np.nan

sk["R_flag"] = sk[kge_col] >= KGE_THR
if nse_col is not None:
    sk["R_flag"] = sk["R_flag"] & (sk[nse_col] >= NSE_THR)
if "n_series" in sk.columns:
    sk["R_flag"] = sk["R_flag"] & (sk["n_series"] >= MIN_SERIES)

# --- Make horizon "contiguous": once it fails, later leads are not reliable ---
def contiguous_horizon(df):
    df = df.sort_values("lead_months").copy()
    flags = df["R_flag"].to_numpy(dtype=bool)
    # find first False after a True streak
    if flags.any():
        first_false_after_true = None
        seen_true = False
        for i, f in enumerate(flags):
            if f:
                seen_true = True
            elif seen_true and (not f):
                first_false_after_true = i
                break
        if first_false_after_true is not None:
            flags[first_false_after_true:] = False
    df["R_flag_contig"] = flags
    return df

sk2 = (
    sk.groupby(["input_kind", "model_family"], dropna=False, group_keys=False)
      .apply(contiguous_horizon)
      .reset_index(drop=True)
)

# --- Reliability horizon summary ---
horizon_rows = []
for (ik, mf), g in sk2.groupby(["input_kind", "model_family"], dropna=False):
    g = g.sort_values("lead_months")
    good = g[g["R_flag_contig"]]
    h = int(good["lead_months"].max()) if len(good) else 0
    horizon_rows.append({
        "input_kind": ik,
        "model_family": mf,
        "trustworthy_horizon_months": h,
        "kge_threshold": KGE_THR,
        "nse_threshold": NSE_THR if nse_col is not None else None,
        "min_series": MIN_SERIES if "n_series" in sk.columns else None,
        "kge_col": kge_col,
        "nse_col": nse_col,
    })
AE1_horizon = pd.DataFrame(horizon_rows).sort_values(["input_kind","model_family"])

# --- Export ---
AE1_by_lead = sk2.sort_values(["input_kind","model_family","lead_months"])
AE1_by_lead.to_csv(f"{OUT_DIR}/AE1_reliability_by_lead.csv", index=False)
AE1_horizon.to_csv(f"{OUT_DIR}/AE1_reliability_horizon.csv", index=False)

print("Saved:")
print(f" - {OUT_DIR}/AE1_reliability_by_lead.csv")
print(f" - {OUT_DIR}/AE1_reliability_horizon.csv")
display(AE1_horizon)
