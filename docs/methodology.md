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
  - Worst-quartile membership uses CMS's **Bottom Quartile** column for both
    directions, because CMS already orients it to the worst-performing quartile
    (for lower-better rates it is the higher number, e.g. COB-AD 2024: bottom 15.9,
    median 13.1, top 8.3): higher-better → `rate ≤ Bottom`; lower-better →
    `rate ≥ Bottom`.
  - Year-over-year changes are **direction-adjusted** (sign flipped for
    lower-better rates) before any averaging, so a positive change always means
    the rate got better.

## Page (A) — 2024 Measures by State and Domain (`state-domain.html`)

Computed in the browser from `docs/data/view_b.json`; no extra build step.

- **Observation** = one state × one 2024 measure rate (`MeasureKey` = program × measure × rate definition) with a
  CMS `Eval`. **On track** (better than the median) = `Eval == "On Track"`, which is direction-aware
  (higher-better: `rate ≥ median`; lower-better: `rate ≤ median`).
- **Ranked overview:** `score(state) = above-median rates / reported rates`
  within the selected program × domain (either can be *All*). A state is ranked
  only if it reported at least `ceil(rates in selection / 2)` rates. Ties are
  broken by number reported. Top 10 and bottom 10 are listed, with excluded states
  named.
- **State rates table:** one row per state × rate, with the CMS median and a gap
  oriented so that positive = better than the median.
- **Domain composite:** per program × domain — states reporting ≥ 1 rate;
  distinct measures (by CMS abbreviation); measure rates; **% of states mostly on track** =
  share of reporting states whose own on-track share in that domain is > 50%; rates reported per state (min · median · max); and states
  reporting every rate. The NPR depression-screening rates are excluded. The reporting-variation notes are generated from the
  same numbers.

## Page (B) — 2024 Across all States by Measure Type and Domain (`viewb.py`, `measures.html`)

- **Per-measure bars:** every reporting state's 2024 canonical rate, sorted
  ascending, colour = rate on a domain scale. One **red dashed line** at the CMS
  median marks the boundary: states on the arrow side are underperforming
  (`Eval = Not on Track`), direction-aware.
- **Titles:** where several rates share one CMS measure name within a program,
  the follow-up period or sub-rate from the rate definition is appended in
  parentheses (e.g. *Follow-Up After Emergency Department Visit for Mental
  Illness: Ages 6 to 17 (Within 30 Days of the ED Visit)*; *Childhood
  Immunization Status: Age 2 (Combination 10)*; CAHPS items also name the child
  population). An age band is added only where titles would otherwise still
  collide, and the all-ages rate is marked *Total*. Every 2024 title is unique.
- **Not publicly reported (NPR):** the two depression-screening rates (CDF-AD,
  CDF-CH) have no published 2024 state rates. They are listed with a note,
  without a chart or median, and are excluded from every composite.
- **Ties:** a rate exactly equal to the CMS median counts as on track / above
  the median (135 of 6,331 state rates in 2024).
- **Domain toolbar:** only domains that contain measures for the selected program.
- **3-up summary card:** top / median-closest / bottom **state** for the measure.
  The top state is the best *reported rate*, which is **not** the same as CMS's
  Top-quartile threshold value — the card says so.
- **Composite state summary:**
  `OnTrackShare(state, program) = on-track rates / reported rates`, 2024,
  pooled across **all measures in all domains**. The charts exclude states with
  < 10 reported rates (none in 2024). The table has one row per state with the Child and Adult
  shares, sorted by `Child − Adult` descending; the gap is used only for ordering
  and is not displayed.

## Section 2.3 — which rates can be trended (`spec_audit.py`)

Trendability comes from **CMS's own rate-level determinations** for 2022–2024,
transcribed into `data/reference/cms_trendable_measures.csv` from the
[CMS methods brief](https://www.medicaid.gov/medicaid/quality-of-care/downloads/trend-methods-brief-2024.pdf) (Tables 1 and 2). CMS's three criteria:

1. The measure was publicly reported for each of the three years (public
   reporting requires ≥ 25 states using Core Set specifications and meeting CMS
   data-quality standards).
2. A consistent set of at least 20 states reported it using Core Set
   specifications in all three years.
3. Specifications were comparable for all three years (no specification or
   data-source change that would make results incomparable).

CMS rates each measure, and sometimes each rate within a measure, **Trend**,
**Trend with caution** or **Do Not Trend**. This build uses Trend and Trend with
caution and flags the latter. CMS finds at least one trendable rate for 20 Child
and 23 Adult Core Set measures ([CMS fact sheet](https://www.medicaid.gov/medicaid/quality-of-care/downloads/2024-core-set-reporting.pdf)); the build reproduces
both counts. Measures that left the Core Set before 2024 (FVA-AD, HPC-AD,
PPC-AD, PPC-CH; NCIDDS-AD was renamed NCIIDD-AD) are outside CMS's assessment and
are not trended.

**This site's additional check (not a CMS criterion):** a state's change is left
out when CMS's comments record a state-reported deviation from the Core Set
specifications in one year of the pair but not the other (the state changed how
it calculated the rate). A deviation reported in both years is kept: it shifts
the rate's level, not its change, and CMS still publishes and trends such rates.

The state roll-up chart shows only states with at least 10 comparable changes;
all states stay in the table.

The 2024 mandatory-reporting change is carried as a window-level warning: CMS
notes it may affect comparability with earlier years.

## Section 2.2 — year-over-year baseline & classification (`trend.py`)

For every state × rate × transition (2022→2023, 2023→2024) where the state
reported the rate in both years and the change passed Section 2.3:

```
Δ rate        = StateRate(t) − StateRate(t−1)
adj. Δ        = Δ rate  (higher-is-better)   |   −Δ rate  (lower-is-better)
baseline      = mean(adj. Δ) over the same program × domain × transition
band          = baseline ± 0.5 × SD(adj. Δ in that group)
Improving     : adj. Δ > baseline + 0.5 SD
Declining     : adj. Δ < baseline − 0.5 SD
Stable        : otherwise
```

Groups are **program × domain**. A program × domain × transition with no
comparable change is listed on the Trends page with the reason (for example,
every rate in Experience of Care is “Do Not Trend” because CAHPS data were first
reported for 2023).

**State roll-up — mean adj. Δ** = sum of the state's adj. Δ values ÷ number of
comparable changes, per program. Worked example (from the Trends page, which
shows it for any state): a higher-is-better rate going 50.0 → 52.0 gives adj. Δ
= +2.0; a lower-is-better rate going 20.0 → 21.0 gives Δ = +1.0 and adj. Δ =
−1.0; mean adj. Δ for those two changes = (+2.0 − 1.0) ÷ 2 = +0.5. Rates are in
their own units, so per-100,000 admission rates move in larger steps than
percentages.

**Persistent Bottom Quartile:** the state's rate is in CMS's bottom
(worst-performing) quartile in ≥ 2 of the 3 years, regardless of movement.

## Section 3.1 — policy context

A hand-maintained dated Markdown page (`docs/policy-context.md`), deliberately
outside the data-refresh cycle, shown as the site's first page. Forward-looking; not causally attributed to
2022–2024 movements.

## Removed in this version

Analyses that were in V1 and are not part of this version are preserved on the
[2026 Version V1 (Expanded Scope) branch](https://github.com/CORPUZ-2024/Medicaid_2019_Qual_Measure/tree/2026_Version_V1_Expanded_Scope).

## Reproduce

```
pip install -r requirements.txt
python run.py --fetch      # download raw + build
# outputs -> docs/data/*.json ; open docs/index.html
```
