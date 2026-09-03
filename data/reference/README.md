# `data/reference/` — analyst-maintained inputs

These small tables are **not** part of the data.medicaid.gov Quality download.
They encode judgements the spec (v2) says must come from a named external source
rather than be inferred from the rate data. Each row cites its source; rows
marked `analyst_todo` / `Unknown` are scaffolding to be completed before the
corresponding output is trusted.

| File | Feeds | Source of record |
|------|-------|------------------|
| `spec_changes.csv` | 2.3c specification-change gate | NCQA *HEDIS Measure Trending Determinations* memo (annual, by Measurement Year); CMS *Criteria for Using the … Core Set Measures to Assess Trends* brief |
| `cms_trendable_measures.csv` | 2.3b — overrides the computed trendability filter when CMS's own list is available | CMS *Criteria for Using the 2024 Child and Adult Core Set Measures to Assess Trends in State Performance* (Sept 2025) |
| `state_fiscal_exposure.csv` | 3.2 fiscal-exposure component (Low/Med/High) | KFF Medicaid expansion tracker; state provider-tax reliance; published state budget-shortfall estimates |
| `state_enrollment.csv` | 3.2 beneficiary-magnitude estimate | CMS Medicaid & CHIP enrollment reports (most recent monthly "Medicaid and CHIP Enrollment Trends Snapshot") |
| `measure_eligible_population_share.csv` | 3.2 beneficiary-magnitude estimate | Each measure's own denominator definition (`Rate Definition` field) |

When a file is empty except for its header, the pipeline still runs — the
dependent output is emitted with `null`s and a `"needs_analyst_input": true`
marker rather than a fabricated number.
