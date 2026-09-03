"""Regenerate the six Appendix-A notebooks as thin, documented wrappers around
src/coreset/. Run:  python notebooks/_gen_notebooks.py
"""
from __future__ import annotations
import nbformat as nbf
from pathlib import Path

HERE = Path(__file__).resolve().parent
BOOT = (
    "import sys, pathlib\n"
    "sys.path.insert(0, str(pathlib.Path.cwd().parent / 'src'))\n"
    "import pandas as pd\n"
    "pd.set_option('display.max_columns', 40)\n"
)

NOTEBOOKS = {
    "01_ingest_clean.ipynb": [
        ("md", "# 01 · Ingest & clean (spec 2.1)\n\n"
               "Generalises `2019Medicaid.ipynb`'s cleaning: load the three Core Set vintages, "
               "normalise schema drift, tag `CoreSetYear`, select the canonical (CMS "
               "mean/median) rate, log DQ exceptions, derive `Direction` / `Eval` / "
               "`InBottomQuartile` / `MeasureKey`, attach HHS regions."),
        ("code", BOOT + "from coreset import ingest, clean"),
        ("code", "raw = ingest.load_all()\nraw.groupby('CoreSetYear').size()"),
        ("code", "df = clean.build_clean(write=True)\ndf.shape"),
        ("code", "df.groupby(['CoreSetYear','ReportProg'])['MeasureKey'].nunique()"),
        ("code", "pd.read_csv(clean.config.PROCESSED / 'dq_exceptions.csv').shape  # residual collisions (logged, not dropped)"),
    ],
    "02_view_b_adult_child.ipynb": [
        ("md", "# 02 · View B extension — Adult + Child, 2024 (spec Section 1)\n\n"
               "All states × all measures, plus the cross-state summary layer the original "
               "repo lacked: per-measure 3-up card and the composite `OnTrackShare`."),
        ("code", BOOT + "from coreset import clean, viewb"),
        ("code", "df = clean.load_clean()\nvb = viewb.build_view_b(df)\nlen(vb['measures']), list(vb['domains'])"),
        ("code", "pd.DataFrame([{'measure': m['measure_name'], 'prog': m['program'],\n"
                 "  'top': m['summary_card']['top_state'].get('state'),\n"
                 "  'bottom': m['summary_card']['bottom_state'].get('state'),\n"
                 "  'on_track': m['n_on_track'], 'not': m['n_not_on_track']}\n"
                 "  for m in vb['measures']]).head(20)"),
        ("code", "pd.DataFrame(vb['composite']).query('meets_ranking_cutoff').head(15)"),
    ],
    "03_trend_baseline.ipynb": [
        ("md", "# 03 · Three-year baseline & classification (spec 2.2)\n\n"
               "Direction-aware baseline = mean YoY ΔStateRate per (program, direction) group; "
               "Improving / Stable / Declining at ±0.5 SD; Persistent Bottom Quartile ≥ 2 of 3 years."),
        ("code", BOOT + "from coreset import clean, trend"),
        ("code", "df = clean.load_clean()\nbase, deltas = trend.baseline_table(df)\nbase"),
        ("code", "out = trend.classify(df)\npd.DataFrame(out['state_rollup']).head(15)"),
        ("code", "pd.DataFrame(out['measure_rollup']).head(15)"),
    ],
    "04_specification_change_audit.ipynb": [
        ("md", "# 04 · Comparability gate (spec 2.3)\n\n"
               "2.3b trendable filter (computed approximation of CMS's 3-part criterion), "
               "2.3c specification-change seed, 2.3d state-level 'other specifications' flag. "
               "A DeltaRate that fails any check renders as *Not comparable*."),
        ("code", BOOT + "from coreset import clean, trend, spec_audit"),
        ("code", "df = clean.load_clean()\ntm = spec_audit.trendable_measures(df)\n"
                 "tm.groupby('program')[['present_all_years','meets_state_threshold','trendable_computed']].sum()"),
        ("code", "spec_audit.other_spec_flags().groupby('CoreSetYear').size()"),
        ("code", "g = spec_audit.gate_trend_detail(trend.classify(df)['detail'], df)\n"
                 "pd.Series([d['classification_display'] for d in g]).value_counts()"),
    ],
    "05_regional_stratification.ipynb": [
        ("md", "# 05 · HHS-region stratification (spec 2.4)\n\n"
               "Section 2.2 re-run with HHSRegion added, over gated-comparable pairs only, "
               "with a region-vs-national delta. The 2019 notebook's ad hoc 4-region grouping is retired."),
        ("code", BOOT + "from coreset import clean, trend, spec_audit, regional"),
        ("code", "df = clean.load_clean()\n"
                 "g = spec_audit.gate_trend_detail(trend.classify(df)['detail'], df)\n"
                 "reg = regional.regional_trends(g)\npd.DataFrame(reg['region_overall'])"),
        ("code", "pd.DataFrame(reg['highlights']['most_below_national'])"),
    ],
    "06_risk_scoring.ipynb": [
        ("md", "# 06 · At-risk scoring (spec 3.2)\n\n"
               "Component-wise composite risk (trend / fiscal / reporting-capacity exposure). "
               "Beneficiary **magnitude** only — no dollar figure (out of scope in v2). "
               "Reference tables in `data/reference/` are analyst-maintained; missing inputs "
               "yield `null`, never a fabricated number."),
        ("code", BOOT + "from coreset import clean, trend, spec_audit, risk"),
        ("code", "df = clean.load_clean()\n"
                 "tr = trend.classify(df)\n"
                 "g = spec_audit.gate_trend_detail(tr['detail'], df)\n"
                 "k = risk.score(df, g, tr['persistent_bottom'])\n"
                 "pd.DataFrame([{'program': s['program'], 'state': s['state'],\n"
                 "  'risk': s['composite_risk_0_100'],\n"
                 "  **{c: s['components'][c].get('raw') for c in s['components']}}\n"
                 "  for s in k['scores']]).head(20)"),
        ("code", "k['beneficiary_magnitude']"),
    ],
}


def build():
    for name, cells in NOTEBOOKS.items():
        nb = nbf.v4.new_notebook()
        nb.cells = [
            nbf.v4.new_markdown_cell(src) if kind == "md" else nbf.v4.new_code_cell(src)
            for kind, src in cells
        ]
        nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
        nbf.write(nb, HERE / name)
        print("wrote", name)


if __name__ == "__main__":
    build()
