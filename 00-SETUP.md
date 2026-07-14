# 00 — Setup portale e prerequisiti (~15 min)

## 1. Risorsa Azure
1. Vai su **https://ai.azure.com** (Azure AI Foundry).
2. Crea o seleziona un **Foundry resource** (Microsoft.CognitiveServicesAIFoundry) in una
   **region supportata** da Content Understanding, ad es.:
   - `westus`, `swedencentral`, `australiaeast` (verifica la disponibilità aggiornata nel portale).
3. Assicurati che il tuo utente abbia ruolo **Owner** o **Cognitive Services User/Contributor**.

## 2. Progetto Content Understanding
1. Nel portale apri **Content Understanding** (sotto *Foundry Tools* / *Tools*).
2. Crea un nuovo **progetto**: `esercizi-cu`.
3. Verifica di vedere le sezioni: **Analyzers** (Document/Image/Audio/Video) e **Classifiers**.

## 3. Storage (serve per Esercizio 3 batch)
- Collega o crea un **Azure Blob Storage**; caricheremo lì i PDF per il classifier/splitting.
- In alternativa, per singoli file, la UI consente l'upload diretto.

## 4. Sample locali
I file sono già in `sample-documents/`:
- `invoice.pdf` — fattura singola.
- `mixed_financial_docs.pdf` — **più documenti concatenati** (per classify + split).
- `receipt.png` — scontrino (documento-immagine).
- `pieChart.jpg` — grafico a torta (1283x617).

## 5. Dataset pubblici opzionali (per estendere gli esercizi)
- **RVL-CDIP** (16 classi documenti): https://adamharley.com/rvl-cdip/
- **FUNSD** (form annotati): https://guillaumejaume.github.io/FUNSD/
- **DocLayNet** (layout: titoli/tabelle/figure): https://github.com/DS4SD/DocLayNet
- **Unsplash** (immagini uso libero): https://unsplash.com

## Checklist prima di iniziare
- [ ] Progetto `esercizi-cu` creato
- [ ] Vedo Analyzers e Classifiers nella UI
- [ ] Blob storage collegato (per Es. 3)
- [ ] File sample accessibili
