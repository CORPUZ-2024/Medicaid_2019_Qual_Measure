"""Section 2.2 - three-year trend (2022-2024): data-driven baseline and the
Improving / Stable / Declining classification, plus Persistent Bottom Quartile.

Year-over-year change
---------------------
For each state, measure rate (MeasureKey) and adjacent-year transition (2022->2023,
2023->2024) where the state reported the rate in both years:

    delta          = StateRate(t) - StateRate(t-1)                 (raw, signed)
    improve_delta  = delta        for higher-is-better rates
                   = -delta       for lower-is-better rates        (positive = better)

Only changes that pass the Section 2.3 gate (CMS trendability + state deviation check)
are used below.

Baseline (program x domain)
---------------------------
For each (ReportProg, Domain, transition): baseline = mean(improve_delta) over all
comparable state x rate changes in that group; band = 0.5 x SD of the same values.

Classification
--------------
Improving  if improve_delta > baseline + 0.5 SD
Declining  if improve_delta < baseline - 0.5 SD
Stable     otherwise.

Persistent Bottom Quartile: the state's rate is in CMS's bottom (worst-performing)
quartile in >= 2 of the 3 years, regardless of movement.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from . import config

GROUP = ["ReportProg", "Domain", "transition"]


def deltas(clean: pd.DataFrame) -> pd.DataFrame:
    """One row per (MeasureKey, State, transition) where both years have a rate."""
    p = clean.dropna(subset=["StateRate"])
    attrs = (p.sort_values("CoreSetYear").groupby("MeasureKey")
             [["ReportProg", "Domain", "MeasureName", "MeasureAbbr", "RateDefinition", "Direction"]]
             .last())
    wide = p.pivot_table(index=["MeasureKey", "State", "StateAbbr"], columns="CoreSetYear",
                         values="StateRate", aggfunc="first")
    recs = []
    for (y0, y1) in config.YEAR_TRANSITIONS:
        if y0 not in wide.columns or y1 not in wide.columns:
            continue
        w = wide[[y0, y1]].dropna().reset_index().rename(columns={y0: "rate_from", y1: "rate_to"})
        w["transition"] = f"{y0}->{y1}"
        recs.append(w)
    d = pd.concat(recs, ignore_index=True).merge(attrs, left_on="MeasureKey", right_index=True)
    d["delta"] = d["rate_to"] - d["rate_from"]
    higher = d["Direction"].eq(config.DIRECTION_HIGHER)
    d["improve_delta"] = np.where(higher, d["delta"], -d["delta"])
    return d


def classify(gated: pd.DataFrame, clean: pd.DataFrame) -> dict:
    comp = gated[gated["comparable"]].copy()

    base = (comp.groupby(GROUP)
            .agg(baseline_mean=("improve_delta", "mean"), baseline_sd=("improve_delta", "std"),
                 n_changes=("improve_delta", "size"), n_rates=("MeasureKey", "nunique"),
                 n_states=("State", "nunique"))
            .reset_index())
    # every program x domain x transition, including groups with nothing trendable
    allg = (gated[GROUP].drop_duplicates())
    base = allg.merge(base, on=GROUP, how="left")
    excl = (gated[~gated["comparable"]].groupby(GROUP).size().rename("n_changes_excluded")
            .reset_index())
    base = base.merge(excl, on=GROUP, how="left").fillna({"n_changes": 0, "n_rates": 0,
                                                          "n_states": 0, "n_changes_excluded": 0})

    comp = comp.merge(base[GROUP + ["baseline_mean", "baseline_sd"]], on=GROUP, how="left")
    sd = comp["baseline_sd"].fillna(0)
    lo = comp["baseline_mean"] - config.CLASS_BAND_SD * sd
    hi = comp["baseline_mean"] + config.CLASS_BAND_SD * sd
    comp["classification"] = np.select(
        [comp["improve_delta"] > hi, comp["improve_delta"] < lo], ["Improving", "Declining"], "Stable")

    persistent = _persistent_bottom(clean)

    state_roll = []
    for (prog, state), g in comp.groupby(["ReportProg", "State"]):
        pb = persistent[(persistent["ReportProg"] == prog) & (persistent["State"] == state)]
        state_roll.append({
            "program": prog, "state": state, "abbr": g["StateAbbr"].iloc[0],
            "n_changes": int(len(g)),
            "n_rates": int(g["MeasureKey"].nunique()),
            "n_improving": int((g["classification"] == "Improving").sum()),
            "n_declining": int((g["classification"] == "Declining").sum()),
            "n_stable": int((g["classification"] == "Stable").sum()),
            "sum_improve_delta": round(float(g["improve_delta"].sum()), 2),
            "mean_improve_delta": round(float(g["improve_delta"].mean()), 2),
            "n_persistent_bottom": int(pb["persistent_bottom"].sum()),
        })
    state_roll.sort(key=lambda r: (r["program"], r["mean_improve_delta"]))

    meas_roll = []
    for key, g in comp.groupby("MeasureKey"):
        meas_roll.append({
            "measure_key": key, "program": g["ReportProg"].iloc[0], "domain": g["Domain"].iloc[0],
            "measure_name": g["MeasureName"].iloc[0], "measure_abbr": g["MeasureAbbr"].iloc[0],
            "rate_definition": g["RateDefinition"].iloc[0], "direction": g["Direction"].iloc[0],
            "cms_determination": g["cms_determination"].iloc[0],
            "n_changes": int(len(g)),
            "n_improving": int((g["classification"] == "Improving").sum()),
            "n_declining": int((g["classification"] == "Declining").sum()),
            "n_stable": int((g["classification"] == "Stable").sum()),
            "mean_improve_delta": round(float(g["improve_delta"].mean()), 2),
        })
    meas_roll.sort(key=lambda r: r["mean_improve_delta"])

    detail = [{
        "measure_key": r["MeasureKey"], "program": r["ReportProg"], "domain": r["Domain"],
        "measure_abbr": r["MeasureAbbr"], "state": r["State"], "abbr": r["StateAbbr"],
        "transition": r["transition"], "direction": r["Direction"],
        "cms_determination": r["cms_determination"],
        "rate_from": round(float(r["rate_from"]), 2), "rate_to": round(float(r["rate_to"]), 2),
        "delta": round(float(r["delta"]), 2), "improve_delta": round(float(r["improve_delta"]), 2),
        "baseline_mean": round(float(r["baseline_mean"]), 3),
        "baseline_sd": None if pd.isna(r["baseline_sd"]) else round(float(r["baseline_sd"]), 3),
        "classification": r["classification"],
    } for r in comp.to_dict("records")]

    return {
        "window": "2022-2024",
        "transitions": [f"{a}->{b}" for a, b in config.YEAR_TRANSITIONS],
        "class_band_sd": config.CLASS_BAND_SD,
        "baseline": _round_records(base.sort_values(GROUP).to_dict("records"),
                                   ["baseline_mean", "baseline_sd"]),
        "state_rollup": state_roll,
        "measure_rollup": meas_roll,
        "detail": detail,
        "persistent_bottom": [
            {"program": r["ReportProg"], "state": r["State"], "measure_key": r["MeasureKey"],
             "years_in_bottom": int(r["years_in_bottom"])}
            for r in persistent[persistent["persistent_bottom"]].to_dict("records")
        ],
    }


def _persistent_bottom(clean: pd.DataFrame) -> pd.DataFrame:
    p = clean.dropna(subset=["StateRate"]).copy()
    p["in_bottom"] = p["InBottomQuartile"].map(
        lambda v: True if v in (True, "True", "true") else (
            False if v in (False, "False", "false") else np.nan))
    g = (p.groupby(["ReportProg", "State", "MeasureKey"])
         .agg(years_in_bottom=("in_bottom", "sum"), years_scored=("in_bottom", "count"))
         .reset_index())
    g["persistent_bottom"] = g["years_in_bottom"] >= config.PERSISTENT_BOTTOM_MIN_YEARS
    return g


def _round_records(recs, keys):
    for r in recs:
        for k in keys:
            v = r.get(k)
            r[k] = None if v is None or pd.isna(v) else round(float(v), 3)
        for k in ("n_changes", "n_rates", "n_states", "n_changes_excluded"):
            if k in r:
                r[k] = int(r[k])
    return recs
