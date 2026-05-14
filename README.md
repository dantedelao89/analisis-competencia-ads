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

Cuando Claude te confirme que ya está todo listo, simplemente escribe:

```
https://www.facebook.com/aivideoskool
```

(reemplaza por el link del competidor que quieras analizar)

**Eso es todo.** En 5 minutos tienes un dashboard listo.

---

## 🔑 ¿Dónde pongo mis API keys?

La primera vez que uses la skill, Claude te va a pedir dos llaves:

### 1. Token de Apify (para descargar los anuncios)

- Crea cuenta gratis: https://console.apify.com/sign-up
- Ve a: https://console.apify.com/settings/integrations
- Copia el token que empieza con `apify_api_...`
- **Pégaselo a Claude en el chat** (no tienes que editar ningún archivo)

### 2. API key de Google Gemini (para analizar los videos)

- Entra a: https://aistudio.google.com/apikey
- Haz click en **"Create API key"**
- Copia la llave (empieza con `AIza...`)
- **Pégasela a Claude en el chat**

Claude guarda las dos llaves automáticamente en un archivo `.env` dentro de tu carpeta. Ese archivo nunca se sube a internet (está protegido por `.gitignore`). Solo lo necesitas configurar **una vez**.

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

Y si analizaste varios competidores, pídele a Claude:

```
Hazme el dashboard cross-competidor
```

Te genera un `dashboard.html` con timeline, comparativa lado a lado y explorador de todos los videos.

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

---

## 🆘 Si algo sale mal

Solo dile a Claude en el chat: *"Me dio error"* o *"No encontró nada"*. Él diagnostica y arregla.

---

## 📄 Licencia

MIT — úsalo libremente.

Creado por [@dantedelao89](https://github.com/dantedelao89)
