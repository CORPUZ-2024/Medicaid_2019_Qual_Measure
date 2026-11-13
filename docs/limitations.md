# Limitations — scope and approach

Section 4 of the v2 spec, kept current with what this build actually does.

## 1. The window still straddles the reporting-regime change

2022–2024 has only **two** year-over-year transitions, so the 2023→2024
transition — the one crossing the voluntary-to-mandatory Child Core Set reporting
boundary — is **half** the trend signal, not a third. Every trend line is gated by
Section 2.3 before it is drawn; a 2023→2024 "decline" for a previously
inconsistent reporter may be a reporting-completeness effect.

## 2. CMS's trendability is measure-level; state changes are not all equal

Which rates are trended follows CMS's own determinations ([methods brief](https://www.medicaid.gov/medicaid/quality-of-care/downloads/trend-methods-brief-2024.pdf)).
CMS judges trendability for the measure across a consistent set of ≥ 20 states;
this site then uses every state that reported the rate in both years of a
transition. A state that reported only in 2023 and 2024 contributes one change,
not two. CMS's own trend results use the change in the **state median** from 2022
to 2024 with a Wilcoxon signed-rank test; this site's state-level classification
is a different, descriptive measure.

## 3. "Baseline = average YoY change" is a relative standard, and mixes units

If every state declines in a domain in a given year, the baseline shifts down
with them, and a state merely tracking the new, worse baseline reads as
**Stable**; a state can even read as **Improving** with a small decline. The
classification flags *relative* outliers, not absolute quality. Baselines are
pooled by program × domain, and some domains combine percentages with
per-100,000 or per-1,000 rates and ratios, so the SD in those groups is driven by
the larger-unit rates.

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

Analyses that were in V1 and are not part of this version, and their
limitations, are documented on the
[2026 Version V1 (Expanded Scope) branch](https://github.com/CORPUZ-2024/Medicaid_2019_Qual_Measure/tree/2026_Version_V1_Expanded_Scope).

## 7. The policy analysis is forward-looking and time-sensitive

The 2025 reconciliation law's major provisions take effect in 2027 and postdate
every year of data here. Treating them as an explanation for 2022–2024 movements
would be a causal claim the data cannot support; their role is contextualising
risk for future cycles. See the dated panel on the [Policy Context](index.html)
page.

## 8. "On track" composites are relative by construction

The CMS median splits the reporting states roughly in half on every measure. So
the domain composite on [(A)](state-domain.html) ("% of states mostly on track")
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
