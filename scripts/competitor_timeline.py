#!/usr/bin/env python3
"""Resumen cross-competidor: ads nuevos + longevidad por marca.
Uso: python3 scripts/competitor_timeline.py [días-de-corte-para-'nuevo']
"""
import json, sys, glob
from pathlib import Path
from datetime import datetime, timezone

today = datetime.now(timezone.utc)
NEW_DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 7

def parse_dt(s):
    if not s: return None
    try:
        return datetime.fromisoformat(s.replace("Z","+00:00"))
    except Exception:
        return None

results = []
for folder in sorted(Path("competitor-ads").iterdir()):
    if not folder.is_dir() or folder.name.startswith("_"):
        continue
    # Prefer full backup if exists
    raw_full = folder / "ads_raw_full.json"
    raw = folder / "ads_raw.json"
    src = raw_full if raw_full.exists() else raw
    if not src.exists():
        continue
    data = json.load(open(src))
    if not isinstance(data, list) or not data:
        continue

    page_name = (data[0].get("snapshot") or {}).get("pageName") or folder.name

    starts = []
    for ad in data:
        dt = parse_dt(ad.get("startDateFormatted"))
        if dt: starts.append((dt, ad))

    if not starts:
        continue

    # New: launched within last NEW_DAYS days
    new_ads = [(dt, ad) for dt, ad in starts if (today - dt).days <= NEW_DAYS and (today - dt).days >= 0]

    # Longest running
    oldest = min(starts, key=lambda x: x[0])
    days_running = (today - oldest[0]).days

    results.append({
        "folder": folder.name,
        "page_name": page_name,
        "total_ads": len(data),
        "new_count": len(new_ads),
        "oldest_date": oldest[0],
        "oldest_days": days_running,
        "oldest_title": (oldest[1].get("snapshot") or {}).get("title") or "(sin título)",
        "new_titles": [(ad.get("snapshot") or {}).get("title") or "(sin título)" for _, ad in new_ads[:5]],
    })

# ===== Report =====
print("=" * 78)
print(f"REPORTE CROSS-COMPETIDOR — corte 'nuevo' = últimos {NEW_DAYS} días (hoy: {today.strftime('%Y-%m-%d')})")
print("=" * 78)
print()

# Filter: 4+ new ads
qualifies = [r for r in results if r["new_count"] >= 4]
print(f"🆕 COMPETIDORES CON ≥ 4 ADS NUEVOS (últimos {NEW_DAYS} días)")
print("-" * 78)
if not qualifies:
    print(f"  Ninguno cumple el umbral de 4 ads nuevos en los últimos {NEW_DAYS} días.")
else:
    for r in sorted(qualifies, key=lambda x: -x["new_count"]):
        print(f"  ✓ {r['page_name']:30s}  {r['new_count']:3d} nuevos  (de {r['total_ads']} totales)")
        for t in r["new_titles"]:
            print(f"      → {t[:70]}")
print()

# All competitors with breakdown
print(f"📊 RESUMEN DE TODOS LOS COMPETIDORES")
print("-" * 78)
print(f"  {'Marca':30s}  {'Total':>6s}  {'Nuevos':>7s}  {'Más viejo':>22s}")
for r in sorted(results, key=lambda x: -x["new_count"]):
    flag = "🆕" if r["new_count"] >= 4 else "  "
    print(f"  {flag} {r['page_name']:27s}  {r['total_ads']:>6d}  {r['new_count']:>7d}  {r['oldest_date'].strftime('%Y-%m-%d')} ({r['oldest_days']}d)")
print()

# Longest runners
print(f"⏳ TOP CAMPAÑAS MÁS DURADERAS (ad activo desde hace más tiempo)")
print("-" * 78)
for r in sorted(results, key=lambda x: -x["oldest_days"]):
    print(f"  {r['oldest_days']:4d} días  {r['page_name']:28s}  {r['oldest_title'][:55]}")
    print(f"            desde: {r['oldest_date'].strftime('%Y-%m-%d')}")
print()
