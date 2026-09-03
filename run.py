#!/usr/bin/env python
"""End-to-end build: raw CSVs -> cleaned panel -> Sections 1-3 analysis ->
docs/data/*.json for the GitHub Pages site.

Usage:
    python run.py            # full build
    python run.py --fetch    # (re)download the three raw Core Set CSVs first

Raw data: data.medicaid.gov, Quality theme
  2022  https://data.medicaid.gov/dataset/dfd13757-d763-4f7a-9641-3f06ce21b4c6
  2023  https://data.medicaid.gov/dataset/e85033c7-367e-467e-9e81-8e85048102b8
  2024  https://data.medicaid.gov/dataset/a5023394-ab10-465b-bb4a-7de5ac98d90c
"""

from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from coreset import build, config  # noqa: E402

RAW_URLS = {
    2022: "https://data.medicaid.gov/sites/default/files/uploaded_resources/2022-child-and-adult-health-care-quality-measures_0.csv",
    2023: "https://data.medicaid.gov/sites/default/files/uploaded_resources/2023-child-and-adult-health-care-quality-measures.csv",
    2024: "https://download.medicaid.gov/data/2024-child-and-adult-health-care-quality-measures.csv",
}


def fetch() -> None:
    config.RAW.mkdir(parents=True, exist_ok=True)
    for year, url in RAW_URLS.items():
        dest = config.RAW / config.RAW_FILES[year]
        print(f"[fetch] {year}  {url}")
        urllib.request.urlretrieve(url, dest)
        print(f"[fetch]   -> {dest}  ({dest.stat().st_size/1e6:.1f} MB)")


if __name__ == "__main__":
    if "--fetch" in sys.argv:
        fetch()
    build.main()
