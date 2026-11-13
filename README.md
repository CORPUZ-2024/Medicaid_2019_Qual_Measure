# Child and Adult Health Care Quality Measures (2022–2024) — 2026 Version V2

Cross-state quality-measure visualization and trend analysis for the CMS
Medicaid/CHIP **Child and Adult Core Sets**, built on the
[data.medicaid.gov Quality theme](https://data.medicaid.gov/datasets?theme%5B0%5D=Quality).

This project began as a single-year (FFY2019) visualization of *View A* (a
state × domain snapshot) and *View B* (all states for one measure). Those
original notebooks live on the [**`2022_Version`** branch](../../tree/2022_Version).
The first 2022–2024 expansion is preserved
as **2026 Version V1 (Expanded Scope)** on the
[**`2026_Version_V1_Expanded_Scope`** branch](https://github.com/CORPUZ-2024/Medicaid_2019_Qual_Measure/tree/2026_Version_V1_Expanded_Scope).
`main` is **Version V2**: a focused edit of V1, logged in
[`project_plan/2026_V2_Final_Edits_Change_Log.md`](project_plan/2026_V2_Final_Edits_Change_Log.md).

## 🔗 Interactive site

**https://corpuz-2024.github.io/Medicaid_2019_Qual_Measure/** — source in [`docs/`](docs/)
*(Settings → Pages → Deploy from a branch → `main` / `/docs`)*

| Tab | What it shows |
|------|---------------|
| [Policy Context](https://corpuz-2024.github.io/Medicaid_2019_Qual_Measure/) | **First tab.** Why Core Set reporting matters (significance, requirements, cadence, link to reimbursement / value-based care); the current policy and funding landscape including the Nov 2026 midterms; how those changes may show up in quality measures vs other metrics. Primary sources linked. |
| [(A) 2024 Measures by State and Domain](https://corpuz-2024.github.io/Medicaid_2019_Qual_Measure/state-domain.html) | **New.** Top / bottom 10 states by % of reported measures above the CMS median per domain; a filterable state × domain rate table (View A style); a domain composite chart and table (states, distinct measures, % of states above median, reporting variation) |
| [(B) 2024 Across all States by Measure Type and Domain](https://corpuz-2024.github.io/Medicaid_2019_Qual_Measure/measures.html) | Formerly "View B (2024)". Every measure, both Core Sets, all states — per-program domain toolbar, follow-up period in non-distinct titles, red dashed underperforming line, composite on-track share across all domains, Child vs Adult table by state |
| [Trends 2022–24](https://corpuz-2024.github.io/Medicaid_2019_Qual_Measure/trends.html) | CMS's trendability criteria and the rates CMS does not trend; year-over-year baseline by program × domain; Improving / Stable / Declining; state roll-up with a worked example of the mean direction-adjusted change |
| [Limitations](https://corpuz-2024.github.io/Medicaid_2019_Qual_Measure/limitations.html) · [Methodology](https://corpuz-2024.github.io/Medicaid_2019_Qual_Measure/methodology.html) | Scope caveats and how every number is produced |
| [V1 archive](https://corpuz-2024.github.io/Medicaid_2019_Qual_Measure/v1/) | The previous site, frozen |

### What changed in V2 (vs V1)

- **Removed tabs.** Two V1 analysis tabs, with their pages, JSON, code and
  notebooks, are not part of `main`. See the [2026 Version V1 (Expanded Scope)](https://github.com/CORPUZ-2024/Medicaid_2019_Qual_Measure/tree/2026_Version_V1_Expanded_Scope) branch.
- **Site renamed** from "Core Set · View B Extension" to **Child and Adult Health
  Care Quality Measures**.
- **Policy Context is now the first tab and was rewritten** (last reviewed
  2026-11-12). The V1 panel's content is kept in its §4.
- **New tab (A) 2024 Measures by State and Domain** (see table above).
- **View B renamed to (B) 2024 Across all States by Measure Type and Domain** with:
  a domain toolbar that lists only that program's domains; follow-up periods
  appended to non-distinct measure titles; one red dashed median line instead of
  red bar borders; a note that the composite pools all measures across all
  domains; the Ranked column dropped; the bottom table now one row per state
  (Child % and Adult %, sorted by Child − Adult descending, gap not shown).

> The sections below describe the V1 build that V2 inherits. Items marked
> *(V1 only)* were removed from `main` in V2 and live on the
> [`2026_Version_V1_Expanded_Scope`](https://github.com/CORPUZ-2024/Medicaid_2019_Qual_Measure/tree/2026_Version_V1_Expanded_Scope) branch.

## What changed — **scope**

- **Both programs, every measure.** The original View B was wired only to
  `Child_Data`; it now runs for the Child **and** Adult Core Sets across all
  domains (6 for Adult, including Experience of Care and LTSS).
- **Three vintages, not one.** 2022 / 2023 / 2024 files are pulled from
  data.medicaid.gov, tagged with `CoreSetYear`, and concatenated. The window
  matches CMS's own *Trends in State Performance: 2022 to 2024* product.
- **A cross-state summary layer** the 2019 project lacked: per-measure top /
  median / bottom-performing **state**, plus a composite *on-track share* per
  state (share of a state's measures at or better than the CMS median).
- **Year-over-year analysis:** which states improved or declined most, and which
  stayed in the bottom quartile, measured against a **data-driven baseline** —
  the average direction-adjusted rate change by program × domain for each year
  transition, rather than a fixed threshold.
- **Analysis sections:** a dated policy/funding panel (kept and rewritten in V2) (2025 reconciliation law,
  the 2024 voluntary→mandatory reporting transition) and an at-risk /
  positioned-for-success score with a **beneficiary-magnitude** estimate
  *(V1 only)*.
  Dollar / increased-utilization-cost impact is **deliberately out of scope** —
  the rate-to-cost relationship was not consistent enough across domains to
  document as one reproducible formula.
- **Not in scope:** rewriting the original View A / View B notebooks,
  claims-level utilization, plan-level performance, and state waiver terms.

## What changed — **approach**

- **Row ambiguity resolved with CMS's own flag, not "keep first".** The 2019
  project kept the first of each duplicate descriptor row. This build keeps the
  row CMS itself marked `Rate Used in Calculating State Mean and Median = Yes`
  (one canonical population roll-up per state / measure / rate definition) and
  **logs** any residual collision to `data/processed/dq_exceptions.csv` instead
  of dropping it silently. On the three downloaded files that residual set is
  currently empty.
- **"Measure Type" is a direction flag, not a taxonomy.** In the source data
  that column only holds *"Higher rates are better"* / *"Lower rates are
  better"*. So the "by measure type" view is served by a **direction filter +
  domain accordion**, and every benchmark comparison (on-track, worst-quartile,
  trend baseline) is **direction-aware** — a 2-point rise is good for one
  measure and bad for another.
- **Unit of analysis = `ReportProg | Measure Name | Rate Definition`**, finer
  than a measure name, because one name (e.g. *Follow-Up After ED Visit*) covers
  several non-comparable rate definitions (7-day vs 30-day, and so on).
- **Trendability follows CMS's own list.** A state's year-over-year change is
  used only if CMS rates that measure rate "Trend" or "Trend with caution" for
  2022–2024 ([CMS methods brief](https://www.medicaid.gov/medicaid/quality-of-care/downloads/trend-methods-brief-2024.pdf): publicly reported all 3 years,
  ≥ 20 consistent states using Core Set specifications, comparable
  specifications), and the state did not change its reported deviation from
  the specifications between the two years. The 2024 mandatory-reporting change is carried as an
  explicit caveat.
- *(V1 only)* **Risk score is transparent, not modelled.** Every component (trend exposure,
  ordinal fiscal exposure, reporting-capacity exposure) is echoed back per
  state. Inputs that need an external source live in `data/reference/`; until an
  analyst fills them, the dependent output is `null`, never a guessed number.
- **Reproducible package, not just notebooks.** Logic lives in `src/coreset/`;
  `python run.py` rebuilds `docs/data/*.json` end to end. The notebooks
  under `notebooks/` are thin, executable wrappers over that package.

## Repository layout

```
src/coreset/      ingest · clean · states · viewb · trend · spec_audit · build
run.py            orchestrator:  python run.py [--fetch]
data/raw/         2022 / 2023 / 2024 Core Set CSVs (data.medicaid.gov, untouched)
data/reference/   CMS's 2022–2024 trending determinations (cms_trendable_measures.csv)
data/processed/   generated: cleaned panel + DQ exception log
notebooks/        01–04, one per Appendix-A step (05/06 are V1 only)
docs/             GitHub Pages site (static HTML + Plotly, reads docs/data/*.json)
docs/v1/          frozen copy of the V1 site
project_plan/     the V0 and v2 implementation specs + V2 change log
```

## Run locally

```bash
pip install -r requirements.txt
python run.py --fetch                      # download 3 raw CSVs + build docs/data/*.json
cd docs && python -m http.server 8765      # open http://localhost:8765/
```

**Data source:** [data.medicaid.gov — Quality theme](https://data.medicaid.gov/datasets?theme%5B0%5D=Quality)
(2022 / 2023 / 2024 *Child and Adult Health Care Quality Measures*).
