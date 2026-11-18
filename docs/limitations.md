# Limitations — scope and approach

Section 4 of the v2 spec, kept current with what this build actually does. Terms
(*measure*, *measure rate*, *state rate*, *state rate change*) are defined in
[Terms used on this site](index.html#terms).

## 1. The window still straddles the reporting-regime change

2022–2024 has only **two** year-over-year transitions, so the 2023→2024
transition — the one crossing the voluntary-to-mandatory Child Core Set reporting
boundary — is **half** the trend signal, not a third. Every trend line is gated by
Section 2.3 before it is drawn; a 2023→2024 "decline" for a previously
inconsistent reporter may be a reporting-completeness effect.

## 2. CMS decides trendability per measure rate; state rate changes are not all equal

Which measure rates are trended follows CMS's own determinations ([methods brief](https://www.medicaid.gov/medicaid/quality-of-care/downloads/trend-methods-brief-2024.pdf)).
CMS judges each measure rate across a consistent set of ≥ 20 states; this site
then uses every state that reported the measure rate in both years of a
transition. A state that reported only in 2023 and 2024 contributes one state rate
change, not two. CMS's own trend results use the change in the **state median**
from 2022 to 2024 with a Wilcoxon signed-rank test; this site's state-level
classification is a different, descriptive measure.

CMS also changed 28 measure rates in substance between years: a window (postpartum
60 → 90 days; 6 months → 12 weeks), an age band, a population or denominator, or a
numerator. These pairs are not matched, so their state rate changes are not counted.
CMS marks 22 of the 28 as Trend or Trend with caution for the later year, so this is the
site's most conservative choice and it undercounts trendable changes. Pairing them means
judging, rate by rate, whether the change keeps the measure comparable. That judgment
has not been made.

## 3. "Baseline = average YoY change" is a relative standard, and mixes units

If every state declines in a domain in a given year, the baseline shifts down
with them, and a state merely tracking the new, worse baseline reads as
**Stable**; a state can even read as **Improving** with a small decline. The
classification flags *relative* outliers, not absolute quality. Baselines are
pooled by program × domain, and some domains combine percentages with
per-100,000 or per-1,000 measure rates and ratios, so the SD in those groups is
driven by the larger-unit measure rates.

## 4. Row-level ambiguity in the source data

The original repo's README flags "identical descriptor, different rate" rows for
2019. This build resolves them by keeping the row CMS itself marked
`Rate Used in Calculating State Mean and Median = Yes` (one canonical population
rollup per state × measure rate), and logs any residual collision to
`data/processed/dq_exceptions.csv` rather than dropping it silently. On the three
downloaded vintages that residual set is currently empty, but a future vintage
could reintroduce it.

## 5. The public-release threshold makes coverage uneven and non-random

Measures are publicly released only when ≥ 25 states report. "Bottom quartile"
and "not reported" are different things; missing state rates are handled
explicitly and never counted as a low score.

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

## 8. "On track" composites are relative by construction, and weighted by measure rate

The CMS median splits the reporting states roughly in half on every measure rate.
So the domain composite on [(A)](state-domain.html) ("% of states mostly on
track") measures how *broadly* above-median performance is spread across states,
not whether the country got better in absolute terms. A state's rank on (A) is
also limited to the measure rates it chose to report. The ranking cutoff (at least
half of the selection's measure rates) reduces, but does not remove, the effect of
states reporting different numbers of measures.

All on-track scores count **measure rates**, not measures, so a measure with many
measure rates carries more weight: Child Experience of Care is one measure with 15
measure rates, while most measures have one to three. This changes rankings. Scoring
each measure equally instead gives a Spearman correlation of 0.78 with the measure-rate
score across the 52 states. The biggest moves are California (39th → 15th), Washington
(33rd → 11th) and West Virginia (21st → 42nd). The site uses the measure-rate score.

## 9. "Reported a measure" is this site's rule

Page (A) counts a state as reporting a measure when at least one of its measure
rates has a published state rate. CMS's 2024 fact sheet counts reporting by
measure ("number of states reporting all measures") but does not state its rule
for a partly reported measure, so this site's counts may not match CMS's. They are
also per program × domain, not per Core Set, so they are not directly comparable
with CMS's Core Set-wide figures. Published state rates exclude measure rates CMS
did not publicly report for a state (for example, calculated with other
specifications), so a state that reported to CMS can still appear as not
reporting here.

## 10. The Reason themes are this site's grouping

The Reason filter on the Trends page groups CMS's stated reasons into themes by
keyword. The grouping is this site's, not CMS's, and a reason can touch more than
one theme (for example, a measure rate first reported for 2023 using the AHRQ
CAHPS Database is both newly reported and a data-source change); each reason is
filed under the first matching theme. The Reason column always shows CMS's full
text.

## 11. Scope boundary

This build covers the Core Set quality-measure data itself. It does **not**
incorporate claims-level utilization, managed-care-plan-level performance, or
state waiver terms — all of which affect measure performance but sit outside the
data.medicaid.gov Quality theme. It also does not translate measure performance
into dollar cost.

## 12. Build-specific notes

- "Measure Type" in the source is a **direction flag** (higher/lower better), not
  a measure taxonomy. The V0 "by measure type" ask is served by the direction
  filter plus the domain toolbar — see [methodology](methodology.html#measure-type).
- The unit of analysis is the **measure rate** (`ReportProg | Measure Name | Rate
  Definition`), finer than CMS's measure list, because one measure spans several
  measure rates (e.g. 7-day vs 30-day follow-up) that are not comparable to each
  other.
- Section 2.5's narrative tracks (agency-report and peer-reviewed context for
  flagged declines) are specified but not wired to a live source in this build.
- The 2024 file did not contain USVI or Guam rows despite the mandatory-reporting
  expansion; only 50 states + DC + PR appear in all three vintages.
