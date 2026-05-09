#!/usr/bin/env python3
"""Genera analysis.html con UI master-detail (sidebar + detail pane).
Uso: python3 scripts/build_html.py <carpeta_competidor>
"""
import sys, json, html
from pathlib import Path
from collections import Counter

AUD_META = {
    "cold":         {"emoji": "🧊", "label": "FRÍO",        "full": "FRÍO (TOFU)",        "color": "#3b82f6"},
    "warm":         {"emoji": "🌡️", "label": "TIBIO",       "full": "TIBIO (MOFU)",       "color": "#f59e0b"},
    "retargeting":  {"emoji": "🔥", "label": "RETARGETING", "full": "RETARGETING (BOFU)", "color": "#ef4444"},
}

PURPOSE_COLORS = {
    "hook": "#a855f7", "pain": "#ef4444", "solución": "#3b82f6", "solucion": "#3b82f6",
    "demo": "#10b981", "oferta": "#f59e0b", "objeción": "#eab308", "objecion": "#eab308",
    "cta": "#ec4899", "social proof": "#8b5cf6", "fomo": "#ef4444",
    "transición": "#64748b", "transicion": "#64748b", "target": "#06b6d4",
    "aspiracional": "#8b5cf6", "introducción": "#a855f7",
    "value prop": "#3b82f6", "promesa": "#3b82f6", "urgencia": "#ef4444",
    "revelación": "#a855f7", "educativo": "#3b82f6",
}


def esc(s):
    return html.escape(str(s) if s is not None else "")


def purpose_color(p):
    return PURPOSE_COLORS.get((p or "").strip().lower().split("/")[0].strip(), "#64748b")


def build(folder: Path):
    raw = json.load(open(folder / "ads_raw.json"))
    vids = json.load(open(folder / "video_analyses.json"))
    page_name = (raw[0].get("snapshot") or {}).get("pageName") or folder.name

    # Aggregates
    formats = Counter((ad.get("snapshot") or {}).get("displayFormat") or "?" for ad in raw)
    aud_counts = Counter()
    purposes = Counter()
    total_scenes = 0
    prices = Counter()
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
        if a.get("price_mentioned"):
            prices[a["price_mentioned"]] += 1

    # Order: price-mentioned first, then high-confidence
    vids_sorted = sorted(vids, key=lambda v: (
        0 if v["analysis"].get("price_mentioned") else 1,
        v.get("title", "z"),
    ))

    # Build embedded JSON for client-side rendering
    payload = {
        "videos": [],
        "meta": {
            "page_name": page_name,
            "folder": folder.name,
            "total_ads": len(raw),
            "total_unique": len(vids),
            "total_scenes": total_scenes,
            "formats": dict(formats),
            "audiences": dict(aud_counts),
            "prices": dict(prices),
            "purposes": dict(purposes.most_common()),
        },
    }
    for entry in vids_sorted:
        a = entry["analysis"]
        payload["videos"].append({
            "ad_id": entry["ad_id"],
            "title": entry.get("title") or "(sin título)",
            "duplicate_of_ad_ids": entry.get("duplicate_of_ad_ids", [entry["ad_id"]]),
            "video_path": f"videos/{entry['ad_id']}.mp4",
            "language": a.get("detected_language"),
            "tone": a.get("tone"),
            "hook": a.get("hook_first_3s"),
            "transcript_orig": a.get("transcript_original", ""),
            "transcript_es": a.get("transcript_es", ""),
            "cta_verbal": a.get("cta_verbal"),
            "price": a.get("price_mentioned"),
            "social_proof": a.get("social_proof_mentioned"),
            "value_props": a.get("value_props_dichas") or [],
            "key_visuals": a.get("key_visual_elements") or [],
            "audience": a.get("audience") or {},
            "scenes": a.get("scenes_breakdown") or [],
        })

    # CSS
    css = """
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#0a0a0b; --bg2:#13131a; --bg3:#1c1c25; --bg4:#252531;
  --border:#2a2a35; --border2:#3a3a48;
  --txt:#e8e8ec; --txt2:#9b9ba5; --txt3:#6b6b75;
  --accent:#a78bfa; --accent2:#22d3ee; --accent3:#34d399;
  --sidebar-w:340px; --header-h:auto;
}
html,body{background:var(--bg);color:var(--txt);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,sans-serif;font-size:14px;line-height:1.5;overflow:hidden;height:100vh}

/* TOP HEADER */
.top{position:sticky;top:0;background:var(--bg);border-bottom:1px solid var(--border);z-index:50;padding:14px 24px;display:flex;align-items:center;gap:24px;flex-wrap:wrap}
.brand{font-size:18px;font-weight:700;letter-spacing:-.01em;background:linear-gradient(135deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;flex-shrink:0}
.brand .small{font-size:11px;color:var(--txt3);font-weight:500;-webkit-text-fill-color:var(--txt3);margin-left:6px}
.kpis-strip{display:flex;gap:18px;flex-wrap:wrap;flex:1}
.kpi-mini{display:flex;flex-direction:column;gap:1px}
.kpi-mini .l{font-size:10px;color:var(--txt3);text-transform:uppercase;letter-spacing:.08em;font-weight:600}
.kpi-mini .v{font-size:16px;font-weight:700;color:var(--txt)}
.aud-pills{display:flex;gap:6px;flex-wrap:wrap}
.aud-pill{font-size:11px;padding:3px 10px;border-radius:999px;font-weight:600;border:1px solid}

/* MAIN LAYOUT */
.app{display:grid;grid-template-columns:var(--sidebar-w) 1fr;height:calc(100vh - 65px);}
@media(max-width:900px){.app{grid-template-columns:1fr;height:auto;overflow:auto}html,body{overflow:auto}}

/* SIDEBAR */
.sidebar{background:var(--bg2);border-right:1px solid var(--border);overflow-y:auto;display:flex;flex-direction:column}
.search{padding:12px;border-bottom:1px solid var(--border);position:sticky;top:0;background:var(--bg2);z-index:5}
.search input{width:100%;background:var(--bg);border:1px solid var(--border);border-radius:8px;padding:8px 12px;color:var(--txt);font-size:13px;outline:none}
.search input:focus{border-color:var(--accent)}
.filters{display:flex;gap:6px;flex-wrap:wrap;margin-top:8px}
.filter-btn{font-size:11px;padding:4px 10px;border-radius:999px;background:var(--bg3);border:1px solid var(--border);color:var(--txt2);cursor:pointer;transition:all .15s}
.filter-btn:hover{border-color:var(--accent)}
.filter-btn.active{background:var(--accent);border-color:var(--accent);color:#000;font-weight:600}
.video-list{flex:1;padding:6px}
.vid-item{padding:12px;border-radius:10px;cursor:pointer;display:flex;flex-direction:column;gap:6px;transition:background .12s;border:1px solid transparent}
.vid-item:hover{background:var(--bg3)}
.vid-item.active{background:var(--bg3);border-color:var(--accent)}
.vid-item .num{font-size:10px;color:var(--txt3);font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-weight:600}
.vid-item .title{font-size:13px;font-weight:600;color:var(--txt);line-height:1.3;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.vid-item .meta{display:flex;gap:5px;flex-wrap:wrap;align-items:center}
.tag-mini{font-size:10px;padding:2px 7px;border-radius:5px;font-weight:600;line-height:1.4}

/* DETAIL */
.detail{overflow-y:auto;background:var(--bg)}
.detail-empty{display:flex;align-items:center;justify-content:center;height:100%;color:var(--txt3);font-size:14px;padding:40px;text-align:center}
.detail-content{padding:0;max-width:1200px;margin:0 auto}

/* DETAIL HEADER */
.dh{padding:24px 32px 18px;border-bottom:1px solid var(--border)}
.dh h2{font-size:24px;font-weight:700;letter-spacing:-.01em;margin-bottom:10px}
.dh .ids{font-size:11px;color:var(--txt3);font-family:ui-monospace,SFMono-Regular,Menlo,monospace;margin-top:6px}
.dh-badges{display:flex;gap:8px;flex-wrap:wrap}
.badge{display:inline-flex;align-items:center;gap:5px;padding:4px 11px;border-radius:999px;font-size:12px;font-weight:600;border:1px solid}
.badge-aud{}
.badge-price{background:rgba(34,197,94,.15);border-color:#22c55e;color:#22c55e}
.badge-tone{background:var(--bg3);border-color:var(--border);color:var(--txt2)}
.badge-lang{background:var(--bg3);border-color:var(--border);color:var(--txt2);font-family:ui-monospace,SFMono-Regular,Menlo,monospace}

/* DETAIL BODY: TWO COLUMN */
.db{display:grid;grid-template-columns:380px 1fr;gap:24px;padding:24px 32px}
@media(max-width:1100px){.db{grid-template-columns:1fr}}
.dvideo{position:sticky;top:24px;align-self:start}
@media(max-width:1100px){.dvideo{position:relative;top:0}}
.dvideo video{width:100%;border-radius:12px;background:#000;display:block;border:1px solid var(--border)}
.dmeta{display:flex;flex-direction:column;gap:14px;margin-top:14px}
.meta-card{background:var(--bg2);border:1px solid var(--border);border-radius:10px;padding:12px 14px}
.meta-card .l{font-size:10px;color:var(--txt3);text-transform:uppercase;letter-spacing:.08em;font-weight:700;margin-bottom:6px}
.meta-card .v{font-size:13px;color:var(--txt);line-height:1.5}
.meta-card .v em{color:var(--accent2);font-style:italic}

.dinfo{display:flex;flex-direction:column;gap:18px}

/* TABS */
.tabs{display:flex;border-bottom:1px solid var(--border);gap:0}
.tab{padding:10px 16px;cursor:pointer;font-size:13px;font-weight:600;color:var(--txt2);border-bottom:2px solid transparent;transition:all .15s}
.tab:hover{color:var(--txt)}
.tab.active{color:var(--accent);border-bottom-color:var(--accent)}
.tab-count{display:inline-block;font-size:11px;color:var(--txt3);margin-left:6px;padding:1px 6px;background:var(--bg3);border-radius:4px}
.tab.active .tab-count{background:rgba(167,139,250,.2);color:var(--accent)}
.tab-panel{display:none;padding:18px 0}
.tab-panel.active{display:block}

/* OVERVIEW TAB */
.hook-card{background:linear-gradient(135deg,rgba(167,139,250,.08),rgba(34,211,238,.05));border:1px solid rgba(167,139,250,.3);border-radius:12px;padding:16px}
.hook-card .l{font-size:10px;color:var(--accent);text-transform:uppercase;letter-spacing:.1em;font-weight:700;margin-bottom:6px}
.hook-card .v{font-size:14px;color:var(--txt);line-height:1.55}

.aud-card{background:var(--bg2);border:1px solid var(--border);border-radius:12px;padding:16px;margin-top:14px}
.aud-card .l{font-size:10px;color:var(--txt3);text-transform:uppercase;letter-spacing:.08em;font-weight:700;margin-bottom:8px}
.aud-card .reasoning{font-size:13px;color:var(--txt);line-height:1.65;margin-bottom:10px}
.signals{display:flex;flex-wrap:wrap;gap:5px;margin-top:6px}
.signal-chip{font-size:11px;padding:3px 9px;border-radius:6px;background:var(--bg3);border:1px solid var(--border);color:var(--txt2);font-family:ui-monospace,SFMono-Regular,Menlo,monospace}

.tags-card{margin-top:14px}
.tags-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}
@media(max-width:600px){.tags-grid{grid-template-columns:1fr}}
.tag-list{display:flex;flex-wrap:wrap;gap:5px;margin-top:6px}
.tag{font-size:11.5px;padding:4px 9px;background:var(--bg3);border:1px solid var(--border);border-radius:5px;color:var(--txt2)}

/* SCENES TAB */
.scenes-timeline{display:flex;height:36px;border-radius:8px;overflow:hidden;margin-bottom:18px;border:1px solid var(--border);background:var(--bg2)}
.timeline-seg{cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:600;color:#fff;text-shadow:0 1px 2px rgba(0,0,0,.4);transition:filter .15s;border-right:1px solid rgba(0,0,0,.2)}
.timeline-seg:hover{filter:brightness(1.2)}
.timeline-seg:last-child{border-right:none}

.scene{display:grid;grid-template-columns:auto auto 1fr;gap:14px;padding:14px;border-radius:10px;margin:8px 0;background:var(--bg2);border:1px solid var(--border);cursor:default;transition:border-color .15s}
.scene:hover{border-color:var(--border2)}
.scene.highlight{border-color:var(--accent);box-shadow:0 0 0 1px var(--accent)}
.scene-time{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12px;color:var(--accent2);font-weight:600;align-self:start;padding-top:3px;white-space:nowrap}
.scene-purpose{font-size:10px;text-transform:uppercase;letter-spacing:.05em;font-weight:700;align-self:start;padding:3px 8px;border-radius:5px;color:#fff;text-align:center;white-space:nowrap}
.scene-content{display:flex;flex-direction:column;gap:6px;min-width:0}
.scene-row{font-size:13px;line-height:1.5;word-wrap:break-word}
.scene-row .label{color:var(--txt3);font-size:10px;text-transform:uppercase;letter-spacing:.05em;font-weight:700;margin-right:6px;display:inline-block;width:54px}
.scene-row.visual{color:var(--txt)}
.scene-row.audio{color:#c4b5fd;font-style:italic}
.scene-row.audio-es{color:#67e8f9;font-style:italic}
.scene-row.text{color:var(--txt2);font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:11.5px}
.shot-type{display:inline-block;font-size:10px;color:var(--txt3);font-style:normal;margin-left:6px;padding:1px 5px;background:var(--bg3);border-radius:4px}

/* TRANSCRIPT TAB */
.transcript-block{background:var(--bg2);border:1px solid var(--border);border-radius:10px;padding:18px;margin-bottom:14px}
.transcript-block .l{font-size:10px;color:var(--txt3);text-transform:uppercase;letter-spacing:.08em;font-weight:700;margin-bottom:10px;display:flex;align-items:center;justify-content:space-between}
.transcript-block .v{font-size:14px;color:var(--txt);line-height:1.7;font-style:italic}

/* OVERVIEW (when no video selected) */
.overview-pane{padding:32px}
.ov-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;margin-bottom:24px}
.ov-card{background:var(--bg2);border:1px solid var(--border);border-radius:14px;padding:18px}
.ov-card .l{font-size:11px;color:var(--txt3);text-transform:uppercase;letter-spacing:.08em;font-weight:600;margin-bottom:8px}
.ov-card .v{font-size:24px;font-weight:700;letter-spacing:-.02em}
.ov-card .v.small{font-size:14px;font-weight:600}
.ov-bar{display:flex;height:38px;border-radius:10px;overflow:hidden;margin:14px 0;border:1px solid var(--border)}
.ov-bar-seg{display:flex;align-items:center;justify-content:center;font-weight:600;font-size:12px;color:#fff;text-shadow:0 1px 2px rgba(0,0,0,.3)}

.bar-chart{display:flex;flex-direction:column;gap:6px;margin:14px 0}
.bar-row{display:grid;grid-template-columns:140px 1fr 60px;gap:10px;align-items:center;font-size:12.5px}
.bar-track{height:22px;background:var(--bg3);border-radius:6px;overflow:hidden}
.bar-fill{height:100%;border-radius:6px;display:flex;align-items:center;justify-content:flex-end;padding-right:8px;color:#fff;font-weight:600;font-size:11px;min-width:24px}
.bar-label{color:var(--txt2);text-transform:capitalize}
.bar-count{color:var(--txt3);text-align:right;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:11px}

h3.section-h{font-size:13px;color:var(--txt2);margin:24px 0 10px;font-weight:600;text-transform:uppercase;letter-spacing:.05em}

/* SCROLLBARS */
.sidebar::-webkit-scrollbar,.detail::-webkit-scrollbar{width:8px}
.sidebar::-webkit-scrollbar-track,.detail::-webkit-scrollbar-track{background:transparent}
.sidebar::-webkit-scrollbar-thumb,.detail::-webkit-scrollbar-thumb{background:var(--border);border-radius:4px}
.sidebar::-webkit-scrollbar-thumb:hover,.detail::-webkit-scrollbar-thumb:hover{background:var(--border2)}
"""

    # JavaScript (client-side rendering)
    js = """
const DATA = window.__DATA__;
const AUD_META = """ + json.dumps({k: v for k, v in AUD_META.items()}) + """;
const PURPOSE_COLORS = """ + json.dumps(PURPOSE_COLORS) + """;

const $ = (s, el=document) => el.querySelector(s);
const $$ = (s, el=document) => [...el.querySelectorAll(s)];
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const purposeColor = p => PURPOSE_COLORS[(p||"").trim().toLowerCase().split("/")[0].trim()] || "#64748b";

let state = { selected: null, search: "", filter: "all" };

function renderSidebar() {
  const list = $("#video-list");
  const q = state.search.toLowerCase();
  const filter = state.filter;
  const items = DATA.videos.map((v, i) => ({v, i})).filter(({v}) => {
    if (filter !== "all" && v.audience?.audience_temperature !== filter) return false;
    if (q && !((v.title + " " + v.transcript_orig + " " + (v.transcript_es||"")).toLowerCase().includes(q))) return false;
    return true;
  });
  list.innerHTML = items.length === 0
    ? '<div style="padding:20px;text-align:center;color:var(--txt3);font-size:13px">Sin resultados</div>'
    : items.map(({v, i}) => {
      const aud = v.audience?.audience_temperature;
      const audMeta = aud ? AUD_META[aud] : null;
      const audTag = audMeta ? `<span class="tag-mini" style="background:${audMeta.color}20;border:1px solid ${audMeta.color}40;color:${audMeta.color}">${audMeta.emoji} ${audMeta.label}</span>` : "";
      const priceTag = v.price ? `<span class="tag-mini" style="background:rgba(34,197,94,.15);border:1px solid #22c55e40;color:#22c55e">💰 ${esc(v.price)}</span>` : "";
      return `<div class="vid-item ${state.selected === i ? "active" : ""}" data-i="${i}">
        <div class="num">#${String(i+1).padStart(2,"0")}</div>
        <div class="title">${esc(v.title)}</div>
        <div class="meta">${audTag}${priceTag}</div>
      </div>`;
    }).join("");
  $$("#video-list .vid-item").forEach(el => el.addEventListener("click", () => selectVideo(parseInt(el.dataset.i))));
}

function selectVideo(i) {
  state.selected = i;
  history.replaceState(null, "", "#v" + i);
  renderSidebar();
  renderDetail();
}

function renderDetail() {
  const pane = $("#detail");
  if (state.selected === null) {
    pane.innerHTML = renderOverview();
    return;
  }
  const v = DATA.videos[state.selected];
  const aud = v.audience || {};
  const audMeta = AUD_META[aud.audience_temperature];
  const badges = [];
  if (audMeta) badges.push(`<span class="badge badge-aud" style="background:${audMeta.color}25;border-color:${audMeta.color};color:${audMeta.color}">${audMeta.emoji} ${audMeta.full} · ${esc(aud.confidence||"?")}</span>`);
  if (v.price) badges.push(`<span class="badge badge-price">💰 ${esc(v.price)}</span>`);
  if (v.tone) badges.push(`<span class="badge badge-tone">🎭 ${esc(v.tone)}</span>`);
  if (v.language) badges.push(`<span class="badge badge-lang">${esc(v.language).toUpperCase()}</span>`);

  pane.innerHTML = `
  <div class="detail-content">
    <div class="dh">
      <h2>#${String(state.selected+1).padStart(2,"0")} · ${esc(v.title)}</h2>
      <div class="dh-badges">${badges.join("")}</div>
      <div class="ids">Ad ID(s): ${esc((v.duplicate_of_ad_ids||[]).join(", "))}</div>
    </div>
    <div class="db">
      <div class="dvideo">
        <video controls preload="metadata" src="${esc(v.video_path)}"></video>
        <div class="dmeta">
          ${v.cta_verbal ? `<div class="meta-card"><div class="l">📢 CTA verbal</div><div class="v"><em>"${esc(v.cta_verbal)}"</em></div></div>` : ""}
          ${v.social_proof ? `<div class="meta-card"><div class="l">🏅 Social proof</div><div class="v">${esc(v.social_proof)}</div></div>` : ""}
        </div>
      </div>
      <div class="dinfo">
        <div class="tabs">
          <div class="tab active" data-tab="overview">Overview</div>
          <div class="tab" data-tab="scenes">Escenas <span class="tab-count">${(v.scenes||[]).length}</span></div>
          <div class="tab" data-tab="transcript">Transcripción</div>
        </div>
        <div class="tab-panel active" data-panel="overview">${renderOverviewTab(v, aud)}</div>
        <div class="tab-panel" data-panel="scenes">${renderScenesTab(v)}</div>
        <div class="tab-panel" data-panel="transcript">${renderTranscriptTab(v)}</div>
      </div>
    </div>
  </div>`;

  $$(".tab", pane).forEach(t => t.addEventListener("click", () => {
    $$(".tab", pane).forEach(x => x.classList.remove("active"));
    $$(".tab-panel", pane).forEach(x => x.classList.remove("active"));
    t.classList.add("active");
    $(`.tab-panel[data-panel="${t.dataset.tab}"]`, pane).classList.add("active");
  }));
}

function renderOverviewTab(v, aud) {
  const audMeta = AUD_META[aud?.audience_temperature];
  const signals = (aud?.signals_detected || []).map(s => `<span class="signal-chip">${esc(s)}</span>`).join("");
  const reasonBlock = aud?.reasoning ? `
    <div class="aud-card">
      <div class="l">${audMeta ? audMeta.emoji + " " + audMeta.full : "Audiencia"} · clasificación</div>
      <div class="reasoning">${esc(aud.reasoning)}</div>
      ${signals ? `<div class="l" style="margin-top:12px;margin-bottom:6px">Señales detectadas</div><div class="signals">${signals}</div>` : ""}
    </div>` : "";

  const valueProps = (v.value_props||[]).map(t => `<span class="tag">${esc(t)}</span>`).join("");
  const visuals = (v.key_visuals||[]).map(t => `<span class="tag">${esc(t)}</span>`).join("");
  const tagsBlock = (valueProps || visuals) ? `
    <div class="tags-card">
      <div class="tags-grid">
        ${valueProps ? `<div><div class="meta-card" style="padding:14px 16px"><div class="l">💡 Value props dichas</div><div class="tag-list">${valueProps}</div></div></div>` : ""}
        ${visuals ? `<div><div class="meta-card" style="padding:14px 16px"><div class="l">🎨 Elementos visuales clave</div><div class="tag-list">${visuals}</div></div></div>` : ""}
      </div>
    </div>` : "";

  return `
    ${v.hook ? `<div class="hook-card"><div class="l">⚡ Hook (primeros 3s)</div><div class="v">${esc(v.hook)}</div></div>` : ""}
    ${reasonBlock}
    ${tagsBlock}`;
}

function renderScenesTab(v) {
  const scenes = v.scenes || [];
  if (!scenes.length) return '<div style="color:var(--txt3);padding:20px;text-align:center">Sin escenas analizadas</div>';

  const total = scenes.length;
  const timeline = scenes.map((s, idx) => {
    const c = purposeColor(s.purpose);
    const pct = 100 / total;
    return `<div class="timeline-seg" data-idx="${idx}" style="background:${c};width:${pct}%" title="${esc(s.purpose||"")} (${esc(s.timestamp_start)})">${total <= 12 ? esc((s.purpose||"").slice(0,8)) : ""}</div>`;
  }).join("");

  const sceneRows = scenes.map((s, idx) => {
    const c = purposeColor(s.purpose);
    const audio = s.audio_dialogue ? `<div class="scene-row audio"><span class="label">AUDIO</span>"${esc(s.audio_dialogue)}"</div>` : "";
    const audioEs = s.audio_dialogue_es ? `<div class="scene-row audio-es"><span class="label">AUDIO ES</span>"${esc(s.audio_dialogue_es)}"</div>` : "";
    const text = s.on_screen_text ? `<div class="scene-row text"><span class="label">TEXTO</span>${esc(s.on_screen_text)}</div>` : "";
    const shot = s.shot_type ? `<span class="shot-type">${esc(s.shot_type)}</span>` : "";
    return `<div class="scene" data-idx="${idx}">
      <div class="scene-time">${esc(s.timestamp_start)}–${esc(s.timestamp_end)}</div>
      <div class="scene-purpose" style="background:${c}">${esc(s.purpose||"—")}</div>
      <div class="scene-content">
        <div class="scene-row visual"><span class="label">VISUAL</span>${esc(s.visual||"")}${shot}</div>
        ${audio}${audioEs}${text}
      </div>
    </div>`;
  }).join("");

  return `<div class="scenes-timeline" id="timeline">${timeline}</div>${sceneRows}`;
}

function renderTranscriptTab(v) {
  const orig = v.transcript_orig
    ? `<div class="transcript-block">
        <div class="l"><span>Original (${esc((v.language||"?").toUpperCase())})</span></div>
        <div class="v">"${esc(v.transcript_orig)}"</div>
      </div>` : "";
  const es = v.transcript_es
    ? `<div class="transcript-block">
        <div class="l"><span>🇪🇸 Traducción al español</span></div>
        <div class="v">"${esc(v.transcript_es)}"</div>
      </div>` : "";
  return orig + es || '<div style="color:var(--txt3);padding:20px;text-align:center">Sin transcripción</div>';
}

function renderOverview() {
  const m = DATA.meta;
  const totalAud = Object.values(m.audiences).reduce((a,b)=>a+b,0);
  const audBar = ["cold","warm","retargeting"].filter(k => m.audiences[k]).map(k => {
    const n = m.audiences[k]; const pct = n*100/totalAud;
    const aud = AUD_META[k];
    return `<div class="ov-bar-seg" style="background:${aud.color};width:${pct}%">${aud.emoji} ${aud.full}: ${n} (${pct.toFixed(0)}%)</div>`;
  }).join("");

  const purposes = m.purposes;
  const maxP = Math.max(...Object.values(purposes), 1);
  const purposeBars = Object.entries(purposes).slice(0,10).map(([k,n]) => {
    const pct = n*100/maxP;
    const c = purposeColor(k);
    return `<div class="bar-row">
      <div class="bar-label">${esc(k)}</div>
      <div class="bar-track"><div class="bar-fill" style="width:${pct}%;background:${c}">${n}</div></div>
      <div class="bar-count">${(n*100/m.total_scenes).toFixed(0)}%</div>
    </div>`;
  }).join("");

  return `<div class="overview-pane">
    <h2 style="font-size:24px;margin-bottom:6px">📊 Resumen del análisis</h2>
    <p style="color:var(--txt2);margin-bottom:24px;font-size:14px">Seleccioná un video del panel izquierdo para ver el análisis detallado.</p>

    <div class="ov-grid">
      <div class="ov-card"><div class="l">Ads activos</div><div class="v">${m.total_ads}</div></div>
      <div class="ov-card"><div class="l">Creativos únicos</div><div class="v">${m.total_unique}</div></div>
      <div class="ov-card"><div class="l">Escenas analizadas</div><div class="v">${m.total_scenes}</div></div>
      <div class="ov-card"><div class="l">Precios mencionados</div><div class="v small">${Object.entries(m.prices).map(([p,n])=>`${esc(p)} (${n})`).join(" · ")||"—"}</div></div>
    </div>

    <h3 class="section-h">Distribución por etapa del funnel</h3>
    <div class="ov-bar">${audBar}</div>

    <h3 class="section-h">Roles narrativos detectados (${m.total_scenes} escenas)</h3>
    <div class="bar-chart">${purposeBars}</div>

    <h3 class="section-h">Distribución por formato</h3>
    <div class="ov-grid">
      ${Object.entries(m.formats).map(([k,n])=>`<div class="ov-card"><div class="l">${esc(k)}</div><div class="v">${n}</div></div>`).join("")}
    </div>
  </div>`;
}

function setupFilters() {
  $("#search").addEventListener("input", e => { state.search = e.target.value; renderSidebar(); });
  $$(".filter-btn").forEach(b => b.addEventListener("click", () => {
    $$(".filter-btn").forEach(x => x.classList.remove("active"));
    b.classList.add("active");
    state.filter = b.dataset.filter;
    renderSidebar();
  }));
}

// Init
setupFilters();
renderSidebar();
const hash = location.hash.match(/^#v(\\d+)$/);
if (hash) selectVideo(parseInt(hash[1]));
else renderDetail();
"""

    # Filter buttons (only show audiences that exist)
    filter_btns = '<button class="filter-btn active" data-filter="all">Todos</button>'
    for k in ["cold", "warm", "retargeting"]:
        if k in aud_counts:
            m = AUD_META[k]
            filter_btns += f'<button class="filter-btn" data-filter="{k}" style="border-color:{m["color"]}40">{m["emoji"]} {m["label"]} ({aud_counts[k]})</button>'

    # Top header KPIs
    aud_pills = ""
    for k in ["cold", "warm", "retargeting"]:
        if k in aud_counts:
            m = AUD_META[k]
            aud_pills += f'<span class="aud-pill" style="background:{m["color"]}25;border-color:{m["color"]};color:{m["color"]}">{m["emoji"]} {aud_counts[k]}</span>'

    out = f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(page_name)} — análisis de ads</title>
<style>{css}</style>
</head>
<body>
<div class="top">
  <div class="brand">{esc(page_name)} <span class="small">facebook.com/{esc(folder.name)}</span></div>
  <div class="kpis-strip">
    <div class="kpi-mini"><span class="l">Ads activos</span><span class="v">{len(raw)}</span></div>
    <div class="kpi-mini"><span class="l">Creativos únicos</span><span class="v">{len(vids)}</span></div>
    <div class="kpi-mini"><span class="l">Escenas</span><span class="v">{total_scenes}</span></div>
    <div class="kpi-mini"><span class="l">Funnel</span><span class="aud-pills">{aud_pills}</span></div>
  </div>
</div>
<div class="app">
  <aside class="sidebar">
    <div class="search">
      <input id="search" placeholder="🔍 Buscar título, copy, transcripción..." />
      <div class="filters">{filter_btns}</div>
    </div>
    <div class="video-list" id="video-list"></div>
  </aside>
  <main class="detail" id="detail"></main>
</div>
<script>window.__DATA__ = {json.dumps(payload, ensure_ascii=False)};</script>
<script>{js}</script>
</body>
</html>'''

    out_path = folder / "analysis.html"
    out_path.write_text(out, encoding="utf-8")
    print(f"Wrote {out_path} ({len(out)/1024:.1f} KB)")


if __name__ == "__main__":
    folder = Path(sys.argv[1] if len(sys.argv) > 1 else "competitor-ads/aivideoskool")
    build(folder)
