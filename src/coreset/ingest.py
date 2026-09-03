"""Section 2.1 - load the three raw Core Set vintages, normalise their schema,
tag each with CoreSetYear, and concatenate.

Schema drift handled here (confirmed by inspecting the actual downloads):
  * 2022 names the year column "FFY"; 2023/2024 name it "Core Set Year".
  * 2024 ships a "Mean" column; 2022/2023 do not (filled as NA).
  * Column order is otherwise consistent across all three files.
"""

from __future__ import annotations

import pandas as pd

from . import config

# Raw CMS header -> canonical name.
RAW_RENAME = {
    "State": "State",
    "Domain": "Domain",
    "Reporting Program": "ReportProg",
    "Measure Name": "MeasureName",
    "Measure Abbreviation": "MeasureAbbr",
    "Measure Type": "MeasureType",
    "Rate Definition": "RateDefinition",
    "FFY": "CoreSetYear",
    "Core Set Year": "CoreSetYear",
    "Population": "Population",
    "Methodology": "Methodology",
    "State Rate": "StateRate",
    "Number of States Reporting": "NumStatesReporting",
    "Mean": "Mean",
    "Median": "Median",
    "Bottom Quartile": "Bottom",
    "Top Quartile": "Top",
    "Notes": "Notes",
    "Source": "Source",
    "State-Specific Comments": "StateSpecificComments",
    "Rate Used in Calculating State Mean and Median": "RateUsedInMeanMedian",
}

CANONICAL_ORDER = [
    "CoreSetYear", "State", "ReportProg", "Domain", "MeasureName", "MeasureAbbr",
    "RateDefinition", "MeasureType", "Population", "Methodology",
    "StateRate", "NumStatesReporting", "Mean", "Median", "Bottom", "Top",
    "RateUsedInMeanMedian", "Notes", "Source", "StateSpecificComments",
]

NUMERIC_COLS = ["StateRate", "NumStatesReporting", "Mean", "Median", "Bottom", "Top"]


def load_year(year: int) -> pd.DataFrame:
    path = config.RAW / config.RAW_FILES[year]
    df = pd.read_csv(path, dtype=str)
    df = df.rename(columns=RAW_RENAME)
    for col in CANONICAL_ORDER:
        if col not in df.columns:
            df[col] = pd.NA
    df["CoreSetYear"] = int(year)
    for col in NUMERIC_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    for col in ["State", "ReportProg", "Domain", "MeasureName", "MeasureAbbr",
                "RateDefinition", "MeasureType", "Population", "RateUsedInMeanMedian"]:
        df[col] = df[col].astype("string").str.strip()
    return df[CANONICAL_ORDER]


def load_all() -> pd.DataFrame:
    frames = [load_year(y) for y in config.CORE_SET_YEARS]
    combined = pd.concat(frames, ignore_index=True)
    return combined
