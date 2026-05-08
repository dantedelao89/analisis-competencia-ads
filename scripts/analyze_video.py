#!/usr/bin/env python3
"""Analiza un video de ad con Gemini 3 Flash Preview.
Uso: python3 scripts/analyze_video.py <ruta_video.mp4>
Output: imprime JSON con transcripción, traducción al español si aplica, hook, on-screen text, escenas y tono.
"""
import os, sys, json, base64, urllib.request, urllib.error

KEY = os.environ["GEMINI_API_KEY"]
MODEL = "gemini-3-flash-preview"
ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={KEY}"

PROMPT = """Sos un analista de paid ads. Te paso un video de un anuncio publicitario. Devolveme EXCLUSIVAMENTE un objeto JSON válido (sin markdown, sin comentarios) con este schema:

{
  "detected_language": "código ISO 639-1 (ej: 'en', 'es', 'pt')",
  "transcript_original": "transcripción literal del audio en el idioma original",
  "transcript_es": "traducción natural al español rioplatense; si detected_language ya es 'es' devolvé null",
  "on_screen_text": ["texto", "que", "aparece", "en", "pantalla", "ordenado"],
  "hook_first_3s": "qué pasa visualmente Y qué se dice en los primeros 3 segundos — el gancho",
  "scene_summary": "descripción cronológica breve de las escenas clave (3-6 oraciones)",
  "tone": "uno o dos adjetivos: aspiracional / agresivo / educativo / urgente / FOMO / etc.",
  "key_visual_elements": ["billetes en primer plano", "texto grande superpuesto", "rostro hablando a cámara", "..."],
  "value_props_dichas": ["promesa concreta 1", "promesa concreta 2"],
  "cta_verbal": "si la voz menciona algún CTA explícito, ponelo aquí; si no, null"
}

Importante: si el audio está vacío o es solo música, transcript_original debe ser "" y detected_language null."""

def main(path):
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    payload = {
        "contents": [{"parts": [
            {"inline_data": {"mime_type": "video/mp4", "data": b64}},
            {"text": PROMPT},
        ]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.2,
        },
    }
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            resp = json.load(r)
    except urllib.error.HTTPError as e:
        print("HTTP error:", e.code, e.read().decode()[:1000], file=sys.stderr)
        sys.exit(1)

    text = resp["candidates"][0]["content"]["parts"][0]["text"]
    parsed = json.loads(text)
    print(json.dumps(parsed, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main(sys.argv[1])
