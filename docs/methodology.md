# Methodology

How every number on this site is produced. Source code: `src/coreset/`,
orchestrated by `run.py`. Spec of record:
`project_plan/Medicaid_ViewB_GitHub_Pages_Implementation_Spec_v2.txt`.

## Data source

data.medicaid.gov — Quality theme. Three Core Set vintages:

| Core Set year | Reflects care in | Released | File |
|---|---|---|---|
| 2022 | ~2021 | Sept 2023 | `data/raw/2022-core-set.csv` |
| 2023 | ~2022 | Sept 2024 | `data/raw/2023-core-set.csv` |
| 2024 | ~2023 | Sept 2025 | `data/raw/2024-core-set.csv` |

`python run.py --fetch` re-downloads all three.

## Schema normalisation (`ingest.py`)

The 2022 file names the year column `FFY`; 2023/2024 name it `Core Set Year`. The
2024 file adds a `Mean` column the earlier two lack. Columns are renamed to the
2019 notebook's convention (`ReportProg`, `MeasureName`, `StateRate`, …), a
`CoreSetYear` integer is tagged on, and the three frames are concatenated.

## Canonical rate & row uniqueness (`clean.py`)

One CMS "Measure Name" spans several **Rate Definition** rows (e.g. 7-day vs
30-day follow-up) and, within each, several **Population** breakouts. CMS marks
exactly one Population row per (state, measure, rate definition) with
`Rate Used in Calculating State Mean and Median = Yes`. Those rows are the
**canonical rate**. This replaces the 2019 notebook's arbitrary "keep first
occurrence" fix with CMS's own designation. Any collision that survives is
written to `data/processed/dq_exceptions.csv`, not dropped.

**Unit of analysis:** `MeasureKey = ReportProg | MeasureName | RateDefinition`.

## <a id="measure-type"></a>"Measure Type" is a direction flag

In the data.medicaid.gov files the column literally named "Measure Type" holds
only two values — *"Higher rates are better for this measure"* and *"Lower rates
are better for this measure"*. It is **directionality**, not a taxonomy. So:

- The V0 ask to *"provide visuals … by measure type"* is served by the
  **direction filter** on page (B) plus the **domain toolbar**.
- Everywhere a rate is compared to a benchmark, the comparison is
  **direction-aware**:
  - `Eval` (On Track): higher-better → `rate ≥ median`; lower-better → `rate ≤ median`.
  - Worst-quartile membership: higher-better → `rate ≤ Bottom Quartile`;
    lower-better → `rate ≥ Top Quartile`.
  - Trend baseline is computed **per direction group**, so improving and
    declining measures never share a baseline.

## Page (A) — 2024 Measures by State and Domain (`state-domain.html`)

Computed in the browser from `docs/data/view_b.json`; no extra build step.

- **Observation** = one state × one 2024 measure series (`MeasureKey`) with a
  CMS `Eval`. **Above the median** = `Eval == "On Track"`, which is direction-aware
  (higher-better: `rate ≥ median`; lower-better: `rate ≤ median`).
- **Ranked overview:** `score(state) = above-median series / reported series`
  within the selected program × domain (either can be *All*). A state is ranked
  only if it reported at least `ceil(series in selection / 2)` series. Ties are
  broken by number reported. Top 10 and bottom 10 are listed, with excluded states
  named.
- **State rates table:** one row per state × series, with the CMS median and a gap
  oriented so that positive = better than the median.
- **Domain composite:** per program × domain — states reporting ≥ 1 series;
  distinct measures (by CMS abbreviation); rate series; **% of states above the
  median** = share of reporting states whose own above-median share in that
  domain is > 50%; series reported per state (min · median · max); and states
  reporting every series. The reporting-variation notes are generated from the
  same numbers.

## Page (B) — 2024 Across all States by Measure Type and Domain (`viewb.py`, `measures.html`)

- **Per-measure bars:** every reporting state's 2024 canonical rate, sorted
  ascending, colour = rate on a domain scale. One **red dashed line** at the CMS
  median marks the boundary: states on the arrow side are underperforming
  (`Eval = Not on Track`), direction-aware.
- **Titles:** where several series share one CMS measure name within a program,
  the follow-up period or sub-rate from the rate definition is appended in
  parentheses (e.g. *Follow-Up After Emergency Department Visit for Mental
  Illness: Ages 6 to 17 (Within 30 Days of the ED Visit)*). If the extra text
  would still not make the title unique, the plain name is kept and the rate
  definition line underneath tells the series apart.
- **Domain toolbar:** only domains that contain measures for the selected program.
- **3-up summary card:** top / median-closest / bottom **state** for the measure.
  The top state is the best *reported rate*, which is **not** the same as CMS's
  Top-quartile threshold value — the card says so.
- **Composite state summary:**
  `OnTrackShare(state, program) = on-track series / reported series`, 2024,
  pooled across **all measures in all domains**. The charts exclude states with
  < 10 reported series. The table has one row per state with the Child and Adult
  shares, sorted by `Child − Adult` descending; the gap is used only for ordering
  and is not displayed.

## Section 2.2 — baseline & classification (`trend.py`)

For each `(ReportProg, MeasureType)` group and each adjacent-year transition
(2022→2023, 2023→2024):

```
DeltaRate(s) = StateRate(s, t) − StateRate(s, t−1)   for states reporting BOTH years
baseline     = mean(DeltaRate) over that group ;  band = 0.5 × SD
```

Direction-aware classification:

| Direction | Improving | Declining |
|---|---|---|
| higher-better | Δ > baseline + 0.5 SD | Δ < baseline − 0.5 SD |
| lower-better | Δ < baseline − 0.5 SD | Δ > baseline + 0.5 SD |

else **Stable**. `improve_delta` is the direction-adjusted change (positive =
better) and is what the rollups average.

**Persistent Bottom Quartile:** in worst-quartile territory (direction-aware,
using CMS's own threshold columns) in ≥ 2 of the 3 years, regardless of movement.

## Section 2.3 — comparability gate (`spec_audit.py`)

Before a DeltaRate is shown as a trend line it must pass all of:

- **2.3b trendable** — present all 3 years **and** ≥ 20 states reporting in all 3
  years **and** no specification change in the window. This is a **computed
  approximation** of CMS's criterion; populate
  `data/reference/cms_trendable_measures.csv` to use CMS's own list instead.
- **2.3c specification change** — from `data/reference/spec_changes.csv`, seeded
  with the confirmed 2024 redefinition of *Prenatal and Postpartum Care*.
- **2.3d "other specifications"** — a `(year, state, measure)` whose comment or
  methodology text indicates the state deviated from the standard specification.
  If either state in a pairwise comparison is flagged in either year, the
  comparison renders as **Not comparable**.

**2.3a** (Child + Adult-behavioral-health reporting became mandatory with the
2024 Core Set) is carried as a window-level warning on the Trends page.

## Section 3.1 — policy context

A hand-maintained dated Markdown page (`docs/policy-context.md`), deliberately
outside the data-refresh cycle, shown as the site's first page. Forward-looking; not causally attributed to
2022–2024 movements.

## Removed in this version

The HHS-region stratification (Section 2.4) and the at-risk score (Section 3.2)
are preserved, with their code and pages, on the
[2026 Version V1 (Expanded Scope) branch](https://github.com/CORPUZ-2024/Medicaid_2019_Qual_Measure/tree/2026_Version_V1_Expanded_Scope)
and in the [V1 archive](v1/methodology.html).

## Reproduce

```
pip install -r requirements.txt
python run.py --fetch      # download raw + build
# outputs -> docs/data/*.json ; open docs/index.html
```
