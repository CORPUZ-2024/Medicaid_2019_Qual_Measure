"""Paths and shared constants for the Core Set View B extension pipeline."""

from __future__ import annotations

from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
RAW = DATA / "raw"
PROCESSED = DATA / "processed"
REGION_LOOKUP = DATA / "region_lookup.csv"
REFERENCE = DATA / "reference"
DOCS = ROOT / "docs"
DOCS_DATA = DOCS / "data"

# ---------------------------------------------------------------------------
# Trend window (spec v2 section 2.1) - CMS's own 2022-2024 trending span.
# ---------------------------------------------------------------------------
CORE_SET_YEARS = [2022, 2023, 2024]
YEAR_TRANSITIONS = [(2022, 2023), (2023, 2024)]

# Raw file name per Core Set year (downloaded from data.medicaid.gov, Quality theme).
RAW_FILES = {
    2022: "2022-core-set.csv",
    2023: "2023-core-set.csv",
    2024: "2024-core-set.csv",
}

# ---------------------------------------------------------------------------
# Canonical (post-cleaning) column names. Mirrors the 2019 notebook's rename
# step so downstream code reads the same as the original repo where possible.
# ---------------------------------------------------------------------------
COLS = dict(
    State="State",
    StateAbbr="StateAbbr",
    ReportProg="ReportProg",
    Domain="Domain",
    MeasureName="MeasureName",
    MeasureAbbr="MeasureAbbr",
    RateDefinition="RateDefinition",
    MeasureType="MeasureType",          # CMS field: directionality, see note below
    Direction="Direction",              # derived: "higher_better" | "lower_better"
    CoreSetYear="CoreSetYear",
    Population="Population",
    Methodology="Methodology",
    StateRate="StateRate",
    NumStatesReporting="NumStatesReporting",
    Mean="Mean",
    Median="Median",
    Bottom="Bottom",
    Top="Top",
    RateUsedInMeanMedian="RateUsedInMeanMedian",
    Eval="Eval",
    MeasureKey="MeasureKey",            # ReportProg | MeasureName | RateDefinition
)

# NOTE on "Measure Type": in the data.medicaid.gov Quality files the column
# literally named "Measure Type" contains only two values -
#   "Higher rates are better for this measure"
#   "Lower rates are better for this measure"
# i.e. it is a *directionality* flag, not a measure taxonomy. The V0 ask to
# "provide visuals ... by measure type" and the v2 baseline "by measure type"
# are therefore served by (a) this directionality split and (b) the Domain
# accordion. This interpretation is documented in docs/methodology/measure-type.md.
DIRECTION_HIGHER = "higher_better"
DIRECTION_LOWER = "lower_better"

# ---------------------------------------------------------------------------
# Domains by program (spec section 0).
# ---------------------------------------------------------------------------
CHILD_DOMAINS = [
    "Behavioral Health Care",
    "Care of Acute and Chronic Conditions",
    "Dental and Oral Health Services",
    "Maternal and Perinatal Health",
    "Primary Care Access and Preventive Care",
]
ADULT_DOMAINS = [
    "Primary Care Access and Preventive Care",
    "Maternal and Perinatal Health",
    "Care of Acute and Chronic Conditions",
    "Behavioral Health Care",
    "Experience of Care",
    "Long-Term Services and Supports",
]

# Domain -> continuous colour scale (mirrors 2019Medicaid.ipynb color_dict pattern;
# adult_color_dict added for the 6 Adult domains per spec 1.1).
# Domain -> Plotly.js continuous colour scale. Only names built into plotly.js
# core are used (Purples/Teal/Oranges are Plotly-Express-only and silently fall
# back). Shared across both programs so a domain that appears in a vintage where
# the spec did not expect it (e.g. "Experience of Care" arrived on the 2024 Child
# Core Set) still resolves.
DOMAIN_COLOR_SCALE = {
    "Behavioral Health Care": "Blues",
    "Care of Acute and Chronic Conditions": "YlGnBu",
    "Dental and Oral Health Services": "Greens",
    "Maternal and Perinatal Health": "Reds",
    "Primary Care Access and Preventive Care": "YlOrRd",
    "Experience of Care": "Portland",
    "Long-Term Services and Supports": "Greys",
}
DOMAIN_COLOR_DEFAULT = "Viridis"


def color_scale_for(domain: str) -> str:
    return DOMAIN_COLOR_SCALE.get(domain, DOMAIN_COLOR_DEFAULT)

# Domains weighted higher in the risk score (spec 3.2.1): most exposed to
# administrative-capacity strain from new eligibility / work-requirement systems.
RISK_DOMAIN_WEIGHTS = {
    "Behavioral Health Care": 1.5,
    "Long-Term Services and Supports": 1.5,
}
RISK_DOMAIN_WEIGHT_DEFAULT = 1.0

# CAHPS-survey domains most often excluded from CMS trend analysis (spec section 0).
SURVEY_DOMAINS = {"Experience of Care", "Long-Term Services and Supports"}

# ---------------------------------------------------------------------------
# Trendability filter thresholds (spec 2.3b).
# ---------------------------------------------------------------------------
TREND_MIN_STATES = 20            # consistent set of >= 20 states across all 3 years
PUBLIC_RELEASE_MIN_STATES = 25   # CMS public-release threshold (spec limitation #5)

# Composite OnTrackShare ranking cutoff (spec 1.2.B).
MIN_REPORTED_MEASURES_FOR_RANKING = 10

# Classification band width, in SD of the per-group baseline delta (spec 2.2).
CLASS_BAND_SD = 0.5

# Persistent-bottom-quartile: in bottom-quartile territory in >= N of 3 years.
PERSISTENT_BOTTOM_MIN_YEARS = 2
