#!/usr/bin/env python3
"""Descarga y analiza todos los videos únicos de un ads_raw.json.
Uso: python3 scripts/process_all_videos.py <carpeta_competidor>
Genera: <carpeta>/videos/<adArchiveID>.mp4 y <carpeta>/video_analyses.json
"""
import os, sys, json, base64, urllib.request, urllib.error, hashlib
from pathlib import Path

KEY = os.environ["GEMINI_API_KEY"]
MODEL = "gemini-3-flash-preview"
ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={KEY}"

PROMPT = """Sos un analista de paid ads. Te paso un video de un anuncio. Devolveme EXCLUSIVAMENTE un objeto JSON válido (sin markdown, sin comentarios) con este schema:

{
  "detected_language": "código ISO 639-1 (ej: 'en', 'es', 'pt')",
  "transcript_original": "transcripción literal completa del audio en idioma original",
  "transcript_es": "traducción natural al español rioplatense; si detected_language == 'es' devolvé null",
  "scenes_breakdown": [
    {
      "scene_number": 1,
      "timestamp_start": "0:00",
      "timestamp_end": "0:03",
      "visual": "descripción detallada de qué se ve: encuadre, personas, ambiente, ropa, gestos, transiciones",
      "audio_dialogue": "qué dice exactamente la voz en esta escena (idioma original)",
      "audio_dialogue_es": "qué dice traducido al español rioplatense; null si ya estaba en español",
      "on_screen_text": "texto que aparece en pantalla en esta escena específica (o '' si no hay)",
      "shot_type": "primer plano / plano medio / plano general / inserto de UI / texto pleno / etc.",
      "purpose": "rol narrativo: hook / pain / solución / demo / oferta / objeción / CTA / social proof"
    }
  ],
  "hook_first_3s": "resumen del gancho (visual + auditivo) en los primeros 3 segundos",
  "tone": "uno o dos adjetivos: aspiracional / agresivo / educativo / urgente / FOMO / etc.",
  "key_visual_elements": ["billetes en primer plano", "texto grande superpuesto", "..."],
  "value_props_dichas": ["promesa concreta 1", "promesa concreta 2"],
  "cta_verbal": "si la voz menciona un CTA explícito ponelo; si no, null",
  "price_mentioned": "si el video menciona precio, copialo literal; si no, null",
  "social_proof_mentioned": "número de miembros, testimonios, logos, etc; si no hay, null"
}

Reglas importantes:
- scenes_breakdown debe ser una secuencia ORDENADA por timestamp con TODAS las escenas relevantes (típicamente 5-15 escenas en un ad de 20-60s; si hay un cambio de plano significativo es una escena nueva).
- Los timestamps son aproximados pero ordenados (formato 'm:ss' o 's').
- audio_dialogue es lo que se DICE en esa escena específica, no toda la transcripción. Si la escena no tiene diálogo (silencio, música), poné "".
- on_screen_text es el texto literal de esa escena, no acumulado.
- transcript_original es la transcripción global continua; scenes_breakdown la disecciona por escena.
- Si el audio está vacío o solo música, transcript_original = "" y detected_language = null."""


def download(url: str, out: Path) -> int:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as r, open(out, "wb") as f:
        data = r.read()
        f.write(data)
    return len(data)


def analyze(video_path: Path) -> dict:
    with open(video_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    payload = {
        "contents": [{"parts": [
            {"inline_data": {"mime_type": "video/mp4", "data": b64}},
            {"text": PROMPT},
        ]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.2},
    }
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=300) as r:
        resp = json.load(r)
    return json.loads(resp["candidates"][0]["content"]["parts"][0]["text"])


def main(folder: str):
    folder = Path(folder)
    raw = json.load(open(folder / "ads_raw.json"))
    vids_dir = folder / "videos"
    vids_dir.mkdir(exist_ok=True)

    # Dedupe by SD url (mismo creative = misma url base hasta el query string)
    seen = {}
    for ad in raw:
        s = ad.get("snapshot") or {}
        videos = s.get("videos") or []
        if not videos:
            continue
        v = videos[0] or {}
        sd = v.get("videoSdUrl") or v.get("videoHdUrl")
        if not sd:
            continue
        # Hash by path before query string (Facebook signs URLs but file is same)
        key = sd.split("?")[0].split("/")[-1]
        if key in seen:
            seen[key]["ad_ids"].append(ad["adArchiveID"])
            continue
        seen[key] = {
            "ad_id": ad["adArchiveID"],
            "ad_ids": [ad["adArchiveID"]],
            "title": s.get("title") or "",
            "url": sd,
            "key": key,
        }

    print(f"Total ads: {len(raw)} | Videos únicos: {len(seen)}")

    results = []
    for i, (k, info) in enumerate(seen.items(), 1):
        out = vids_dir / f"{info['ad_id']}.mp4"
        if not out.exists():
            try:
                size = download(info["url"], out)
                print(f"[{i}/{len(seen)}] downloaded {info['ad_id']} ({size/1024:.0f} KB) — {info['title'][:50]}")
            except Exception as e:
                print(f"[{i}/{len(seen)}] DOWNLOAD FAIL {info['ad_id']}: {e}")
                continue
        else:
            print(f"[{i}/{len(seen)}] cached {info['ad_id']}")

        try:
            analysis = analyze(out)
        except Exception as e:
            print(f"  -> Gemini FAIL: {e}")
            analysis = {"error": str(e)}

        results.append({
            "ad_id": info["ad_id"],
            "duplicate_of_ad_ids": info["ad_ids"],
            "title": info["title"],
            "video_file": str(out.relative_to(folder.parent.parent)),
            "analysis": analysis,
        })
        print(f"  -> lang={analysis.get('detected_language')} | price={analysis.get('price_mentioned')}")

    out_json = folder / "video_analyses.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nSaved: {out_json}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "competitor-ads/aivideoskool")
