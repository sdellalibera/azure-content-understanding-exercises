# 01 — Analisi Documenti

**Categoria:** documenti · **Template portale:** Document

| Esercizio | Modalità | Schema | Sample |
|---|---|---|---|
| A | Guidato | fornito (`schemi-json/01-invoice-schema.json`) | `invoice.pdf` |
| B | Autonomo | **da progettare** | `receipt.png` |

---

## Esercizio A — Field extraction avanzata (guidato)

**Obiettivo:** estrarre campi strutturati con confidence + grounding, includendo campi *generate* (dedotti, non copiati).

### Passi
1. `esercizi-cu` → **Create analyzer** → template **Document**.
2. Importa/replica i campi da `schemi-json/01-invoice-schema.json`.
3. **Run/Analyze** su `invoice.pdf`.

### Schema (riepilogo)
| Campo | Tipo | Metodo |
|---|---|---|
| `vendor_name`, `invoice_id`, `currency` | string | extract |
| `invoice_date` | date | extract |
| `invoice_total` | number | extract |
| `line_items` | array (`description`,`quantity`,`unit_price`,`amount`) | extract |
| `payment_terms_days` | integer | **generate** (es. "Net 30" → 30) |
| `is_overdue` | boolean | **generate** (data vs oggi) |
| `risk_note` | string | **generate** (se mancano dati chiave) |

### Verifica
- [ ] **Grounding**: cliccando un valore si evidenzia la regione nel PDF.
- [ ] **Confidence**: annotati i campi a bassa confidence.
- [ ] Campi *generate* dedotti, non copiati.
- [ ] `line_items` popolato con i 4 sotto-campi.

### Challenge
- Soglia confidence a 0.8 → quali campi vanno in human-review?
- `risk_note` scatta solo se manca `invoice_total` o `invoice_date`.
- Riusa lo schema su `receipt.png`: regge?

---

## Esercizio B — Record spese (autonomo, schema da progettare)

> Nessun JSON fornito: **progetti tu i campi** (tipo + metodo + description).

**Scenario:** team *Expense Management*. Trasforma uno scontrino in un record pronto per il rimborso, con controlli di policy.

### Requisiti (l'analyzer deve produrre)
1. Esercente + dati transazione (chi/quando/dove).
2. Dettaglio voci con importi.
3. Ripartizione imponibile / imposta / totale.
4. **Categoria di spesa** (classify: pasti/trasporti/cancelleria/altro).
5. **Flag soglia** booleano dedotto (es. > 50 → serve giustificativo).
6. **Nota di conformità** generata (cosa manca/verificare).

### Vincoli (parte non base)
- Almeno **1 array**, **1 classify**, **2 generate**.
- Description efficaci; gestisci i dati mancanti nei campi generate.

### Verifica
- [ ] Grounding sui campi extract.
- [ ] Categoria di spesa coerente con le voci.
- [ ] Flag soglia corretto al variare dell'importo.
- [ ] Nota di conformità utile a un revisore.

### Challenge
- Rendi lo schema riutilizzabile anche su `invoice.pdf` (campi opzionali).
- Aggiungi `confidence_flag` (generate) per marcare i record "da rivedere".
