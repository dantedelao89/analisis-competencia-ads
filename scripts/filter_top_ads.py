#!/usr/bin/env python3
"""Filtra ads_raw.json a los top N ads por antigüedad (long-runners).
Uso: python3 scripts/filter_top_ads.py <carpeta> <N>
Sobreescribe ads_raw.json y deja un backup ads_raw_full.json.
"""
import json, sys, shutil
from pathlib import Path

folder = Path(sys.argv[1])
n = int(sys.argv[2])
src = folder / "ads_raw.json"
backup = folder / "ads_raw_full.json"

if not backup.exists():
    shutil.copy(src, backup)

data = json.load(open(src))
# Dedupe by video file key, keep oldest startDate per video
seen = {}
for ad in data:
    s = ad.get("snapshot") or {}
    videos = s.get("videos") or []
    if not videos:
        continue
    v = videos[0] or {}
    sd_url = v.get("videoSdUrl") or v.get("videoHdUrl") or ""
    if not sd_url:
        continue
    key = sd_url.split("?")[0].split("/")[-1]
    start = ad.get("startDateFormatted") or "9999"
    if key not in seen or start < seen[key]["start"]:
        seen[key] = {"ad": ad, "start": start}

# Sort by start ascending (oldest = longest runner = priority)
ranked = sorted(seen.values(), key=lambda x: x["start"])
top_ads = [r["ad"] for r in ranked[:n]]

with open(src, "w") as f:
    json.dump(top_ads, f, ensure_ascii=False, indent=2)

print(f"Filtered: {len(data)} ads → {len(top_ads)} top long-runners")
print(f"Oldest: {ranked[0]['start'][:10]}  Newest of top {n}: {ranked[min(n,len(ranked))-1]['start'][:10]}")
print(f"Backup en: {backup}")
