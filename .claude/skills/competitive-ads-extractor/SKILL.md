---
name: competitive-ads-extractor
description: Extrae anuncios reales de competidores desde Meta Ad Library (Facebook + Instagram) usando Apify, descarga los videos y los analiza con Gemini 3 Flash Preview (transcripción + traducción al español + desglose escena por escena con timestamp + visual + audio + on-screen text + rol narrativo). Úsalo cuando el usuario pegue un link de Facebook, mencione una marca/competidor, o pida "extraé ads", "analizá la publicidad de X", "qué está corriendo X", "scrapeá ads", "bajame los videos", "transcribime los videos", "qué dicen los videos" o cualquier variante.
---

# Competitive Ads Extractor

> ⚠️ **EL USUARIO ES 100% PRINCIPIANTE.** Nunca le pidas que abra una terminal, edite archivos, ni toque código. **Vos hacés TODO**. Si falta algo, **preguntale en el chat** con lenguaje cálido, links clickeables y pasos numerados.

---

## 🎯 Flujo ultra-simple (objetivo del alumno)

El alumno solo tiene que **pegar un link de Facebook** (ej: `https://www.facebook.com/aivideoskool`) o nombrar una marca. Vos te encargás del resto:

1. Detectás qué credenciales faltan en `.env` y las pedís conversacionalmente.
2. Extraés los ads activos con Apify.
3. Descargás los videos y los analizás con Gemini Flash 3.
4. Generás un informe escena-por-escena en español.
5. Le entregás todo con un resumen ejecutivo.

**Si el alumno solo pega una URL de Facebook como primer mensaje, NO le hagas preguntas innecesarias. Asumí que quiere análisis completo y arrancá el setup.**

---

## ⚙️ Setup automático (CRÍTICO — primer paso siempre)

Antes de cualquier extracción, **SIEMPRE** verificá qué claves hay:

```bash
test -f .env && grep -qE "^APIFY_TOKEN=apify_api_" .env && echo "APIFY_OK" || echo "APIFY_FALTA"
test -f .env && grep -qE "^GEMINI_API_KEY=AIza" .env && echo "GEMINI_OK" || echo "GEMINI_FALTA"
```

Según lo que falte, seguí los flujos de abajo. **Pedí UNA credencial a la vez** (primero Apify, después Gemini).

---

### 🔵 Si falta APIFY_TOKEN → onboarding Apify

**No corras nada todavía.** Mostrale exactamente este mensaje (adaptá al tono del chat):

> 👋 ¡Hola! Voy a analizar los ads de tu competidor. Antes de arrancar necesito **2 llaves gratuitas** (te guío paso a paso). Empecemos por la primera:
>
> ### 🔑 1 de 2 — Token de Apify
>
> Apify es la herramienta que se mete en la Facebook Ad Library y baja los anuncios por nosotros. Es gratis y te regalan saldo al registrarte.
>
> **Hacé esto (3 minutos):**
>
> 1️⃣ Abrí 👉 https://console.apify.com/sign-up
>    *(Click en "Sign up with Google" — es 1 solo click, sin tarjeta de crédito)*
>
> 2️⃣ Una vez adentro, abrí 👉 https://console.apify.com/settings/integrations
>
> 3️⃣ Vas a ver una caja que dice **"Personal API tokens"** con un token que empieza con `apify_api_...`. Clickeá el ícono de copiar (📋) al lado.
>
> 4️⃣ **Pegámelo acá en el chat** y yo lo guardo. ✅
>
> *💰 Te regalan ~$5 USD gratis. Cada análisis cuesta menos de $0.01 USD, así que te alcanza para analizar miles de marcas.*

Cuando el alumno te pegue el token (formato: `apify_api_` + letras/números):

1. **Validalo silenciosamente:**
   ```bash
   curl -s -o /dev/null -w "%{http_code}" "https://api.apify.com/v2/users/me?token=<TOKEN_PEGADO>"
   ```
   - `200` → válido, seguir.
   - cualquier otro código → decile amablemente: *"Mmm, parece que se copió mal o le falta algún carácter. ¿Me lo pegás de nuevo?"*

2. **Guardalo en `.env`** (append, NUNCA sobreescribir):
   ```bash
   echo "APIFY_TOKEN=<TOKEN>" >> .env
   ```
   Si `.gitignore` no existe, creá uno con `.env`, `competitor-ads/`, `*.log` adentro.

3. **Pasá al siguiente paso** con este mensaje:

> ✅ ¡Perfecto, Apify listo! Ahora la segunda y última llave:

---

### 🟣 Si falta GEMINI_API_KEY → onboarding Gemini

> ### 🔑 2 de 2 — API key de Google Gemini
>
> Gemini es el cerebro que mira los videos y te dice **qué pasa en cada escena, qué dice cada persona, qué texto aparece en pantalla, traducido al español**. También es gratis con cuota generosa.
>
> **Hacé esto (2 minutos):**
>
> 1️⃣ Abrí 👉 https://aistudio.google.com/apikey
>    *(logueate con tu Gmail — sin instalación, sin tarjeta)*
>
> 2️⃣ Click en el botón azul **"Create API key"** (o "Crear clave de API").
>
> 3️⃣ Te aparece una clave que empieza con `AIza...`. Click en el ícono de copiar (📋).
>
> 4️⃣ **Pegámela acá en el chat** ✅
>
> *🎁 Plan gratuito: 1.500 requests por día. Cada video cuesta 1 request, así que podés analizar cientos de ads gratis.*

Cuando la pegue:

1. **Validá:**
   ```bash
   curl -s -o /dev/null -w "%{http_code}" "https://generativelanguage.googleapis.com/v1beta/models?key=<KEY>"
   ```
   - `200` → válida.
   - `400/403` → *"Esa clave no me la acepta Google. ¿La pegás de nuevo desde aistudio.google.com/apikey?"*

2. **Guardala:**
   ```bash
   echo "GEMINI_API_KEY=<KEY>" >> .env
   ```

3. **Confirmá y arrancá el análisis sin pedir más nada:**

> 🎉 ¡Listo, todo configurado! Ya tengo Apify + Gemini funcionando.
>
> Ahora arranco con el análisis de **<marca>**. Va a tardar unos 5 minutos:
> - 🔍 Extraigo los ads activos (~1 min)
> - 📥 Descargo los videos (~1 min)
> - 🎬 Los analizo escena por escena con Gemini (~3 min)
> - 📊 Te entrego el informe completo
>
> Aguantame un cachito... ⏳

---

### 🟢 Si todo OK → cargar variables y arrancar

```bash
set -a; source .env; set +a
```

NO menciones esto al alumno. Hacelo en silencio.

---

## 🚀 Pipeline de extracción y análisis

### Paso 1 — entender qué quiere

Si el alumno pegó una URL `facebook.com/<algo>` → extraela y usala directo. **No preguntes país, no preguntes cantidad — usá los defaults.**

Si solo dijo un nombre de marca:
- Asumí `country=US` (mayor cobertura de ads).
- Si la marca es claramente latina (Glovo en AR, Rappi, Mercado Libre), preguntá país en una sola línea: *"¿De qué país buscás los ads? (US, AR, MX, ES, BR...)"*

### Paso 2 — armar la URL de Meta Ad Library

**Si tenés URL de página directo** (lo más común):
```
https://www.facebook.com/<NombreDeLaPagina>
```

**Si tenés keyword/marca:**
```
https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=<COUNTRY>&q=<KEYWORD>&search_type=keyword_unordered&media_type=all
```

### Paso 3 — extraer con Apify

```bash
set -a; source .env; set +a
mkdir -p competitor-ads/<marca-slug>

curl -s "https://api.apify.com/v2/acts/apify~facebook-ads-scraper/run-sync-get-dataset-items?token=$APIFY_TOKEN" \
  -X POST -H 'Content-Type: application/json' \
  -d '{
    "startUrls": [{"url": "<URL>"}],
    "resultsLimit": 200,
    "isDetailsPerAd": true,
    "includeAboutPage": true,
    "activeStatus": "active"
  }' \
  -o competitor-ads/<marca-slug>/ads_raw.json
```

**Defaults:** `resultsLimit: 200` con `activeStatus: "active"` — trae todos los ads activos sin volar el presupuesto. Solo bajá a 30-50 si el alumno pide algo rápido o si la marca tiene cientos de ads.

### Paso 4 — generar CSV (rápido)

```bash
python3 -c "
import json, csv
d = json.load(open('competitor-ads/<marca>/ads_raw.json'))
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
import csv
with open('competitor-ads/<marca>/ads_summary.csv','w',newline='',encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print(len(rows))
"
```

### Paso 5 — descargar videos + análisis con Gemini

**Por defecto siempre hacelo.** El video es donde está la info más valiosa (precio real, hooks, escenas, on-screen text). El copy escrito solo es la punta del iceberg.

```bash
python3 scripts/process_all_videos.py competitor-ads/<marca>
```

Esto:
1. Lee `ads_raw.json`.
2. Deduplica videos (varios ads usan el mismo creativo).
3. Descarga los `.mp4` SD a `videos/`.
4. Por cada video llama a `gemini-3-flash-preview` con prompt estructurado.
5. Guarda `video_analyses.json`.

**Schema del output por video:**

```jsonc
{
  "detected_language": "en",                    // ISO 639-1
  "transcript_original": "...",                 // transcripción global continua
  "transcript_es": "...",                       // traducción ES; null si ya está en español
  "scenes_breakdown": [                         // ⭐ lo más valioso
    {
      "scene_number": 1,
      "timestamp_start": "0:00",
      "timestamp_end": "0:03",
      "visual": "encuadre + qué se ve + ambiente + ropa + gestos",
      "audio_dialogue": "qué dice la voz EN ESTA escena",
      "audio_dialogue_es": "traducción rioplatense",
      "on_screen_text": "texto literal de esta escena",
      "shot_type": "primer plano / plano medio / plano general / inserto UI",
      "purpose": "hook / pain / solución / demo / oferta / objeción / CTA / social proof"
    }
  ],
  "hook_first_3s": "resumen del gancho",
  "tone": "aspiracional / agresivo / educativo / FOMO / etc.",
  "key_visual_elements": ["..."],
  "value_props_dichas": ["..."],
  "cta_verbal": "CTA verbal o null",
  "price_mentioned": "precio si aparece, o null",
  "social_proof_mentioned": "social proof o null",
  "audience": {
    "audience_temperature": "cold | warm | retargeting",
    "confidence": "high | medium | low",
    "reasoning": "por qué se clasifica así",
    "signals_detected": ["señales específicas detectadas"]
  }
}
```

**Clasificación de audiencia (CRÍTICO para análisis serio):**
- 🧊 **cold (TOFU)**: ad de captación. Explica quién/qué es la marca, hooks fuertes, define el problema, producción alta. Ejemplo: revelación "I'm AI".
- 🌡️ **warm (MOFU)**: ad de engagement. Demos del producto, casos de uso, testimonios. Asume cierto contexto.
- 🔥 **retargeting (BOFU)**: ad de conversión. Asume familiaridad total. Urgencia/escasez (Black Friday, last chance), descuentos, recordatorios, CTA imperativo corto.

Si los videos ya fueron analizados sin clasificación de audiencia, corré:
```bash
python3 scripts/classify_audience.py competitor-ads/<marca>
```
Eso clasifica usando el JSON existente sin re-procesar videos (mucho más rápido).

### Paso 6 — generar `analysis.md` y `analysis.html`

```bash
python3 scripts/build_analysis.py competitor-ads/<marca>   # markdown
python3 scripts/build_html.py competitor-ads/<marca>       # HTML interactivo
```

Generan dos formatos del mismo informe:

- **`analysis.md`** — texto plano con metadata, transcripciones, traducción al español, **desglose escena por escena con timestamps**, agregado de patrones narrativos. Ideal para leer en el editor o subir a GitHub.

- **`analysis.html`** — informe visual interactivo, autocontenido (un solo archivo). Tema oscuro modernos con:
  - KPIs con cards
  - Barra de distribución por funnel (cold/warm/retargeting) con colores
  - Bar chart de roles narrativos
  - Cards por creativo con **video embebido** (HTML5 `<video>` reproduce los .mp4 locales)
  - Badges de audiencia, precio, tono
  - Razonamiento de la clasificación con chips de señales
  - Transcripciones colapsables (original + español)
  - Escenas con timestamp, plano, propósito, visual, audio, texto
  - Tabla de contenido sticky con links a cada video

Se abre con doble click en cualquier navegador. Es el formato a entregar al alumno.

### Paso 7 — entregar al alumno

Mostrale los archivos como links clickeables y resumile en 3-5 bullets lo más jugoso (cosas que SOLO salen del análisis, no obvias):

> 🎯 **Listo. Encontré N ads activos de <marca>** (X creativos únicos, Y escenas analizadas).
>
> **Lo más interesante:**
> - 💰 <hallazgo de precio o oferta del video, si lo hay>
> - 🎬 <patrón narrativo dominante>
> - 🔑 <hook estrella que se repite>
> - ⚡ <oportunidad para el alumno>
>
> **📂 Archivos generados** (abrí el primero):
> - [analysis.html](competitor-ads/<marca>/analysis.html) ⭐ **informe visual interactivo (doble click para abrir)**
> - [analysis.md](competitor-ads/<marca>/analysis.md) ← versión texto / markdown
> - [ads_summary.csv](competitor-ads/<marca>/ads_summary.csv) ← tabla para Excel
> - [video_analyses.json](competitor-ads/<marca>/video_analyses.json) ← datos crudos del análisis
> - [videos/](competitor-ads/<marca>/videos/) ← N videos en .mp4
>
> ¿Querés que compare con otro competidor, o que profundice en algún ad específico?

---

## 📦 Schema del output del actor de Apify

```jsonc
{
  "adArchiveID": "1354041633403636",
  "pageID": "825120160874613",
  "startDateFormatted": "2026-01-30T08:00:00.000Z",
  "endDateFormatted": "2026-02-04T08:00:00.000Z",
  "collationCount": 1,                              // variantes A/B
  "snapshot": {
    "pageName": "Notion",
    "body": { "text": "Copy del ad..." },
    "ctaText": "Learn more",
    "ctaType": "LEARN_MORE",
    "linkUrl": "https://...",
    "displayFormat": "VIDEO",                       // VIDEO | IMAGE | DCO | CAROUSEL
    "images": [{ "originalImageUrl": "..." }],
    "videos": [{ "videoHdUrl": "...", "videoSdUrl": "...", "videoPreviewImageUrl": "..." }],
    "cards": [],
    "brandedContent": { "pageName": "...", "pageProfileUri": "..." }
  }
}
```

**Heurística de "qué funciona"**: ads viejos que siguen activos = los que la marca está escalando. Ordená por `startDateFormatted` ascendente. `collationCount > 1` = variantes A/B (señal de inversión seria).

---

## ⚠️ Errores comunes y respuestas conversacionales

| Error | Qué le decís al alumno |
|---|---|
| Apify `401` | *"El token de Apify no me lo acepta. ¿Lo pegás de nuevo desde [acá](https://console.apify.com/settings/integrations)?"* |
| Apify `402` (sin saldo) | *"Se te acabó el saldo gratis de Apify. Podés cargar más [acá](https://console.apify.com/billing) ($5 USD mínimo) o esperar al mes que viene."* |
| Apify JSON vacío `[]` | *"No encontré ads activos de esa marca. Puede ser que no esté pauteando, que el nombre esté distinto, o que esté en otro país. Probemos con otro nombre o decime de qué país?"* |
| Gemini `429` | Esperar 30s y reintentar. No molestes al alumno. |
| Gemini `400 invalid api key` | *"La key de Gemini no me la acepta. ¿La regenerás en [aistudio.google.com/apikey](https://aistudio.google.com/apikey) y me la pegás?"* |
| Timeout en Apify | Reintentar con `resultsLimit: 50`. |

---

## 🛑 Lo que NO hace esta skill

- No scrapea TikTok ni LinkedIn (solo Meta = Facebook + Instagram).
- No estima performance real (`spend`/`impressions` solo vienen en ads políticos / EU).
- No usa navegador (Claude in Chrome / computer-use). Todo por API.
- No sube los datos extraídos a ningún lado. Todo queda en la máquina del alumno.

---

## 💡 Ejemplos de uso

- *"https://www.facebook.com/aivideoskool"* (solo el link → todo automático)
- *"Analizá los ads de Glovo en Argentina"*
- *"Comparame Rappi y PedidosYa, qué dolores usan?"*
- *"Bajame los videos top de Notion y decime qué hooks usan"*
- *"Mostrame qué CTAs usa más Asana"*

---

## 🔁 Si el alumno corre por segunda vez

Si `.env` ya tiene ambas claves, **NO repitas el onboarding**. Saludá corto y arrancá:

> 👋 Buenas. Arrancando análisis de **<marca>**... ⏳

Si una clave dejó de funcionar (ej. revoked), el flujo de validación lo va a detectar y vas a pedirla de nuevo conversacionalmente.
