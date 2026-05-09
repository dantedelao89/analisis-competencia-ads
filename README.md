# 🕵️ Análisis de Competencia — Ads de Facebook / Instagram

Herramienta para espiar y analizar la publicidad de tus competidores en Meta Ad Library (Facebook + Instagram).

**Vos solo pegás el link de la página de Facebook del competidor — Claude se encarga de TODO** (extraer ads, descargar videos, transcribirlos, traducirlos al español, analizar escena por escena, y entregarte un informe ejecutivo).

> 🆓 **Cero código. Cero terminal.** Hablás en castellano, te entrega resultados.

---

## 🚀 Cómo empezar (5 minutos)

### 1️⃣ Instalá Claude Code (si no lo tenés)

👉 https://docs.claude.com/en/docs/claude-code/install

### 2️⃣ Cloná este proyecto

Abrí la terminal y pegá:

```bash
git clone <URL_DEL_REPO>
cd analisis_competencia
```

### 3️⃣ Abrí Claude Code en la carpeta

```bash
claude
```

### 4️⃣ Pegale el link del competidor

Solo escribí algo como:

```
https://www.facebook.com/aivideoskool
```

O algo en castellano:

```
analizá los ads de Notion en Estados Unidos
```

**Listo.** Claude te va a guiar paso a paso pidiéndote 2 llaves gratis (Apify y Google Gemini). Solo se piden la primera vez.

---

## 🎬 Lo que vas a recibir

Después de ~5 minutos, en la carpeta `competitor-ads/<marca>/` vas a tener:

| Archivo | Qué contiene |
|---|---|
| 🎨 **`analysis.html`** ⭐ | **Informe visual interactivo** (doble click para abrir en navegador). Videos embebidos, badges de audiencia, escenas colapsables, tema oscuro moderno |
| 📊 `analysis.md` | Versión texto plano del mismo informe (para editor / GitHub) |
| 📈 `ads_summary.csv` | Tabla limpia para abrir en Excel / Google Sheets |
| 💾 `ads_raw.json` | Datos crudos por si querés re-analizar después |
| 🎞️ `videos/` | Los `.mp4` originales de los ads en HD |
| 🎬 `video_analyses.json` | Análisis estructurado por video (audio, visual, on-screen text, escenas) |

---

## 💡 Qué le podés pedir a Claude

- *Pegá un link*: `https://www.facebook.com/<paginaDelCompetidor>`
- *"Analizá los ads de [marca] en [país]"*
- *"Comparame [marca A] vs [marca B], qué pain points usa cada uno?"*
- *"Cuántos ads tiene corriendo [marca] ahora?"*
- *"Qué hooks usan en los primeros 3 segundos los ads top de [marca]?"*
- *"Mostrame qué texto en pantalla usa [marca]"*
- *"Traducime al español todos los ads de [marca]"*

---

## 💰 ¿Cuánto cuesta?

| | Plan gratis incluye | Para qué te alcanza |
|---|---|---|
| **Apify** | $5 USD de saldo (sin tarjeta) | ~16.000 ads extraídos |
| **Gemini** | 1.500 requests/día | Cientos de videos analizados |

**Cada análisis típico cuesta menos de $0.01 USD.** Con las cuentas gratis te alcanza para mucho.

---

## 🆘 Algo no funciona

Cualquier error, **decíselo a Claude en el chat** (*"me dio error"*, *"no encontró nada"*, etc.) y te ayuda a resolverlo. **No necesitás tocar archivos ni código.**

---

## 🔒 Sobre tus llaves

Tus tokens de Apify y Gemini se guardan en un archivo `.env` que **nunca** se sube a internet (está en `.gitignore`). Si compartís este proyecto con alguien, esa persona usa sus propias llaves.

---

## 🛠️ Qué hace por debajo (para curiosos)

1. **Apify** se mete en https://www.facebook.com/ads/library/ y baja los ads del competidor en JSON estructurado.
2. **Python** descarga los `.mp4` de los videos.
3. **Gemini 3 Flash Preview** mira cada video y devuelve un análisis JSON con transcripción, traducción al español, desglose escena por escena (timestamp + visual + audio + texto en pantalla + rol narrativo).
4. **Un script** junta todo en un `analysis.md` legible.

Todo se ejecuta en tu máquina. No hay servidores intermedios.
