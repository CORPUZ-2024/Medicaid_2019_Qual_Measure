"""Section 3.2 - at-risk / positioned-for-success scoring.

Produces a reproducible, component-wise score per state (no black box). Dollar /
cost-impact estimation is intentionally out of scope (spec 3.2); the beneficiary
figure is a magnitude estimate only and is emitted as null with
``needs_analyst_input`` when the reference tables in data/reference/ are empty
rather than being fabricated.

Components (per state, per program):
  1. trend_exposure  - count of Declining or Persistent-Bottom measures among
                       those that passed the 2.3 gate, domain-weighted
                       (Behavioral Health Care & LTSS x1.5).
  2. fiscal_exposure - ordinal Low/Med/High from data/reference/state_fiscal_exposure.csv.
  3. reporting_capacity_exposure - share of a state's 2024 measures that were not
                       reported by that state in 2023 (proxy for 2.3a exposure).
  composite_risk = weighted sum, scaled 0-100, with every input echoed back.
"""

from __future__ import annotations

import pandas as pd

from . import config

W_TREND = 0.5
W_FISCAL = 0.3
W_REPORTING = 0.2
FISCAL_ORDINAL = {"low": 0.0, "medium": 0.5, "high": 1.0}


def _domain_weight(domain: str) -> float:
    return config.RISK_DOMAIN_WEIGHTS.get(domain, config.RISK_DOMAIN_WEIGHT_DEFAULT)


def _trend_exposure(gated_detail, persistent_bottom) -> pd.DataFrame:
    df = pd.DataFrame([d for d in gated_detail if d.get("comparable")])
    decl = df[df["classification"] == "Declining"].copy()
    decl["w"] = decl["domain"].map(_domain_weight)
    trend_part = (decl.groupby(["program", "state"])
                  .agg(n_declining=("w", "size"), weighted_declining=("w", "sum"))
                  .reset_index())

    pb = pd.DataFrame(persistent_bottom)
    if not pb.empty:
        pb = (pb.groupby(["program", "state"]).size()
              .rename("n_persistent_bottom").reset_index())
    else:
        pb = pd.DataFrame(columns=["program", "state", "n_persistent_bottom"])

    out = trend_part.merge(pb, on=["program", "state"], how="outer").fillna(0)
    for c in ["n_declining", "weighted_declining", "n_persistent_bottom"]:
        out[c] = out[c].astype(float)
    out["trend_exposure_raw"] = out["weighted_declining"] + 0.5 * out["n_persistent_bottom"]
    return out


def _reporting_capacity_exposure(clean: pd.DataFrame) -> pd.DataFrame:
    rated = clean.dropna(subset=["StateRate"])
    rows = []
    for (prog, state), g in rated.groupby(["ReportProg", "State"]):
        m24 = set(g.loc[g.CoreSetYear == 2024, "MeasureKey"])
        m23 = set(g.loc[g.CoreSetYear == 2023, "MeasureKey"])
        if not m24:
            continue
        new = len(m24 - m23)
        rows.append({"program": prog, "state": state,
                     "n_measures_2024": len(m24),
                     "n_new_vs_2023": new,
                     "reporting_capacity_exposure_raw": new / len(m24)})
    return pd.DataFrame(rows)


def _fiscal_exposure() -> pd.DataFrame:
    path = config.REFERENCE / "state_fiscal_exposure.csv"
    df = pd.read_csv(path, comment="#") if path.exists() else pd.DataFrame()
    df = df.dropna(how="all")
    if df.empty or "fiscal_exposure" not in df.columns:
        return pd.DataFrame(columns=["State", "fiscal_exposure", "fiscal_exposure_score"])
    df = df[df["fiscal_exposure"].notna()].copy()
    df["fiscal_exposure_score"] = df["fiscal_exposure"].str.lower().map(FISCAL_ORDINAL)
    return df[["State", "expansion_status", "provider_tax_reliance",
              "fiscal_exposure", "fiscal_exposure_score"]]


def _beneficiary_magnitude(gated_detail, clean: pd.DataFrame) -> dict:
    enr_path = config.REFERENCE / "state_enrollment.csv"
    share_path = config.REFERENCE / "measure_eligible_population_share.csv"
    enr = pd.read_csv(enr_path, comment="#") if enr_path.exists() else pd.DataFrame()
    enr = enr.dropna(how="all")
    share = pd.read_csv(share_path, comment="#") if share_path.exists() else pd.DataFrame()
    share = share.dropna(how="all")

    if enr.empty or share.empty:
        return {
            "needs_analyst_input": True,
            "formula": ("affected_beneficiaries(state, measure) = "
                        "state_medicaid_chip_enrollment x measure_eligible_population_share "
                        "x (baseline_on_track_rate - projected_rate_under_declining_trend)"),
            "note": ("Populate data/reference/state_enrollment.csv and "
                     "measure_eligible_population_share.csv to produce magnitude "
                     "estimates. No values are fabricated. Dollar/cost impact is "
                     "out of scope per spec 3.2."),
            "estimates": [],
        }

    # If both tables are present, compute per (state, measure) declining magnitude.
    df = pd.DataFrame([d for d in gated_detail
                       if d.get("comparable") and d["classification"] == "Declining"
                       and d["transition"] == "2023->2024"])
    enr_map = dict(zip(enr["State"], pd.to_numeric(enr["total_medicaid_chip_enrollment"], errors="coerce")))
    est = []
    for _, r in df.iterrows():
        e = enr_map.get(r["state"])
        sh = _match_share(share, r["measure_key"], r["program"])
        if e is None or sh is None:
            continue
        drop = abs(r["improve_delta"]) / 100.0
        est.append({"state": r["state"], "program": r["program"],
                    "measure_key": r["measure_key"],
                    "affected_beneficiaries_estimate": int(round(e * sh * drop))})
    return {"needs_analyst_input": False, "estimates": est}


def _match_share(share: pd.DataFrame, measure_key: str, program: str):
    for _, r in share.iterrows():
        pat = str(r.get("measure_name_contains", ""))
        if pat and pat.lower() in measure_key.lower():
            if not r.get("program") or str(r["program"]) in program:
                return float(r["eligible_population_share"])
    return None


def score(clean: pd.DataFrame, gated_detail, persistent_bottom) -> dict:
    te = _trend_exposure(gated_detail, persistent_bottom)
    rc = _reporting_capacity_exposure(clean)
    fx = _fiscal_exposure()

    base = te.merge(rc, on=["program", "state"], how="outer")
    base = base.merge(fx, on="State", right_on=None, how="left") if "State" in fx.columns and not fx.empty \
        else base.assign(fiscal_exposure=pd.NA, fiscal_exposure_score=pd.NA)
    if "State" in base.columns:
        base = base.drop(columns=["State"])
    base = base.fillna({"trend_exposure_raw": 0, "reporting_capacity_exposure_raw": 0,
                        "n_declining": 0, "n_persistent_bottom": 0, "weighted_declining": 0})

    # normalise each raw component to 0-1 within program
    for col in ["trend_exposure_raw", "reporting_capacity_exposure_raw"]:
        base[col + "_n"] = base.groupby("program")[col].transform(
            lambda s: (s - s.min()) / (s.max() - s.min()) if s.max() > s.min() else 0.0)

    fiscal_missing = base["fiscal_exposure_score"].isna().all()
    base["fiscal_component"] = (
        pd.to_numeric(base["fiscal_exposure_score"], errors="coerce")
        .fillna(0.5)  # neutral when unknown
    )

    base["composite_risk_0_100"] = (
        100 * (W_TREND * base["trend_exposure_raw_n"]
               + W_FISCAL * base["fiscal_component"]
               + W_REPORTING * base["reporting_capacity_exposure_raw_n"])
    ).round(1)

    base = base.sort_values(["program", "composite_risk_0_100"], ascending=[True, False])

    records = []
    for _, r in base.iterrows():
        records.append({
            "program": r["program"], "state": r["state"],
            "composite_risk_0_100": float(r["composite_risk_0_100"]),
            "components": {
                "trend_exposure": {
                    "weight": W_TREND,
                    "n_declining_gated": int(r.get("n_declining", 0) or 0),
                    "weighted_declining": round(float(r.get("weighted_declining", 0) or 0), 2),
                    "n_persistent_bottom": int(r.get("n_persistent_bottom", 0) or 0),
                    "raw": round(float(r["trend_exposure_raw"]), 2),
                    "normalized": round(float(r["trend_exposure_raw_n"]), 3),
                },
                "fiscal_exposure": {
                    "weight": W_FISCAL,
                    "category": (r["fiscal_exposure"] if pd.notna(r.get("fiscal_exposure")) else None),
                    "score": (float(r["fiscal_exposure_score"]) if pd.notna(r.get("fiscal_exposure_score")) else None),
                    "used_neutral_default": bool(pd.isna(r.get("fiscal_exposure_score"))),
                },
                "reporting_capacity_exposure": {
                    "weight": W_REPORTING,
                    "n_new_measures_vs_2023": int(r.get("n_new_vs_2023", 0) or 0),
                    "raw": round(float(r["reporting_capacity_exposure_raw"]), 3),
                    "normalized": round(float(r["reporting_capacity_exposure_raw_n"]), 3),
                },
            },
        })

    return {
        "weights": {"trend_exposure": W_TREND, "fiscal_exposure": W_FISCAL,
                    "reporting_capacity_exposure": W_REPORTING},
        "fiscal_exposure_missing": bool(fiscal_missing),
        "domain_weights": config.RISK_DOMAIN_WEIGHTS,
        "scores": records,
        "beneficiary_magnitude": _beneficiary_magnitude(gated_detail, clean),
        "notes": [
            "composite_risk is a relative index within program, not a probability.",
            "fiscal_exposure uses a neutral 0.5 for every state until "
            "data/reference/state_fiscal_exposure.csv is populated.",
            "Dollar / increased-utilization-cost impact is intentionally out of "
            "scope (spec 3.2); only beneficiary magnitude is modelled, and only "
            "when its reference tables are supplied.",
        ],
    }
