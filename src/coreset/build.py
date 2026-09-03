"""Assemble every analysis output into docs/data/*.json for the GitHub Pages site.

Run via the repo-root orchestrator:  python run.py
"""

from __future__ import annotations

import datetime as dt
import json

from . import clean, config, regional, risk, spec_audit, trend, viewb


def _write(name: str, payload) -> None:
    config.DOCS_DATA.mkdir(parents=True, exist_ok=True)
    path = config.DOCS_DATA / name
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=None, default=str)
    print(f"[build] wrote {path.relative_to(config.ROOT)}  ({path.stat().st_size/1024:,.0f} KB)")


def main() -> None:
    generated = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    df = clean.build_clean(write=True)

    # ---- Section 1 -------------------------------------------------------------
    view_b = viewb.build_view_b(df)

    # ---- Section 2.2 / 2.3 / 2.4 --------------------------------------------
    trend_raw = trend.classify(df)
    audit = spec_audit.audit_summary(df)
    gated_detail = spec_audit.gate_trend_detail(trend_raw["detail"], df)
    trend_raw["detail_gated"] = gated_detail
    reg = regional.regional_trends(gated_detail)

    # ---- Section 3.2 -------------------------------------------------------
    risk_out = risk.score(df, gated_detail, trend_raw["persistent_bottom"])

    meta = {
        "generated_utc": generated,
        "repo": "CORPUZ-2024/Medicaid_2019_Qual_Measure",
        "spec": "project_plan/Medicaid_ViewB_GitHub_Pages_Implementation_Spec_v2.txt",
        "data_source": "data.medicaid.gov - Quality theme",
        "core_set_years": config.CORE_SET_YEARS,
        "canonical_rows": int(len(df)),
        "n_states": int(df["State"].nunique()),
    }

    _write("meta.json", meta)
    _write("view_b.json", view_b)
    _write("trend.json", {
        "meta": {k: trend_raw[k] for k in ("window", "transitions", "class_band_sd")},
        "baseline": trend_raw["baseline"],
        "state_rollup": trend_raw["state_rollup"],
        "measure_rollup": trend_raw["measure_rollup"],
        "detail": gated_detail,
        "persistent_bottom": trend_raw["persistent_bottom"],
        "audit": audit,
    })
    _write("regional.json", reg)
    _write("risk.json", risk_out)
    print("[build] done")


if __name__ == "__main__":
    main()
