# Laboratorio Content Understanding SDK + Microsoft Agent Framework

Sei esercizi progressivi in italiano: configurare il client, creare un analyzer,
analizzare **un tuo documento**, preparare il contesto LLM e usare il provider
ufficiale Content Understanding in un agente Microsoft Agent Framework (MAF).
Non viene creato o distribuito automaticamente alcun agente hosted.

## Struttura

```text
esercizi/
  01-client.md ... 06-esecuzione-agente.md  Istruzioni e blocchi da copiare
  analyzer-template.json                   Template per il conto hotel fornito
  documenti/                              Qui inserisci il tuo file (ignorato da Git)
  sample-documents/                        Vecchi sample conservati, solo opzionali
soluzioni/
  01-client.ipynb ... 06-esecuzione-agente.ipynb
  verifica_notebook.py                     Controlli locali senza Azure
  output/                                 Risultati locali, ignorati da Git
.env.example
requirements.txt
```

`esercizi` contiene le consegne Markdown; `soluzioni` contiene sei notebook con
codice completo e spiegazioni per ciascun blocco. Gli unici valori da fornire sono
credenziali, documento, configurazione dell'analyzer e deployment del modello.
Non sono incluse risposte simulate al posto delle chiamate Azure.

## Prerequisiti

1. Python **3.12 o successivo**, VS Code con estensioni Python e Jupyter, oppure
   JupyterLab. I notebook usano `await` direttamente: non serve `asyncio.run()`.
2. Una risorsa Microsoft Foundry con Content Understanding in una
   [regione supportata](https://learn.microsoft.com/azure/ai-services/content-understanding/language-region-support),
   endpoint e API key. La sola costruzione del client non verifica le credenziali.
3. Modelli e **default model mappings** configurati nella risorsa CU. Il template
   usa i modelli logici `gpt-4.1` e `text-embedding-3-large`: devono essere associati
   ai deployment effettivi della risorsa. Segui la
   [configurazione ufficiale](https://learn.microsoft.com/azure/ai-services/content-understanding/concepts/models-deployments).
   Non confondere questi mappings con il deployment chat dell'agente.
4. Per 5-6: un progetto Foundry e un deployment chat che supporti tool calling
   (per esempio GPT-4.1), Azure CLI, `az login` nel tenant corretto e autorizzazioni
   per inferenza sul progetto/risorsa (tipicamente **Azure AI User** sul progetto).
   La chiave CU non autentica il modello: il codice usa `AzureCliCredential`.
5. Un PDF, PNG o JPEG piccolo, non sensibile e autorizzato all'uso nel laboratorio.
   I documenti sono inviati ad Azure CU; negli esercizi 5-6 il contenuto estratto
   passa anche al deployment del modello. Le chiamate possono generare costi.

## Installazione (PowerShell, dalla root)

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m ipykernel install --user --name cu-lab --display-name "Python (CU lab)"
.\.venv\Scripts\python.exe -m jupyter lab
```

In VS Code seleziona **Python (CU lab)** come kernel. Le versioni dei pacchetti
CU e MAF sono fissate: `to_llm_input` e l'integrazione CU richiedono lo SDK
**preview 1.2.0b3**; la versione stabile 1.1.0 non basta. La preview usa
l'API `2026-06-01-preview`. Non aggiornare i pacchetti separatamente senza
riverificare la compatibilita.

## Percorso

| # | Consegna | Soluzione | Risultato |
|---|---|---|---|
| 1 | [Client](esercizi/01-client.md) | [Notebook 1](soluzioni/01-client.ipynb) | `.env` e client con API key |
| 2 | [Analyzer](esercizi/02-analyzer.md) | [Notebook 2](soluzioni/02-analyzer.ipynb) | Analyzer dal portale o dal template, esportato in JSON |
| 3 | [Analisi](esercizi/03-analisi.md) | [Notebook 3](soluzioni/03-analisi.ipynb) | Risultato SDK e JSON completo |
| 4 | [Output LLM](esercizi/04-output-llm.md) | [Notebook 4](soluzioni/04-output-llm.ipynb) | `to_llm_input`: YAML + Markdown |
| 5 | [Agente MAF](esercizi/05-agente-maf.md) | [Notebook 5](soluzioni/05-agente-maf.ipynb) | Agente con provider ufficiale |
| 6 | [Esecuzione](esercizi/06-esecuzione-agente.md) | [Notebook 6](soluzioni/06-esecuzione-agente.ipynb) | Allegato, risposta e osservazione del provider |

Per svolgere le consegne crea notebook vuoti in `soluzioni` e incolla i blocchi
indicati nell'ordine. Per consultare le soluzioni apri quelli gia presenti.
Esegui dall'alto verso il basso. Ogni soluzione ripete l'inizializzazione necessaria
e funziona con un **kernel nuovo**: nessuna variabile passa da un notebook all'altro.
Restano dipendenze **su disco**: 1 crea `.env`, 2 salva l'analyzer per 3-6,
3 salva l'analisi riutilizzata da 4. Il notebook 6 include la costruzione di 5.

Il documento del percorso e `sample_hotel_bill_mario_rossi.pdf`: una copia locale
del conto hotel fornito, con il nome sostituito su entrambe le pagine e il resto
invariato. **Non e un documento interamente anonimizzato**: indirizzi, riferimenti
e dettagli di pagamento preesistenti restano presenti. Per questo il PDF rimane
ignorato da Git e non viene distribuito automaticamente con un clone. Se non lo
possiedi, inserisci un tuo conto hotel e adegua `DOCUMENT_PATH` e i controlli.
Il template e adattato a hotel, ospite, soggiorno, addebiti, accrediti e saldo;
non incorpora i valori attesi nelle descrizioni inviate al servizio.
I vecchi sample sono conservati in
`esercizi/sample-documents` e provengono dalla cartella `data` di
[`Azure-Samples/azure-ai-content-understanding-python`](https://github.com/Azure-Samples/azure-ai-content-understanding-python).
Non sono usati automaticamente.

## Sicurezza, errori e ripetizione

- Non inserire chiavi nelle celle. `.env`, documenti personali, analyzer
  personalizzato e output sono ignorati da Git. Gli output delle celle **non lo
  sono**: usa **Clear All Outputs** prima di condividere o committare un notebook.
- 2 non sovrascrive analyzer Azure: con un ID esistente usa la modalita `portale`
  per recuperarlo oppure scegli un nuovo ID. Cambiare il template non aggiorna
  automaticamente l'analyzer gia salvato.
- 3 sovrascrive il risultato locale ed effettua una nuova analisi a ogni esecuzione.
  4 ricarica lo stesso risultato senza costi Azure; il blocco opzionale rianalizza.
  6 rianalizza il file nel primo turno di ogni nuova sessione.
- `401/403`: verifica endpoint, key, tenant e ruoli; non disabilitare controlli.
  `404`: verifica ID analyzer, risorsa, progetto e deployment.
  Errori sui modelli CU: verifica deployment e default mappings.
  `429`: rispetta retry/quota e riduci le chiamate.
  Timeout/rete privata: esegui da una rete autorizzata.
- Il provider puo restituire uno stato di errore senza sollevare un'eccezione:
  6 controlla esplicitamente `documents` e non considera la risposta LLM una prova
  di estrazione riuscita. `max_wait=None` attende l'analisi senza differimento.
- Nessuna cella elimina risorse Azure. A fine laboratorio rimuovi dal portale
  **solo** gli analyzer e i deployment creati appositamente, se non piu necessari.

## Verifica locale

```powershell
.\.venv\Scripts\python.exe soluzioni\verifica_notebook.py
```

Controlla formato, sintassi, assenza di output, corrispondenza dei blocchi con le
consegne e contratti principali usando gli SDK installati e client fittizi.
Non invia documenti, non legge `.env` e non certifica permessi o risposte Azure:
la verifica end-to-end richiede i tuoi dati e l'esecuzione dei notebook.

## Riferimenti

- [SDK Python CU](https://learn.microsoft.com/python/api/overview/azure/ai-contentunderstanding-readme)
- [`to_llm_input`, esempio ufficiale](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/contentunderstanding/azure-ai-contentunderstanding/samples/sample_to_llm_input.py)
- [CU come context provider MAF](https://learn.microsoft.com/azure/ai-services/content-understanding/integrations/agent-framework)
- [Sample MAF multi-turn](https://github.com/microsoft/agent-framework/blob/main/python/samples/02-agents/context_providers/azure_content_understanding/02_multi_turn_session.py)
