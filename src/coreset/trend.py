"""Section 2.2 - three-year trend (2022-2024): data-driven baseline and the
Improving / Stable / Declining / Persistent-Bottom-Quartile classification.

Baseline (spec 2.2)
-------------------
For each (ReportProg, MeasureType) group and each adjacent-year transition,
    DeltaRate(s) = StateRate(s, t) - StateRate(s, t-1)          (raw, signed)
restricted to states s that reported the measure in *both* years.
The group mean of DeltaRate is the baseline; its SD sets the band.
Grouping by MeasureType matters because MeasureType here is directionality, so
"higher rates better" and "lower rates better" measures - which move in opposite
directions when performance improves - never share a baseline.

Classification (direction-aware)
--------------------------------
higher_better:  Improving  if delta > baseline + 0.5 SD
                Declining  if delta < baseline - 0.5 SD
lower_better :  Improving  if delta < baseline - 0.5 SD   (rate fell faster than typical)
                Declining  if delta > baseline + 0.5 SD
else Stable.

Persistent Bottom Quartile: in bottom-quartile territory (direction-aware, using
CMS's own quartile thresholds) in >= 2 of the 3 years, regardless of movement.

Comparability gating from Section 2.3 is applied later (build.py) - this module
produces the raw signal only.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from . import config

GROUP = ["ReportProg", "MeasureType"]


def _panel(clean: pd.DataFrame) -> pd.DataFrame:
    """One row per (MeasureKey, State, Year) with the canonical rate."""
    cols = ["MeasureKey", "ReportProg", "Domain", "MeasureName", "MeasureAbbr",
            "RateDefinition", "MeasureType", "Direction", "State", "StateAbbr",
            "HHSRegion", "CoreSetYear", "StateRate", "InBottomQuartile"]
    p = clean[cols].copy()
    p = p.dropna(subset=["StateRate"])
    return p


def baseline_table(clean: pd.DataFrame) -> pd.DataFrame:
    p = _panel(clean)
    wide = p.pivot_table(index=["MeasureKey", "ReportProg", "MeasureType", "Direction",
                                "Domain", "MeasureName", "MeasureAbbr", "State"],
                         columns="CoreSetYear", values="StateRate", aggfunc="first")
    recs = []
    for (y0, y1) in config.YEAR_TRANSITIONS:
        if y0 not in wide.columns or y1 not in wide.columns:
            continue
        d = (wide[y1] - wide[y0]).dropna()
        tmp = d.reset_index().rename(columns={0: "delta"})
        tmp.columns = [*tmp.columns[:-1], "delta"]
        tmp["transition"] = f"{y0}->{y1}"
        recs.append(tmp)
    deltas = pd.concat(recs, ignore_index=True)

    base = (deltas.groupby(GROUP + ["transition"])["delta"]
            .agg(baseline_mean="mean", baseline_sd="std", n_pairs="count")
            .reset_index())
    return base, deltas


def classify(clean: pd.DataFrame) -> dict:
    base, deltas = baseline_table(clean)
    merged = deltas.merge(base, on=GROUP + ["transition"], how="left")

    state_ref = (clean[["State", "StateAbbr", "HHSRegion"]]
                 .drop_duplicates("State"))
    merged = merged.merge(state_ref, on="State", how="left")

    lo = merged["baseline_mean"] - config.CLASS_BAND_SD * merged["baseline_sd"]
    hi = merged["baseline_mean"] + config.CLASS_BAND_SD * merged["baseline_sd"]
    higher = merged["Direction"].eq(config.DIRECTION_HIGHER)

    cls = np.where(
        merged["delta"] > hi,
        np.where(higher, "Improving", "Declining"),
        np.where(
            merged["delta"] < lo,
            np.where(higher, "Declining", "Improving"),
            "Stable",
        ),
    )
    merged["classification"] = cls
    merged["improve_delta"] = np.where(higher, merged["delta"], -merged["delta"])

    persistent = _persistent_bottom(clean)

    # ---- per-state rollup --------------------------------------------------
    state_roll = []
    for (prog, state), g in merged.groupby(["ReportProg", "State"]):
        pb = persistent[(persistent["ReportProg"] == prog)
                        & (persistent["State"] == state)]
        state_roll.append({
            "program": prog,
            "state": state,
            "abbr": g["StateAbbr"].iloc[0],
            "region": int(g["HHSRegion"].iloc[0]) if pd.notna(g["HHSRegion"].iloc[0]) else None,
            "n_transitions_scored": int(len(g)),
            "n_improving": int((g["classification"] == "Improving").sum()),
            "n_declining": int((g["classification"] == "Declining").sum()),
            "n_stable": int((g["classification"] == "Stable").sum()),
            "mean_improve_delta": round(float(g["improve_delta"].mean()), 2),
            "n_persistent_bottom_measures": int(pb["persistent_bottom"].sum()),
        })
    state_roll.sort(key=lambda r: (r["program"], r["mean_improve_delta"]))

    # ---- per-measure rollup ---------------------------------------------------
    meas_roll = []
    for key, g in merged.groupby("MeasureKey"):
        meas_roll.append({
            "measure_key": key,
            "program": g["ReportProg"].iloc[0],
            "domain": g["Domain"].iloc[0],
            "measure_name": g["MeasureName"].iloc[0],
            "direction": g["Direction"].iloc[0],
            "n_improving": int((g["classification"] == "Improving").sum()),
            "n_declining": int((g["classification"] == "Declining").sum()),
            "n_stable": int((g["classification"] == "Stable").sum()),
            "mean_improve_delta": round(float(g["improve_delta"].mean()), 2),
        })
    meas_roll.sort(key=lambda r: r["mean_improve_delta"])

    return {
        "window": "2022-2024",
        "transitions": [f"{a}->{b}" for a, b in config.YEAR_TRANSITIONS],
        "class_band_sd": config.CLASS_BAND_SD,
        "baseline": _round_records(base.to_dict("records"),
                                   ["baseline_mean", "baseline_sd"]),
        "state_rollup": state_roll,
        "measure_rollup": meas_roll,
        "detail": [
            {
                "measure_key": r["MeasureKey"], "program": r["ReportProg"],
                "domain": r["Domain"], "state": r["State"], "abbr": r["StateAbbr"],
                "region": int(r["HHSRegion"]) if pd.notna(r["HHSRegion"]) else None,
                "transition": r["transition"], "direction": r["Direction"],
                "delta": round(float(r["delta"]), 2),
                "improve_delta": round(float(r["improve_delta"]), 2),
                "baseline_mean": round(float(r["baseline_mean"]), 3),
                "baseline_sd": round(float(r["baseline_sd"]), 3),
                "classification": r["classification"],
            }
            for r in merged.to_dict("records")
        ],
        "persistent_bottom": [
            {"program": r["ReportProg"], "state": r["State"],
             "measure_key": r["MeasureKey"], "years_in_bottom": int(r["years_in_bottom"])}
            for r in persistent[persistent["persistent_bottom"]].to_dict("records")
        ],
    }


def _persistent_bottom(clean: pd.DataFrame) -> pd.DataFrame:
    p = clean.dropna(subset=["StateRate"]).copy()
    p["in_bottom"] = p["InBottomQuartile"].map(
        lambda v: True if v in (True, "True", "true") else (
            False if v in (False, "False", "false") else np.nan))
    g = (p.groupby(["ReportProg", "State", "MeasureKey"])
         .agg(years_in_bottom=("in_bottom", "sum"),
              years_scored=("in_bottom", "count"))
         .reset_index())
    g["persistent_bottom"] = g["years_in_bottom"] >= config.PERSISTENT_BOTTOM_MIN_YEARS
    return g


def _round_records(recs, keys):
    for r in recs:
        for k in keys:
            if r.get(k) is not None and not pd.isna(r[k]):
                r[k] = round(float(r[k]), 3)
    return recs
