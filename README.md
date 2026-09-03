# Medicaid Child &amp; Adult Core Set — View B Extension (2022–2024)

Cross-state quality-measure visualization and trend analysis for the CMS
Medicaid/CHIP **Child and Adult Core Sets**, built on the
[data.medicaid.gov Quality theme](https://data.medicaid.gov/datasets?theme%5B0%5D=Quality).

This project began as a single-year (FFY2019) visualization of *View A* (a
state × domain snapshot) and *View B* (all states for one measure). Those
original notebooks now live on the
[**`2022_Version`** branch](../../tree/2022_Version). `master` extends the View B
idea to the **2022, 2023, and 2024** Core Set vintages and adds trend, regional,
policy, and at-risk analysis layers, implemented per
[`project_plan/Medicaid_ViewB_GitHub_Pages_Implementation_Spec_v2.txt`](project_plan/Medicaid_ViewB_GitHub_Pages_Implementation_Spec_v2.txt).

## 🔗 Interactive site

**https://corpuz-2024.github.io/Medicaid_2019_Qual_Measure/** — source in [`docs/`](docs/)
*(enable once via Settings → Pages → Deploy from a branch → `master` / `/docs`)*

| Page | What it shows |
|------|---------------|
| [View B (2024)](https://corpuz-2024.github.io/Medicaid_2019_Qual_Measure/) | Every measure, **both** Core Sets, all states — sorted bars, per-measure top/median/bottom-state cards, composite on-track share |
| [Trends 2022–24](https://corpuz-2024.github.io/Medicaid_2019_Qual_Measure/trends.html) | Data-driven baseline; Improving / Stable / Declining / Persistent-Bottom; comparability gate |
| [Regional](https://corpuz-2024.github.io/Medicaid_2019_Qual_Measure/regional.html) | The same trend stratified by HHS region, vs the national average |
| [At-Risk Analysis](https://corpuz-2024.github.io/Medicaid_2019_Qual_Measure/risk.html) | Component-wise state risk index (trend / fiscal / reporting-capacity exposure) |
| [Policy Context](https://corpuz-2024.github.io/Medicaid_2019_Qual_Measure/policy.html) · [Limitations](https://corpuz-2024.github.io/Medicaid_2019_Qual_Measure/limitations.html) · [Methodology](https://corpuz-2024.github.io/Medicaid_2019_Qual_Measure/methodology.html) | Dated policy panel, scope caveats, and how every number is produced |

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
  the average rate change by program × measure direction for each year
  transition, rather than a fixed threshold.
- **HHS-region stratification** (the 10-region CDC/HHS scheme), replacing the
  2019 notebook's ad hoc four-region grouping (which omitted AK, HI, and DC).
- **Analysis sections:** a dated policy/funding panel (2025 reconciliation law,
  the 2024 voluntary→mandatory reporting transition) and an at-risk /
  positioned-for-success score with a **beneficiary-magnitude** estimate.
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
- **Comparability gating before any trend line is drawn.** A state × measure ×
  transition change is shown as a number only if the measure is trendable
  (reported all 3 years, ≥ 20 consistently reporting states, stable spec), its
  specification did not change between those years, and neither state used
  "other specifications" — otherwise it renders **"Not comparable"**. The 2024
  mandatory-reporting change is carried as an explicit caveat.
- **Risk score is transparent, not modelled.** Every component (trend exposure,
  ordinal fiscal exposure, reporting-capacity exposure) is echoed back per
  state. Inputs that need an external source live in `data/reference/`; until an
  analyst fills them, the dependent output is `null`, never a guessed number.
- **Reproducible package, not just notebooks.** Logic lives in `src/coreset/`;
  `python run.py` rebuilds `docs/data/*.json` end to end. The six notebooks
  under `notebooks/` are thin, executable wrappers over that package.

## Repository layout

```
src/coreset/      ingest · clean · viewb · trend · spec_audit · regional · risk · build
run.py            orchestrator:  python run.py [--fetch]
data/raw/         2022 / 2023 / 2024 Core Set CSVs (data.medicaid.gov, untouched)
data/reference/   analyst-maintained inputs (trendable list, fiscal exposure, enrollment)
data/processed/   generated: cleaned panel + DQ exception log
notebooks/        01–06, one per Appendix-A step
docs/             GitHub Pages site (static HTML + Plotly, reads docs/data/*.json)
project_plan/     the V0 and v2 implementation specs
```

## Run locally

```bash
pip install -r requirements.txt
python run.py --fetch                      # download 3 raw CSVs + build docs/data/*.json
cd docs && python -m http.server 8765      # open http://localhost:8765/
```

**Data source:** [data.medicaid.gov — Quality theme](https://data.medicaid.gov/datasets?theme%5B0%5D=Quality)
(2022 / 2023 / 2024 *Child and Adult Health Care Quality Measures*).
