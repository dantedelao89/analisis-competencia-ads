# 🕵️ Análisis de Competencia — Facebook & Instagram Ads

Espía los anuncios que tu competidor está corriendo en **Facebook e Instagram** ahora mismo. Le pasas el link de la página y Claude te entrega un dashboard completo con cada video transcrito, traducido al español y analizado escena por escena.

**Tú solo pegas el link de Facebook del competidor. Claude hace todo lo demás.**

---

## ⚠️ ¿Para qué sirve y para qué no?

✅ **Funciona con:** Facebook Ads e Instagram Ads (de la Meta Ad Library)

❌ **No funciona con:** TikTok, YouTube, LinkedIn, Reels orgánicos, posts normales

Si quieres usarla para TikTok u otra red, tienes que cambiar el "actor" de Apify dentro de `scripts/process_all_videos.py`. Hay actors para todo en https://apify.com/store

---

## 🚀 Cómo usarla (5 minutos)

### Paso 1 — Instala Claude Code

Si no lo tienes todavía:
👉 https://docs.claude.com/en/docs/claude-code/install

### Paso 2 — Crea una carpeta vacía y entra a ella

Por ejemplo en tu Escritorio:

```
mkdir analisis-competencia
cd analisis-competencia
```

### Paso 3 — Abre Claude Code

```
claude
```

### Paso 4 — Copia y pega este mensaje en Claude

```
Clona este repositorio en mi carpeta actual y mueve todos los archivos
(incluyendo la carpeta .claude) a la raíz del proyecto:

https://github.com/dantedelao89/analisis-competencia-ads

Después dime qué necesitas de mí para empezar.
```

Claude va a clonar el repo y te va a pedir **dos llaves gratuitas** (Apify + Gemini). Te guía paso a paso en el chat. **Tú no tocas ningún archivo.**

### Paso 5 — Pásale el link de tu competidor

Cuando Claude te confirme que ya está todo listo, simplemente escribe el link de la página de Facebook del competidor. Cualquiera de estos formatos funciona:

```
https://www.facebook.com/aivideoskool
https://www.facebook.com/profile.php?id=61577852912181
https://www.facebook.com/martinvelardefilm
```

**Eso es todo.** En 5 minutos tienes un dashboard listo.

---

## 🔑 ¿Dónde pongo mis API keys?

Tienes dos opciones:

### Opción A (recomendada) — Deja que Claude te guíe

La primera vez, Claude detecta que faltan las llaves y te las pide en el chat con instrucciones paso a paso. Tú solo pegas las llaves en el chat, Claude las guarda automáticamente en un archivo `.env` dentro de tu carpeta. **No tocas ningún archivo manualmente.**

### Opción B — Crearlas tú mismo

Si prefieres hacerlo a mano:

1. Copia el archivo `.env.example` y renómbralo a `.env`
2. Abre `.env` con cualquier editor de texto
3. Reemplaza los placeholders con tus llaves reales:

```
APIFY_TOKEN=apify_api_xxxxxxxxxxxxxxxx
GEMINI_API_KEY=AIzaxxxxxxxxxxxxxxxxxx
```

⚠️ **Importante:** No dejes espacios alrededor del `=`, ni comillas alrededor de las llaves. Si te equivocas, no te preocupes — la skill detecta y corrige automáticamente los errores de formato más comunes.

### ¿De dónde saco las llaves?

**Token de Apify** (para descargar los anuncios):
- Crea cuenta gratis: https://console.apify.com/sign-up
- Ve a: https://console.apify.com/settings/integrations
- Copia el token que empieza con `apify_api_...`

**API key de Google Gemini** (para analizar los videos):
- Entra a: https://aistudio.google.com/apikey
- Haz click en **"Create API key"**
- Copia la llave (empieza con `AIza...`)

El archivo `.env` nunca se sube a internet — está protegido por `.gitignore`. Solo necesitas configurar las llaves **una vez**.

---

## 📂 ¿Qué te entrega Claude?

Por cada competidor que analices, vas a tener:

```
competitor-ads/
└── nombre-del-competidor/
    ├── 🎨 analysis.html        ← Abre este (doble click)
    ├── 📊 analysis.md
    ├── 📈 ads_summary.csv
    ├── 🎬 video_analyses.json
    └── 🎞️ videos/  (todos los .mp4 en HD)
```

El `analysis.html` es un dashboard interactivo con:
- **Lista de creativos** a la izquierda con filtros por audiencia (frío/tibio/retargeting)
- **Video embebido** que puedes reproducir directamente
- **Hook** (primeros 3 segundos analizados)
- **Transcripción original y traducción al español**
- **Desglose escena por escena** con timestamps, qué se ve, qué se dice y qué texto aparece en pantalla
- **Clasificación de audiencia** con razonamiento (por qué este ad es para frío, tibio o retargeting)

### Dashboard comparativo

Si analizaste varios competidores, pídele a Claude:

```
Hazme el dashboard cross-competidor
```

Te genera un `dashboard.html` con:
- **Resumen** con KPIs globales y competidores que están lanzando ads nuevos
- **Timeline** con qué tan viejo es el ad más antiguo de cada competidor (los que llevan más tiempo activos son los ganadores escalados)
- **Comparativa lado a lado** de todas las métricas
- **Explorador de videos** filtrable con todos los creativos de todos los competidores

---

## 💰 Costo

| Servicio | Plan gratuito |
|---|---|
| **Apify** | $5 USD gratis al registrarte (~16,000 anuncios) |
| **Gemini** | 1,500 análisis por día gratis |

Un análisis típico cuesta **menos de $0.01 USD**. Con las cuentas gratuitas te alcanza para mucho.

---

## 💡 Ejemplos de lo que le puedes pedir a Claude

- `https://www.facebook.com/notion` ← lo más simple, solo el link
- *"Analiza los ads de Glovo en México"*
- *"Compara Notion, Asana y ClickUp"*
- *"Bájame los videos top del nicho de fitness"*
- *"Hazme el dashboard con todos los competidores que analicé"*
- *"¿Qué competidor tiene los ads que llevan más tiempo activos?"*
- *"Búscame ads en español dentro de los competidores que ya analicé"*

---

## 🆘 Si algo sale mal

Solo dile a Claude en el chat: *"Me dio error"* o *"No encontró nada"*. Él diagnostica y arregla.

Los errores más comunes ya están cubiertos automáticamente:
- ✅ Formato del `.env` (espacios, comillas, saltos de línea de Windows)
- ✅ URLs de página vs. URLs de Ad Library (acepta cualquier formato)
- ✅ Validación de las llaves antes de gastar créditos
- ✅ Detección de competidores con muchos ads (filtra automáticamente a los top 30 más relevantes)

---

## 📄 Licencia

MIT — úsalo libremente.

Creado por [@dantedelao89](https://github.com/dantedelao89)
