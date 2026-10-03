# Esercizio 2 - Analyzer dal portale oppure da template

**Obiettivo:** ottenere un analyzer riutilizzabile per il conto hotel e salvarne
la definizione nella repo locale. Prima copia i blocchi **1 e 3** dell'esercizio 1
(root e configurazione). La soluzione li include gia.

## 1. Scegli un percorso

**Percorso A, portale:** apri [Microsoft Foundry](https://ai.azure.com), seleziona
la risorsa configurata in `.env` e apri Content Understanding. Crea un analyzer
documentale, carica la copia `sample_hotel_bill_mario_rossi.pdf`, definisci i campi
del template e prova l'estrazione. **Salva/pubblica l'analyzer**, non soltanto il
progetto di lavoro nel portale, e copia il suo analyzer ID.
I nomi dei pulsanti possono cambiare; il controllo decisivo e che
`client.get_analyzer(analyzer_id=...)` riesca sulla stessa risorsa.
Imposta `MODALITA = "portale"` sotto: il codice **scarica con lo SDK** il JSON
dell'analyzer creato nel portale. Non serve cercare un pulsante di export.

**Percorso B, template:** copia `esercizi/analyzer-template.json` in
`esercizi/analyzer-personalizzato.json` e leggilo nell'editor. E gia adattato
al conto hotel: `Hotel`, `Ospite`, `NumeroConto`, `Camera`, `Arrivo`, `Partenza`,
`Movimenti`, `TotaleAddebiti`, `TotaleAccrediti`, `Saldo`, `Sintesi`.
Modifica almeno una descrizione per chiarire cosa estrarre e scegli un ID univoco.
Le date statunitensi MM-DD-YY non vanno interpretate come DD-MM-YY.
`models` contiene nomi logici: controlla i default model mappings CU nel README.

Il template non codifica i valori attesi e non classifica automaticamente il
documento come "pagato" sulla sola presenza di una riga di pagamento.
`estimateFieldSourceAndConfidence` supporta i campi `extract`; `generate` e
riservato alla sintesi. Saldo e totali sono campi distinti.

<!-- cell:choice -->
```python
MODALITA = "template"  # "template" oppure "portale"
ANALYZER_ID = "hotel-bill-mario-rossi-v1"  # Scegli un ID tuo, non condiviso.
TEMPLATE_PATH = ROOT / "esercizi" / "analyzer-personalizzato.json"

if MODALITA not in {"template", "portale"}:
    raise ValueError("MODALITA deve essere template oppure portale.")
if not ANALYZER_ID.strip() or ANALYZER_ID.startswith("prebuilt-"):
    raise ValueError("Usa un ID di analyzer personalizzato.")
if MODALITA == "template":
    if not TEMPLATE_PATH.exists():
        TEMPLATE_PATH.write_text(
            (ROOT / "esercizi" / "analyzer-template.json").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
    print("Apri e personalizza prima di continuare:", TEMPLATE_PATH)
```

## 2. Crea o recupera l'analyzer e scaricalo

Esegui **dopo aver salvato** le modifiche al template. La creazione e
un'operazione asincrona del servizio: `poller.result()` ne attende il termine.
`allow_replace=False` impedisce sovrascritture: se l'ID esiste gia, scegli un
nuovo ID o passa a `portale` per recuperarlo. Non intercettiamo gli errori Azure.

<!-- cell:create -->
```python
from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import ContentAnalyzer
from azure.core.credentials import AzureKeyCredential

with ContentUnderstandingClient(
    endpoint=CU_ENDPOINT, credential=AzureKeyCredential(CU_KEY)
) as client:
    if MODALITA == "template":
        definition = json.loads(TEMPLATE_PATH.read_text(encoding="utf-8"))
        analyzer = ContentAnalyzer(definition)
        poller = client.begin_create_analyzer(
            analyzer_id=ANALYZER_ID,
            resource=analyzer,
            allow_replace=False,
        )
        poller.result()
    analyzer = client.get_analyzer(analyzer_id=ANALYZER_ID)

if not analyzer.field_schema or not analyzer.field_schema.fields:
    raise ValueError("L'analyzer selezionato non contiene uno schema di campi.")

(OUTPUT / "analyzer.json").write_text(
    json.dumps(analyzer.as_dict(), ensure_ascii=False, indent=2), encoding="utf-8"
)
(OUTPUT / "analyzer-selection.json").write_text(
    json.dumps(
        {"analyzer_id": ANALYZER_ID, "endpoint": CU_ENDPOINT.rstrip("/")},
        indent=2,
    ),
    encoding="utf-8",
)
print("Analyzer salvato:", ANALYZER_ID)
print("Campi:", ", ".join(analyzer.field_schema.fields))
```

## 3. Ricarica l'analyzer selezionato

Questo blocco serve anche come preparazione di 3-6. Legge **file persistiti**,
non variabili di un altro kernel. La definizione JSON e una copia locale;
l'analisi usa l'ID della risorsa Azure, non invia il JSON a ogni chiamata.
Se cambi endpoint, esegui nuovamente 2 sulla nuova risorsa.

<!-- cell:selection -->
```python
selection_path = OUTPUT / "analyzer-selection.json"
if not selection_path.is_file():
    raise FileNotFoundError("Completa prima l'esercizio 2: manca la selezione analyzer.")
selection = json.loads(selection_path.read_text(encoding="utf-8"))
if selection["endpoint"] != CU_ENDPOINT.rstrip("/"):
    raise ValueError("L'analyzer salvato appartiene a un altro endpoint. Riesegui 2.")
ANALYZER_ID = selection["analyzer_id"]
print("Analyzer selezionato:", ANALYZER_ID)
```

## Cosa verificare

- `soluzioni/output/analyzer.json` contiene `baseAnalyzerId`, `config`,
  `fieldSchema` e `models`.
- L'analyzer e recuperabile sulla risorsa corretta.
- Sai spiegare perche un file JSON locale non e da solo un analyzer distribuito.
- Per una modifica successiva crea una nuova versione con un ID diverso; gli
  esercizi successivi useranno la nuova selezione salvata.
