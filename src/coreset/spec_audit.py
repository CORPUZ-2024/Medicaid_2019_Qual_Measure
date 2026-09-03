"""Section 2.3 - reporting & measure-specification comparability gating.

Before any DeltaRate from 2.2 is rendered as a trend line it must pass all of:

  (i)   2.3b  the measure is on CMS's own trendable list for 2022-2024
              (approximated here when data/reference/cms_trendable_measures.csv
              is empty; the approximation is flagged in the output).
  (ii)  2.3c  the measure's specification did not change between the two years
              compared (data/reference/spec_changes.csv).
  (iii) 2.3d  neither state in the pairwise comparison is flagged "other
              specifications" for either year.

Also carries the 2.3a mandatory-reporting discontinuity as a window-level note:
Child Core Set reporting and Adult behavioral-health measures became MANDATORY
with the 2024 Core Set, so the 2023->2024 point rests on a structurally larger
set of reporting states.
"""

from __future__ import annotations

import re

import pandas as pd

from . import config, ingest

OTHER_SPEC_RE = re.compile(r"other specification|other data source|deviat", re.I)

MANDATORY_2024_NOTE = (
    "Child Core Set reporting, and the behavioral-health measures on the Adult "
    "Core Set, became mandatory starting with the 2024 Core Set. The 2023->2024 "
    "transition therefore crosses a voluntary-to-mandatory reporting boundary and "
    "carries half of a two-transition trend signal. Treat a 2023->2024 'decline' "
    "for a previously-inconsistent reporter as possibly a reporting-completeness "
    "effect, not a care-quality change."
)


# ---------------------------------------------------------------------------
# 2.3b - trendability
# ---------------------------------------------------------------------------
def trendable_measures(clean: pd.DataFrame) -> pd.DataFrame:
    rated = clean.dropna(subset=["StateRate"])
    years = set(config.CORE_SET_YEARS)

    rows = []
    for key, g in rated.groupby("MeasureKey"):
        by_year = g.groupby("CoreSetYear")["State"].nunique()
        present_all = years.issubset(set(by_year.index))
        # consistent set of >= 20 states reporting in ALL three years
        states_by_year = {y: set(g.loc[g.CoreSetYear == y, "State"]) for y in years if y in by_year.index}
        consistent = set.intersection(*states_by_year.values()) if len(states_by_year) == len(years) else set()
        rows.append({
            "measure_key": key,
            "program": g["ReportProg"].iloc[0],
            "domain": g["Domain"].iloc[0],
            "measure_name": g["MeasureName"].iloc[0],
            "measure_abbr": g["MeasureAbbr"].iloc[0],
            "present_all_years": bool(present_all),
            "n_consistent_states": int(len(consistent)),
            "meets_state_threshold": bool(len(consistent) >= config.TREND_MIN_STATES),
        })
    df = pd.DataFrame(rows)

    override = _load_cms_trendable()
    df["cms_listed_trendable"] = pd.NA
    if override is not None and len(override):
        key_map = {(r["program"], r["measure_name"]): r["trendable_2022_2024"]
                   for _, r in override.iterrows()}
        df["cms_listed_trendable"] = df.apply(
            lambda r: key_map.get((r["program"], r["measure_name"]), pd.NA), axis=1)

    spec_break = _spec_change_measures()
    df["spec_change_in_window"] = df["measure_name"].apply(
        lambda n: any(pat.lower() in str(n).lower() for pat in spec_break))

    df["trendable_computed"] = (
        df["present_all_years"] & df["meets_state_threshold"] & ~df["spec_change_in_window"]
    )
    df["trendable_source"] = "computed_approximation" if override is None or not len(override) \
        else "cms_list_with_computed_fallback"
    return df


def _load_cms_trendable():
    path = config.REFERENCE / "cms_trendable_measures.csv"
    if not path.exists():
        return None
    df = pd.read_csv(path, comment="#")
    return df.dropna(how="all")


def _spec_change_measures() -> list[str]:
    path = config.REFERENCE / "spec_changes.csv"
    if not path.exists():
        return []
    df = pd.read_csv(path, comment="#")
    df = df[df["ncqa_comparable"].astype(str).str.lower() == "no"]
    return df["measure_name_contains"].dropna().tolist()


def spec_change_records() -> list[dict]:
    path = config.REFERENCE / "spec_changes.csv"
    if not path.exists():
        return []
    return pd.read_csv(path, comment="#").fillna("").to_dict("records")


# ---------------------------------------------------------------------------
# 2.3d - state-level "other specifications" flag
# ---------------------------------------------------------------------------
def other_spec_flags() -> pd.DataFrame:
    """(CoreSetYear, State, MeasureName) -> flagged True when the state's
    row for that measure carries a methodology-deviation comment."""
    raw = ingest.load_all()
    text = (raw["StateSpecificComments"].astype(str) + " || "
            + raw["Notes"].astype(str) + " || "
            + raw["Methodology"].astype(str))
    raw = raw.assign(other_spec=text.apply(lambda t: bool(OTHER_SPEC_RE.search(t))))
    flagged = (raw.groupby(["CoreSetYear", "State", "MeasureName"])["other_spec"]
               .any().reset_index())
    return flagged[flagged["other_spec"]]


# ---------------------------------------------------------------------------
# Combine into a per-(measure, state, transition) comparability verdict
# ---------------------------------------------------------------------------
def gate_trend_detail(trend_detail: list[dict], clean: pd.DataFrame) -> list[dict]:
    tm = trendable_measures(clean).set_index("measure_key")
    osf = other_spec_flags()
    osf_set = set(zip(osf["CoreSetYear"], osf["State"], osf["MeasureName"]))
    name_by_key = clean.drop_duplicates("MeasureKey").set_index("MeasureKey")["MeasureName"].to_dict()

    out = []
    for d in trend_detail:
        key = d["measure_key"]
        y0, y1 = (int(x) for x in d["transition"].split("->"))
        mname = name_by_key.get(key)
        reasons = []

        if key in tm.index:
            row = tm.loc[key]
            listed = row.get("cms_listed_trendable")
            if pd.notna(listed) and str(listed).strip().lower() == "no":
                reasons.append("not on CMS trendable list")
            elif pd.isna(listed) and not bool(row["trendable_computed"]):
                if not row["present_all_years"]:
                    reasons.append("not reported in all 3 years")
                if not row["meets_state_threshold"]:
                    reasons.append(f"<{config.TREND_MIN_STATES} consistently-reporting states")
                if row["spec_change_in_window"]:
                    reasons.append("specification change in window (2.3c)")
        else:
            reasons.append("measure not present in trend panel")

        st = d["state"]
        if (y0, st, mname) in osf_set or (y1, st, mname) in osf_set:
            reasons.append("state flagged 'other specifications' (2.3d)")

        d2 = dict(d)
        d2["comparable"] = len(reasons) == 0
        d2["not_comparable_reasons"] = reasons
        if not d2["comparable"]:
            d2["classification_display"] = "Not comparable"
        else:
            d2["classification_display"] = d2["classification"]
        out.append(d2)
    return out


def audit_summary(clean: pd.DataFrame) -> dict:
    tm = trendable_measures(clean)
    return {
        "mandatory_2024_note": MANDATORY_2024_NOTE,
        "trend_min_states": config.TREND_MIN_STATES,
        "public_release_min_states": config.PUBLIC_RELEASE_MIN_STATES,
        "n_measure_keys": int(len(tm)),
        "n_trendable_computed": int(tm["trendable_computed"].sum()),
        "n_trendable_by_program": tm.groupby("program")["trendable_computed"].sum().astype(int).to_dict(),
        "trendable_source": tm["trendable_source"].iloc[0] if len(tm) else None,
        "spec_changes": spec_change_records(),
        "trendable_detail": tm.to_dict("records"),
        "caveat": ("The trendable filter here is a computed approximation of CMS's "
                   "three-part criterion (publicly reported all 3 years; >=20 "
                   "consistently reporting states; stable specs). Populate "
                   "data/reference/cms_trendable_measures.csv from CMS's own brief "
                   "to replace the approximation. CMS reported 19 Child + 22 Adult "
                   "measures trendable for 2022-2024."),
    }
