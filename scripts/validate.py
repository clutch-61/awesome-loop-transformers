#!/usr/bin/env python3
"""Validate data/papers.json before opening a pull request."""

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "data" / "papers.json").read_text(encoding="utf-8"))

errors = []
CATS = {c["name"] for c in DATA["categories"]}
REQUIRED = ("id", "date", "title", "authors", "venue", "category", "tags", "summary", "paper")
URL_FIELDS = ("paper", "code", "project", "deepDiveEn", "deepDiveZh", "zhPdf")
URL_RE = re.compile(r"^https?://")

ids = Counter()
titles = Counter()

for i, p in enumerate(DATA["papers"]):
    where = f"papers[{i}] {p.get('id', '?')}"
    for key in REQUIRED:
        if key not in p:
            errors.append(f"{where}: missing {key}")
    if p.get("category") not in CATS:
        errors.append(f"{where}: unknown category {p.get('category')!r}")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", p.get("date", "")):
        errors.append(f"{where}: bad date {p.get('date')!r}")
    if not isinstance(p.get("tags"), list) or not p.get("tags"):
        errors.append(f"{where}: tags must be a non-empty list")
    for lang in ("en", "zh"):
        text = p.get("summary", {}).get(lang, "")
        if not text.strip():
            errors.append(f"{where}: empty summary.{lang}")
        if len(text) > 1200:
            errors.append(f"{where}: summary.{lang} is very long ({len(text)} chars)")
    for f in URL_FIELDS:
        if p.get(f) and not URL_RE.match(p[f]):
            errors.append(f"{where}: {f} is not an http(s) URL")
    ids[p.get("id")] += 1
    titles[re.sub(r"[^a-z0-9]+", "", p.get("title", "").lower())] += 1

for k, v in ids.items():
    if v > 1:
        errors.append(f"duplicate id {k} ({v} entries)")
for k, v in titles.items():
    if v > 1:
        errors.append(f"duplicate title {k!r} ({v} entries)")

counts = Counter(p["category"] for p in DATA["papers"])
for c in DATA["categories"]:
    if c["count"] != counts[c["name"]]:
        errors.append(f"category count stale for {c['name']}: {c['count']} != {counts[c['name']]}")

if errors:
    print("FAIL")
    for e in errors:
        print(" -", e)
    sys.exit(1)

print(f"OK: {len(DATA['papers'])} papers, {len(CATS)} categories, "
      f"{sum(1 for p in DATA['papers'] if p.get('code'))} code links, "
      f"{sum(1 for p in DATA['papers'] if p.get('star'))} starred")
for c in DATA["categories"]:
    print(f"  {c['count']:3d}  {c['name']}")
