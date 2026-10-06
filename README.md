# Azure AI Content Understanding: esercizi pratici

Questo repository raccoglie nove notebook Jupyter per imparare a usare
**Azure AI Content Understanding** con Python, partendo dalla configurazione del
client fino all'integrazione con un agente Microsoft Agent Framework (MAF).

Gli esercizi usano documenti PDF sintetici e mostrano come:

- autenticarsi in Azure con `DefaultAzureCredential`;
- usare analyzer prebuilt;
- analizzare documenti composti da più pagine;
- creare e rimuovere analyzer personalizzati;
- preparare il risultato di un'analisi come contesto per un LLM;
- classificare e segmentare un PDF multi-documento;
- usare Content Understanding come context provider di un agente;
- usare confidence e grounding per instradare i campi;
- applicare il workflow agentic alla revisione di un contratto;
- segmentare documenti diversi collocati nella stessa pagina.

> [!IMPORTANT]
> L'esecuzione dei notebook effettua chiamate a servizi Azure e può generare
> costi. I PDF inclusi nel repository contengono esclusivamente dati sintetici.

## Contenuto del repository

| Esercizio | Obiettivo | Notebook |
| --- | --- | --- |
| 1 | Configurare l'ambiente e creare il client | [`01-client.ipynb`](esercizi/01-client.ipynb) |
| 2 | Recuperare e usare l'analyzer prebuilt per ricevute di hotel | [`02-analyzer.ipynb`](esercizi/02-analyzer.ipynb) |
| 3 | Analizzare un documento di due pagine | [`03-analisi.ipynb`](esercizi/03-analisi.ipynb) |
| 4 | Usare un analyzer custom e preparare l'input per un LLM | [`04-output-llm.ipynb`](esercizi/04-output-llm.ipynb) |
| 5 | Classificare e segmentare un PDF multi-documento | [`05-classificazione.ipynb`](esercizi/05-classificazione.ipynb) |
| 6 | Analizzare un documento con un agente MAF | [`06-agente-maf.ipynb`](esercizi/06-agente-maf.ipynb) |
| 7 | Usare confidence, grounding e revisione umana | [`07-confidence-grounding.ipynb`](esercizi/07-confidence-grounding.ipynb) |
| 8 | Revisionare un contratto con il workflow agentic | [`08-agentic-contract.ipynb`](esercizi/08-agentic-contract.ipynb) |
| 9 | Segmentare documenti diversi nella stessa pagina | [`09-in-page-segmentation.ipynb`](esercizi/09-in-page-segmentation.ipynb) |

Le risorse usate dai notebook si trovano nelle cartelle:

- [`file`](file): sette PDF di esempio;
- [`modelli`](modelli): definizioni JSON degli analyzer personalizzati;
- [`esercizi`](esercizi): notebook da eseguire in ordine.

## Prerequisiti

Prima di iniziare assicurati di avere:

1. Python 3.12 o successivo;
2. Azure CLI;
3. una risorsa Microsoft Foundry con Content Understanding disponibile in una
   regione supportata;
4. il ruolo **Cognitive Services User** assegnato sulla risorsa;
5. un progetto Foundry con un deployment `gpt-5.4`, necessario per l'esercizio 6.

## Configurazione

Apri PowerShell nella root del repository e crea un ambiente virtuale:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m ipykernel install --prefix .venv --name cu-lab --display-name "Python (CU lab)"
```

Crea quindi il file di configurazione locale:

```powershell
Copy-Item .env.example .env
```

Completa `.env` con i valori del tuo ambiente:

```dotenv
FOUNDRY_SERVICES_ENDPOINT=https://<risorsa>.services.ai.azure.com/
FOUNDRY_ENDPOINT=https://<progetto>.services.ai.azure.com/
```

| Variabile | Utilizzo |
| --- | --- |
| `FOUNDRY_SERVICES_ENDPOINT` | Endpoint della risorsa usato da tutti gli esercizi |
| `FOUNDRY_ENDPOINT` | Endpoint del progetto Foundry usato nell'esercizio 6 |

Il file `.env` è escluso dal controllo versione. Non inserire credenziali o
segreti nei notebook: l'autenticazione usa l'identità Azure locale.

Accedi infine ad Azure:

```powershell
az login
```

Se disponi di più sottoscrizioni, seleziona quella corretta:

```powershell
az account set --subscription "<nome-o-id-sottoscrizione>"
```

## Esecuzione

Avvia JupyterLab dalla root del repository:

```powershell
.\.venv\Scripts\python.exe -m jupyter lab --notebook-dir=.
```

Apri un notebook nella cartella [`esercizi`](esercizi), seleziona il kernel
**Python (CU lab)** ed esegui le celle dall'alto verso il basso.

In Visual Studio Code puoi aprire direttamente il repository e selezionare
`.venv\Scripts\python.exe` come interprete del notebook. La configurazione
inclusa mantiene la directory di lavoro nella cartella del notebook, come
richiesto dai percorsi relativi `..\.env`, `..\file` e `..\modelli`.

Per ripetere un esercizio da uno stato pulito usa **Restart Kernel and Run All**.

## Analyzer usati

Gli esercizi 2 e 3 usano l'analyzer prebuilt
`prebuilt-receipt.hotel`.

Gli esercizi 4, 5, 7, 8 e 9 caricano invece le definizioni:

- [`nota_spese.json`](modelli/nota_spese.json), per estrarre i dati di una nota
  spese e restituire confidence e grounding;
- [`classificatore_documenti.json`](modelli/classificatore_documenti.json), per
  classificare e segmentare documenti aggregati;
- [`contratto_agentic.json`](modelli/contratto_agentic.json), per correlare
  clausole e revisionare un contratto con il workflow agentic;
- [`segmentazione_in_pagina.json`](modelli/segmentazione_in_pagina.json), per
  classificare regioni diverse di una singola pagina.

Gli analyzer custom vengono creati per la singola esecuzione e rimossi al
termine, anche se l'analisi genera un errore. Un'interruzione forzata del kernel
durante una chiamata, tuttavia, potrebbe impedire la rimozione della risorsa.

L'esercizio 6 usa `prebuilt-documentSearch` come context provider di un agente.
Gli esercizi 8 e 9 richiedono le funzionalità preview della versione API
`2026-06-01-preview`.

## Output e comportamento

I risultati vengono mostrati direttamente nelle celle dei notebook. Gli
esercizi non scrivono su disco JSON, Markdown, PDF segmentati o altre cartelle
di output.

In particolare, l'esercizio 5 visualizza categorie, confidence e intervalli di
pagine restituiti dal servizio senza dividere fisicamente il PDF.

L'esercizio 7 usa soglie didattiche per mostrare l'instradamento automatico,
alla revisione umana o allo scarto. L'esercizio 9 visualizza anche il poligono
`source` di ogni segmento senza creare PDF separati.

Gli errori di configurazione, autenticazione, input o servizio non vengono
mascherati: sono restituiti direttamente da Python o da Azure per facilitarne
la diagnosi.
