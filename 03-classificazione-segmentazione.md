# 03 — Classificazione & Segmentazione

**Categoria:** classificazione/segmentazione · **Template portale:** Document (Classifier)

| Esercizio | Modalità | Schema | Sample |
|---|---|---|---|
| A | Guidato | fornito (`schemi-json/03-classifier-categories.json`) | `mixed_financial_docs.pdf` |
| B | Autonomo | **da progettare** | `mixed_financial_docs.pdf` |
| C | Bonus | fornito (opzioni) | PDF con figure/tabelle |

> **Formato GA (importante).** La classificazione fa parte dell'*analyzer*: categorie in
> **`config.contentCategories`**, split con **`config.enableSegment: true`**, categoria
> **`Other`** obbligatoria, routing opzionale con **`analyzerId`** per categoria.
> Un file senza `config.contentCategories` → errore *"doesn't contain routing rules"*.

---

## Esercizio A — Classify + split + routing (guidato)

**Obiettivo:** un PDF con più documenti concatenati → segmentare, classificare, instradare.

### Parte A.1 — Classifier + splitting
1. **Classifiers** → **Create classifier** → **Import** `schemi-json/03-classifier-categories.json`.
2. Categorie: `Invoice`, `Bank_Statement`, `Receipt`, `Contract`, **`Other`** (obbligatoria).
3. `enableSegment: true` → segmenta in sotto-documenti (range di pagine).
4. Carica `mixed_financial_docs.pdf` ed esegui.

**Verifica:** ogni segmento ha `category` + `startPageNumber`/`endPageNumber`; numero segmenti = documenti reali; categorie corrette.

### Parte A.2 — Routing (classify → route → extract)
Collega un analyzer a una categoria via `analyzerId`:
```json
"Invoice": { "description": "...", "analyzerId": "esercizio1-invoice-analyzer" },
"Receipt": { "description": "...", "analyzerId": "prebuilt-receipt" }
```
- Categorie senza `analyzerId` → solo classificate.
- Riesegui → i segmenti instradati mostrano i campi estratti (es. `line_items` per Invoice).
- Extra: `omitContent: true` (top) restituisce solo l'output degli analyzer; supporto **gerarchico** fino a 5 livelli.

---

## Esercizio B — Smistatore PDF misti (autonomo, schema da progettare)

> Definisci tu il classifier (rispettando il formato GA sopra).

**Scenario:** un ufficio riceve pacchetti PDF misti. Costruisci uno smistatore che segmenta, classifica e instrada solo alcune categorie.

### Requisiti
1. Categorie con description distintive (a tua scelta) + **`Other`**.
2. **Splitting** attivo (segmenti con categoria + pagine).
3. **Routing selettivo**: ≥1 categoria con `analyzerId`, le altre solo classificate.
4. (Avanzato) livello **gerarchico**: un `analyzerId` che classifica sottotipi.

### Vincoli (parte non base)
- Description che disambiguino categorie simili (es. fattura vs ordine d'acquisto).
- Motiva quali categorie instradare (costo vs valore) e la gestione di `Other`.

### Verifica
- [ ] Numero segmenti = documenti reali.
- [ ] Ogni segmento: categoria + pagine coerenti.
- [ ] Segmenti instradati con campi estratti; gli altri no.
- [ ] Documento fuori categoria → `Other`.

### Challenge
- Crea un PDF misto tuo (`invoice.pdf` + pagina contratto + `receipt`) e verifica i confini.
- Introduci una categoria ambigua e affina le description finché la classificazione si stabilizza.

---

## Esercizio C — Bonus: segmentazione semantica per RAG

**Obiettivo:** chunk semantici (paragrafi, tabelle, figure) con immagini incorporate → base per un indice RAG.

### Passi
1. **Create analyzer** → template *content extraction / chunking* (Document).
2. Abilita: layout/structure, **estrazione immagini incorporate** con location, **semantic chunking**.
3. Esegui su `mixed_financial_docs.pdf` (o un PDF DocLayNet con figure/tabelle).

### Verifica
- [ ] Output in unità logiche (non un blob unico).
- [ ] Tabelle in forma strutturata.
- [ ] Immagini/figure con riferimenti di posizione (pagina + bounding region).

### A valle (concettuale)
Ogni chunk → documento in **Azure AI Search** (vettore + metadati); immagini → retrieval multimodale.
