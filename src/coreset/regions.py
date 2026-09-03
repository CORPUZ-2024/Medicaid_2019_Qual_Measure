"""HHS-region and state-abbreviation lookup (spec section 2.4).

The authoritative HHS region -> state mapping lives in ``data/region_lookup.csv``.
The ad hoc four-region grouping in the original 2019Medicaid.ipynb
(NE_states / W_states / S_states / midwest_states) is intentionally retired in
favour of this table, as the spec instructs.
"""

from __future__ import annotations

import pandas as pd

from . import config


def load_region_lookup() -> pd.DataFrame:
    """State -> (StateAbbr, HHSRegion, HHSRegionHQ)."""
    df = pd.read_csv(config.REGION_LOOKUP, dtype={"HHSRegion": "Int64"})
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


def attach_regions(df: pd.DataFrame) -> pd.DataFrame:
    """Add StateAbbr / HHSRegion / HHSRegionHQ columns by static lookup on State."""
    lookup = load_region_lookup()
    out = df.copy()
    out["State"] = out["State"].map(normalize_state_name)
    merged = out.merge(lookup, on="State", how="left")
    missing = sorted(merged.loc[merged["HHSRegion"].isna(), "State"].dropna().unique())
    if missing:
        # Not fatal - surfaced so a new territory in a future vintage is noticed.
        print(f"[regions] WARNING: no HHS region mapping for: {missing}")
    return merged
