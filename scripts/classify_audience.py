#!/usr/bin/env python3
"""Clasifica cada video como cold / warm / retargeting usando los análisis ya hechos.
No re-procesa videos — usa el JSON de video_analyses.json y manda solo texto a Gemini.
Uso: python3 scripts/classify_audience.py <carpeta>
Sobreescribe video_analyses.json agregando el campo 'audience' a cada entry.
"""
import os, sys, json, urllib.request, urllib.error
from pathlib import Path

KEY = os.environ["GEMINI_API_KEY"]
MODEL = "gemini-3-flash-preview"
ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={KEY}"

PROMPT_HEADER = """Sos analista senior de paid ads. Te paso el análisis estructurado de un video publicitario (ya transcrito y desglosado escena por escena). Tu tarea: determinar a qué etapa del funnel apunta este ad.

Devolvé EXCLUSIVAMENTE un objeto JSON con este schema:

{
  "audience_temperature": "cold" | "warm" | "retargeting",
  "confidence": "high" | "medium" | "low",
  "reasoning": "explicación breve (1-3 oraciones) de por qué clasificás así, citando elementos concretos del análisis (hook, copy, escenas, oferta, social proof, etc.)",
  "signals_detected": ["lista de señales específicas que detectaste, ej: 'no explica qué es el producto', 'menciona descuento', 'asume familiaridad', etc."]
}

Definiciones:
- cold (audiencia fría / TOFU): primer contacto. Explica QUIÉN es la marca y QUÉ hace. Hook fuerte para captar atención de desconocidos. Define el problema antes de vender. Usa social proof grande para legitimarse. Producción alta. Copy más educativo o curioso. Ejemplos: "Most people don't know that...", "Did you know...", revelación tipo "I'm AI".
- warm (audiencia tibia / MOFU): la persona ya vio algo de la marca. Demos del producto en acción, casos de uso específicos, testimonios. Habla del cómo más que del qué. Asume cierto contexto. Profundiza en value props.
- retargeting (audiencia caliente / BOFU): la persona ya interactuó (visitó, agregó al carrito, miró videos). Asume conocimiento total del producto. Corto, directo. Usa urgencia/escasez ("last chance", "limited time"), descuentos específicos, prueba social muy concreta, recordatorios ("you saw us"), CTA imperativo y simple.

Reglas:
- Si el ad tiene oferta con descuento agresivo o urgencia explícita → casi siempre retargeting.
- Si el ad explica desde cero qué es el producto → cold.
- Si el ad muestra demos largas, varios casos de uso o testimonios → warm.
- Si tenés dudas, elegí cold (es la default más segura) y poné confidence: low.

Análisis del video a clasificar:
"""

def classify(analysis_obj):
    payload = {
        "contents": [{"parts": [
            {"text": PROMPT_HEADER + json.dumps(analysis_obj, ensure_ascii=False)}
        ]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.1},
    }
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        resp = json.load(r)
    return json.loads(resp["candidates"][0]["content"]["parts"][0]["text"])


def main(folder: str):
    folder = Path(folder)
    path = folder / "video_analyses.json"
    data = json.load(open(path))
    print(f"Clasificando {len(data)} videos...")
    for i, entry in enumerate(data, 1):
        analysis = entry.get("analysis") or {}
        if "error" in analysis:
            print(f"[{i}/{len(data)}] skip {entry['ad_id']} (error previo)")
            continue
        if "audience" in analysis:
            print(f"[{i}/{len(data)}] cached {entry['ad_id']}")
            continue
        try:
            cls = classify(analysis)
            analysis["audience"] = cls
            print(f"[{i}/{len(data)}] {entry['ad_id']}: {cls.get('audience_temperature','?'):12s} ({cls.get('confidence','?')})")
        except Exception as e:
            print(f"[{i}/{len(data)}] FAIL {entry['ad_id']}: {e}")
            analysis["audience"] = {"error": str(e)}
        # Save incrementally so we don't lose progress
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\nDone. Updated: {path}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "competitor-ads/aivideoskool")
