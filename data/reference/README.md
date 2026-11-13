# `data/reference/` — analyst-maintained inputs

These small tables are **not** part of the data.medicaid.gov Quality download.
They encode judgements the spec (v2) says must come from a named external source
rather than be inferred from the rate data. Each row cites its source.

| File | Feeds | Source of record |
|------|-------|------------------|
| `cms_trendable_measures.csv` | 2.3 — CMS's rate-level 2022–2024 trending determinations (Trend / Trend with caution / Do Not Trend) | CMS *Criteria for Using the Child and Adult Core Set Measures to Assess Trends in State Performance in Medicaid and CHIP* (Methods Brief, Sept 2025), Tables 1–2 |

The pipeline reads this file on every build. A rate with no matching row is
treated as Do Not Trend ("not covered by CMS's 2022-2024 trend assessment").
