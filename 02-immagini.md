# 02 — Analisi Immagini

**Categoria:** immagini · **Template portale:** Image

| Esercizio | Modalità | Schema | Sample |
|---|---|---|---|
| A | Guidato | fornito (`schemi-json/02-chart-schema.json`) | `pieChart.jpg` (+ 1 foto Unsplash) |
| B | Autonomo | **da progettare** | `pieChart.jpg` + 1 foto reale |

---

## Esercizio A — Chart + scene understanding (guidato)

**Obiettivo:** oltre l'OCR — interpretare contenuto visuale, estrarre dati da un grafico e generare insight.

### Parte A.1 — Chart
1. **Create analyzer** → template **Image**.
2. Replica i campi da `schemi-json/02-chart-schema.json`.
3. Analizza `pieChart.jpg`.

| Campo | Tipo | Metodo |
|---|---|---|
| `chart_type` | string (pie/bar/line/other) | classify |
| `title` | string | extract |
| `data_series` | array (`label`,`value_percent`) | extract |
| `dominant_segment` | string | generate |
| `insight_summary` | string | generate |

**Verifica:** label+valori corrispondono alle fette · `dominant_segment` = fetta maggiore · `chart_type` = pie.

### Parte A.2 — Scene (challenge)
Su una foto Unsplash definisci: `main_objects` (array), `scene_category` (classify), `contains_text` (boolean), `caption` (generate). Confronta la ricchezza dell'output con il grafico.

---

## Esercizio B — Auto-tagging asset (autonomo, schema da progettare)

> Nessun JSON fornito: **un solo schema** deve gestire sia grafici sia foto reali.

**Scenario:** motore di auto-tagging per una libreria di asset visivi. Ogni immagine va descritta e catalogata, distinguendo grafici da foto.

### Requisiti
1. **Tipo immagine** (classify: chart/photo/screenshot/diagram).
2. Se grafico: **dati** (etichette+valori) + titolo.
3. Se foto: **soggetti principali** + **categoria scena**.
4. **Caption** generata per il catalogo.
5. **Tag** (array) per la ricerca.
6. `contains_text` (boolean, dedotto).

### Vincoli (parte non base)
- Campi opzionali + description "compila solo se pertinente" (evita dati allucinati).
- Almeno **1 array**, **1 classify**, **1 generate**.

### Verifica
- [ ] `pieChart.jpg`: dati estratti, tipo = chart.
- [ ] Foto reale: tag/categoria coerenti, nessun dato-grafico inventato.
- [ ] Caption usabile così com'è.

### Challenge
- Gerarchia scene (es. `outdoor > urban`): coerente?
- Tag su 2-3 immagini: abbastanza discriminanti per la ricerca?
