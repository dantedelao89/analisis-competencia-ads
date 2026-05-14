---
name: competitive-ads-extractor
description: Extrae anuncios reales de competidores desde Meta Ad Library (Facebook + Instagram) usando Apify, descarga los videos y los analiza con Gemini 3 Flash Preview (transcripción + traducción al español + desglose escena por escena con timestamp + visual + audio + on-screen text + rol narrativo). Úsalo cuando el usuario pegue un link de Facebook (incluyendo facebook.com/<página>, facebook.com/profile.php?id=..., o cualquier formato de página de Facebook), mencione una marca/competidor, o pida "extrae ads", "analiza la publicidad de X", "qué está corriendo X", "scrapea ads", "bájame los videos", "transcríbeme los videos", "qué dicen los videos" o cualquier variante.
---

# Competitive Ads Extractor

> ⚠️ **EL USUARIO ES 100% PRINCIPIANTE.** No le pidas que abra una terminal extra, ni que ejecute comandos. **Tú haces TODO.**

> 🇲🇽 **IDIOMA: ESPAÑOL NEUTRAL MEXICANO.** Usa "tú", "puedes", "haz", "dile", "necesitas". **NUNCA uses "vos", "tenés", "decís", "podés", "andá", "hacé".**

---

## 🚨 REGLAS CRÍTICAS (lee antes de hacer cualquier cosa)

### REGLA 1 — Las llaves SIEMPRE están en `.env`, NUNCA en el shell environment

❌ **NO hagas esto:**
```bash
echo $APIFY_TOKEN  # ← INCORRECTO, el shell environment está vacío cada vez
```

✅ **SIEMPRE haz esto antes de usar las llaves:**
```bash
set -a && source .env && set +a
```

Cada llamada a `Bash` que ejecutes es una sesión nueva. **Las variables NO persisten entre llamadas.** Por lo tanto, **antes de cada comando que necesite las llaves, debes cargar el .env explícitamente.**

### REGLA 2 — Las URLs de página de Facebook SÍ funcionan directamente

El actor `apify/facebook-ads-scraper` acepta TODOS estos formatos sin transformación:

```
✅ https://www.facebook.com/aivideoskool
✅ https://www.facebook.com/martinvelardefilm
✅ https://www.facebook.com/profile.php?id=61577852912181
✅ https://www.facebook.com/ads/library/?...&q=keyword
✅ https://www.facebook.com/ads/library/?...&view_all_page_id=...
```

❌ **NUNCA le digas al alumno** *"esa URL es la página, no la Ad Library, necesito el formato facebook.com/ads/library/..."*. **ESO ES FALSO.** El actor resuelve la página directamente.

Si el alumno te pasa `facebook.com/martinvelardefilm` → úsalo TAL CUAL en `startUrls`.

### REGLA 3 — Flujo lineal estricto después del clone

Cuando el alumno acabe de clonar el repo, **sigue este flujo en este orden exacto. No te saltes pasos.**

1. **Pídele que configure el `.env`** (instrucciones abajo)
2. **Espera su confirmación** ("ya lo hice", "listo", "ok")
3. **Valida las llaves** con `fix_env.py` + grep
4. **Confírmale que están bien** y pídele el link del competidor
5. **Recibe el link** (cualquier formato de Facebook) y ejecuta el pipeline

NO le pidas el link antes de tener las llaves validadas. NO le pidas las llaves "exportadas en el shell".

---

## 🎬 FLUJO COMPLETO PASO A PASO

### Paso 0 — Detecta dónde estás parado

Cuando el alumno inicia conversación o pega un link, antes de hacer cualquier cosa, verifica el estado del proyecto:

```bash
# ¿Existe el .env?
test -f .env && echo "ENV_EXISTS" || echo "ENV_MISSING"
# Si existe, ¿tiene las llaves?
test -f .env && grep -qE "^APIFY_TOKEN=apify_api_" .env && echo "APIFY_OK" || echo "APIFY_FALTA"
test -f .env && grep -qE "^GEMINI_API_KEY=AIza" .env && echo "GEMINI_OK" || echo "GEMINI_FALTA"
```

**Decide el flujo según el resultado:**

| Estado | Qué hacer |
|---|---|
| ENV_MISSING | Ir a **Paso 1** (guía de creación del .env) |
| ENV_EXISTS pero alguna falta | Ir a **Paso 2** (auto-fix y validación) |
| Ambas OK | Ir directo al **Paso 3** (pedir URL del competidor) |

---

### Paso 1 — Guía al alumno a crear el `.env` (si no existe)

**Dile EXACTAMENTE este mensaje** (adáptalo al tono pero mantén la estructura):

> 👋 ¡Bienvenido! Antes de poder analizar a tus competidores, necesitas configurar dos llaves gratuitas. Hazlo así:
>
> ### 📋 Paso 1 — Renombra el archivo de ejemplo
>
> En tu carpeta del proyecto vas a encontrar un archivo llamado `.env.example`. **Cámbiale el nombre a `.env`** (sin el `.example`).
>
> ### 🔑 Paso 2 — Consigue tus 2 llaves gratuitas
>
> **Apify** (para descargar los anuncios):
> 1. Crea cuenta gratis en https://console.apify.com/sign-up
> 2. Ve a https://console.apify.com/settings/integrations
> 3. Copia el token que empieza con `apify_api_...`
>
> **Google Gemini** (para analizar los videos):
> 1. Entra a https://aistudio.google.com/apikey
> 2. Haz click en **"Create API key"**
> 3. Copia la llave (empieza con `AIza...`)
>
> ### 📝 Paso 3 — Pega las llaves en el archivo `.env`
>
> Abre el archivo `.env` con cualquier editor de texto (TextEdit en Mac, Notepad en Windows, o el editor de tu Claude Code). Vas a ver dos líneas — reemplaza los placeholders con tus llaves reales:
>
> ```
> APIFY_TOKEN=apify_api_aqui_va_tu_token
> GEMINI_API_KEY=AIza_aqui_va_tu_llave
> ```
>
> ⚠️ **Importante:** sin espacios alrededor del `=`, sin comillas alrededor de las llaves. Si te equivocas, no te preocupes, yo lo arreglo automáticamente.
>
> ### ✅ Paso 4 — Avísame cuando termines
>
> Cuando hayas guardado el archivo, **escríbeme "listo"** o "ya está", y yo valido que todo esté bien antes de continuar.

**ESPERA SU CONFIRMACIÓN.** No corras nada más hasta que el alumno diga "listo", "ya está" o algo similar.

---

### Paso 2 — Auto-fix y validación (después de que el alumno confirme)

Cuando el alumno confirme que ya configuró el `.env`, ejecuta estos comandos en orden:

```bash
# 1. Saneamiento automático del .env
python3 scripts/fix_env.py

# 2. Validar formato de las llaves
test -f .env && grep -qE "^APIFY_TOKEN=apify_api_" .env && echo "APIFY_FORMAT_OK" || echo "APIFY_FORMAT_BAD"
test -f .env && grep -qE "^GEMINI_API_KEY=AIza" .env && echo "GEMINI_FORMAT_OK" || echo "GEMINI_FORMAT_BAD"

# 3. Validar que las llaves funcionen contra los servicios
set -a && source .env && set +a
APIFY_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "https://api.apify.com/v2/users/me?token=$APIFY_TOKEN")
GEMINI_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "https://generativelanguage.googleapis.com/v1beta/models?key=$GEMINI_API_KEY")
echo "APIFY: $APIFY_STATUS"
echo "GEMINI: $GEMINI_STATUS"
```

**Interpretación:**
- APIFY: `200` = funciona · cualquier otra cosa = inválido
- GEMINI: `200` = funciona · `400/403` = inválido

**Si alguna falla:**
> Mmm, la llave de **[Apify/Gemini]** no me responde. ¿Puedes verificar que la copiaste correcta desde [link]? Pégala de nuevo en el `.env` y avísame.

**Si ambas funcionan:**
> ✅ ¡Perfecto, las dos llaves están funcionando!
>
> Ahora pásame el **link de la página de Facebook del competidor** que quieres analizar. Por ejemplo:
> - `https://www.facebook.com/notion`
> - `https://www.facebook.com/martinvelardefilm`
> - `https://www.facebook.com/profile.php?id=61577852912181`
>
> Cualquiera de estos formatos funciona.

**ESPERA EL LINK.** No avances hasta tener el link.

---

### Paso 3 — Pipeline de extracción y análisis

Cuando el alumno te pase el link, ejecuta el pipeline. **SIEMPRE** carga el `.env` al inicio de cada bash:

#### 3.1 — Crear carpeta y extraer ads con Apify

Sluggea el nombre de la marca a partir de la URL:
- `facebook.com/martinvelardefilm` → slug = `martinvelardefilm`
- `facebook.com/profile.php?id=12345` → slug temporal = `_tmp_12345` (renombrar después usando `pageName` del response)

```bash
set -a && source .env && set +a
mkdir -p competitor-ads/<slug>

curl -s -w "HTTP %{http_code} en %{time_total}s\n" \
  "https://api.apify.com/v2/acts/apify~facebook-ads-scraper/run-sync-get-dataset-items?token=$APIFY_TOKEN" \
  -X POST -H 'Content-Type: application/json' \
  -d '{
    "startUrls": [{"url": "<LINK_QUE_PEGÓ_EL_ALUMNO>"}],
    "resultsLimit": 200,
    "isDetailsPerAd": true,
    "includeAboutPage": true,
    "activeStatus": "active"
  }' \
  -o competitor-ads/<slug>/ads_raw.json
```

**IMPORTANTE:** el campo `startUrls` recibe el link de la página tal cual lo pegó el alumno. **NO lo transformes.**

#### 3.2 — Si hay > 50 ads, filtrar a top long-runners

```bash
python3 scripts/filter_top_ads.py competitor-ads/<slug> 30
```

(Solo si la marca tiene más de 50 ads activos — si tiene menos, sáltate este paso.)

#### 3.3 — Generar CSV

```bash
python3 -c "
import json, csv
d = json.load(open('competitor-ads/<slug>/ads_raw.json'))
rows = []
for ad in d:
    s = ad.get('snapshot') or {}
    body = ((s.get('body') or {}).get('text') or '').strip()
    vids = s.get('videos') or []
    rows.append({
        'adArchiveID': ad.get('adArchiveID') or '',
        'pageName': s.get('pageName') or '',
        'startDate': (ad.get('startDateFormatted') or '')[:10],
        'endDate': (ad.get('endDateFormatted') or '')[:10],
        'displayFormat': s.get('displayFormat') or '',
        'collationCount': ad.get('collationCount') or 1,
        'title': s.get('title') or '',
        'ctaText': s.get('ctaText') or '',
        'linkUrl': s.get('linkUrl') or '',
        'copy': body.replace(chr(10),' / '),
        'videoHdUrl': (vids[0] or {}).get('videoHdUrl','') if vids else '',
    })
with open('competitor-ads/<slug>/ads_summary.csv','w',newline='',encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print(f'CSV: {len(rows)} filas')
"
```

#### 3.4 — Descargar videos + análisis con Gemini

```bash
python3 scripts/process_all_videos.py competitor-ads/<slug>
```

#### 3.5 — Clasificar audiencia (si no se hizo en 3.4)

```bash
python3 scripts/classify_audience.py competitor-ads/<slug>
```

#### 3.6 — Generar informes

```bash
python3 scripts/build_analysis.py competitor-ads/<slug>
python3 scripts/build_html.py competitor-ads/<slug>
```

#### 3.7 — Abrir el HTML automáticamente

```bash
open competitor-ads/<slug>/analysis.html
```

(En Linux usar `xdg-open`, en Windows usar `start`.)

#### 3.8 — Resumir al alumno

> 🎯 **Listo. Analicé N ads de <marca>** (X creativos únicos, Y escenas).
>
> **Hallazgos clave:**
> - <insight 1>
> - <insight 2>
> - <insight 3>
>
> 📂 **Archivos generados** (ya abrí el HTML en tu navegador):
> - [analysis.html](competitor-ads/<slug>/analysis.html) ⭐ informe visual
> - [analysis.md](competitor-ads/<slug>/analysis.md) versión texto
> - [ads_summary.csv](competitor-ads/<slug>/ads_summary.csv) tabla Excel
> - [videos/](competitor-ads/<slug>/videos/) los .mp4 descargados
>
> ¿Quieres analizar otro competidor o comparar varios con un dashboard?

---

## 📦 Schema del output del actor de Apify

```jsonc
{
  "adArchiveID": "1354041633403636",
  "pageID": "825120160874613",
  "startDateFormatted": "2026-01-30T08:00:00.000Z",
  "endDateFormatted": "2026-02-04T08:00:00.000Z",
  "collationCount": 1,
  "snapshot": {
    "pageName": "Notion",
    "body": { "text": "Copy del ad..." },
    "ctaText": "Learn more",
    "ctaType": "LEARN_MORE",
    "linkUrl": "https://...",
    "displayFormat": "VIDEO",
    "images": [{ "originalImageUrl": "..." }],
    "videos": [{ "videoHdUrl": "...", "videoSdUrl": "...", "videoPreviewImageUrl": "..." }],
    "cards": [],
    "brandedContent": { "pageName": "...", "pageProfileUri": "..." }
  }
}
```

**Heurística de "qué funciona"**: ads viejos que siguen activos = los que la marca está escalando. Ordena por `startDateFormatted` ascendente. `collationCount > 1` = variantes A/B.

---

## 🎬 Análisis profundo de videos con Gemini 3 Flash

El script `scripts/process_all_videos.py` ya hace todo el flujo:

1. Lee `competitor-ads/<marca>/ads_raw.json`.
2. Deduplica videos (varios ads suelen usar el mismo creativo).
3. Descarga los `.mp4` SD a `videos/`.
4. Por cada video llama a `gemini-3-flash-preview` con prompt estructurado.
5. Guarda `video_analyses.json`.

**Schema del output por video:**

```jsonc
{
  "detected_language": "en",
  "transcript_original": "...",
  "transcript_es": "...",
  "scenes_breakdown": [
    {
      "scene_number": 1,
      "timestamp_start": "0:00",
      "timestamp_end": "0:03",
      "visual": "...",
      "audio_dialogue": "...",
      "audio_dialogue_es": "...",
      "on_screen_text": "...",
      "shot_type": "...",
      "purpose": "hook / pain / solución / demo / oferta / objeción / CTA / social proof"
    }
  ],
  "hook_first_3s": "...",
  "tone": "...",
  "key_visual_elements": ["..."],
  "value_props_dichas": ["..."],
  "cta_verbal": "...",
  "price_mentioned": "...",
  "social_proof_mentioned": "...",
  "audience": {
    "audience_temperature": "cold | warm | retargeting",
    "confidence": "high | medium | low",
    "reasoning": "...",
    "signals_detected": ["..."]
  }
}
```

**Clasificación de audiencia:**
- 🧊 **cold (TOFU)**: explica quién/qué es la marca, hooks fuertes, define el problema, producción alta.
- 🌡️ **warm (MOFU)**: demos del producto, casos de uso, testimonios. Asume cierto contexto.
- 🔥 **retargeting (BOFU)**: asume familiaridad total. Urgencia/escasez, descuentos, CTA imperativo corto.

---

## ⚠️ Errores comunes y respuestas conversacionales

| Error | Qué le dices al alumno |
|---|---|
| `.env` con espacios o comillas | No le dices nada — `fix_env.py` lo arregla automático. |
| Apify `401` | *"La llave de Apify no funciona. ¿La copias de nuevo desde [acá](https://console.apify.com/settings/integrations)?"* |
| Apify `402` (sin saldo) | *"Se acabó el saldo gratis de Apify. Carga más [aquí](https://console.apify.com/billing) ($5 USD mínimo) o espera al mes que viene."* |
| Apify JSON vacío `[]` | *"No encontré ads activos de esa marca. Tal vez no está pauteando, o el nombre está distinto, o está en otro país. ¿Probamos con otro nombre o me dices el país?"* |
| Gemini `429` | Espera 30s y reintenta. No molestes al alumno. |
| Gemini `400 invalid api key` | *"La llave de Gemini no la acepta Google. ¿La regeneras en [aistudio.google.com/apikey](https://aistudio.google.com/apikey) y me la pegas?"* |
| Timeout en Apify | Reintenta con `resultsLimit: 50`. |

---

## 🛑 Lo que NO hace esta skill

- No scrapea TikTok ni LinkedIn (solo Meta = Facebook + Instagram).
- No estima performance real (`spend`/`impressions` solo vienen en ads políticos / EU).
- No usa navegador. Todo por API.
- No sube datos extraídos a ningún lado. Todo queda local.

---

## 💡 Ejemplos de uso

- `https://www.facebook.com/aivideoskool` (solo el link → todo automático)
- *"Analiza los ads de Glovo en México"*
- *"Compara Rappi y PedidosYa, qué pain points usan"*
- *"Bájame los videos top de Notion y dime qué hooks usan"*
- *"Hazme el dashboard cross-competidor con todos los que ya analicé"*

---

## 🔁 Segunda corrida (alumno que ya configuró todo)

Si `.env` ya tiene ambas llaves válidas, **NO repitas el onboarding**. Saluda corto y arranca:

> 👋 ¡Hola de nuevo! Detecté tus llaves, voy a analizar **<marca>**...
