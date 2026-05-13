#!/usr/bin/env python3
"""Dashboard HTML cross-competidor — agrega todos los competitor-ads/*/ en una sola vista.
Output: dashboard.html en la raíz del proyecto.
Uso: python3 scripts/build_dashboard.py
"""
import json, html
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter

ROOT = Path(__file__).resolve().parent.parent
TODAY = datetime.now(timezone.utc)

AUD_META = {
    "cold":         {"emoji": "🧊", "label": "FRÍO",        "full": "FRÍO (TOFU)",        "color": "#3b82f6"},
    "warm":         {"emoji": "🌡️", "label": "TIBIO",       "full": "TIBIO (MOFU)",       "color": "#f59e0b"},
    "retargeting":  {"emoji": "🔥", "label": "RETARGETING", "full": "RETARGETING (BOFU)", "color": "#ef4444"},
}

PURPOSE_COLORS = {
    "hook": "#a855f7", "pain": "#ef4444", "solución": "#3b82f6", "solucion": "#3b82f6", "solution": "#3b82f6",
    "demo": "#10b981", "oferta": "#f59e0b", "objeción": "#eab308", "objecion": "#eab308",
    "cta": "#ec4899", "social proof": "#8b5cf6", "fomo": "#ef4444",
    "transición": "#64748b", "transicion": "#64748b", "target": "#06b6d4",
    "aspiracional": "#8b5cf6", "introducción": "#a855f7", "revelación": "#a855f7",
    "value prop": "#3b82f6", "promesa": "#3b82f6", "urgencia": "#ef4444", "educativo": "#3b82f6",
}

NEW_DAYS = 7


def parse_dt(s):
    if not s: return None
    try: return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception: return None


def collect():
    comps = []
    base = ROOT / "competitor-ads"
    if not base.exists(): return comps
    for folder in sorted(base.iterdir()):
        if not folder.is_dir() or folder.name.startswith("_"): continue
        raw_full = folder / "ads_raw_full.json"
        raw = folder / "ads_raw.json"
        src = raw_full if raw_full.exists() else raw
        va = folder / "video_analyses.json"
        if not src.exists(): continue
        ads = json.load(open(src))
        if not isinstance(ads, list) or not ads: continue
        page_name = (ads[0].get("snapshot") or {}).get("pageName") or folder.name
        videos = json.load(open(va)) if va.exists() else []

        starts = [parse_dt(a.get("startDateFormatted")) for a in ads if a.get("startDateFormatted")]
        starts = [s for s in starts if s]
        oldest = min(starts) if starts else None
        new_count = sum(1 for s in starts if 0 <= (TODAY - s).days <= NEW_DAYS) if starts else 0

        # Aggregates from video analyses
        aud_counts = Counter()
        purposes = Counter()
        prices = Counter()
        total_scenes = 0
        languages = Counter()
        for v in videos:
            a = v.get("analysis", {})
            if "error" in a: continue
            if a.get("audience", {}).get("audience_temperature"):
                aud_counts[a["audience"]["audience_temperature"]] += 1
            for s in a.get("scenes_breakdown") or []:
                total_scenes += 1
                p = (s.get("purpose") or "").strip().lower()
                if p: purposes[p] += 1
            if a.get("price_mentioned"):
                prices[a["price_mentioned"]] += 1
            if a.get("detected_language"):
                languages[a["detected_language"]] += 1

        comps.append({
            "slug": folder.name,
            "page_name": page_name,
            "total_ads": len(ads),
            "unique_videos": len(videos),
            "new_count": new_count,
            "oldest_dt": oldest.isoformat() if oldest else None,
            "oldest_days": (TODAY - oldest).days if oldest else 0,
            "aud_counts": dict(aud_counts),
            "purposes": dict(purposes.most_common()),
            "prices": dict(prices),
            "total_scenes": total_scenes,
            "languages": dict(languages),
            "videos": [normalize_video(v, folder.name) for v in videos],
        })
    return comps


def normalize_video(v, slug):
    a = v.get("analysis", {})
    return {
        "competitor": slug,
        "ad_id": v["ad_id"],
        "title": v.get("title") or "(sin título)",
        "duplicate_of_ad_ids": v.get("duplicate_of_ad_ids", [v["ad_id"]]),
        "video_path": f"competitor-ads/{slug}/videos/{v['ad_id']}.mp4",
        "language": a.get("detected_language"),
        "tone": a.get("tone"),
        "hook": a.get("hook_first_3s"),
        "transcript_orig": a.get("transcript_original", "") or "",
        "transcript_es": a.get("transcript_es", "") or "",
        "cta_verbal": a.get("cta_verbal"),
        "price": a.get("price_mentioned"),
        "social_proof": a.get("social_proof_mentioned"),
        "value_props": a.get("value_props_dichas") or [],
        "key_visuals": a.get("key_visual_elements") or [],
        "audience": a.get("audience") or {},
        "scenes": a.get("scenes_breakdown") or [],
    }


CSS = r"""
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#0a0a0b; --bg2:#13131a; --bg3:#1c1c25; --bg4:#252531;
  --border:#2a2a35; --border2:#3a3a48;
  --txt:#e8e8ec; --txt2:#9b9ba5; --txt3:#6b6b75;
  --accent:#a78bfa; --accent2:#22d3ee; --accent3:#34d399;
}
html,body{background:var(--bg);color:var(--txt);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,sans-serif;font-size:14px;line-height:1.5;height:100vh;overflow:hidden}
.top{position:sticky;top:0;background:var(--bg);border-bottom:1px solid var(--border);z-index:50;padding:14px 24px;display:flex;align-items:center;gap:24px;flex-wrap:wrap}
.brand{font-size:18px;font-weight:700;letter-spacing:-.01em;background:linear-gradient(135deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;flex-shrink:0}
.brand .sub{font-size:11px;color:var(--txt3);font-weight:500;-webkit-text-fill-color:var(--txt3);margin-left:8px}
.kpis-strip{display:flex;gap:24px;flex-wrap:wrap;flex:1}
.kpi-mini{display:flex;flex-direction:column;gap:1px}
.kpi-mini .l{font-size:10px;color:var(--txt3);text-transform:uppercase;letter-spacing:.08em;font-weight:600}
.kpi-mini .v{font-size:16px;font-weight:700;color:var(--txt)}

.nav-tabs{display:flex;border-bottom:1px solid var(--border);padding:0 24px;background:var(--bg);position:sticky;top:65px;z-index:49}
.nav-tab{padding:12px 16px;cursor:pointer;font-size:13px;font-weight:600;color:var(--txt2);border-bottom:2px solid transparent;transition:all .15s}
.nav-tab:hover{color:var(--txt)}
.nav-tab.active{color:var(--accent);border-bottom-color:var(--accent)}

.main{overflow-y:auto;height:calc(100vh - 110px)}
.tab-content{display:none;padding:24px 32px;max-width:1400px;margin:0 auto}
.tab-content.active{display:block}

/* Section headings */
h2{font-size:22px;font-weight:700;letter-spacing:-.01em;margin-bottom:6px}
h2 .sub{color:var(--txt2);font-size:13px;font-weight:400;margin-left:8px}
h3{font-size:14px;color:var(--txt2);margin:28px 0 12px;font-weight:600;text-transform:uppercase;letter-spacing:.05em}

/* Cards */
.card{background:var(--bg2);border:1px solid var(--border);border-radius:14px;padding:18px}
.cards-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;margin:14px 0}
.kpi-card .l{font-size:11px;color:var(--txt3);text-transform:uppercase;letter-spacing:.08em;font-weight:600;margin-bottom:6px}
.kpi-card .v{font-size:28px;font-weight:700;letter-spacing:-.02em}
.kpi-card .v.small{font-size:14px;font-weight:600}

/* Competitor cards */
.comp-card{background:var(--bg2);border:1px solid var(--border);border-radius:14px;padding:20px;display:flex;flex-direction:column;gap:12px}
.comp-card .name{font-size:16px;font-weight:700}
.comp-card .meta{font-size:12px;color:var(--txt3);font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
.comp-stats{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-top:4px}
.cs-stat{background:var(--bg3);padding:8px 10px;border-radius:8px;text-align:center}
.cs-stat .l{font-size:9px;color:var(--txt3);text-transform:uppercase;letter-spacing:.06em;font-weight:700;margin-bottom:3px}
.cs-stat .v{font-size:16px;font-weight:700}
.comp-badges{display:flex;flex-wrap:wrap;gap:5px}
.tag{font-size:10.5px;padding:3px 8px;border-radius:5px;font-weight:600;line-height:1.4}

/* Timeline */
.timeline{position:relative;margin:24px 0;padding-left:0}
.timeline-row{display:grid;grid-template-columns:180px 1fr 80px;gap:12px;align-items:center;padding:10px 0;border-bottom:1px solid var(--border)}
.timeline-name{font-size:13px;font-weight:600}
.timeline-name .sub{font-size:11px;color:var(--txt3);font-weight:400;display:block}
.timeline-track{position:relative;height:30px;background:var(--bg3);border-radius:8px;overflow:hidden}
.timeline-seg{position:absolute;top:0;bottom:0;background:linear-gradient(90deg,var(--accent),var(--accent2));border-radius:6px;display:flex;align-items:center;justify-content:center;color:#fff;font-size:11px;font-weight:600;text-shadow:0 1px 2px rgba(0,0,0,.4)}
.timeline-days{text-align:right;font-size:12px;color:var(--txt2);font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
.timeline-new{font-size:10px;background:#22c55e;color:#0a0a0b;font-weight:700;padding:2px 6px;border-radius:999px;margin-left:6px;vertical-align:middle}

/* Comparison table */
.compare-table{width:100%;border-collapse:collapse;font-size:13px;margin-top:14px}
.compare-table th,.compare-table td{padding:10px 12px;text-align:left;border-bottom:1px solid var(--border)}
.compare-table th{font-size:11px;color:var(--txt3);text-transform:uppercase;letter-spacing:.06em;font-weight:700;background:var(--bg2);position:sticky;top:0}
.compare-table th:first-child,.compare-table td:first-child{position:sticky;left:0;background:var(--bg);z-index:1}
.compare-table tbody tr:hover td{background:var(--bg2)}

/* Funnel bar */
.aud-bar{display:flex;height:24px;border-radius:6px;overflow:hidden;border:1px solid var(--border);background:var(--bg3)}
.aud-bar-seg{display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:700;color:#fff;text-shadow:0 1px 2px rgba(0,0,0,.4);min-width:24px}

/* Bar chart */
.bar-chart{display:flex;flex-direction:column;gap:6px;margin:14px 0}
.bar-row{display:grid;grid-template-columns:160px 1fr 80px;gap:10px;align-items:center;font-size:12.5px}
.bar-track{height:22px;background:var(--bg3);border-radius:6px;overflow:hidden}
.bar-fill{height:100%;border-radius:6px;display:flex;align-items:center;justify-content:flex-end;padding-right:8px;color:#fff;font-weight:600;font-size:11px;min-width:24px}
.bar-label{color:var(--txt2);text-transform:capitalize}
.bar-count{color:var(--txt3);text-align:right;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:11px}

/* Videos tab */
.videos-layout{display:grid;grid-template-columns:340px 1fr;gap:20px;height:calc(100vh - 160px)}
@media(max-width:900px){.videos-layout{grid-template-columns:1fr;height:auto}}
.videos-sidebar{background:var(--bg2);border:1px solid var(--border);border-radius:12px;overflow:hidden;display:flex;flex-direction:column}
.videos-filters{padding:12px;border-bottom:1px solid var(--border)}
.videos-filters input{width:100%;background:var(--bg);border:1px solid var(--border);border-radius:8px;padding:8px 12px;color:var(--txt);font-size:13px;outline:none;margin-bottom:8px}
.videos-filters input:focus{border-color:var(--accent)}
.filter-group{margin-bottom:8px}
.filter-group .l{font-size:10px;color:var(--txt3);text-transform:uppercase;letter-spacing:.08em;font-weight:700;margin-bottom:4px}
.filter-chips{display:flex;gap:5px;flex-wrap:wrap}
.chip{font-size:11px;padding:4px 9px;border-radius:999px;background:var(--bg3);border:1px solid var(--border);color:var(--txt2);cursor:pointer;transition:all .15s}
.chip:hover{border-color:var(--accent)}
.chip.active{background:var(--accent);border-color:var(--accent);color:#000;font-weight:600}

.video-list{flex:1;overflow-y:auto;padding:6px}
.vid-item{padding:10px 12px;border-radius:8px;cursor:pointer;display:flex;flex-direction:column;gap:5px;border:1px solid transparent;transition:background .12s}
.vid-item:hover{background:var(--bg3)}
.vid-item.active{background:var(--bg3);border-color:var(--accent)}
.vid-item .num{font-size:10px;color:var(--txt3);font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-weight:600}
.vid-item .title{font-size:12.5px;font-weight:600;color:var(--txt);line-height:1.3;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.vid-item .comp-tag{font-size:10px;color:var(--accent2);font-weight:600}
.vid-item .tags{display:flex;gap:4px;flex-wrap:wrap}

/* Video detail */
.video-detail{background:var(--bg2);border:1px solid var(--border);border-radius:12px;overflow:hidden;overflow-y:auto;display:flex;flex-direction:column}
.vd-empty{display:flex;align-items:center;justify-content:center;height:100%;color:var(--txt3);font-size:13px;padding:40px;text-align:center}
.vd-header{padding:18px 24px;border-bottom:1px solid var(--border)}
.vd-header h3{font-size:18px;font-weight:700;margin:0 0 8px;text-transform:none;letter-spacing:-.01em;color:var(--txt)}
.vd-badges{display:flex;flex-wrap:wrap;gap:6px}
.badge{display:inline-flex;align-items:center;gap:4px;padding:3px 9px;border-radius:999px;font-size:11px;font-weight:600;border:1px solid}
.badge-price{background:rgba(34,197,94,.15);border-color:#22c55e;color:#22c55e}
.badge-tone{background:var(--bg3);border-color:var(--border);color:var(--txt2)}
.badge-comp{background:rgba(34,211,238,.15);border-color:#22d3ee;color:#22d3ee}
.badge-lang{background:var(--bg3);border-color:var(--border);color:var(--txt2);font-family:ui-monospace,SFMono-Regular,Menlo,monospace}

.vd-body{display:grid;grid-template-columns:320px 1fr;gap:18px;padding:18px 24px}
@media(max-width:1100px){.vd-body{grid-template-columns:1fr}}
.vd-video video{width:100%;border-radius:10px;background:#000;display:block;border:1px solid var(--border)}
.vd-meta{display:flex;flex-direction:column;gap:10px;margin-top:12px}
.meta-card{background:var(--bg3);border:1px solid var(--border);border-radius:8px;padding:10px 12px}
.meta-card .l{font-size:9px;color:var(--txt3);text-transform:uppercase;letter-spacing:.08em;font-weight:700;margin-bottom:4px}
.meta-card .v{font-size:12.5px;color:var(--txt);line-height:1.5}
.meta-card .v em{color:var(--accent2);font-style:italic}

.vd-info{display:flex;flex-direction:column;gap:12px}
.hook-card{background:linear-gradient(135deg,rgba(167,139,250,.08),rgba(34,211,238,.05));border:1px solid rgba(167,139,250,.3);border-radius:10px;padding:12px 14px}
.hook-card .l{font-size:9px;color:var(--accent);text-transform:uppercase;letter-spacing:.1em;font-weight:700;margin-bottom:5px}
.hook-card .v{font-size:13px;color:var(--txt);line-height:1.55}

.aud-card{background:var(--bg3);border:1px solid var(--border);border-radius:10px;padding:12px 14px}
.aud-card .l{font-size:9px;color:var(--txt3);text-transform:uppercase;letter-spacing:.08em;font-weight:700;margin-bottom:6px}
.aud-card .reasoning{font-size:12.5px;color:var(--txt);line-height:1.6}
.signals{display:flex;flex-wrap:wrap;gap:4px;margin-top:6px}
.signal-chip{font-size:10px;padding:2px 7px;border-radius:5px;background:var(--bg);border:1px solid var(--border);color:var(--txt2);font-family:ui-monospace,SFMono-Regular,Menlo,monospace}

.sub-tabs{display:flex;border-bottom:1px solid var(--border);gap:0;margin-top:6px}
.sub-tab{padding:8px 14px;cursor:pointer;font-size:12px;font-weight:600;color:var(--txt2);border-bottom:2px solid transparent}
.sub-tab:hover{color:var(--txt)}
.sub-tab.active{color:var(--accent);border-bottom-color:var(--accent)}
.sub-tab-count{display:inline-block;font-size:10px;color:var(--txt3);margin-left:4px;padding:1px 5px;background:var(--bg3);border-radius:3px}
.sub-tab.active .sub-tab-count{background:rgba(167,139,250,.2);color:var(--accent)}
.sub-panel{display:none;padding:12px 0}
.sub-panel.active{display:block}

.scenes-timeline{display:flex;height:30px;border-radius:6px;overflow:hidden;margin-bottom:14px;border:1px solid var(--border);background:var(--bg3)}
.timeline-purpose-seg{cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:9px;font-weight:600;color:#fff;text-shadow:0 1px 2px rgba(0,0,0,.4);border-right:1px solid rgba(0,0,0,.2)}
.timeline-purpose-seg:hover{filter:brightness(1.2)}
.timeline-purpose-seg:last-child{border-right:none}

.scene{display:grid;grid-template-columns:auto auto 1fr;gap:12px;padding:12px;border-radius:8px;margin:6px 0;background:var(--bg3);border:1px solid var(--border)}
.scene-time{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:11px;color:var(--accent2);font-weight:600;align-self:start;padding-top:3px;white-space:nowrap}
.scene-purpose{font-size:9px;text-transform:uppercase;letter-spacing:.05em;font-weight:700;align-self:start;padding:3px 7px;border-radius:5px;color:#fff;text-align:center;white-space:nowrap}
.scene-content{display:flex;flex-direction:column;gap:5px;min-width:0}
.scene-row{font-size:12px;line-height:1.5;word-wrap:break-word}
.scene-row .label{color:var(--txt3);font-size:9px;text-transform:uppercase;letter-spacing:.05em;font-weight:700;margin-right:5px;display:inline-block;width:50px}
.scene-row.visual{color:var(--txt)}
.scene-row.audio{color:#c4b5fd;font-style:italic}
.scene-row.audio-es{color:#67e8f9;font-style:italic}
.scene-row.text{color:var(--txt2);font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:11px}

.transcript-block{background:var(--bg3);border:1px solid var(--border);border-radius:8px;padding:14px;margin-bottom:10px}
.transcript-block .l{font-size:9px;color:var(--txt3);text-transform:uppercase;letter-spacing:.08em;font-weight:700;margin-bottom:8px}
.transcript-block .v{font-size:13px;color:var(--txt);line-height:1.7;font-style:italic}

::-webkit-scrollbar{width:8px;height:8px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:4px}
::-webkit-scrollbar-thumb:hover{background:var(--border2)}
"""


def main():
    comps = collect()
    all_videos = []
    for c in comps:
        for v in c["videos"]:
            all_videos.append(v)

    # Global aggregates
    total_ads = sum(c["total_ads"] for c in comps)
    total_unique = sum(c["unique_videos"] for c in comps)
    total_scenes = sum(c["total_scenes"] for c in comps)
    global_aud = Counter()
    global_purposes = Counter()
    for c in comps:
        for k, n in c["aud_counts"].items():
            global_aud[k] += n
        for k, n in c["purposes"].items():
            global_purposes[k] += n

    # New ads ≥ 4 winners
    winners = [c for c in comps if c["new_count"] >= 4]
    winners_sorted = sorted(winners, key=lambda c: -c["new_count"])

    # Longest runners
    longest = sorted([c for c in comps if c["oldest_days"]], key=lambda c: -c["oldest_days"])
    max_days = longest[0]["oldest_days"] if longest else 1

    payload = {
        "competitors": comps,
        "videos": all_videos,
        "today": TODAY.strftime("%Y-%m-%d"),
        "new_days": NEW_DAYS,
        "aud_meta": AUD_META,
        "purpose_colors": PURPOSE_COLORS,
    }

    # === RENDER ===
    def esc(s): return html.escape(str(s) if s is not None else "")

    # Tab 1: Overview
    kpis_html = f"""
    <div class="cards-grid">
      <div class="card kpi-card"><div class="l">Competidores</div><div class="v">{len(comps)}</div></div>
      <div class="card kpi-card"><div class="l">Ads activos (total)</div><div class="v">{total_ads}</div></div>
      <div class="card kpi-card"><div class="l">Creativos analizados</div><div class="v">{total_unique}</div></div>
      <div class="card kpi-card"><div class="l">Escenas totales</div><div class="v">{total_scenes}</div></div>
    </div>
    """

    # Global funnel bar
    total_classified = sum(global_aud.values())
    aud_bar_segs = ""
    if total_classified:
        for k in ["cold", "warm", "retargeting"]:
            n = global_aud.get(k, 0)
            if n == 0: continue
            pct = n*100/total_classified
            m = AUD_META[k]
            aud_bar_segs += f'<div class="aud-bar-seg" style="background:{m["color"]};width:{pct}%">{m["emoji"]} {m["full"]}: {n} ({pct:.0f}%)</div>'

    # Global purposes bar chart
    max_p = max(global_purposes.values()) if global_purposes else 1
    purposes_html = ""
    for k, n in list(global_purposes.most_common())[:12]:
        color = PURPOSE_COLORS.get(k.lower().split("/")[0].strip(), "#64748b")
        pct = n*100/max_p
        purposes_html += f'<div class="bar-row"><div class="bar-label">{esc(k)}</div><div class="bar-track"><div class="bar-fill" style="width:{pct}%;background:{color}">{n}</div></div><div class="bar-count">{n*100/total_scenes:.0f}%</div></div>'

    # Winners
    winners_html = ""
    if winners_sorted:
        for c in winners_sorted:
            winners_html += f'''
            <div class="card comp-card">
              <div class="name">🆕 {esc(c["page_name"])} <span class="meta">+{c["new_count"]} nuevos</span></div>
              <div class="meta">de {c["total_ads"]} ads totales · {c["unique_videos"]} creativos analizados</div>
            </div>'''
    else:
        winners_html = '<div class="card" style="grid-column:1/-1;color:var(--txt3);text-align:center;padding:24px">Ningún competidor lanzó ≥ 4 ads en los últimos 7 días.</div>'

    # Tab 2: Timeline
    timeline_rows = ""
    for c in sorted(comps, key=lambda x: -x["oldest_days"]):
        pct = (c["oldest_days"]*100/max_days) if max_days else 0
        new_badge = f'<span class="timeline-new">+{c["new_count"]} nuevos</span>' if c["new_count"] >= 4 else ""
        timeline_rows += f'''
        <div class="timeline-row">
          <div class="timeline-name">{esc(c["page_name"])}{new_badge}<span class="sub">{esc(c["slug"])}</span></div>
          <div class="timeline-track"><div class="timeline-seg" style="left:0;width:{max(pct,6):.0f}%">{c["oldest_days"]} días</div></div>
          <div class="timeline-days">{c["oldest_dt"][:10] if c["oldest_dt"] else "—"}</div>
        </div>'''

    # Tab 3: Comparativa
    compare_table = """
    <table class="compare-table">
      <thead><tr>
        <th>Competidor</th>
        <th>Total ads</th>
        <th>Creativos únicos</th>
        <th>🆕 Nuevos (7d)</th>
        <th>⏳ Más viejo (días)</th>
        <th>🧊 Cold</th>
        <th>🌡️ Warm</th>
        <th>🔥 Retarget</th>
        <th>Precios</th>
        <th>Idiomas</th>
      </tr></thead>
      <tbody>
    """
    for c in sorted(comps, key=lambda x: -x["total_ads"]):
        prices_str = ", ".join(c["prices"].keys()) if c["prices"] else "—"
        langs_str = ", ".join(c["languages"].keys()) if c["languages"] else "—"
        compare_table += f'''
        <tr>
          <td><strong>{esc(c["page_name"])}</strong></td>
          <td>{c["total_ads"]}</td>
          <td>{c["unique_videos"]}</td>
          <td>{c["new_count"]}{" 🆕" if c["new_count"]>=4 else ""}</td>
          <td>{c["oldest_days"]}</td>
          <td>{c["aud_counts"].get("cold",0)}</td>
          <td>{c["aud_counts"].get("warm",0)}</td>
          <td>{c["aud_counts"].get("retargeting",0)}</td>
          <td style="font-size:12px;color:var(--txt2)">{esc(prices_str[:50])}</td>
          <td style="font-size:12px;color:var(--txt2)">{esc(langs_str)}</td>
        </tr>'''
    compare_table += "</tbody></table>"

    # Competitor cards detail
    comp_cards_html = ""
    for c in sorted(comps, key=lambda x: -x["total_ads"]):
        # Funnel mini bar
        tot_cls = sum(c["aud_counts"].values())
        mini_bar = ""
        if tot_cls:
            for k in ["cold","warm","retargeting"]:
                n = c["aud_counts"].get(k,0)
                if n==0: continue
                pct = n*100/tot_cls
                m = AUD_META[k]
                mini_bar += f'<div class="aud-bar-seg" style="background:{m["color"]};width:{pct}%">{m["emoji"]}{n}</div>'

        comp_cards_html += f'''
        <div class="card comp-card">
          <div class="name">{esc(c["page_name"])}</div>
          <div class="meta">{esc(c["slug"])} · {", ".join(c["languages"].keys())}</div>
          <div class="comp-stats">
            <div class="cs-stat"><div class="l">Ads activos</div><div class="v">{c["total_ads"]}</div></div>
            <div class="cs-stat"><div class="l">Nuevos 7d</div><div class="v" style="color:{'#22c55e' if c['new_count']>=4 else 'var(--txt)'}">{c["new_count"]}</div></div>
            <div class="cs-stat"><div class="l">Más viejo</div><div class="v">{c["oldest_days"]}d</div></div>
          </div>
          <div class="aud-bar">{mini_bar}</div>
          <a href="competitor-ads/{esc(c["slug"])}/analysis.html" target="_blank" style="font-size:12px;color:var(--accent2);text-decoration:none">→ Ver análisis detallado</a>
        </div>'''

    out = f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Dashboard — Análisis de competencia</title>
<style>{CSS}</style>
</head>
<body>

<div class="top">
  <div class="brand">📊 Dashboard de Competencia <span class="sub">Análisis cross-competidor</span></div>
  <div class="kpis-strip">
    <div class="kpi-mini"><span class="l">Competidores</span><span class="v">{len(comps)}</span></div>
    <div class="kpi-mini"><span class="l">Ads activos</span><span class="v">{total_ads}</span></div>
    <div class="kpi-mini"><span class="l">Creativos</span><span class="v">{total_unique}</span></div>
    <div class="kpi-mini"><span class="l">Escenas</span><span class="v">{total_scenes}</span></div>
    <div class="kpi-mini"><span class="l">Generado</span><span class="v" style="font-size:13px;font-weight:600">{TODAY.strftime("%Y-%m-%d")}</span></div>
  </div>
</div>

<nav class="nav-tabs">
  <div class="nav-tab active" data-tab="overview">📈 Resumen</div>
  <div class="nav-tab" data-tab="timeline">⏳ Timeline</div>
  <div class="nav-tab" data-tab="compare">🆚 Comparativa</div>
  <div class="nav-tab" data-tab="videos">🎞️ Videos ({total_unique})</div>
</nav>

<div class="main">
  <div class="tab-content active" data-panel="overview">
    <h2>Resumen global</h2>
    {kpis_html}

    <h3>🆕 Competidores con ≥ 4 ads nuevos (últimos {NEW_DAYS} días)</h3>
    <div class="cards-grid">{winners_html}</div>

    <h3>📊 Distribución global del funnel</h3>
    <div class="aud-bar" style="height:32px">{aud_bar_segs}</div>

    <h3>🎭 Roles narrativos detectados ({total_scenes} escenas)</h3>
    <div class="bar-chart">{purposes_html}</div>

    <h3>🏢 Todos los competidores</h3>
    <div class="cards-grid" style="grid-template-columns:repeat(auto-fit,minmax(280px,1fr))">{comp_cards_html}</div>
  </div>

  <div class="tab-content" data-panel="timeline">
    <h2>Timeline competitiva <span class="sub">Ad más viejo aún activo (proxy de "ad ganador escalado")</span></h2>
    <div class="card" style="margin-top:14px">
      <div class="timeline">{timeline_rows}</div>
    </div>
    <p style="color:var(--txt3);font-size:12px;margin-top:14px">💡 Los ads que llevan más tiempo activos son los que la marca está escalando. Si un competidor mantiene un creativo por meses, es porque le sigue rindiendo el ROAS.</p>
  </div>

  <div class="tab-content" data-panel="compare">
    <h2>Comparativa lado a lado <span class="sub">Métricas clave por competidor</span></h2>
    <div style="overflow-x:auto;margin-top:14px">{compare_table}</div>
  </div>

  <div class="tab-content" data-panel="videos">
    <h2>Explorador de videos <span class="sub">Filtrá y compará todos los creativos analizados</span></h2>
    <div class="videos-layout">
      <aside class="videos-sidebar">
        <div class="videos-filters">
          <input id="search" placeholder="🔍 Buscar título, copy, transcripción..." />
          <div class="filter-group">
            <div class="l">Competidor</div>
            <div class="filter-chips" id="comp-filters"></div>
          </div>
          <div class="filter-group">
            <div class="l">Audiencia</div>
            <div class="filter-chips" id="aud-filters"></div>
          </div>
        </div>
        <div class="video-list" id="video-list"></div>
      </aside>
      <section class="video-detail" id="video-detail">
        <div class="vd-empty">Seleccioná un video de la lista para ver el análisis completo.</div>
      </section>
    </div>
  </div>
</div>

<script>window.__DATA__ = {json.dumps(payload, ensure_ascii=False)};</script>
<script>
const D = window.__DATA__;
const AUD = D.aud_meta;
const PC = D.purpose_colors;
const $ = (s, el=document) => el.querySelector(s);
const $$ = (s, el=document) => [...el.querySelectorAll(s)];
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c]));
const pColor = p => PC[(p||"").trim().toLowerCase().split("/")[0].trim()] || "#64748b";

// Tab navigation
$$(".nav-tab").forEach(t => t.addEventListener("click", () => {{
  $$(".nav-tab").forEach(x => x.classList.remove("active"));
  $$(".tab-content").forEach(x => x.classList.remove("active"));
  t.classList.add("active");
  $(`.tab-content[data-panel="${{t.dataset.tab}}"]`).classList.add("active");
  if (t.dataset.tab === "videos" && !window._vidsInit) {{ initVideos(); window._vidsInit = true; }}
}}));

// Videos browser
let vState = {{ search: "", comp: "all", aud: "all", selected: null }};

function initVideos() {{
  const compFilters = $("#comp-filters");
  const auds = ["all", ...new Set(D.videos.map(v => v.audience?.audience_temperature).filter(Boolean))];
  const comps = ["all", ...new Set(D.videos.map(v => v.competitor))];

  compFilters.innerHTML = comps.map(c => `<div class="chip ${{c==="all"?"active":""}}" data-comp="${{esc(c)}}">${{c==="all"?"Todos":esc(c)}}</div>`).join("");
  $("#aud-filters").innerHTML = auds.map(a => {{
    const m = AUD[a];
    const label = a==="all" ? "Todas" : (m ? m.emoji + " " + m.label : esc(a));
    return `<div class="chip ${{a==="all"?"active":""}}" data-aud="${{esc(a)}}">${{label}}</div>`;
  }}).join("");

  $("#search").addEventListener("input", e => {{ vState.search = e.target.value; renderList(); }});
  $$("#comp-filters .chip").forEach(c => c.addEventListener("click", () => {{
    $$("#comp-filters .chip").forEach(x => x.classList.remove("active"));
    c.classList.add("active"); vState.comp = c.dataset.comp; renderList();
  }}));
  $$("#aud-filters .chip").forEach(c => c.addEventListener("click", () => {{
    $$("#aud-filters .chip").forEach(x => x.classList.remove("active"));
    c.classList.add("active"); vState.aud = c.dataset.aud; renderList();
  }}));
  renderList();
}}

function renderList() {{
  const list = $("#video-list");
  const q = vState.search.toLowerCase();
  const items = D.videos.filter(v => {{
    if (vState.comp !== "all" && v.competitor !== vState.comp) return false;
    if (vState.aud !== "all" && v.audience?.audience_temperature !== vState.aud) return false;
    if (q && !((v.title + " " + v.transcript_orig + " " + (v.transcript_es||"") + " " + v.competitor).toLowerCase().includes(q))) return false;
    return true;
  }});
  list.innerHTML = items.length === 0
    ? '<div style="padding:18px;text-align:center;color:var(--txt3);font-size:12px">Sin resultados</div>'
    : items.map((v, i) => {{
      const aud = v.audience?.audience_temperature;
      const audM = aud ? AUD[aud] : null;
      const audTag = audM ? `<span class="tag" style="background:${{audM.color}}20;border:1px solid ${{audM.color}}40;color:${{audM.color}}">${{audM.emoji}}</span>` : "";
      const priceTag = v.price ? `<span class="tag" style="background:rgba(34,197,94,.15);border:1px solid #22c55e40;color:#22c55e">💰 ${{esc(v.price)}}</span>` : "";
      const idx = D.videos.indexOf(v);
      return `<div class="vid-item ${{vState.selected===idx?"active":""}}" data-i="${{idx}}">
        <div class="comp-tag">▸ ${{esc(v.competitor)}}</div>
        <div class="title">${{esc(v.title)}}</div>
        <div class="tags">${{audTag}}${{priceTag}}</div>
      </div>`;
    }}).join("");
  $$(".vid-item", list).forEach(el => el.addEventListener("click", () => selectVid(parseInt(el.dataset.i))));
}}

function selectVid(i) {{
  vState.selected = i;
  renderList();
  renderDetail(D.videos[i]);
}}

function renderDetail(v) {{
  const aud = v.audience || {{}};
  const audM = AUD[aud.audience_temperature];
  const badges = [];
  badges.push(`<span class="badge badge-comp">▸ ${{esc(v.competitor)}}</span>`);
  if (audM) badges.push(`<span class="badge" style="background:${{audM.color}}25;border-color:${{audM.color}};color:${{audM.color}}">${{audM.emoji}} ${{audM.full}}</span>`);
  if (v.price) badges.push(`<span class="badge badge-price">💰 ${{esc(v.price)}}</span>`);
  if (v.tone) badges.push(`<span class="badge badge-tone">🎭 ${{esc(v.tone)}}</span>`);
  if (v.language) badges.push(`<span class="badge badge-lang">${{esc(v.language).toUpperCase()}}</span>`);

  const scenes = v.scenes || [];
  const tlSegs = scenes.length ? scenes.map((s, idx) => {{
    const c = pColor(s.purpose);
    return `<div class="timeline-purpose-seg" style="background:${{c}};width:${{(100/scenes.length)}}%" title="${{esc(s.purpose||"")}}">${{scenes.length<=10?esc((s.purpose||"").slice(0,6)):""}}</div>`;
  }}).join("") : "";

  const sceneRows = scenes.map(s => {{
    const c = pColor(s.purpose);
    const audio = s.audio_dialogue ? `<div class="scene-row audio"><span class="label">AUDIO</span>"${{esc(s.audio_dialogue)}}"</div>` : "";
    const audioEs = s.audio_dialogue_es ? `<div class="scene-row audio-es"><span class="label">AUDIO ES</span>"${{esc(s.audio_dialogue_es)}}"</div>` : "";
    const text = s.on_screen_text ? `<div class="scene-row text"><span class="label">TEXTO</span>${{esc(s.on_screen_text)}}</div>` : "";
    return `<div class="scene">
      <div class="scene-time">${{esc(s.timestamp_start)}}–${{esc(s.timestamp_end)}}</div>
      <div class="scene-purpose" style="background:${{c}}">${{esc(s.purpose||"—")}}</div>
      <div class="scene-content">
        <div class="scene-row visual"><span class="label">VISUAL</span>${{esc(s.visual||"")}}</div>
        ${{audio}}${{audioEs}}${{text}}
      </div>
    </div>`;
  }}).join("");

  const signals = (aud.signals_detected || []).map(s => `<span class="signal-chip">${{esc(s)}}</span>`).join("");
  const audBlock = aud.reasoning ? `
    <div class="aud-card">
      <div class="l">${{audM ? audM.emoji + " " + audM.full + " · " + esc(aud.confidence||"") : "Audiencia"}}</div>
      <div class="reasoning">${{esc(aud.reasoning)}}</div>
      ${{signals ? `<div class="signals" style="margin-top:8px">${{signals}}</div>` : ""}}
    </div>` : "";

  $("#video-detail").innerHTML = `
    <div class="vd-header">
      <h3>${{esc(v.title)}}</h3>
      <div class="vd-badges">${{badges.join("")}}</div>
    </div>
    <div class="vd-body">
      <div class="vd-video">
        <video controls preload="metadata" src="${{esc(v.video_path)}}"></video>
        <div class="vd-meta">
          ${{v.cta_verbal ? `<div class="meta-card"><div class="l">📢 CTA verbal</div><div class="v"><em>"${{esc(v.cta_verbal)}}"</em></div></div>` : ""}}
          ${{v.social_proof ? `<div class="meta-card"><div class="l">🏅 Social proof</div><div class="v">${{esc(v.social_proof)}}</div></div>` : ""}}
        </div>
      </div>
      <div class="vd-info">
        ${{v.hook ? `<div class="hook-card"><div class="l">⚡ Hook (primeros 3s)</div><div class="v">${{esc(v.hook)}}</div></div>` : ""}}
        ${{audBlock}}
        <div class="sub-tabs">
          <div class="sub-tab active" data-stab="scenes">Escenas <span class="sub-tab-count">${{scenes.length}}</span></div>
          <div class="sub-tab" data-stab="transcript">Transcripción</div>
        </div>
        <div class="sub-panel active" data-spanel="scenes">
          ${{tlSegs ? `<div class="scenes-timeline">${{tlSegs}}</div>` : ""}}
          ${{sceneRows || '<div style="color:var(--txt3);padding:14px;text-align:center;font-size:12px">Sin escenas</div>'}}
        </div>
        <div class="sub-panel" data-spanel="transcript">
          ${{v.transcript_orig ? `<div class="transcript-block"><div class="l">Original (${{esc((v.language||"?").toUpperCase())}})</div><div class="v">"${{esc(v.transcript_orig)}}"</div></div>` : ""}}
          ${{v.transcript_es ? `<div class="transcript-block"><div class="l">🇪🇸 Traducción al español</div><div class="v">"${{esc(v.transcript_es)}}"</div></div>` : ""}}
          ${{(!v.transcript_orig && !v.transcript_es) ? '<div style="color:var(--txt3);padding:14px;text-align:center;font-size:12px">Sin transcripción</div>' : ""}}
        </div>
      </div>
    </div>`;
  $$("#video-detail .sub-tab").forEach(t => t.addEventListener("click", () => {{
    $$("#video-detail .sub-tab").forEach(x => x.classList.remove("active"));
    $$("#video-detail .sub-panel").forEach(x => x.classList.remove("active"));
    t.classList.add("active");
    $(`#video-detail .sub-panel[data-spanel="${{t.dataset.stab}}"]`).classList.add("active");
  }}));
}}
</script>
</body>
</html>'''

    out_path = ROOT / "dashboard.html"
    out_path.write_text(out, encoding="utf-8")
    print(f"Wrote {out_path} ({len(out)/1024:.1f} KB)")
    print(f"  Competidores: {len(comps)} | Videos: {total_unique} | Escenas: {total_scenes}")


if __name__ == "__main__":
    main()
