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
| 1 | Remove tabs: Regional, At-Risk Analysis | Removed `regional.html`, `risk.html`, `data/regional.json`, `data/risk.json`, `src/coreset/regional.py`, `src/coreset/risk.py`, notebooks 05/06, and the risk-only reference CSVs. All of them are preserved on `2026_Version_V1_Expanded_Scope` and at `docs/v1/`. |
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
