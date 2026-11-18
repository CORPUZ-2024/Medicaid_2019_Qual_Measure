# 2026 Version V2 — Final Edits change log

**Date:** 2026-11-12 (last updated 2026-11-18) · **Branch:** `main` · **Previous version:**
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

## Terminology, reconciliation and navigation (2026-11-18)

| Request | Implementation |
|---|---|
| (A) Domain composite wording | "how the nation is doing" → "how the country is doing". Dropped *Measure rates* and *Rates reported per state (min · median · max)* columns. *States reporting every rate* → **States that reported all measures**, counted per distinct measure. |
| (A) Reporting-variation sentence | Per domain: "There are x measures and y measure rates. Of the S reporting states, z reported at least 1 measure rate for each measure (reported all measures), while n reported all measure rates for all measures in this domain." z equals the composite column; n is counted separately. "depth" wording removed. |
| Terms used across all pages | Four fixed terms: **measure**, **measure rate**, **state rate**, **state rate change**. Defined in a *Terms used on this site* section (`policy-context.md`, anchor `#terms`), with CMS's usage quoted from its 2024 fact sheet and 2022–2024 trend methods brief. Pages, column headers, tooltips and calculations use them consistently. |
| Trends: Reason column and filter | The Reason column shows CMS's full text again. The Reason filter groups reasons into six themes by keyword (`REASON_THEMES` in `spec_audit.py`): Met all three criteria (65 measure rates), Reporting started in 2023 (25), Not publicly reported all three years (23), Specification or reporting guidance changed (19), Measurement window changed (4), Data source changed (3). A theme with fewer than 3 measure rates falls into Other (none at present). |
| Trends: year-over-year baseline table | Headers are **# of State rate changes Used** and **# of State rate changes Dropped**, with tooltips. Rates column removed. All other counts of changes say "state rate changes." |
| Trend pairing: reworded measure rates | CMS reworded some measure rates between years, so exact-key pairing dropped their state pairs (verification trace finding). 41 reviewed aliases are in `data/reference/rate_aliases.csv`: 21 wording-only changes, and 20 substantive changes that CMS marks Trend or Trend with caution, each with a caveat in its `reason` column. Two CMS-trendable pairs are not aliased because they are different rates (antidepressant 6-month → 12-week; ADD-CH 2+ visits → 1 visit), and each would collide with a same-rate pair. Six Do Not Trend pairs stay unpaired. Result: comparable state rate changes 4,165 → 5,384; CMS-excluded 1,002 → 1,138. The 2024 figures on (A) and (B) are unchanged. |
| Verification trace | An untracked `Verification/` folder holds independent checks. Page (A)'s domain table, composite and CMS-median checks agree with the site. Roll-ups agreed (103 of 103) before the alias change. Ranking sensitivity: scoring each measure equally instead of each measure rate gives a Spearman correlation of 0.78 across 52 states (California 39th → 15th; Washington 33rd → 11th). Documented in Limitations §8. |
| Table of contents | (A), (B) and Trends each have an "On this page" links block below the introduction. Section headings have anchor IDs. |
| Documentation | Methodology rewritten for the terms, the (A) columns and sentence, the Reason themes, the state rate change counts and the rate aliases. Limitations rewritten to 12 sections, adding per-measure-rate weighting, the reported-a-measure rule, the Reason themes and the unpaired rates. READMEs and this log updated. |

**Open items**
- Two CMS-trendable pairs are unpaired because they are different rates (see above). Resolving them would need a rule for choosing among competing predecessors.
- CMS's fact sheet doesn't state its rule for when a partly reported measure counts as reported. This site's rule is in the Terms section and in Limitations §9.
- The baseline and roll-up sensitivity figures were measured before the 20 caveated pairs were added and have not been re-run.
- `Verification/` is untracked. Its scripts reference a Linux path.
