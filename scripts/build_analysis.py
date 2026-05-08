#!/usr/bin/env python3
"""Genera un analysis.md enriquecido con desglose por escena.
Uso: python3 scripts/build_analysis.py <carpeta_competidor>
Lee ads_raw.json + video_analyses.json y produce analysis.md.
"""
import sys, json
from pathlib import Path
from collections import Counter

AUD_EMOJI = {"cold": "🧊", "warm": "🌡️", "retargeting": "🔥"}
AUD_LABEL = {"cold": "FRÍO (TOFU)", "warm": "TIBIO (MOFU)", "retargeting": "RETARGETING (BOFU)"}


def fmt_scene(s):
    out = []
    ts = f"{s.get('timestamp_start','?')}–{s.get('timestamp_end','?')}"
    out.append(f"**[{ts}] · {s.get('shot_type','').strip() or 'plano'} · _{s.get('purpose','').strip() or '—'}_**")
    out.append(f"- 🎬 **Visual:** {s.get('visual','').strip()}")
    audio = (s.get('audio_dialogue') or '').strip()
    audio_es = (s.get('audio_dialogue_es') or '').strip()
    if audio:
        out.append(f"- 🗣️ **Audio:** *“{audio}”*")
    if audio_es:
        out.append(f"- 🗣️ **Audio (ES):** *“{audio_es}”*")
    text = (s.get('on_screen_text') or '').strip()
    if text:
        out.append(f"- 💬 **Texto en pantalla:** {text}")
    return "\n".join(out)


def main(folder: str):
    folder = Path(folder)
    name = folder.name
    raw = json.load(open(folder / "ads_raw.json"))
    vids = json.load(open(folder / "video_analyses.json"))

    n_total = len(raw)
    n_unique = len(vids)
    formats = Counter((ad.get("snapshot") or {}).get("displayFormat") or "?" for ad in raw)
    langs = Counter(v["analysis"].get("detected_language") or "?" for v in vids)
    prices = [v["analysis"].get("price_mentioned") for v in vids if v["analysis"].get("price_mentioned")]
    page_name = (raw[0].get("snapshot") or {}).get("pageName") or name

    out = []
    out.append(f"# Análisis de ads — {page_name}\n")
    out.append(f"**Página:** [facebook.com/{name}](https://www.facebook.com/{name})  ")
    out.append(f"**Ads activos totales:** {n_total} · **Creativos únicos analizados:** {n_unique}  ")
    out.append(f"**Formatos:** {dict(formats)}  ")
    out.append(f"**Idiomas detectados en video:** {dict(langs)}  ")
    if prices:
        out.append(f"**Precios mencionados en video:** {', '.join(set(prices))}  ")

    # Audience temperature breakdown
    aud_counts = Counter()
    for v in vids:
        aud = (v["analysis"].get("audience") or {}).get("audience_temperature")
        if aud:
            aud_counts[aud] += 1
    if aud_counts:
        out.append(f"**Distribución por etapa del funnel:** ")
        parts = []
        for k in ["cold", "warm", "retargeting"]:
            if k in aud_counts:
                parts.append(f"{AUD_EMOJI[k]} {AUD_LABEL[k]}: **{aud_counts[k]}**")
        out.append(" · ".join(parts) + "  ")
    out.append("\n---\n")

    out.append("## 📋 Resumen estructural\n")
    out.append("Cada creativo fue transcrito y descompuesto escena por escena con Gemini 3 Flash Preview. ")
    out.append("Por cada escena tenés timestamp, encuadre, lo que se ve, lo que se dice (original + traducción al español rioplatense) y el rol narrativo.\n\n---\n")

    # Order videos: long-runner first if precio mencionado
    vids_sorted = sorted(vids, key=lambda v: (0 if v["analysis"].get("price_mentioned") else 1))

    for i, entry in enumerate(vids_sorted, 1):
        a = entry["analysis"]
        title = entry.get("title") or "(sin título)"
        out.append(f"## 🎬 Creativo {i} — {title}\n")
        out.append(f"- **Ad ID(s):** `{', '.join(entry['duplicate_of_ad_ids'])}`")
        out.append(f"- **Idioma:** {a.get('detected_language')}")
        out.append(f"- **Tono:** {a.get('tone')}")
        aud = a.get("audience") or {}
        aud_t = aud.get("audience_temperature")
        if aud_t:
            emoji = AUD_EMOJI.get(aud_t, "❓")
            label = AUD_LABEL.get(aud_t, aud_t)
            conf = aud.get("confidence", "?")
            out.append(f"- **{emoji} Audiencia:** {label} _(confianza: {conf})_")
            if aud.get("reasoning"):
                out.append(f"  - _Por qué:_ {aud['reasoning']}")
            if aud.get("signals_detected"):
                out.append(f"  - _Señales:_ " + ", ".join(f"`{s}`" for s in aud["signals_detected"]))
        if a.get("price_mentioned"):
            out.append(f"- **💰 Precio mencionado:** {a['price_mentioned']}")
        if a.get("social_proof_mentioned"):
            out.append(f"- **🏅 Social proof:** {a['social_proof_mentioned']}")
        if a.get("cta_verbal"):
            out.append(f"- **📢 CTA verbal:** *\"{a['cta_verbal']}\"*")
        out.append(f"- **📁 [Ver video](videos/{entry['ad_id']}.mp4)**\n")

        out.append(f"**Hook (primeros 3s):** {a.get('hook_first_3s','—')}\n")

        out.append(f"### Transcripción completa\n")
        out.append(f"**Original ({a.get('detected_language')}):**\n> *\"{a.get('transcript_original','')}\"*\n")
        if a.get("transcript_es"):
            out.append(f"**Traducción al español:**\n> *\"{a.get('transcript_es')}\"*\n")

        scenes = a.get("scenes_breakdown") or []
        if scenes:
            out.append(f"### Desglose escena por escena ({len(scenes)} escenas)\n")
            for s in scenes:
                out.append(fmt_scene(s))
                out.append("")
        out.append("\n---\n")

    out.append("## 🎯 Patrones detectados (vista cruzada)\n")
    purposes = Counter()
    for v in vids:
        for s in v["analysis"].get("scenes_breakdown") or []:
            p = (s.get("purpose") or "").strip().lower()
            if p:
                purposes[p] += 1
    if purposes:
        out.append("**Distribución de roles narrativos** (cuántas escenas en total cumplen cada función):\n")
        for p, n in purposes.most_common():
            out.append(f"- `{p}`: {n} escenas")
        out.append("")

    out.append("\n---\n")
    out.append("## 📁 Archivos generados\n")
    out.append("- [ads_raw.json](ads_raw.json) — datos crudos de Apify")
    out.append("- [ads_summary.csv](ads_summary.csv) — tabla")
    out.append("- [video_analyses.json](video_analyses.json) — análisis crudo de Gemini por video")
    out.append(f"- [videos/](videos/) — {n_unique} archivos `.mp4`")
    out.append("- [analysis.md](analysis.md) — este informe")

    md = "\n".join(out)
    (folder / "analysis.md").write_text(md, encoding="utf-8")
    print(f"Wrote {folder/'analysis.md'} ({len(md)} chars)")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "competitor-ads/aivideoskool")
