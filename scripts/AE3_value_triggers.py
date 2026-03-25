# =========================================
# CELL AE3 — Planning value: Triggers vs RUV
# Inputs:
#   - /content/ae_exports/AE_forecast_with_sigma.csv
#   - (optional) demands_2017_2050.xlsx (search in /content and /content/drive)
# Outputs:
#   - /content/ae_results/AE3_value_triggers.csv
#   - /content/ae_results/AE3_value_ruv.csv
# =========================================

import os
import numpy as np
import pandas as pd
from pathlib import Path
from math import erf, sqrt

OUT_DIR = "/content/ae_results"
os.makedirs(OUT_DIR, exist_ok=True)

IN_FC = "/content/ae_exports/AE_forecast_with_sigma.csv"
fc = pd.read_csv(IN_FC)
fc["target_date"] = pd.to_datetime(fc["target_date"], errors="coerce")
fc = fc[fc["model_family"].astype(str).str.upper().eq("EXOG")].copy()

# ------------------------
# Demand loader (best-effort)
# ------------------------
def find_file_anywhere(filename, roots=("/content", "/content/drive/MyDrive")):
    for r in roots:
        p = Path(r)
        if not p.exists():
            continue
        hits = list(p.rglob(filename))
        if hits:
            return str(hits[0])
    return None

demand_path = find_file_anywhere("demands_2017_2050.xlsx")
demand = None
if demand_path:
    try:
        demand = pd.read_excel(demand_path)
        demand.columns = [str(c).strip() for c in demand.columns]
        print("Loaded demand file:", demand_path)
        print("Demand columns:", demand.columns.tolist()[:30])
    except Exception as e:
        print("Demand file found but could not be read:", e)
        demand = None
else:
    print("Demand file NOT found. AE3 will run in proxy mode (no real demand).")

# ------------------------
# Build drought probability p_below_tau (reuse AE2 logic)
# ------------------------
fc["month"] = fc["target_date"].dt.month.astype(int)

# Threshold tau_q from Base by (input_kind, month)
TAU_Q = 0.20
base = fc[fc["scenario"].astype(str).str.lower().eq("base")].copy()
tau = (
    base.groupby(["input_kind","month"])["y_hat"]
        .quantile(TAU_Q)
        .reset_index()
        .rename(columns={"y_hat":"tau"})
)
fc = fc.merge(tau, on=["input_kind","month"], how="left")

def norm_cdf(x):
    return 0.5 * (1.0 + erf(x / sqrt(2.0)))

eps = 1e-9
z = (fc["tau"].to_numpy(dtype=float) - fc["y_hat"].to_numpy(dtype=float)) / np.maximum(fc["sigma_hat"].to_numpy(dtype=float), eps)
fc["p_below_tau"] = np.vectorize(norm_cdf)(z)

# ------------------------
# Aggregate supply index (planning variable)
# Default: focus on Reservoir if exists, else River, else Aquifer
# ------------------------
preferred = ["Reservoir", "River", "Aquifer"]
avail = [k for k in preferred if k in set(fc["input_kind"].astype(str).unique())]
focus_input = avail[0] if avail else str(fc["input_kind"].astype(str).unique()[0])
print("AE3 focus input_kind:", focus_input)

fc_focus = fc[fc["input_kind"].astype(str).eq(focus_input)].copy()

# basin-level supply index as mean across points (robust to different counts)
# you can switch to sum if units are additive (hm3) and consistent.
supply = (
    fc_focus.groupby(["target_date","lead_months","scenario"], dropna=False)
            .agg(
                mean_supply=("y_hat","mean"),
                mean_sigma=("sigma_hat","mean"),
                mean_p_below=("p_below_tau","mean"),
                n_points=("point_id","nunique")
            )
            .reset_index()
)

# ------------------------
# Build (optional) demand series aligned to target_date
# Heuristic: try to find a date column and a demand column; else proxy with constant 1.
# ------------------------
def build_demand_series(df):
    # Find date col
    date_candidates = [c for c in df.columns if "date" in c.lower() or "fecha" in c.lower()]
    if not date_candidates:
        return None
    dcol = date_candidates[0]
    tmp = df.copy()
    tmp[dcol] = pd.to_datetime(tmp[dcol], errors="coerce")
    tmp = tmp.dropna(subset=[dcol])
    # Find numeric demand-like columns
    num_cols = [c for c in tmp.columns if c != dcol and pd.api.types.is_numeric_dtype(tmp[c])]
    if not num_cols:
        return None
    # If multiple numeric cols, sum them (total demand)
    tmp["demand_total"] = tmp[num_cols].sum(axis=1)
    out = tmp[[dcol, "demand_total"]].rename(columns={dcol:"target_date"})
    # Monthly aggregation
    out = out.groupby("target_date")["demand_total"].sum().reset_index()
    return out

demand_series = build_demand_series(demand) if demand is not None else None

if demand_series is None:
    print("Demand parsing failed or not available -> using proxy demand = 1.0")
    demand_series = supply[["target_date"]].drop_duplicates().copy()
    demand_series["demand_total"] = 1.0

# Merge demand into supply table
supply = supply.merge(demand_series, on="target_date", how="left")
supply["demand_total"] = supply["demand_total"].fillna(method="ffill").fillna(method="bfill").fillna(1.0)

# Normalize both to Base mean (dimensionless) to avoid unit mismatch
base_supply_mean = supply[supply["scenario"].astype(str).str.lower().eq("base")]["mean_supply"].mean()
base_demand_mean = supply["demand_total"].mean()

supply["supply_norm"] = supply["mean_supply"] / (base_supply_mean if base_supply_mean != 0 else 1.0)
supply["demand_norm"] = supply["demand_total"] / (base_demand_mean if base_demand_mean != 0 else 1.0)

# ------------------------
# Case A: Trigger policy (stages) -> expected cost
# ------------------------
# Stages based on drought probability (mean across points):
#   stage 0: p<0.30  -> reduction 0%
#   stage 1: 0.30-0.50 -> 5%
#   stage 2: 0.50-0.70 -> 10%
#   stage 3: >=0.70 -> 20%
def stage_from_p(p):
    if p < 0.30:
        return 0
    if p < 0.50:
        return 1
    if p < 0.70:
        return 2
    return 3

reductions = {0:0.00, 1:0.05, 2:0.10, 3:0.20}

supply["stage_trigger"] = supply["mean_p_below"].apply(stage_from_p)
supply["reduction"] = supply["stage_trigger"].map(reductions).astype(float)

# Costs (tunable)
SHORTAGE_W = 10.0     # penalty weight for unmet demand
RESTRICT_W = 1.0      # penalty weight for applying restrictions

# Apply restrictions to demand
supply["demand_eff"] = supply["demand_norm"] * (1.0 - supply["reduction"])
supply["deficit"] = np.maximum(0.0, supply["demand_eff"] - supply["supply_norm"])

# Expected cost under trigger policy
supply["cost_trigger"] = SHORTAGE_W * (supply["deficit"]**2) + RESTRICT_W * (supply["reduction"]**2)

AE3_tr = (
    supply.groupby(["lead_months","scenario"], dropna=False)
          .agg(
              target_date=("target_date","first"),
              mean_cost=("cost_trigger","mean"),
              mean_deficit=("deficit","mean"),
              mean_reduction=("reduction","mean"),
              mean_p_below=("mean_p_below","mean"),
          )
          .reset_index()
)

# Compare vs Base
base_tr = AE3_tr[AE3_tr["scenario"].astype(str).str.lower().eq("base")][["lead_months","mean_cost"]].rename(columns={"mean_cost":"base_cost"})
AE3_tr = AE3_tr.merge(base_tr, on="lead_months", how="left")
AE3_tr["value_gain_vs_base"] = AE3_tr["base_cost"] - AE3_tr["mean_cost"]

AE3_tr.to_csv(f"{OUT_DIR}/AE3_value_triggers.csv", index=False)
print("Saved:", f"{OUT_DIR}/AE3_value_triggers.csv")

# ------------------------
# Case B: RUV-like (Monte Carlo) using Normal(supply_norm, sigma_norm)
# ------------------------
# Convert sigma to normalized scale
supply["sigma_norm"] = supply["mean_sigma"] / (base_supply_mean if base_supply_mean != 0 else 1.0)
supply["sigma_norm"] = supply["sigma_norm"].clip(lower=1e-6)

# Actions: same restriction levels; utility = -cost
actions = [0,1,2,3]

def utility(deficit, reduction):
    return -(SHORTAGE_W * (deficit**2) + RESTRICT_W * (reduction**2))

N_MC = 400  # Monte Carlo samples per row (tunable)

ruv_rows = []
rng = np.random.default_rng(123)

# Reference climatology distribution: use Base supply across all dates as empirical mean/std
ref_base = supply[supply["scenario"].astype(str).str.lower().eq("base")]
ref_mu = float(ref_base["supply_norm"].mean())
ref_sd = float(ref_base["supply_norm"].std(ddof=0) if ref_base["supply_norm"].std(ddof=0) > 1e-6 else 0.10)

for _, row in supply.iterrows():
    mu = float(row["supply_norm"])
    sd = float(row["sigma_norm"])
    d0 = float(row["demand_norm"])
    lead = int(row["lead_months"])
    scen = row["scenario"]

    # Sample forecast distribution
    s_fore = rng.normal(mu, sd, size=N_MC)

    # For each action, expected utility under forecast
    EU = {}
    for a in actions:
        r = reductions[a]
        d_eff = d0 * (1.0 - r)
        deficit = np.maximum(0.0, d_eff - s_fore)
        EU[a] = float(np.mean(utility(deficit, r)))

    # Decision rule: choose action that maximizes expected utility under forecast
    a_star = max(EU, key=EU.get)
    EU_forecast = EU[a_star]

    # Reference: climatology-based decision
    s_ref = rng.normal(ref_mu, ref_sd, size=N_MC)
    EU_ref = {}
    for a in actions:
        r = reductions[a]
        d_eff = d0 * (1.0 - r)
        deficit = np.maximum(0.0, d_eff - s_ref)
        EU_ref[a] = float(np.mean(utility(deficit, r)))
    a_ref = max(EU_ref, key=EU_ref.get)
    EU_reference = EU_ref[a_ref]

    # "Perfect"/oracle upper bound: chooses best action knowing each realization of s_fore
    # We approximate by per-sample best action
    U_oracle = []
    for s in s_fore:
        best_u = -1e18
        for a in actions:
            r = reductions[a]
            d_eff = d0 * (1.0 - r)
            deficit = max(0.0, d_eff - s)
            u = utility(deficit, r)
            if u > best_u:
                best_u = u
        U_oracle.append(best_u)
    EU_perfect = float(np.mean(U_oracle))

    # Relative Utility Value (bounded, may be noisy if denom ~0)
    denom = (EU_perfect - EU_reference)
    ruv = (EU_forecast - EU_reference) / denom if abs(denom) > 1e-8 else np.nan

    ruv_rows.append({
        "target_date": row["target_date"],
        "lead_months": lead,
        "scenario": scen,
        "action_star": int(a_star),
        "action_ref": int(a_ref),
        "EU_forecast": EU_forecast,
        "EU_reference": EU_reference,
        "EU_perfect": EU_perfect,
        "RUV": ruv,
    })

AE3_ruv = pd.DataFrame(ruv_rows)

# Aggregate by lead/scenario
AE3_ruv_agg = (
    AE3_ruv.groupby(["lead_months","scenario"], dropna=False)
           .agg(
               target_date=("target_date","first"),
               RUV_mean=("RUV","mean"),
               RUV_p25=("RUV", lambda x: np.nanquantile(x, 0.25)),
               RUV_p75=("RUV", lambda x: np.nanquantile(x, 0.75)),
               EU_gain=("EU_forecast", "mean")
           )
           .reset_index()
)

AE3_ruv_agg.to_csv(f"{OUT_DIR}/AE3_value_ruv.csv", index=False)
print("Saved:", f"{OUT_DIR}/AE3_value_ruv.csv")

display(AE3_tr.head(12))
display(AE3_ruv_agg.head(12))
