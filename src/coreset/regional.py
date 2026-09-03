"""Section 2.4 - HHS-region stratification.

Re-runs the 2.2 delta calculation with HHSRegion as an added groupby dimension,
using only the pairwise comparisons that passed the 2.3 comparability gate, and
computes a region-vs-national delta so the page can state, concretely, e.g.
"Region 4's Behavioral Health Care measures improved X points less than the
national average between 2023 and 2024."
"""

from __future__ import annotations

import pandas as pd

from . import regions


def regional_trends(gated_detail: list[dict]) -> dict:
    df = pd.DataFrame([d for d in gated_detail if d.get("comparable")])
    if df.empty:
        return {"note": "no comparable pairwise deltas after 2.3 gating", "regions": []}

    df = df.dropna(subset=["region"])
    df["region"] = df["region"].astype(int)

    # national reference per (program, domain, transition)
    nat = (df.groupby(["program", "domain", "transition"])["improve_delta"]
           .mean().rename("national_mean_improve_delta").reset_index())

    grp = (df.groupby(["program", "domain", "transition", "region"])
           .agg(n=("improve_delta", "size"),
                mean_improve_delta=("improve_delta", "mean"),
                n_improving=("classification", lambda s: (s == "Improving").sum()),
                n_declining=("classification", lambda s: (s == "Declining").sum()),
                n_stable=("classification", lambda s: (s == "Stable").sum()))
           .reset_index()
           .merge(nat, on=["program", "domain", "transition"], how="left"))
    grp["region_vs_national"] = grp["mean_improve_delta"] - grp["national_mean_improve_delta"]

    hq = {r.HHSRegion: r.HHSRegionHQ for r in regions.load_region_lookup().itertuples()}

    records = []
    for _, r in grp.iterrows():
        records.append({
            "program": r["program"], "domain": r["domain"], "transition": r["transition"],
            "region": int(r["region"]), "region_hq": hq.get(int(r["region"])),
            "n_pairs": int(r["n"]),
            "mean_improve_delta": round(float(r["mean_improve_delta"]), 2),
            "national_mean_improve_delta": round(float(r["national_mean_improve_delta"]), 2),
            "region_vs_national": round(float(r["region_vs_national"]), 2),
            "n_improving": int(r["n_improving"]),
            "n_declining": int(r["n_declining"]),
            "n_stable": int(r["n_stable"]),
        })

    # region-level headline: biggest under/over-performance vs national
    records.sort(key=lambda x: x["region_vs_national"])
    highlights = {
        "most_below_national": records[:5],
        "most_above_national": list(reversed(records[-5:])),
    }

    # per-region overall rollup across all domains/transitions
    overall = (df.groupby(["program", "region"])
               .agg(mean_improve_delta=("improve_delta", "mean"),
                    n_declining=("classification", lambda s: (s == "Declining").sum()),
                    n_improving=("classification", lambda s: (s == "Improving").sum()),
                    n_pairs=("improve_delta", "size"))
               .reset_index())
    region_overall = [
        {"program": r["program"], "region": int(r["region"]),
         "region_hq": hq.get(int(r["region"])),
         "mean_improve_delta": round(float(r["mean_improve_delta"]), 2),
         "n_improving": int(r["n_improving"]), "n_declining": int(r["n_declining"]),
         "n_pairs": int(r["n_pairs"])}
        for _, r in overall.iterrows()
    ]

    return {
        "note": ("Region-level view. Always drill through to the state view - a "
                 "region can post a flat average while containing one sharply "
                 "improving and one sharply declining state (spec limitation #8)."),
        "region_by_domain": records,
        "region_overall": sorted(region_overall, key=lambda x: (x["program"], x["mean_improve_delta"])),
        "highlights": highlights,
    }
