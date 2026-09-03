"""Section 2.1 (continued) - resolve row uniqueness, derive analysis columns.

Key decisions, all documented in docs/methodology/data-cleaning.md:

1. Canonical rate.  One CMS "Measure Name" spans several "Rate Definition" rows
   (e.g. 7-day vs 30-day follow-up) and, within each, several "Population"
   breakouts (Medicaid+CHIP combined, expansion-CHIP only, separate-CHIP only).
   CMS flags exactly one Population row per (state, measure, rate definition) with
   ``Rate Used in Calculating State Mean and Median == "Yes"``.  We keep those
   rows as the canonical rate.  This replaces the 2019 notebook's arbitrary
   "keep first occurrence" fix with CMS's own designation.

2. Dedupe key.  (CoreSetYear, State, ReportProg, Domain, MeasureName,
   RateDefinition, Population).  Any collision that survives canonical-rate
   selection is written to data/processed/dq_exceptions.csv and the first row
   kept - it is logged, never silently dropped (spec 2.1).

3. MeasureKey = "ReportProg | MeasureName | RateDefinition" is the unit of
   analysis for View B and every trend calculation - it is the finest grain at
   which a rate is comparable across states and years.

4. Direction.  The CMS "Measure Type" column is a directionality flag; we map it
   to Direction in {higher_better, lower_better} and use it everywhere a rate has
   to be compared to a benchmark.

5. Eval (On Track / Not on Track).  Re-derived from the 2019 notebook's idea but
   made direction-aware:
       higher_better -> On Track iff StateRate >= Median
       lower_better  -> On Track iff StateRate <= Median
"""

from __future__ import annotations

import pandas as pd

from . import config, ingest, regions

DEDUPE_KEY = [
    "CoreSetYear", "State", "ReportProg", "Domain",
    "MeasureName", "RateDefinition", "Population",
]

DIRECTION_MAP = {
    "Higher rates are better for this measure": config.DIRECTION_HIGHER,
    "Lower rates are better for this measure": config.DIRECTION_LOWER,
}


def _derive_direction(df: pd.DataFrame) -> pd.Series:
    d = df["MeasureType"].map(DIRECTION_MAP)
    unknown = df.loc[d.isna() & df["MeasureType"].notna(), "MeasureType"].unique()
    if len(unknown):
        print(f"[clean] WARNING: unmapped Measure Type values: {list(unknown)}")
    return d.fillna(config.DIRECTION_HIGHER)


def _derive_eval(df: pd.DataFrame) -> pd.Series:
    higher = df["Direction"].eq(config.DIRECTION_HIGHER)
    have = df["StateRate"].notna() & df["Median"].notna()
    on_track = pd.Series(pd.NA, index=df.index, dtype="object")
    on_track[have & higher] = (df.loc[have & higher, "StateRate"]
                               >= df.loc[have & higher, "Median"])
    on_track[have & ~higher] = (df.loc[have & ~higher, "StateRate"]
                                <= df.loc[have & ~higher, "Median"])
    return on_track.map({True: "On Track", False: "Not on Track"}).astype("string")


def _in_bottom_quartile(df: pd.DataFrame) -> pd.Series:
    """Direction-aware 'worst quartile' membership using CMS's own quartile
    threshold columns.  higher_better -> rate at/below Bottom; lower_better ->
    rate at/above Top (a high rate is the bad end)."""
    higher = df["Direction"].eq(config.DIRECTION_HIGHER)
    have = df["StateRate"].notna()
    res = pd.Series(pd.NA, index=df.index, dtype="object")
    m = have & higher & df["Bottom"].notna()
    res[m] = df.loc[m, "StateRate"] <= df.loc[m, "Bottom"]
    m = have & ~higher & df["Top"].notna()
    res[m] = df.loc[m, "StateRate"] >= df.loc[m, "Top"]
    return res.astype("object")


def build_clean(write: bool = True) -> pd.DataFrame:
    raw = ingest.load_all()

    # --- canonical rate: the Population row CMS used for its mean/median ------
    is_canonical = raw["RateUsedInMeanMedian"].str.lower().eq("yes")
    canonical = raw[is_canonical].copy()
    non_canonical = raw[~is_canonical].copy()

    # --- dedupe + exceptions log ------------------------------------------------
    dup_mask = canonical.duplicated(DEDUPE_KEY, keep=False)
    exceptions = canonical[dup_mask].sort_values(DEDUPE_KEY)
    canonical = canonical.drop_duplicates(DEDUPE_KEY, keep="first")

    # --- derived columns ------------------------------------------------------
    canonical["Direction"] = _derive_direction(canonical)
    canonical["Eval"] = _derive_eval(canonical)
    canonical["InBottomQuartile"] = _in_bottom_quartile(canonical)
    canonical["MeasureKey"] = (
        canonical["ReportProg"].str.replace(" Core Set", "", regex=False)
        + " | " + canonical["MeasureName"].fillna("")
        + " | " + canonical["RateDefinition"].fillna("")
    )

    # The non-canonical rows are retained on disk (non_canonical_rows.csv) so
    # spec_audit can derive the 2.3d "other specifications" state-level
    # comparability flag from them.

    canonical = regions.attach_regions(canonical)

    canonical = canonical.sort_values(
        ["CoreSetYear", "ReportProg", "Domain", "MeasureName", "RateDefinition", "State"]
    ).reset_index(drop=True)

    if write:
        config.PROCESSED.mkdir(parents=True, exist_ok=True)
        canonical.to_csv(config.PROCESSED / "core_set_clean.csv", index=False)
        exceptions.to_csv(config.PROCESSED / "dq_exceptions.csv", index=False)
        non_canonical.to_csv(config.PROCESSED / "non_canonical_rows.csv", index=False)
        print(f"[clean] canonical rows: {len(canonical):,}  "
              f"| dq exceptions: {len(exceptions):,}  "
              f"| non-canonical rows retained for 2.3d: {len(non_canonical):,}")

    return canonical


def load_clean() -> pd.DataFrame:
    path = config.PROCESSED / "core_set_clean.csv"
    if not path.exists():
        return build_clean(write=True)
    return pd.read_csv(path)
