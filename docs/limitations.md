# Limitations — scope and approach

Section 4 of the v2 spec, kept current with what this build actually does.

## 1. The window still straddles the reporting-regime change

2022–2024 has only **two** year-over-year transitions, so the 2023→2024
transition — the one crossing the voluntary-to-mandatory Child Core Set reporting
boundary — is **half** the trend signal, not a third. Every trend line is gated by
Section 2.3 before it is drawn; a 2023→2024 "decline" for a previously
inconsistent reporter may be a reporting-completeness effect.

## 2. Matching CMS's window is not the same as matching CMS's filter

The date range here is identical to CMS's own 2022–2024 trending product, which
is a real improvement over an independently chosen window. But the
**trendable-measure filter in this build is a computed approximation** of CMS's
three-part criterion, not CMS's published list. Populate
`data/reference/cms_trendable_measures.csv` from the CMS *Criteria for Using the
2024 … Core Set Measures* brief to replace it. CMS found 19 Child and 22 Adult
measures trendable for this window.

## 3. "Baseline = average YoY change" is a relative standard

If every state declines on a measure in a given year, the baseline shifts down
with them, and a state merely tracking the new, worse baseline reads as
**Stable**. The classification flags *relative* outliers, not absolute quality.

## 4. Row-level ambiguity in the source data

The original repo's README flags "identical descriptor, different rate" rows for
2019. This build resolves them by keeping the row CMS itself marked
`Rate Used in Calculating State Mean and Median = Yes` (one canonical population
rollup per state / measure / rate definition), and logs any residual collision to
`data/processed/dq_exceptions.csv` rather than dropping it silently. On the three
downloaded vintages that residual set is currently empty, but a future vintage
could reintroduce it.

## 5. The public-release threshold makes coverage uneven and non-random

Measures are publicly released only when ≥ 25 states report. "Bottom quartile"
and "not reported" are different things; nulls are handled explicitly and never
counted as a low score.

## 6. Removed analyses

The beneficiary-magnitude estimate, the at-risk score and the HHS-region view
were removed from this version. Their limitations are documented on the
[2026 Version V1 (Expanded Scope) branch](https://github.com/CORPUZ-2024/Medicaid_2019_Qual_Measure/tree/2026_Version_V1_Expanded_Scope) and in the
[V1 archive](v1/limitations.html).

## 7. The policy analysis is forward-looking and time-sensitive

The 2025 reconciliation law's major provisions take effect in 2027 and postdate
every year of data here. Treating them as an explanation for 2022–2024 movements
would be a causal claim the data cannot support; their role is contextualising
risk for future cycles. See the dated panel on the [Policy Context](index.html)
page.

## 8. "Above the median" composites are relative by construction

The CMS median splits the reporting states roughly in half on every measure. So
the domain composite on [(A)](state-domain.html) ("% of states above the median")
measures how *broadly* above-median performance is spread across states, not
whether the nation got better in absolute terms. A state's rank on (A) is also
limited to the measures it chose to report. The ranking cutoff (at least half of
the selection's series) reduces, but does not remove, the effect of reporting
depth.

## 9. Scope boundary

This build covers the Core Set quality-measure data itself. It does **not**
incorporate claims-level utilization, managed-care-plan-level performance, or
state waiver terms — all of which affect measure performance but sit outside the
data.medicaid.gov Quality theme. It also does not translate measure performance
into dollar cost.

## 10. Build-specific notes

- "Measure Type" in the source is a **direction flag** (higher/lower better), not
  a measure taxonomy. The V0 "by measure type" ask is served by the direction
  filter plus the domain accordion — see [methodology](methodology.html#measure-type).
- The unit of analysis is `ReportProg | Measure Name | Rate Definition`, finer
  than CMS's measure list, because one measure name spans several rate
  definitions (e.g. 7-day vs 30-day follow-up) that are not comparable to each
  other.
- Section 2.5's narrative tracks (agency-report and peer-reviewed context for
  flagged declines) are specified but not wired to a live source in this build.
- The 2024 file did not contain USVI or Guam rows despite the mandatory-reporting
  expansion; only 50 states + DC + PR appear in all three vintages.
