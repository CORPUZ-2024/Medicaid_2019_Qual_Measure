# Methodology

How every number on this site is produced. Source code: `src/coreset/`,
orchestrated by `run.py`. Spec of record:
`project_plan/Medicaid_ViewB_GitHub_Pages_Implementation_Spec_v2.txt`.

## Terms

Every page uses four terms with fixed meanings (full table with CMS usage:
[Terms used on this site](index.html#terms)):

- **Measure** — a Core Set measure, identified by its CMS abbreviation (e.g. FUH-AD).
  Used for counting what states reported.
- **Measure rate** — one rate definition within a measure (CMS column *Rate
  Definition*), e.g. FUH-AD 7-day and 30-day. The unit of every performance and
  trend calculation.
- **State rate** — one state's published value for a measure rate (CMS column
  *State Rate*).
- **State rate change** — one state's change on one measure rate between two
  adjacent years. The unit counted on the Trends page.

A state **reported a measure** when at least one of its measure rates has a
published state rate.

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

## Canonical state rate & row uniqueness (`clean.py`)

One CMS measure spans several **measure rates** (Rate Definition rows, e.g. 7-day
vs 30-day follow-up) and, within each, several **Population** breakouts. CMS marks
exactly one Population row per (state, measure rate) with
`Rate Used in Calculating State Mean and Median = Yes`. That row's value is the
**canonical state rate**. This replaces the 2019 notebook's arbitrary "keep first
occurrence" fix with CMS's own designation. Any collision that survives is
written to `data/processed/dq_exceptions.csv`, not dropped.

**Unit of analysis:** the measure rate, `MeasureKey = ReportProg | MeasureName | RateDefinition`.

## <a id="measure-type"></a>"Measure Type" is a direction flag

In the data.medicaid.gov files the column literally named "Measure Type" holds
only two values — *"Higher rates are better for this measure"* and *"Lower rates
are better for this measure"*. It is **directionality**, not a taxonomy. So:

- The V0 ask to *"provide visuals … by measure type"* is served by the
  **direction filter** on page (B) plus the **domain toolbar**.
- Everywhere a state rate is compared to a benchmark, the comparison is
  **direction-aware**:
  - `Eval` (On Track): higher-better → `state rate ≥ median`; lower-better → `state rate ≤ median`.
  - Worst-quartile membership uses CMS's **Bottom Quartile** column for both
    directions, because CMS already orients it to the worst-performing quartile
    (for lower-better measure rates it is the higher number, e.g. COB-AD 2024: bottom 15.9,
    median 13.1, top 8.3): higher-better → `state rate ≤ Bottom`; lower-better →
    `state rate ≥ Bottom`.
  - State rate changes are **direction-adjusted** (sign flipped for
    lower-better measure rates) before any averaging, so a positive change always
    means the state rate got better.

## Page (A) — 2024 Measures by State and Domain (`state-domain.html`)

Computed in the browser from `docs/data/view_b.json`; no extra build step.

- **Observation** = one state × one 2024 measure rate with a published state rate
  and a CMS `Eval`. **On track** (better than the median) = `Eval == "On Track"`,
  which is direction-aware.
- **Ranked overview:** `score(state) = on-track measure rates / reported measure rates`
  within the selected program × domain (either can be *All*). A state is ranked
  only if it reported at least `ceil(measure rates in selection / 2)` measure rates.
  Ties are broken by number of measure rates reported. Top 10 and bottom 10 are
  listed, with excluded states named.
- **State rates table:** one row per state × measure rate, with the state rate, the
  CMS median and a gap oriented so that positive = better than the median.
- **Domain composite table** (per program × domain):
  - *States reporting* — states with ≥ 1 published state rate in the domain.
  - *Distinct measures* — distinct CMS abbreviations with ≥ 1 published state rate.
  - *% of states mostly on track* — share of reporting states whose own on-track
    share (calculated per measure rate) in the domain is > 50%. Exactly half does
    not count.
  - *States that reported all measures* — reporting states with a published state
    rate for at least one measure rate of every measure in the domain.
  - The chart hover also shows the domain's number of measure rates.
- **Reporting variation notes** (same numbers), one per program × domain:
  *"There are x measures and y measure rates. Of the S reporting states, z reported
  at least 1 measure rate for each measure (reported all measures), while n reported
  all measure rates for all measures in this domain."* z equals the *States that
  reported all measures* column; n ≤ z, and the gap is states that report a measure
  without publishing all of its measure rates. Two clauses are added where they
  apply: how many of the jurisdictions reported nothing in the domain, and — when it
  spans 10 or more states — the range of states reporting each measure rate.
- The two NPR depression-screening measure rates (CDF) are excluded throughout.

## Page (B) — 2024 Across all States by Measure Type and Domain (`viewb.py`, `measures.html`)

- **Summary tiles:** number of 2024 measure rates (all, Child, Adult), each with its
  number of distinct measures.
- **Per-measure-rate bars:** every reporting state's 2024 canonical state rate,
  sorted ascending, colour = state rate on a domain scale. One **red dashed line**
  at the CMS median marks the boundary: states on the arrow side are
  underperforming (`Eval = Not on Track`), direction-aware.
- **Titles:** where several measure rates share one CMS measure name within a
  program, the follow-up period or sub-rate from the rate definition is appended in
  parentheses (e.g. *Follow-Up After Emergency Department Visit for Mental
  Illness: Ages 6 to 17 (Within 30 Days of the ED Visit)*; *Childhood
  Immunization Status: Age 2 (Combination 10)*; CAHPS items also name the child
  population). An age band is added only where titles would otherwise still
  collide, and the all-ages measure rate is marked *Total*. Every 2024 title is unique.
- **Not publicly reported (NPR):** the two depression-screening measure rates
  (CDF-AD, CDF-CH) have no published 2024 state rates. They are listed with a note,
  without a chart or median, and are excluded from every composite.
- **Ties:** a state rate exactly equal to the CMS median counts as on track
  (135 of 6,331 state rates in 2024).
- **Domain toolbar:** only domains that contain measures for the selected program;
  the small number on each button is its count of measure rates.
- **3-up summary card:** top / median-closest / bottom **state** for the measure
  rate. The top state is the best *published state rate*, which is **not** the same
  as CMS's Top-quartile threshold value — the card says so.
- **Composite state summary:**
  `OnTrackShare(state, program) = on-track measure rates / reported measure rates`,
  2024, pooled across **all measure rates in all domains**. The charts exclude
  states with < 10 reported measure rates (none in 2024). The table has one row per
  state with the Child and Adult shares, sorted by `Child − Adult` descending; the
  gap is used only for ordering and is not displayed.

## Section 2.3 — which measure rates can be trended (`spec_audit.py`)

Trendability comes from **CMS's own determinations, made per measure rate**, for
2022–2024, transcribed into `data/reference/cms_trendable_measures.csv` from the
[CMS methods brief](https://www.medicaid.gov/medicaid/quality-of-care/downloads/trend-methods-brief-2024.pdf) (Tables 1 and 2). CMS's three criteria:

1. The measure was publicly reported for each of the three years (public
   reporting requires ≥ 25 states using Core Set specifications and meeting CMS
   data-quality standards).
2. A consistent set of at least 20 states reported it using Core Set
   specifications in all three years.
3. Specifications were comparable for all three years (no specification or
   data-source change that would make results incomparable).

CMS marks each measure, and sometimes each measure rate within a measure,
**Trend**, **Trend with caution** or **Do Not Trend**. This build uses Trend and
Trend with caution and flags the latter. CMS finds at least one trendable measure
rate for 20 Child and 23 Adult Core Set measures
([CMS fact sheet](https://www.medicaid.gov/medicaid/quality-of-care/downloads/2024-core-set-reporting.pdf)); the build reproduces
both counts. Measures that left the Core Set before 2024 (FVA-AD, HPC-AD,
PPC-AD, PPC-CH; NCIDDS-AD was renamed NCIIDD-AD) are outside CMS's assessment and
are not trended.

**Trendability table (Trends page).** One row per 2024 measure rate, filterable by
determination, program, domain and Reason. The Reason column shows CMS's full
stated reason. The Reason filter groups those reasons into themes by keyword
(`REASON_THEMES` in `spec_audit.py`, first match wins):

| Theme | Matches CMS reasons about | 2024 measure rates |
|---|---|---|
| Met all three criteria | all three criteria met, or consistent specifications | 65 |
| Reporting started in 2023 | measure rates first reported, or added, in 2023 | 25 |
| Not publicly reported all three years | measure rates not publicly reported in every year | 23 |
| Specification or reporting guidance changed | specification, age-criterion, exclusion, calculation or reporting-guidance changes | 19 |
| Measurement window changed | the postpartum window changing from 60 to 90 days | 4 |
| Data source changed | a data-source change for some states | 3 |

A theme covering fewer than 3 measure rates (`REASON_MIN_ROWS`), or a reason
matching no theme, is grouped as **Other** (none in this build).

**This site's additional check (not a CMS criterion):** a state rate change is left
out when CMS's comments record a state-reported deviation from the Core Set
specifications in one year of the pair but not the other (the state changed how
it calculated its state rate). A deviation reported in both years is kept: it
shifts the state rate's level, not its change, and CMS still publishes and trends
such measure rates.

The state roll-up chart shows only states with at least 10 comparable state rate
changes; all states stay in the table.

The 2024 mandatory-reporting change is carried as a window-level warning: CMS
notes it may affect comparability with earlier years.

## Section 2.2 — year-over-year baseline & classification (`trend.py`)

For every state rate change — state × measure rate × transition (2022→2023,
2023→2024) — where the state reported the measure rate in both years and the
change passed Section 2.3:

```
Δ state rate  = StateRate(t) − StateRate(t−1)
adj. Δ        = Δ state rate  (higher-is-better)   |   −Δ state rate  (lower-is-better)
baseline      = mean(adj. Δ) over the same program × domain × transition
band          = baseline ± 0.5 × SD(adj. Δ in that group)
Improving     : adj. Δ > baseline + 0.5 SD
Declining     : adj. Δ < baseline − 0.5 SD
Stable        : otherwise
```

**Rate aliases (`data/reference/rate_aliases.csv`).** CMS sometimes reworded a measure
rate between years without changing what it measures (e.g. \"Inpatient Hospital
Admissions\" became \"Hospitalizations\"). Trend pairing matches on the exact
MeasureKey, so such a rate would lose its state pairs. 21 reworded pairs are aliased:
the earlier year's key is mapped to the later year's key before pairing (`clean.py`).
41 aliases are in use. 21 are wording-only changes. 20 are substantive changes that CMS
marks Trend or Trend with caution for the later year, paired on CMS's determination with
the caveat recorded in the `reason` column. Each was reviewed by hand. Fuzzy text
matching was not used because it also pairs different rates. Two CMS-trendable pairs
are not aliased because they are different rates (antidepressant 6-month → 12-week;
ADD-CH 2+ visits → 1 visit), and each shares its target key with a same-rate pair.
Pairs CMS marks Do Not Trend are not aliased. The aliases raise comparable state rate
changes from 4,165 to 5,384. The 2024 figures on (A) and (B) do not change, because
aliases only affect 2022 and 2023 rows.

Groups are **program × domain**. The baseline table reports, per group:
baseline, SD, stable band, **# of State rate changes Used** (comparable changes in
the group), **States** (distinct states contributing at least one), and
**# of State rate changes Dropped** (changes in the group removed by CMS's
trendability rule or the deviation check). A program × domain × transition with
no comparable state rate change is listed with the reason (for example, every
measure rate in Experience of Care is “Do Not Trend” because CAHPS data were first
reported for 2023).

**State roll-up — mean adj. Δ** = sum of the state's adj. Δ values ÷ number of
comparable state rate changes, per program. Worked example (from the Trends page,
which shows it for any state): a higher-is-better measure rate going 50.0 → 52.0
gives adj. Δ = +2.0; a lower-is-better measure rate going 20.0 → 21.0 gives
Δ = +1.0 and adj. Δ = −1.0; mean adj. Δ for those two state rate changes =
(+2.0 − 1.0) ÷ 2 = +0.5. State rates are in their measure rate's own units, so
per-100,000 admission rates move in larger steps than percentages.

**Measure rates moving most:** for each trendable measure rate, the mean adj. Δ
over all its comparable state rate changes (both transitions), with counts of
Improving / Declining / Stable.

**Persistent Bottom Quartile:** for a measure rate, the state's state rate is in
CMS's bottom (worst-performing) quartile in ≥ 2 of the 3 years, regardless of
movement.

## Section 3.1 — policy context

A hand-maintained dated Markdown page (`docs/policy-context.md`), deliberately
outside the data-refresh cycle, shown as the site's first page. It also holds the
site's [Terms](index.html#terms) section. Forward-looking; not causally attributed
to 2022–2024 movements.

## Removed in this version

Analyses that were in V1 and are not part of this version are preserved on the
[2026 Version V1 (Expanded Scope) branch](https://github.com/CORPUZ-2024/Medicaid_2019_Qual_Measure/tree/2026_Version_V1_Expanded_Scope).

## Reproduce

```
pip install -r requirements.txt
python run.py --fetch      # download raw + build
# outputs -> docs/data/*.json ; open docs/index.html
```
