# Esercizi Content Understanding

Cinque esercizi Jupyter per imparare Azure AI Content Understanding:

- [`esercizi`](esercizi): tracce, risultati attesi e celle vuote da completare.
- [`soluzioni`](soluzioni): notebook completi e autonomi, senza `main()` o chiamate
  a script esterni. Ogni soluzione crea e chiude il proprio client.

## Prerequisiti

1. Python 3.12 o successivo e Azure CLI.
2. Una risorsa Microsoft Foundry con Content Understanding in una regione
   supportata.
3. Il ruolo **Cognitive Services User** sulla risorsa.
4. Una risorsa gia configurata per gli analyzer del laboratorio.
5. Un accesso Azure locale valido tramite `az login`.

## Configurazione

Da PowerShell, nella root della repository:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m ipykernel install --prefix .venv --name cu-lab --display-name "Python (CU lab)"
Copy-Item .env.example .env
az login
```

Compila l'endpoint in `.env`. Gli ID degli analyzer custom sono già definiti
con la stessa nomenclatura e possono essere cambiati se necessario. L'analyzer
prebuilt `prebuilt-receipt.hotel` è invece scritto direttamente nel parametro
`analyzer_id` delle chiamate SDK, senza una variabile dedicata.

## Tracce e soluzioni

| Esercizio | Traccia | Soluzione |
| --- | --- | --- |
| 1. Ambiente e client | [01-client](esercizi/01-client.ipynb) | [01-client](soluzioni/01-client.ipynb) |
| 2. Analyzer prebuilt hotel | [02-analyzer](esercizi/02-analyzer.ipynb) | [02-analyzer](soluzioni/02-analyzer.ipynb) |
| 3. Analisi di due pagine | [03-analisi](esercizi/03-analisi.ipynb) | [03-analisi](soluzioni/03-analisi.ipynb) |
| 4. Custom e input LLM | [04-output-llm](esercizi/04-output-llm.ipynb) | [04-output-llm](soluzioni/04-output-llm.ipynb) |
| 5. Classificazione | [05-classificazione](esercizi/05-classificazione.ipynb) | [05-classificazione](soluzioni/05-classificazione.ipynb) |

Esecuzione:

```powershell
.\.venv\Scripts\python.exe -m jupyter lab --notebook-dir=.
```

In Jupyter seleziona **Python (CU lab)**; in VS Code seleziona l'interprete
`.venv\Scripts\python.exe` dal selettore kernel del notebook. Esegui **Restart
Kernel and Run All** per ripartire da zero, oppure le celle dall'alto verso il
basso. Apri una traccia in `esercizi` per svolgerla, oppure il notebook corrispondente
in `soluzioni` per confrontare il codice. La directory di lavoro del kernel deve
essere quella del notebook (gia configurata in VS Code). I percorsi sono fissi: `..\.env`, `..\file` e
`..\modelli`. Nessuna ricerca automatica di cartelle o configurazioni.

Configurazione, esecuzione e output sono separati in celle. La creazione del
client, le chiamate Azure e la chiusura rimangono nella stessa cella per garantire
la pulizia in caso di errore; gli esercizi custom eliminano anche l'analyzer
temporaneo. Riavviare forzatamente il kernel durante una chiamata non garantisce
la pulizia sul servizio. Le analisi comportano consumo Azure.

I risultati vengono soltanto stampati nelle celle: nessun JSON, Markdown o PDF
segmentato viene scritto su disco, e non vengono create cartelle `output` o
`segmenti`. Il quinto esercizio mostra categorie, confidence e
intervalli di pagine senza dividere fisicamente il PDF.
Gli analyzer custom definiti in [`modelli`](modelli), nella root e con soli file
JSON, vengono
creati per la singola esecuzione e rimossi al termine, anche quando l'analisi fallisce.
Questi JSON contengono solo la definizione dell'analyzer, mai `contents` o output
di un'analisi.

- [`modelli/nota_spese.json`](modelli/nota_spese.json): schema e configurazione della nota spese.
- [`modelli/classificatore_documenti.json`](modelli/classificatore_documenti.json): categorie e segmentazione.

I notebook caricano questi JSON con `json.loads` e li trasformano direttamente in
`ContentAnalyzer`: anche i ruoli modello sono gia dichiarati nei JSON. Gli ID custom
rimangono nelle variabili `AZURE_CONTENTUNDERSTANDING_CUSTOM_*_ANALYZER_ID`
di `.env`.
Non ci sono controlli preventivi su file, campi o deployment: gli eventuali
errori vengono restituiti direttamente da Python o Azure.

## Documentazione

La guida completa è disponibile in
[`documentazione/content-understanding-sdk.pdf`](documentazione/content-understanding-sdk.pdf).
La sorgente modificabile è
[`documentazione/content-understanding-sdk.md`](documentazione/content-understanding-sdk.md).

## Dati di esempio

I cinque PDF in [`file`](file) contengono dati sintetici. Non sono documenti
fiscali validi.
