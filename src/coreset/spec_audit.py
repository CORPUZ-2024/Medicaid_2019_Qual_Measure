"""Section 2.3 - trendability and comparability gating.

A state's year-over-year change on a measure rate is shown as a trend only if:

  (i)   CMS trendability. CMS's own rate-level determination for 2022-2024
        (data/reference/cms_trendable_measures.csv, transcribed from the CMS methods
        brief "Criteria for Using the Child and Adult Core Set Measures to Assess Trends
        in State Performance in Medicaid and CHIP", Sept 2025) is "Trend" or
        "Trend with caution". CMS's three criteria: the measure was publicly reported
        for each of the three years; a consistent set of at least 20 states reported it
        using Core Set specifications in all three years; and the specifications were
        comparable for all three years.
  (ii)  Change in state method (this site's additional check, not a CMS criterion):
        the state's CMS comments record a deviation from the Core Set specifications in
        one year of the pair but not the other, i.e. the state changed how it calculated
        the rate. A deviation reported in BOTH years is kept: it shifts the rate's level
        but not its year-over-year change, and CMS itself still publishes and trends
        those rates.

Also carries the 2024 mandatory-reporting discontinuity as a window-level note.
"""

from __future__ import annotations

import re

import pandas as pd

from . import config, ingest

TRENDABLE = {"Trend", "Trend with caution"}
CMS_BRIEF_URL = ("https://www.medicaid.gov/medicaid/quality-of-care/downloads/"
                 "trend-methods-brief-2024.pdf")
CMS_FACT_SHEET_URL = ("https://www.medicaid.gov/medicaid/quality-of-care/downloads/"
                      "2024-core-set-reporting.pdf")
CMS_TREND_XLSX_URL = ("https://www.medicaid.gov/medicaid/quality-of-care/downloads/"
                      "trend-analysis-2024.xlsx")

OTHER_SPEC_RE = re.compile(r"other specification|other data source|deviat", re.I)

MANDATORY_2024_NOTE = (
    "Child Core Set reporting, and the behavioral-health measures on the Adult Core Set, "
    "became mandatory starting with the 2024 Core Set. CMS notes this may affect "
    "comparability with earlier years because of changes in included populations and "
    "reporting methods. Treat a 2023->2024 decline for a previously inconsistent reporter "
    "as possibly a reporting-completeness effect, not a care-quality change."
)


# ---------------------------------------------------------------------------
# (i) CMS rate-level trending determination
# ---------------------------------------------------------------------------
def _load_cms_rules() -> pd.DataFrame:
    path = config.REFERENCE / "cms_trendable_measures.csv"
    df = pd.read_csv(path, comment="#").dropna(how="all")
    df["rate_regex"] = df["rate_regex"].fillna("")
    return df


def determinations(clean: pd.DataFrame) -> pd.DataFrame:
    """One row per MeasureKey with CMS's determination and reason."""
    rules = _load_cms_rules()
    latest = (clean.sort_values("CoreSetYear")
              .groupby("MeasureKey")
              .agg(program=("ReportProg", "last"), domain=("Domain", "last"),
                   measure_name=("MeasureName", "last"), measure_abbr=("MeasureAbbr", "last"),
                   rate_definition=("RateDefinition", "last"), direction=("Direction", "last"),
                   years=("CoreSetYear", lambda s: sorted({int(y) for y in s})))
              .reset_index())
    out = []
    for r in latest.itertuples(index=False):
        cand = rules[(rules["program"] == r.program) & (rules["measure_abbr"] == r.measure_abbr)]
        hit = None
        for c in cand.itertuples(index=False):
            if not c.rate_regex or re.search(c.rate_regex, str(r.rate_definition).strip(), re.I):
                hit = c
                break
        out.append({
            "measure_key": r.MeasureKey, "program": r.program, "domain": r.domain,
            "measure_name": r.measure_name, "measure_abbr": r.measure_abbr,
            "rate_definition": r.rate_definition, "direction": r.direction,
            "years": r.years,
            "determination": hit.determination if hit is not None else "Do Not Trend",
            "reason": hit.reason if hit is not None else "Not covered by CMS's 2022-2024 trend assessment",
            "source": hit.source if hit is not None else "not_assessed",
        })
    df = pd.DataFrame(out)
    df["trendable"] = df["determination"].isin(TRENDABLE)
    return df


# ---------------------------------------------------------------------------
# (ii) state-reported deviations from Core Set specifications
# ---------------------------------------------------------------------------
def other_spec_flags() -> set:
    """{(CoreSetYear, State, MeasureName)} whose CMS comments record a state-reported
    deviation from the Core Set specifications."""
    raw = ingest.load_all()
    text = (raw["StateSpecificComments"].astype(str) + " || "
            + raw["Notes"].astype(str) + " || " + raw["Methodology"].astype(str))
    raw = raw.assign(other_spec=text.str.contains(OTHER_SPEC_RE))
    f = raw[raw["other_spec"]]
    return set(zip(f["CoreSetYear"].astype(int), f["State"], f["MeasureName"]))


def gate(deltas: pd.DataFrame, clean: pd.DataFrame) -> pd.DataFrame:
    """Add comparable / not_comparable_reasons / cms_determination to each
    state x rate x transition change."""
    det = determinations(clean).set_index("measure_key")
    osf = other_spec_flags()
    name_by_key = det["measure_name"].to_dict()

    comparable, reasons, cms_det = [], [], []
    for r in deltas.itertuples(index=False):
        y0, y1 = (int(x) for x in r.transition.split("->"))
        why = []
        d = det.loc[r.MeasureKey]
        cms_det.append(d["determination"])
        if not d["trendable"]:
            why.append(f"CMS: {d['determination']} ({d['reason']})")
        mname = name_by_key.get(r.MeasureKey)
        if ((y0, r.State, mname) in osf) != ((y1, r.State, mname) in osf):
            why.append("state's reported deviation from Core Set specifications changed between the two years")
        comparable.append(not why)
        reasons.append(why)
    out = deltas.copy()
    out["comparable"] = comparable
    out["not_comparable_reasons"] = reasons
    out["cms_determination"] = cms_det
    return out


def audit_summary(clean: pd.DataFrame, gated: pd.DataFrame) -> dict:
    det = determinations(clean)
    in_2024 = det[det["years"].apply(lambda y: 2024 in y)]
    # CMS counts a measure as trendable when at least one of its rates is
    meas = (in_2024[in_2024["source"] != "not_assessed"]
            .groupby(["program", "measure_abbr"])["trendable"].any().reset_index())
    dev = gated["not_comparable_reasons"].apply(
        lambda w: any("deviation" in x for x in w) and not any(x.startswith("CMS") for x in w))
    return {
        "mandatory_2024_note": MANDATORY_2024_NOTE,
        "sources": {"methods_brief": CMS_BRIEF_URL, "fact_sheet": CMS_FACT_SHEET_URL,
                    "cms_trend_results": CMS_TREND_XLSX_URL},
        "criteria": [
            "The measure was publicly reported by CMS for each of the most recent three years "
            "(public reporting requires at least 25 states using Core Set specifications and "
            "meeting CMS data-quality standards).",
            "The measure was reported by a consistent set of at least 20 states that used Core "
            "Set specifications in all three years.",
            "The measure specifications were comparable for all three years (no specification "
            "or data-source change that would make results incomparable).",
        ],
        "n_measures_trendable_by_program": meas.groupby("program")["trendable"].sum().astype(int).to_dict(),
        "n_measures_assessed_by_program": meas.groupby("program").size().astype(int).to_dict(),
        "n_rates_2024": int(len(in_2024)),
        "n_rates_2024_trendable": int(in_2024["trendable"].sum()),
        "n_changes_total": int(len(gated)),
        "n_changes_comparable": int(gated["comparable"].sum()),
        "n_changes_excluded_cms": int(gated["not_comparable_reasons"].apply(
            lambda w: any(x.startswith("CMS") for x in w)).sum()),
        "n_changes_excluded_deviation_only": int(dev.sum()),
        "determinations": det.drop(columns=["trendable"]).to_dict("records"),
    }
