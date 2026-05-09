#!/usr/bin/env python3
"""Genera analysis.html — informe visual interactivo a partir de video_analyses.json + ads_raw.json.
Uso: python3 scripts/build_html.py <carpeta_competidor>
HTML autocontenido (un solo archivo). Los videos se referencian relativos a videos/<id>.mp4.
"""
import sys, json, html
from pathlib import Path
from collections import Counter

AUD_META = {
    "cold":         {"emoji": "🧊", "label": "FRÍO (TOFU)",          "color": "#3b82f6", "bg": "rgba(59,130,246,.15)"},
    "warm":         {"emoji": "🌡️", "label": "TIBIO (MOFU)",         "color": "#f59e0b", "bg": "rgba(245,158,11,.15)"},
    "retargeting":  {"emoji": "🔥", "label": "RETARGETING (BOFU)",   "color": "#ef4444", "bg": "rgba(239,68,68,.15)"},
}

PURPOSE_COLORS = {
    "hook": "#a855f7", "pain": "#ef4444", "solución": "#3b82f6", "solucion": "#3b82f6",
    "demo": "#10b981", "oferta": "#f59e0b", "objeción": "#eab308", "objecion": "#eab308",
    "cta": "#ec4899", "social proof": "#8b5cf6", "fomo": "#ef4444",
}

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#0a0a0b; --bg2:#13131a; --bg3:#1c1c25; --border:#2a2a35;
  --txt:#e8e8ec; --txt2:#9b9ba5; --txt3:#6b6b75;
  --accent:#a78bfa; --accent2:#22d3ee;
}
html,body{background:var(--bg);color:var(--txt);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;line-height:1.55;font-size:15px}
.container{max-width:1180px;margin:0 auto;padding:32px 24px 80px}
header{padding:48px 0 32px;border-bottom:1px solid var(--border);margin-bottom:40px}
h1{font-size:42px;font-weight:800;letter-spacing:-.02em;margin-bottom:8px;background:linear-gradient(135deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
h2{font-size:28px;margin:48px 0 20px;font-weight:700;letter-spacing:-.01em}
h3{font-size:20px;margin:24px 0 12px;font-weight:600}
.sub{color:var(--txt2);font-size:15px}
.sub a{color:var(--accent2);text-decoration:none}
.sub a:hover{text-decoration:underline}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px;margin:28px 0}
.kpi{background:var(--bg2);border:1px solid var(--border);border-radius:14px;padding:20px}
.kpi-label{color:var(--txt2);font-size:12px;text-transform:uppercase;letter-spacing:.08em;margin-bottom:8px;font-weight:600}
.kpi-value{font-size:28px;font-weight:700;letter-spacing:-.02em}
.kpi-value.small{font-size:18px}
.aud-bar{display:flex;height:42px;border-radius:10px;overflow:hidden;margin:12px 0 28px;border:1px solid var(--border)}
.aud-segment{display:flex;align-items:center;justify-content:center;font-weight:600;font-size:13px;color:#fff;text-shadow:0 1px 2px rgba(0,0,0,.3)}
.video-card{background:var(--bg2);border:1px solid var(--border);border-radius:18px;overflow:hidden;margin-bottom:28px}
.video-header{padding:24px 28px;border-bottom:1px solid var(--border)}
.vc-title-row{display:flex;align-items:flex-start;justify-content:space-between;gap:16px;flex-wrap:wrap}
.vc-title{font-size:22px;font-weight:700;letter-spacing:-.01em}
.vc-num{color:var(--txt3);font-weight:500;margin-right:8px}
.badges{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}
.badge{display:inline-flex;align-items:center;gap:6px;padding:5px 12px;border-radius:999px;font-size:12px;font-weight:600;border:1px solid}
.badge-aud{}
.badge-price{background:rgba(34,197,94,.15);border-color:#22c55e;color:#22c55e}
.badge-tone{background:var(--bg3);border-color:var(--border);color:var(--txt2)}
.video-body{display:grid;grid-template-columns:minmax(280px,420px) 1fr;gap:0}
@media(max-width:900px){.video-body{grid-template-columns:1fr}}
.video-player{background:#000;padding:20px;display:flex;align-items:flex-start;justify-content:center;border-right:1px solid var(--border)}
@media(max-width:900px){.video-player{border-right:none;border-bottom:1px solid var(--border)}}
video{width:100%;max-width:380px;border-radius:10px;display:block;background:#000}
.video-info{padding:24px 28px}
.section-label{color:var(--txt3);font-size:11px;text-transform:uppercase;letter-spacing:.1em;font-weight:700;margin-bottom:8px}
.hook-box{background:var(--bg3);border-left:3px solid var(--accent);padding:14px 16px;border-radius:8px;margin-bottom:18px;font-size:14px;color:var(--txt)}
.aud-reasoning{background:var(--bg3);border-radius:10px;padding:14px;margin:12px 0;font-size:13px;color:var(--txt2);line-height:1.6}
.signals{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}
.signal-chip{font-size:11px;padding:3px 9px;border-radius:6px;background:var(--bg);border:1px solid var(--border);color:var(--txt2);font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
details{margin-top:16px;border:1px solid var(--border);border-radius:10px;overflow:hidden}
details[open]{background:var(--bg)}
summary{padding:12px 16px;cursor:pointer;font-weight:600;font-size:14px;color:var(--txt);background:var(--bg3);user-select:none;list-style:none}
summary::-webkit-details-marker{display:none}
summary::before{content:"▶";display:inline-block;margin-right:8px;font-size:9px;transition:transform .15s;color:var(--txt3)}
details[open] summary::before{transform:rotate(90deg)}
.transcript{padding:16px 20px;font-size:14px;color:var(--txt);background:var(--bg);border-top:1px solid var(--border);line-height:1.7}
.transcript em{color:var(--txt2);font-style:italic}
.scenes{padding:8px;background:var(--bg)}
.scene{display:grid;grid-template-columns:90px 100px 1fr;gap:14px;padding:14px;border-radius:10px;margin:6px 0;background:var(--bg2);border:1px solid var(--border)}
@media(max-width:700px){.scene{grid-template-columns:1fr}}
.scene-time{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:13px;color:var(--accent2);font-weight:600;align-self:start;padding-top:2px}
.scene-purpose{font-size:11px;text-transform:uppercase;letter-spacing:.05em;font-weight:700;align-self:start;padding:3px 8px;border-radius:6px;color:#fff;text-align:center}
.scene-content{display:flex;flex-direction:column;gap:8px}
.scene-row{font-size:13.5px;line-height:1.55}
.scene-row .label{color:var(--txt3);font-size:11px;text-transform:uppercase;letter-spacing:.05em;font-weight:600;margin-right:6px}
.scene-row.visual{color:var(--txt)}
.scene-row.audio{color:var(--accent);font-style:italic}
.scene-row.audio-es{color:#67e8f9;font-style:italic}
.scene-row.text{color:var(--txt2);font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12.5px}
.shot-type{display:inline-block;font-size:11px;color:var(--txt3);font-style:normal;margin-left:6px;padding:1px 6px;background:var(--bg3);border-radius:4px}
.toc{position:sticky;top:24px;background:var(--bg2);border:1px solid var(--border);border-radius:14px;padding:18px;margin-bottom:24px;max-height:80vh;overflow-y:auto}
.toc h4{font-size:12px;text-transform:uppercase;letter-spacing:.1em;color:var(--txt3);margin-bottom:10px;font-weight:700}
.toc-item{display:flex;gap:8px;padding:6px 8px;border-radius:6px;font-size:13px;color:var(--txt2);text-decoration:none;cursor:pointer;align-items:center}
.toc-item:hover{background:var(--bg3);color:var(--txt)}
.toc-num{color:var(--txt3);font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:11px;flex-shrink:0;width:20px}
.layout{display:grid;grid-template-columns:240px 1fr;gap:32px;align-items:start}
@media(max-width:1000px){.layout{grid-template-columns:1fr}.toc{position:relative;top:0;max-height:none}}
.bar-chart{display:flex;flex-direction:column;gap:6px;margin:16px 0}
.bar-row{display:grid;grid-template-columns:140px 1fr 60px;gap:10px;align-items:center;font-size:13px}
.bar-track{height:24px;background:var(--bg3);border-radius:6px;overflow:hidden}
.bar-fill{height:100%;background:linear-gradient(90deg,var(--accent),var(--accent2));border-radius:6px;display:flex;align-items:center;justify-content:flex-end;padding-right:8px;color:#fff;font-weight:600;font-size:11px;min-width:24px}
.bar-label{color:var(--txt2);text-transform:capitalize}
.bar-count{color:var(--txt3);text-align:right;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12px}
footer{margin-top:60px;padding-top:32px;border-top:1px solid var(--border);color:var(--txt3);font-size:13px;text-align:center}
.tag-row{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0}
.tag{font-size:11px;padding:3px 8px;background:var(--bg3);border:1px solid var(--border);border-radius:5px;color:var(--txt2)}
"""


def esc(s):
    return html.escape(str(s) if s is not None else "")


def aud_badge(aud):
    t = aud.get("audience_temperature") if aud else None
    if not t or t not in AUD_META:
        return ""
    m = AUD_META[t]
    conf = aud.get("confidence", "?")
    return f'<span class="badge badge-aud" style="background:{m["bg"]};border-color:{m["color"]};color:{m["color"]}">{m["emoji"]} {m["label"]} · {esc(conf)}</span>'


def purpose_pill(purpose):
    p = (purpose or "").strip().lower()
    color = PURPOSE_COLORS.get(p.split("/")[0].strip(), "#64748b")
    return f'<div class="scene-purpose" style="background:{color}">{esc(purpose or "—")}</div>'


def scene_html(s):
    visual = esc(s.get("visual", ""))
    audio = esc(s.get("audio_dialogue", ""))
    audio_es = esc(s.get("audio_dialogue_es", ""))
    text = esc(s.get("on_screen_text", ""))
    shot = esc(s.get("shot_type", ""))
    ts = f'{esc(s.get("timestamp_start","?"))}–{esc(s.get("timestamp_end","?"))}'
    rows = [f'<div class="scene-row visual"><span class="label">VISUAL</span>{visual}{f"<span class=shot-type>{shot}</span>" if shot else ""}</div>']
    if audio:
        rows.append(f'<div class="scene-row audio"><span class="label">AUDIO</span>“{audio}”</div>')
    if audio_es:
        rows.append(f'<div class="scene-row audio-es"><span class="label">AUDIO ES</span>“{audio_es}”</div>')
    if text:
        rows.append(f'<div class="scene-row text"><span class="label">TEXTO</span>{text}</div>')
    return f'''<div class="scene">
      <div class="scene-time">{ts}</div>
      {purpose_pill(s.get("purpose"))}
      <div class="scene-content">{"".join(rows)}</div>
    </div>'''


def aud_bar(aud_counts, total):
    if not total:
        return ""
    parts = []
    for k in ["cold", "warm", "retargeting"]:
        n = aud_counts.get(k, 0)
        if n == 0:
            continue
        pct = n * 100 / total
        m = AUD_META[k]
        parts.append(f'<div class="aud-segment" style="background:{m["color"]};width:{pct}%;">{m["emoji"]} {m["label"]}: {n} ({pct:.0f}%)</div>')
    return f'<div class="aud-bar">{"".join(parts)}</div>' if parts else ""


def bar_chart(counter, top=8):
    if not counter:
        return ""
    mx = max(counter.values())
    rows = []
    for k, n in counter.most_common(top):
        pct = n * 100 / mx
        rows.append(f'''<div class="bar-row">
          <div class="bar-label">{esc(k)}</div>
          <div class="bar-track"><div class="bar-fill" style="width:{pct}%">{n}</div></div>
          <div class="bar-count">{pct:.0f}%</div>
        </div>''')
    return f'<div class="bar-chart">{"".join(rows)}</div>'


def build(folder: Path):
    raw = json.load(open(folder / "ads_raw.json"))
    vids = json.load(open(folder / "video_analyses.json"))
    page_name = (raw[0].get("snapshot") or {}).get("pageName") or folder.name

    formats = Counter((ad.get("snapshot") or {}).get("displayFormat") or "?" for ad in raw)
    langs = Counter(v["analysis"].get("detected_language") or "?" for v in vids)
    prices = Counter(v["analysis"].get("price_mentioned") for v in vids if v["analysis"].get("price_mentioned"))
    aud_counts = Counter()
    purposes = Counter()
    tones = Counter()
    total_scenes = 0
    for v in vids:
        a = v["analysis"]
        aud = (a.get("audience") or {}).get("audience_temperature")
        if aud:
            aud_counts[aud] += 1
        for s in a.get("scenes_breakdown") or []:
            total_scenes += 1
            p = (s.get("purpose") or "").strip().lower()
            if p:
                purposes[p] += 1
        t = (a.get("tone") or "").strip()
        if t:
            tones[t] += 1

    # Order: long-runners with price first, then everything else
    vids_sorted = sorted(vids, key=lambda v: (
        0 if v["analysis"].get("price_mentioned") else 1,
        -(v["analysis"].get("audience", {}) or {}).get("confidence", "?").count("h"),
    ))

    # TOC
    toc_items = []
    for i, v in enumerate(vids_sorted, 1):
        title = v.get("title") or "(sin título)"
        toc_items.append(f'<a class="toc-item" href="#vid-{i}"><span class="toc-num">{i:02d}</span>{esc(title[:38])}</a>')

    # Video cards
    cards = []
    for i, entry in enumerate(vids_sorted, 1):
        a = entry["analysis"]
        title = entry.get("title") or "(sin título)"
        ad_id = entry["ad_id"]
        dup = entry.get("duplicate_of_ad_ids", [ad_id])
        video_path = f"videos/{ad_id}.mp4"

        badges = []
        if a.get("audience"):
            badges.append(aud_badge(a["audience"]))
        if a.get("price_mentioned"):
            badges.append(f'<span class="badge badge-price">💰 {esc(a["price_mentioned"])}</span>')
        if a.get("tone"):
            badges.append(f'<span class="badge badge-tone">🎭 {esc(a["tone"])}</span>')

        aud = a.get("audience") or {}
        aud_block = ""
        if aud.get("reasoning"):
            signals = aud.get("signals_detected") or []
            sig_html = "".join(f'<span class="signal-chip">{esc(s)}</span>' for s in signals)
            aud_block = f'''<div class="aud-reasoning">
              <div class="section-label">Por qué se clasificó así</div>
              {esc(aud["reasoning"])}
              {f"<div class=signals>{sig_html}</div>" if signals else ""}
            </div>'''

        # Transcripts
        trans_orig = esc(a.get("transcript_original", ""))
        trans_es = esc(a.get("transcript_es", "") or "")
        trans_block = f'''<details>
          <summary>📝 Transcripción completa ({esc(a.get("detected_language","?"))})</summary>
          <div class="transcript"><em>"{trans_orig}"</em></div>
        </details>'''
        if trans_es:
            trans_block += f'''<details>
              <summary>🇪🇸 Traducción al español</summary>
              <div class="transcript"><em>"{trans_es}"</em></div>
            </details>'''

        # Scenes
        scenes = a.get("scenes_breakdown") or []
        scenes_html = "".join(scene_html(s) for s in scenes)
        scenes_block = f'''<details open>
          <summary>🎬 Desglose escena por escena ({len(scenes)})</summary>
          <div class="scenes">{scenes_html}</div>
        </details>''' if scenes else ""

        # Value props / social proof / CTA
        meta_rows = []
        if a.get("hook_first_3s"):
            meta_rows.append(f'<div class="hook-box"><div class="section-label">Hook (primeros 3s)</div>{esc(a["hook_first_3s"])}</div>')
        if a.get("cta_verbal"):
            meta_rows.append(f'<div style="margin-bottom:10px"><span class="section-label" style="display:inline">CTA verbal</span> <em>"{esc(a["cta_verbal"])}"</em></div>')
        if a.get("social_proof_mentioned"):
            meta_rows.append(f'<div style="margin-bottom:10px"><span class="section-label" style="display:inline">Social proof</span> {esc(a["social_proof_mentioned"])}</div>')
        if a.get("value_props_dichas"):
            tags = "".join(f'<span class="tag">{esc(v)}</span>' for v in a["value_props_dichas"])
            meta_rows.append(f'<div><div class="section-label">Value props dichas</div><div class="tag-row">{tags}</div></div>')

        cards.append(f'''<div class="video-card" id="vid-{i}">
          <div class="video-header">
            <div class="vc-title-row">
              <div class="vc-title"><span class="vc-num">#{i:02d}</span>{esc(title)}</div>
            </div>
            <div class="badges">{"".join(badges)}</div>
            <div style="margin-top:10px;font-size:12px;color:var(--txt3)">Ad ID(s): <code style="font-family:ui-monospace,SFMono-Regular,Menlo,monospace">{esc(", ".join(dup))}</code></div>
          </div>
          <div class="video-body">
            <div class="video-player">
              <video controls preload="metadata" src="{video_path}"></video>
            </div>
            <div class="video-info">
              {"".join(meta_rows)}
              {aud_block}
              {trans_block}
              {scenes_block}
            </div>
          </div>
        </div>''')

    # KPIs
    kpis = [
        ("Ads activos", str(len(raw))),
        ("Creativos únicos", str(len(vids))),
        ("Escenas totales", str(total_scenes)),
        ("Idiomas", ", ".join(langs.keys()) or "—"),
    ]
    if prices:
        kpis.append(("Precios mencionados", " · ".join(f"{p} ({n})" for p, n in prices.most_common())))

    kpi_html = "".join(
        f'<div class="kpi"><div class="kpi-label">{esc(l)}</div><div class="kpi-value{" small" if len(v)>16 else ""}">{esc(v)}</div></div>'
        for l, v in kpis
    )

    # Format counts
    fmt_html = "".join(
        f'<div class="kpi"><div class="kpi-label">{esc(k)}</div><div class="kpi-value">{n}</div></div>'
        for k, n in formats.most_common()
    )

    out = f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Análisis de ads — {esc(page_name)}</title>
<style>{CSS}</style>
</head>
<body>
<div class="container">
  <header>
    <h1>Análisis de ads — {esc(page_name)}</h1>
    <p class="sub">Página: <a href="https://www.facebook.com/{esc(folder.name)}" target="_blank">facebook.com/{esc(folder.name)}</a> · Generado con Apify + Gemini 3 Flash</p>
  </header>

  <section>
    <h2>📊 Resumen</h2>
    <div class="kpis">{kpi_html}</div>

    <h3>Etapa del funnel</h3>
    {aud_bar(aud_counts, len(vids))}

    <h3>Distribución por formato</h3>
    <div class="kpis">{fmt_html}</div>

    <h3>Roles narrativos detectados ({total_scenes} escenas)</h3>
    {bar_chart(purposes, top=10)}
  </section>

  <div class="layout">
    <aside class="toc">
      <h4>🎬 Creativos ({len(vids)})</h4>
      {"".join(toc_items)}
    </aside>
    <main>
      <h2>🎞️ Análisis por creativo</h2>
      {"".join(cards)}
    </main>
  </div>

  <footer>
    Generado automáticamente por <a href="https://github.com/dantedelao89/analisis-competencia-ads" style="color:var(--accent2)">competitive-ads-extractor</a> · Apify scraping + Gemini 3 Flash Preview · {len(vids)} videos analizados
  </footer>
</div>
</body>
</html>'''

    out_path = folder / "analysis.html"
    out_path.write_text(out, encoding="utf-8")
    print(f"Wrote {out_path} ({len(out)/1024:.1f} KB)")


if __name__ == "__main__":
    folder = Path(sys.argv[1] if len(sys.argv) > 1 else "competitor-ads/aivideoskool")
    build(folder)
