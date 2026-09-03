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
  **direction filter** on the View B page plus the **domain accordion**.
- Everywhere a rate is compared to a benchmark, the comparison is
  **direction-aware**:
  - `Eval` (On Track): higher-better → `rate ≥ median`; lower-better → `rate ≤ median`.
  - Worst-quartile membership: higher-better → `rate ≤ Bottom Quartile`;
    lower-better → `rate ≥ Top Quartile`.
  - Trend baseline is computed **per direction group**, so improving and
    declining measures never share a baseline.

## Section 1 — View B extension (`viewb.py`)

- **Per-measure bars:** every reporting state's 2024 canonical rate, sorted
  ascending, colour = rate on a domain scale, marker outline = `Eval`, dotted
  line = CMS median.
- **3-up summary card:** top / median-closest / bottom **state** for the measure.
  The top state is the best *reported rate*, which is **not** the same as CMS's
  Top-quartile threshold value — the card says so.
- **Composite state summary (1.2.B):**
  `OnTrackShare(state, program) = on-track measures / reported measures`, 2024,
  split Child/Adult. States with < 10 reported measures are shown but flagged and
  excluded from ranking.

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

## Section 2.4 — HHS regions (`regional.py`)

`data/region_lookup.csv` is the authoritative State → HHS-region table. The
Section 2.2 calculation is re-run with `HHSRegion` added to the grouping, over
**only the gated-comparable pairs**, and `region_vs_national` = region mean
`improve_delta` − national mean for the same program / domain / transition. The
2019 notebook's ad hoc four-region grouping is retired.

## Section 3.1 — policy context

A hand-maintained dated Markdown panel (`docs/policy-context.md`), deliberately
outside the data-refresh cycle. Forward-looking; not causally attributed to
2022–2024 movements.

## Section 3.2 — risk score (`risk.py`)

```
composite_risk(0–100) = 100 × ( 0.5·trend_exposure_n
                              + 0.3·fiscal_exposure
                              + 0.2·reporting_capacity_exposure_n )
```

- **trend_exposure** = weighted count of gated-Declining measures
  (Behavioral Health Care & LTSS ×1.5) + 0.5 × persistent-bottom count;
  min–max normalised within program.
- **fiscal_exposure** = ordinal Low/Med/High from
  `data/reference/state_fiscal_exposure.csv`; a neutral 0.5 is used for every
  state until that file is populated (the page says so).
- **reporting_capacity_exposure** = share of a state's 2024 measures it did not
  report in 2023 (proxy for 2.3a exposure); min–max normalised within program.
- **beneficiary magnitude** =
  `enrollment × eligible_population_share × (baseline − projected rate)`;
  emitted only when both reference tables are supplied, otherwise `null` with
  `needs_analyst_input`. **No dollar figure is produced** (out of scope, v2).

## Reproduce

```
pip install -r requirements.txt
python run.py --fetch      # download raw + build
# outputs -> docs/data/*.json ; open docs/index.html
```
