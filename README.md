# 🕵️ Análisis de Competencia — Ads de Facebook & Instagram

> Espía y analizá los anuncios que tu competidor está corriendo en **Facebook e Instagram** en este momento. Te entrega un dashboard interactivo con cada video transcrito, traducido al español y desglosado escena por escena.

**Cero código. Cero terminal. Vos solo pegás un link y conversás con Claude.**

---

## 🎬 ¿Qué hace exactamente?

Vos le pasás el link de la página de Facebook de un competidor:

```
https://www.facebook.com/aivideoskool
```

Y Claude te entrega, automáticamente:

- 📥 **Todos los ads activos** de esa marca (extraídos de la Meta Ad Library)
- 🎞️ **Los videos descargados** en tu computadora (.mp4 en HD)
- 🎙️ **Transcripción literal** de lo que dice cada video
- 🇪🇸 **Traducción al español** si está en otro idioma
- 🎬 **Desglose escena por escena**: qué se ve, qué se dice, qué texto aparece en pantalla, cuánto dura cada plano
- 🧊🌡️🔥 **Clasificación de cada ad**: ¿es para audiencia fría (captación), tibia o retargeting?
- 💰 **Precios mencionados** dentro de los videos (que casi nunca están en el copy escrito)
- 📊 **Dashboard HTML interactivo** para comparar todos los competidores lado a lado

---

## ⚠️ Importante: ¿para qué sirve y para qué NO?

✅ **SIRVE para:**
- Anuncios pagos en **Facebook** (Meta Ad Library)
- Anuncios pagos en **Instagram** (Meta Ad Library cubre ambos)

❌ **NO sirve (todavía) para:**
- Contenido **orgánico** de Facebook/Instagram (posts normales, reels que no son ads pagos)
- **TikTok Ads Library**
- **YouTube Ads**
- **LinkedIn Ads**

Si querés analizar otras fuentes, podés cambiar el "actor" de Apify que usamos en `scripts/process_all_videos.py` (línea del `curl` que llama a `apify~facebook-ads-scraper`). Hay actors de TikTok, LinkedIn y YouTube en el [marketplace de Apify](https://apify.com/store).

---

## 🚀 CÓMO USARLA — paso a paso para principiantes

### 📋 Lo que vas a necesitar antes de empezar

| Cosa | ¿Es gratis? | ¿Dónde la conseguís? |
|---|---|---|
| **Claude Code** instalado | Sí | https://docs.claude.com/en/docs/claude-code/install |
| **Cuenta de Apify** (para bajar ads) | Sí — te regalan ~$5 USD al registrarte | https://console.apify.com/sign-up |
| **API key de Google Gemini** (para analizar videos) | Sí — 1.500 análisis por día gratis | https://aistudio.google.com/apikey |

⏱️ **Tiempo total de setup la primera vez: 5-10 minutos.**

---

### 1️⃣ Instalá Claude Code (solo la primera vez)

Si nunca usaste Claude Code, entrá acá y seguí las instrucciones para tu sistema operativo:
👉 https://docs.claude.com/en/docs/claude-code/install

Es una herramienta de Anthropic que te permite hablarle a Claude desde una terminal y que ejecute código por vos.

---

### 2️⃣ Creá una carpeta vacía en tu computadora

Por ejemplo en tu escritorio, llamala `analisis-competencia` o como quieras. Esa carpeta va a alojar el proyecto.

---

### 3️⃣ Abrí Claude Code en esa carpeta

Abrí una terminal (Terminal en Mac, PowerShell en Windows), navegá a la carpeta y escribí:

```bash
claude
```

Vas a ver el chat de Claude listo para recibir mensajes.

---

### 4️⃣ Pegale ESTE prompt a Claude (copiá y pegá tal cual)

```
Hola Claude, quiero usar la skill "competitive-ads-extractor" para
analizar anuncios de competidores en Facebook e Instagram.

Por favor:
1. Cloná este repo público en la carpeta actual:
   https://github.com/dantedelao89/analisis-competencia-ads
2. Movemé todos los archivos del repo (incluyendo la carpeta .claude)
   a la raíz de mi proyecto.
3. Después contame qué necesitás de mí para empezar a analizar.
```

Claude va a:
- Clonar el repo
- Mover todo a tu carpeta
- Detectar que falta tu archivo `.env` con las API keys
- **Te va a guiar conversacionalmente** para crear cuenta en Apify y en Google AI Studio, copiar tus tokens y pegarlos en el chat. Vos no tocás archivos.

---

### 5️⃣ Pegale el link de un competidor y listo

Cuando Claude te confirme que las API keys están guardadas, simplemente escribí:

```
Analizá los ads de https://www.facebook.com/<paginaDelCompetidor>
```

O en castellano natural:

```
Espía los anuncios que está corriendo Notion en Estados Unidos
```

**Eso es todo.** Claude se encarga del resto (~5 min):
1. 🔍 Extrae los ads activos vía Apify
2. 📥 Descarga los videos en HD
3. 🧠 Los analiza uno por uno con Gemini 3 Flash
4. 🧊🌡️🔥 Clasifica cada ad por etapa del funnel
5. 📊 Genera un informe HTML interactivo + Markdown + CSV
6. 🎯 Te resume los hallazgos clave

---

## 📂 Qué archivos vas a tener después de cada análisis

```
tu-carpeta/
└── competitor-ads/
    └── <nombre-competidor>/
        ├── 🎨 analysis.html        ⭐ ABRÍ ESTE PRIMERO (doble click)
        ├── 📊 analysis.md          versión texto del informe
        ├── 📈 ads_summary.csv      tabla para Excel/Google Sheets
        ├── 💾 ads_raw.json         datos crudos del extractor
        ├── 🎬 video_analyses.json  análisis estructurado por video
        └── 🎞️ videos/               todos los .mp4 originales en HD
```

Y al final, si analizaste varios competidores, generá el **dashboard cross-competidor**:

```
Hacé el dashboard cross-competidor por favor
```

Te crea `dashboard.html` en la raíz del proyecto con timeline, comparativa lado a lado y explorador de videos filtrable.

---

## 💰 ¿Cuánto cuesta usarla?

| Servicio | Plan gratuito | Para qué te alcanza |
|---|---|---|
| **Apify** | $5 USD al registrarte (sin tarjeta) | ~16.000 ads extraídos |
| **Gemini** | 1.500 requests/día gratis | Cientos de videos analizados por día |
| **Total** | **Gratis para empezar** | Análisis típico = **menos de $0.01 USD** |

---

## 💡 Qué le podés pedir a Claude

Una vez que está todo configurado, podés pedirle cualquiera de estas cosas en castellano natural:

- *"Pegá un link de Facebook directamente"* — el más simple
- *"Analizá los ads de [marca] en [país]"*
- *"Compará Notion vs Asana vs ClickUp, qué pain points usa cada uno"*
- *"Cuántos ads tiene corriendo Shopify ahora mismo?"*
- *"Bajame los videos top de los anuncios de Glovo en Argentina"*
- *"Mostrame qué CTA usan más los anuncios de [marca]"*
- *"Qué hooks (primeros 3 segundos) están usando en el nicho de [X]?"*
- *"Hacé el dashboard comparativo con todos los competidores que analicé"*
- *"¿Qué competidor tiene los ads que llevan más tiempo activos?"*

---

## 🆘 Si algo no funciona

Cualquier error que veas, **decíselo a Claude en el chat**:

- *"Me dio error en la extracción"*
- *"No encontró ads"*
- *"El video no se ve en el HTML"*

Claude diagnostica y resuelve sin que vos toques archivos.

---

## 🔒 Sobre tus API keys

Tus tokens de Apify y Gemini se guardan en un archivo `.env` que **NUNCA se sube a internet** (está en `.gitignore`). Si compartís tu carpeta con alguien, esa persona pone sus propias keys.

⚠️ **Nunca compartas tu `.env` por chat, email o GitHub.**

---

## 🛠️ Para usuarios avanzados — cambiar el actor (TikTok, LinkedIn, etc.)

Este proyecto usa por defecto el actor `apify~facebook-ads-scraper` que sólo cubre Meta Ad Library (Facebook + Instagram).

Para usar otra fuente:

1. Buscá un actor en https://apify.com/store (ej. `apify~tiktok-scraper`)
2. Cambialo en `scripts/process_all_videos.py` (línea del `curl` al endpoint)
3. Ajustá el schema de input si es distinto
4. El resto del pipeline (Gemini, clasificación, dashboard) sigue funcionando igual

---

## 🧑‍💻 ¿Cómo funciona por debajo?

Para los que tengan curiosidad:

1. **Apify** se mete en https://www.facebook.com/ads/library/ y devuelve los ads en JSON estructurado.
2. **Python** descarga los `.mp4` de los videos a tu carpeta.
3. **Gemini 3 Flash Preview** analiza cada video como input multimodal (audio + visual + texto en pantalla) y devuelve un JSON con: transcripción, traducción al español, escena por escena con timestamps, hook, CTA verbal, precio mencionado, social proof, audiencia objetivo, etc.
4. **Scripts de Python** ensamblan todo en `analysis.md`, `analysis.html` y `dashboard.html`.

Todo se ejecuta **localmente en tu máquina**. No hay servidores intermedios. Tus datos no salen de tu computadora (excepto las llamadas a Apify y Google).

---

## 📦 Estructura del proyecto

```
analisis-competencia/
├── .claude/skills/competitive-ads-extractor/SKILL.md   ← Skill para Claude Code
├── scripts/
│   ├── process_all_videos.py     ← Descarga + Gemini
│   ├── classify_audience.py      ← Clasifica cold/warm/retargeting
│   ├── build_analysis.py         ← Genera analysis.md
│   ├── build_html.py             ← Genera analysis.html (por competidor)
│   ├── build_dashboard.py        ← Genera dashboard.html (cross-competidor)
│   ├── filter_top_ads.py         ← Filtra a top N long-runners
│   └── competitor_timeline.py    ← Reporte de timeline en consola
├── .env.example                  ← Plantilla de credenciales
├── .gitignore
├── README.md                     ← Este archivo
└── LICENSE                       ← MIT
```

---

## 📄 Licencia

MIT — usá esto para lo que quieras. Atribución valorada pero no obligatoria.

---

## 🙋 Contacto / créditos

Creado por [@dantedelao89](https://github.com/dantedelao89) con asistencia de Claude Code.

Si esta herramienta te sirvió, una ⭐ en el repo ayuda a que más gente la encuentre.
