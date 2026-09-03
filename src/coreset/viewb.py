"""Section 1 - View B extension: all states x all measures, Adult + Child, 2024.

Outputs (consumed by src/coreset/build.py -> docs/data/view_b.json):

* measures[]        one entry per MeasureKey: the sorted per-state bar data plus
                    CMS quartile thresholds and the 3-up summary card (1.2.A).
* composite[]       per-state OnTrackShare for 2024, split Child/Adult (1.2.B).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from . import config

SUMMARY_YEAR = 2024


def _best_worst(sub: pd.DataFrame) -> tuple[dict, dict, dict]:
    """Top / median-closest / bottom performing *state* for one measure-year.

    Per spec 1.2.A the top-performing state is the state with the best StateRate
    (direction-aware), which is NOT necessarily equal to CMS's Top-quartile
    threshold value - that distinction is surfaced in the UI.
    """
    s = sub.dropna(subset=["StateRate"])
    if s.empty:
        return {}, {}, {}
    higher = s["Direction"].iloc[0] == config.DIRECTION_HIGHER
    ordered = s.sort_values("StateRate", ascending=not higher)
    best = ordered.iloc[0]
    worst = ordered.iloc[-1]
    med = s["StateRate"].median()
    mid = s.iloc[(s["StateRate"] - med).abs().argsort().iloc[0]]

    def pack(row, extra=None):
        d = {"state": row["State"], "abbr": row["StateAbbr"], "rate": round(float(row["StateRate"]), 1)}
        if extra:
            d.update(extra)
        return d

    return (
        pack(best),
        pack(mid, {"cohort_median": round(float(med), 1)}),
        pack(worst),
    )


def build_view_b(clean: pd.DataFrame) -> dict:
    df = clean[clean["CoreSetYear"] == SUMMARY_YEAR].copy()
    measures = []

    for key, sub in df.groupby("MeasureKey", sort=True):
        sub = sub.copy()
        higher = sub["Direction"].iloc[0] == config.DIRECTION_HIGHER
        rated = sub.dropna(subset=["StateRate"]).sort_values("StateRate", ascending=True)
        on = (sub["Eval"] == "On Track").sum()
        off = (sub["Eval"] == "Not on Track").sum()
        top_state, med_state, bot_state = _best_worst(sub)

        measures.append({
            "measure_key": key,
            "program": sub["ReportProg"].iloc[0],
            "domain": sub["Domain"].iloc[0],
            "measure_name": sub["MeasureName"].iloc[0],
            "measure_abbr": sub["MeasureAbbr"].iloc[0],
            "rate_definition": sub["RateDefinition"].iloc[0],
            "direction": sub["Direction"].iloc[0],
            "measure_type_label": sub["MeasureType"].iloc[0],
            "color_scale": config.color_scale_for(sub["Domain"].iloc[0]),
            "n_states_reported": int(rated.shape[0]),
            "cms_num_states_reporting": _first_num(sub, "NumStatesReporting"),
            "cms_mean": _first_num(sub, "Mean"),
            "cms_median": _first_num(sub, "Median"),
            "cms_bottom_quartile": _first_num(sub, "Bottom"),
            "cms_top_quartile": _first_num(sub, "Top"),
            "n_on_track": int(on),
            "n_not_on_track": int(off),
            "bars": [
                {"state": r["State"], "abbr": r["StateAbbr"],
                 "rate": round(float(r["StateRate"]), 1),
                 "eval": r["Eval"] if pd.notna(r["Eval"]) else None,
                 "region": _int_or_none(r["HHSRegion"])}
                for _, r in rated.iterrows()
            ],
            "summary_card": {
                "top_state": top_state,
                "median_state": med_state,
                "bottom_state": bot_state,
                "note": ("Top/bottom = the state with the best/worst reported rate. "
                         "CMS quartile values are computed across all reporting "
                         "states and are not tied to any one state."),
            },
        })

    domains = {
        prog: sorted(df.loc[df["ReportProg"] == prog, "Domain"].dropna().unique())
        for prog in ["Child Core Set", "Adult Core Set"]
    }
    return {
        "summary_year": SUMMARY_YEAR,
        "programs": ["Child Core Set", "Adult Core Set"],
        "domains": domains,
        "measures": measures,
        "composite": build_composite(clean),
    }


def build_composite(clean: pd.DataFrame) -> list[dict]:
    """Spec 1.2.B - OnTrackShare(state, program) for the summary year, capped to
    states meeting MIN_REPORTED_MEASURES_FOR_RANKING before ranking."""
    df = clean[(clean["CoreSetYear"] == SUMMARY_YEAR) & clean["Eval"].notna()].copy()
    rows = []
    for (state, prog), g in df.groupby(["State", "ReportProg"]):
        reported = len(g)
        on_track = (g["Eval"] == "On Track").sum()
        rows.append({
            "state": state,
            "abbr": g["StateAbbr"].iloc[0],
            "region": _int_or_none(g["HHSRegion"].iloc[0]),
            "program": prog,
            "measures_reported": int(reported),
            "measures_on_track": int(on_track),
            "on_track_share": round(on_track / reported, 4) if reported else None,
            "meets_ranking_cutoff": bool(reported >= config.MIN_REPORTED_MEASURES_FOR_RANKING),
        })
    rows.sort(key=lambda r: (r["program"], -(r["on_track_share"] or 0)))
    return rows


def _first_num(sub: pd.DataFrame, col: str):
    v = sub[col].dropna()
    return round(float(v.iloc[0]), 2) if len(v) else None


def _int_or_none(v):
    return int(v) if pd.notna(v) else None
