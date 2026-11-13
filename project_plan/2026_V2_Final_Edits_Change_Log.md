# 2026 Version V2 — Final Edits change log

**Date:** 2026-11-12 · **Branch:** `main` · **Previous version:**
[`2026_Version_V1_Expanded_Scope`](https://github.com/CORPUZ-2024/Medicaid_2019_Qual_Measure/tree/2026_Version_V1_Expanded_Scope)
(formerly `master`; served frozen at `docs/v1/`)

This file records the "Final Edits" request and how each item was carried out.
It follows `V0 specs.txt` and `Medicaid_ViewB_GitHub_Pages_Implementation_Spec_v2.txt`.

## Branches

| Step | Result |
|---|---|
| Copy `master` → `main` | `main` now holds the full 2022–2024 build. The three README-only commits that were on `main` (links to `master`) were replaced. The original FFY2019 notebooks remain on `2022_Version`. |
| Rename `master` → "2026 Version V1 (Expanded Scope)" | Branch `2026_Version_V1_Expanded_Scope`. Git branch names cannot contain spaces, so underscores are used and the parentheses are dropped. |
| Keep the old GitHub Pages site live | The V1 site is copied unchanged (plus an "archived" banner) to `docs/v1/`. Once Pages serves `main` /docs, V1 is at `/v1/` and V2 at the root. |

## Site edits (V2)

| # | Request | Implementation |
|---|---|---|
| 1 | Remove two V1 analysis tabs | Their pages, JSON, code, notebooks and reference inputs were removed. All of them are preserved on `2026_Version_V1_Expanded_Scope` and at `docs/v1/`. |
| 2 | Rename "Core Set · View B Extension" | Site title is now **Child and Adult Health Care Quality Measures** (header injected by `docs/assets/common.js`). |
| 3 | Policy Context first; significance, requirements, cadence, reimbursement/VBC link; current policy & funding; how changes show up in quality measures vs other metrics; keep prior content and update with recent events (midterms); link primary sources | `docs/index.html` is now the Policy Context page (`docs/policy-context.md`, last reviewed 2026-11-12). `policy.html` redirects to it. Sections 1–4 cover the requested order. The V1 content is retained in §4. Every cited source is linked. |
| 4 | New tab **(A) 2024 Measures by State and Domain** | `docs/state-domain.html`: (i) top/bottom-10 states by above-median share within a program × domain (either can be "All"), with a ranking cutoff of at least half the selection's series; (ii) a state × program × domain rate table (View A style); (iii) a domain composite bar chart + sortable table: states reporting, distinct measures, rate series, % of states above median, reporting depth, plus generated reporting-variation notes. |
| 5 | Rename View B tab → **(B) 2024 Across all States by Measure Type and Domain** | `docs/measures.html` (was `index.html`). |
| 5a | Domain toolbar shows only domains for the program | A pill toolbar built from the measures present in the selected program. |
| 5b | Add follow-up period to non-distinct titles | `CS.displayNames()` appends the period or sub-rate from the rate definition, e.g. "…Ages 6 to 17 (Within 30 Days of the ED Visit)". |
| 5c | Dashed red line instead of red borders | Per-bar outlines removed. One red dashed line at the CMS median, labelled with the underperforming side (direction-aware). |
| 5d | Note that the composite covers all measures in all domains | Added to the composite lede. |
| 5e | Drop the Ranked column | Removed. |
| 5f | Bottom table unique by state, Child % and Adult %, sorted by delta (descending), delta not shown | One row per state. Order = Child − Adult on-track share, descending. States with one program sort last. |

## Interpretation decisions (flag for review)

- **"Above the median"** = CMS `Eval = On Track` (at or better than the median,
  direction-aware). This keeps (A) consistent with (B).
- **Domain composite "% of states above median"** = share of reporting states
  whose own above-median share in the domain is > 50%. Because the CMS median
  splits states about 50/50 on every measure, a pooled "% of results above median"
  would be about 50% for every domain and carry no information. The page explains
  this.
- **Delta direction** for the (B) bottom table = Child − Adult.
- Removed analyses are documented in Methodology / Limitations with links to the
  V1 branch and archive.

## Accuracy pass 2 (2026-11-12)

| Request | Implementation |
|---|---|
| Remove all mentions of regions | Region columns, hover text, lookup (`data/region_lookup.csv` → `data/state_lookup.csv`, abbreviations only), `regions.py` → `states.py`, notebooks and docs. The frozen V1 archive (`docs/v1/`, V1 branch) and the original spec files in `project_plan/` are left unchanged as historical records. |
| Empty tables / graphs | Every table shows a reason row when empty (e.g. a state with no published rate in a domain; a program × domain with no trendable rate). Sorting ignores empty/note rows. |
| On track / not on track accuracy | (A) now says “On track / Not on track” instead of “Above / Below median”, which read wrong for lower-is-better rates (e.g. Puerto Rico COB-AD 9.3 vs median 13.1 is on track). Rates keep 2 decimals where values are small, so PCR-AD 0.98 no longer displays as 1.0 against a 0.99 median. Hovers show rate vs median and the gap. **Bug fixed:** worst-quartile tests for lower-is-better rates used CMS's Top Quartile column; they now use Bottom Quartile, which CMS already orients to the worst quartile (share of lower-is-better state rates flagged worst-quartile fell from ~75% to 26%). This changes Persistent Bottom counts. |
| Trends: trendability criteria and non-trendable measures | Trends page summarizes CMS's three criteria and lists every 2024 rate with CMS's determination and reason, transcribed into `data/reference/cms_trendable_measures.csv` from the [CMS methods brief](https://www.medicaid.gov/medicaid/quality-of-care/downloads/trend-methods-brief-2024.pdf); links the brief, the 2024 reporting fact sheet and CMS's trend results. Reproduces CMS's counts (20 Child, 23 Adult measures trendable). Replaces the earlier computed approximation and `spec_changes.csv`. |
| YoY table by program × domain | Baseline = mean direction-adjusted change per program × domain × transition (was program × direction). Roll-ups now use only comparable changes (previously they included changes the gate had excluded). |
| Column definitions on hover | Every derived column header has a definition tooltip (ⓘ); click-to-sort is unchanged and shows ▲/▼. |
| Median label overlap in (B) | The CMS-median label sits in the chart's top margin, above the bars. |
| Deviation check narrowed | The earlier rule dropped any change where either year had a state-reported deviation, which removed nearly all of WA, OK, ME, MT and AK's changes even though CMS publishes and trends those rates. A change is now dropped only when the deviation is present in one year and absent in the other. States with < 10 comparable changes are listed but not charted. |
| Worked example of mean adj. Δ | Trends → State roll-up shows the full calculation for any selected state (default Puerto Rico). |
