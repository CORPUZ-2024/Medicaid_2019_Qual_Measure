"""State-name normalisation and two-letter abbreviation lookup.

The State -> StateAbbr table lives in ``data/state_lookup.csv``.
"""

from __future__ import annotations

import pandas as pd

from . import config


def load_state_lookup() -> pd.DataFrame:
    df = pd.read_csv(config.STATE_LOOKUP)
    df["State"] = df["State"].str.strip()
    return df


# Some CMS files spell the territory differently; normalise to the lookup's key.
STATE_NAME_ALIASES = {
    "District of Columbia": "Dist. of Col.",
    "U.S. Virgin Islands": "Virgin Islands",
    "United States Virgin Islands": "Virgin Islands",
    "USVI": "Virgin Islands",
}


def normalize_state_name(name: str) -> str:
    if not isinstance(name, str):
        return name
    name = name.strip()
    return STATE_NAME_ALIASES.get(name, name)


def attach_state_abbr(df: pd.DataFrame) -> pd.DataFrame:
    """Add a StateAbbr column by static lookup on State."""
    out = df.copy()
    out["State"] = out["State"].map(normalize_state_name)
    merged = out.merge(load_state_lookup(), on="State", how="left")
    missing = sorted(merged.loc[merged["StateAbbr"].isna(), "State"].dropna().unique())
    if missing:
        # Not fatal - surfaced so a new territory in a future vintage is noticed.
        print(f"[states] WARNING: no abbreviation for: {missing}")
    return merged
