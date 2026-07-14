# Esercizi Azure AI Content Understanding

Laboratorio pratico **da portale** (Azure AI Foundry → Content Understanding / Foundry Tools).
Livello: intermedio-avanzato. Non "base base": si lavora con schemi custom, campi *generate*,
classificazione + splitting e segmentazione semantica.

## Contenuto della cartella
```
Esercizi-Azure-Content-Understanding/
├─ README.md                      ← questo file (panoramica + timing)
├─ 00-SETUP.md                    ← preparazione portale e prerequisiti
├─ 01-documenti.md                ← Documenti: A guidato + B autonomo
├─ 02-immagini.md                 ← Immagini: A guidato + B autonomo
├─ 03-classificazione-segmentazione.md ← Classify/split: A guidato + B autonomo + C bonus RAG
├─ sample-documents/              ← file di esempio pronti all'uso
│  ├─ invoice.pdf
│  ├─ mixed_financial_docs.pdf
│  ├─ receipt.png
│  └─ pieChart.jpg
└─ schemi-json/                   ← schemi di riferimento (solo esercizi "A" guidati)
   ├─ 01-invoice-schema.json
   ├─ 02-chart-schema.json
   └─ 03-classifier-categories.json
```

Un file **per categoria**. Ogni file contiene: **A** (guidato, con schema fornito) e
**B** (autonomo, schema da progettare); il file 03 aggiunge **C** (bonus RAG).

## Timing consigliato
| File | Esercizio | Durata |
|---|---|---|
| 00-SETUP | Setup portale + risorsa Foundry | 15 min |
| 01-documenti | A guidato (30) + B autonomo (30) | 60 min |
| 02-immagini | A guidato (25) + B autonomo (25) | 50 min |
| 03-classificazione-segmentazione | A guidato (35) + B autonomo (35) + C bonus (15) | 85 min |

**Percorso ~2h (guidato):** 00 → 01·A → 02·A → 03·A → 03·C.
**Percorso completo (~3h30):** aggiungi gli esercizi **B** (autonomi) di ogni file.

## Obiettivi di apprendimento
- Costruire **schemi custom** con campi `extract`, `generate`, `classify`.
- Interpretare **confidence score** e **grounding** per human-review.
- Gestire un **classifier** con **splitting** di PDF multi-documento.
- Impostare una pipeline **classify → route → extract**.
- Produrre **chunk semantici** con immagini per scenari RAG.

## Fonti dei sample
- `invoice.pdf`, `mixed_financial_docs.pdf`, `receipt.png`, `pieChart.jpg`:
  repo ufficiale `Azure-Samples/azure-ai-content-understanding-python` (cartella `data/`).
- Dataset pubblici extra (opzionali, per volume): RVL-CDIP, FUNSD, DocLayNet, Unsplash — vedi 00-SETUP.md.

> Nota: gli esercizi sono pensati per l'esperienza **portale/Studio**. Gli schemi JSON in `schemi-json/`
> sono da usare come riferimento per i campi da definire nella UI (o da incollare dove la UI lo consente).
