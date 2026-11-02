#!/usr/bin/env python3
"""Export data/papers.json to data/papers.csv for spreadsheet users."""

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "data" / "papers.json").read_text(encoding="utf-8"))

FIELDS = [
    "id", "date", "year", "title", "authors", "venue", "category", "tags",
    "summary_en", "summary_zh", "paper", "code", "project", "star",
    "deep_dive_en", "deep_dive_zh", "zh_pdf", "source",
]

with open(ROOT / "data" / "papers.csv", "w", encoding="utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
    w.writeheader()
    for p in DATA["papers"]:
        w.writerow({
            "id": p["id"],
            "date": p["date"],
            "year": p["date"][:4],
            "title": p["title"],
            "authors": p["authors"],
            "venue": p["venue"],
            "category": p["category"],
            "tags": ";".join(p["tags"]),
            "summary_en": p["summary"]["en"],
            "summary_zh": p["summary"]["zh"],
            "paper": p["paper"],
            "code": p.get("code", ""),
            "project": p.get("project", ""),
            "star": "yes" if p.get("star") else "",
            "deep_dive_en": p.get("deepDiveEn", ""),
            "deep_dive_zh": p.get("deepDiveZh", ""),
            "zh_pdf": p.get("zhPdf", ""),
            "source": p.get("source", ""),
        })
print("wrote", len(DATA["papers"]), "rows to data/papers.csv")
