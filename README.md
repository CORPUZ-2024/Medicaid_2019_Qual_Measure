# Medicaid_2019_Qual_Measure
Visualization Project on the [2019 Medicaid Quality Measure Dataset](https://data.medicaid.gov/dataset/e36d89c0-f62e-56d5-bc7e-b0adf89262b8).

Please note that the graphs are rendered through nbviewer by clicking on the circle icon located in the upper right corner of the notebook. Or click on [View A](https://nbviewer.jupyter.org/github/corpuzn12/Medicaid_2019_Qual_Measure/blob/fcf0a1a5b052dbdd2b1dba4831adaa51ca725322/2019Medicaid.ipynb) or [View B](https://nbviewer.jupyter.org/github/corpuzn12/Medicaid_2019_Qual_Measure/blob/fcf0a1a5b052dbdd2b1dba4831adaa51ca725322/View%20B.ipynb).

## This visualization project has the following design goals: 
### Overview Across all Measure Types by State (View A)
CMS currently provides simple visualizations that allow users to select a specific state and measure name. However, this approach requires multiple visualizations for a single state and measure, as states typically track several measures within a given domain.
To address this limitation, we propose a more practical visualization that provides a domain-level snapshot of each state. This approach would enable users to quickly identify areas where a state is underperforming or excelling within a specific domain. By focusing on the five primary domains, we reduce the effort required in gathering the relevant insights for a given state. </p> 

**Sample Visual:**
<img src="https://user-images.githubusercontent.com/29220349/131366354-5e957cb5-01fe-4218-8535-f431b9bb1adf.JPG" width="90%"></img> </p> 
Through this view, stakeholders can easily spot the Measures in a given domain where a given state is falling behind. 
 
### Overview Across all States by Measure  Type (View B) 
 </p>
Another valuable visualization would be a comparative snapshot of all states relative to a specific measure type. By arranging states in ascending or descending order based on their rates for a shared measure, users can easily identify top, median, and bottom-performing states.
<img src="https://user-images.githubusercontent.com/29220349/134825488-439ed5fa-b1cb-4211-a211-2d17f262d912.JPG" width="90%"></img>

### Ambiguity with the Dataset </p> 
As illustrated below, some entries have identical information except for the values in 'State Rate' and the corresponding 'Median', 'Top' and 'Bottom Values'. The original dataset lacked dates or other distinguishing features that would indicate the accuracy of one entry over another. Given this ambiguity, we opted to retain the first instance of each unique entry for practical purposes.
<img src="https://user-images.githubusercontent.com/29220349/134824766-d20a9546-c3b4-4d96-bb69-914f7f6fd7c3.JPG" width="90%"></img> </p> 

---

## 2022–2024 Extension — View B across both Core Sets, trends, regions, and risk

The sections above describe the original **single-year (FFY2019)** project. The
work below extends that same View B idea to the **2022, 2023, and 2024 Child &
Adult Core Set** vintages and adds the analysis layers the 2019 notebooks did not
have. It implements
[`project_plan/Medicaid_ViewB_GitHub_Pages_Implementation_Spec_v2.txt`](project_plan/Medicaid_ViewB_GitHub_Pages_Implementation_Spec_v2.txt).

### 🔗 Interactive site

**GitHub Pages:** https://corpuz-2024.github.io/Medicaid_2019_Qual_Measure/
&nbsp;·&nbsp; source in [`docs/`](docs/)
&nbsp;·&nbsp; *(enable once via Settings → Pages → Deploy from a branch → `master` / `/docs`)*

| Page | What it shows |
|------|---------------|
| [View B (2024)](https://corpuz-2024.github.io/Medicaid_2019_Qual_Measure/) | Every measure, **both** Core Sets, all states, sorted bars + per-measure top/median/bottom-state cards + composite on-track share |
| [Trends 2022–24](https://corpuz-2024.github.io/Medicaid_2019_Qual_Measure/trends.html) | Data-driven baseline, Improving / Stable / Declining / Persistent-Bottom, comparability gate |
| [Regional](https://corpuz-2024.github.io/Medicaid_2019_Qual_Measure/regional.html) | Same trend, stratified by HHS region, vs the national average |
| [At-Risk Analysis](https://corpuz-2024.github.io/Medicaid_2019_Qual_Measure/risk.html) | Component-wise state risk index (trend / fiscal / reporting-capacity exposure) |
| [Policy Context](https://corpuz-2024.github.io/Medicaid_2019_Qual_Measure/policy.html) · [Limitations](https://corpuz-2024.github.io/Medicaid_2019_Qual_Measure/limitations.html) · [Methodology](https://corpuz-2024.github.io/Medicaid_2019_Qual_Measure/methodology.html) | Dated policy panel, scope caveats, and how every number is produced |

### Changes in **scope**

- **Both programs, every measure.** View B was only ever wired to `Child_Data`;
  it now runs for the Child **and** Adult Core Sets across all domains (6 for
  Adult, incl. Experience of Care and LTSS).
- **Three vintages instead of one.** 2022 / 2023 / 2024 files are pulled from
  data.medicaid.gov (Quality theme), tagged with `CoreSetYear`, and concatenated.
  The window matches CMS's own *Trends in State Performance: 2022 to 2024* product.
- **A cross-state summary layer** the 2019 repo lacked: per-measure top / median /
  bottom-performing **state**, plus a composite *on-track share* per state.
- **Year-over-year analysis:** which states improved or declined most, and which
  stayed in the bottom quartile, against a **data-driven baseline** (average rate
  change by program × measure direction, per year transition).
- **HHS-region stratification** (the CDC/HHS 10-region scheme), replacing the
  2019 notebook's ad hoc 4-region grouping (which was missing AK, HI, DC).
- **Analysis sections:** a dated policy/funding panel (2025 reconciliation law,
  mandatory-reporting transition) and an at-risk / positioned-for-success score
  with a **beneficiary-magnitude** estimate. Dollar / utilization-cost impact is
  **deliberately out of scope** — the rate-to-cost relationship was not
  consistent enough across domains to document as one reproducible formula.
- **Not in scope:** rewriting the View A / View B notebooks above, claims-level
  utilization, plan-level performance, and state waiver terms.

### Changes in **approach**

- **Row ambiguity resolved with CMS's own flag, not "keep first".** The 2019
  project kept the first of each duplicate descriptor row. This build keeps the
  row CMS itself marked `Rate Used in Calculating State Mean and Median = Yes`
  (one canonical population roll-up per state / measure / rate definition) and
  **logs** any residual collision to `data/processed/dq_exceptions.csv` instead
  of dropping it silently. On the three downloaded files that residual set is
  currently empty.
- **"Measure Type" is a direction flag, not a taxonomy.** In the source data that
  column only ever holds *"Higher rates are better"* / *"Lower rates are better"*.
  So the "by measure type" ask is served by a **direction filter + domain
  accordion**, and every benchmark comparison (on-track, worst-quartile, trend
  baseline) is **direction-aware** — a 2-point rise is good for one measure and
  bad for another.
- **Unit of analysis = `ReportProg | Measure Name | Rate Definition`**, finer
  than a measure name, because one name (e.g. *Follow-Up After ED Visit*) covers
  several non-comparable rate definitions (7-day vs 30-day, etc.).
- **Comparability gating before any trend line is drawn.** A state × measure ×
  transition change is only shown as a number if the measure is trendable
  (reported all 3 years, ≥ 20 consistent states, stable spec), its specification
  did not change between those years, and neither state used "other
  specifications" — otherwise it renders **"Not comparable"**. The 2024
  voluntary→mandatory reporting change is carried as an explicit caveat.
- **Risk score is transparent, not modelled.** Every component (trend exposure,
  ordinal fiscal exposure, reporting-capacity exposure) is echoed back per state;
  inputs that need an external source live in `data/reference/` and, until an
  analyst fills them, the dependent output is `null` rather than a guessed number.
- **Reproducible package, not just notebooks.** Logic lives in `src/coreset/`;
  `python run.py` rebuilds `docs/data/*.json` end to end. The six notebooks under
  `notebooks/` are thin, executable wrappers over that package.

### Run it locally

```bash
pip install -r requirements.txt
python run.py --fetch      # download the 3 raw CSVs + build docs/data/*.json
cd docs && python -m http.server 8765   # open http://localhost:8765/
```


