# Esercizi Content Understanding

## Prima di iniziare

1. Installa Python 3.12 o successivo e Azure CLI.
2. Prepara una risorsa Foundry con Content Understanding, endpoint e API key.
3. Distribuisci `gpt-4.1` e `text-embedding-3-large` e configura i relativi
   default model mappings di Content Understanding.
4. Prepara un progetto Foundry con un deployment chat che supporti tool calling.
   Servono endpoint del progetto, nome del deployment e permessi di inferenza.
5. Metti il PDF del conto hotel nella cartella `esercizi`. La copia locale usata
   nel laboratorio si chiama `sample_hotel_bill_mario_rossi.pdf`.

Esegui questi comandi dalla root della repository:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m ipykernel install --user --name cu-lab --display-name "Python (CU lab)"
az login
.\.venv\Scripts\python.exe -m jupyter lab --notebook-dir=esercizi
```

Seleziona il kernel **Python (CU lab)**. Esegui i notebook in ordine, con directory
di lavoro `esercizi`. Nel primo esercizio compila `.env` usando `.env.example`.

## Esercizi

1. [Configurare .env e creare il client](esercizi/01-client.ipynb)
2. [Creare o recuperare un analyzer](esercizi/02-analyzer.ipynb)
3. [Analizzare il documento](esercizi/03-analisi.ipynb)
4. [Convertire il risultato con to_llm_input](esercizi/04-output-llm.ipynb)
5. [Creare un agente MAF con context provider](esercizi/05-agente-maf.ipynb)
6. [Eseguire l'agente sul documento](esercizi/06-esecuzione-agente.ipynb)
