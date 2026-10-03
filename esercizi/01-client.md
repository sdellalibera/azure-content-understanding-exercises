# Esercizio 1 - File .env e client Content Understanding

**Obiettivo:** separare i segreti dal codice e creare `ContentUnderstandingClient`
con `AzureKeyCredential`. Completa prima l'installazione nel README.
Apri un notebook vuoto in `soluzioni`, seleziona Python (CU lab) e incolla ogni
blocco Python in una cella separata. La soluzione e `01-client.ipynb`.

## 1. Individua la root

Questo blocco funziona sia avviando Jupyter dalla root sia dalla cartella
`soluzioni`. Sara il blocco iniziale anche dei notebook successivi.

<!-- cell:root -->
```python
from pathlib import Path
import hashlib
import json
import os

ROOT = Path.cwd().resolve()
if ROOT.name in {"soluzioni", "esercizi"}:
    ROOT = ROOT.parent
if not (ROOT / ".env.example").is_file() or not (ROOT / "esercizi").is_dir():
    raise RuntimeError("Avvia Jupyter dalla root della repo o da soluzioni.")

OUTPUT = ROOT / "soluzioni" / "output"
OUTPUT.mkdir(parents=True, exist_ok=True)
ENV_PATH = ROOT / ".env"
print("Root:", ROOT)
```

## 2. Crea .env senza sovrascriverne uno esistente

Esegui il blocco, poi **apri `.env` nell'editor** prima di proseguire.
Sostituisci endpoint e API key CU con quelli di **Keys and Endpoint** della
risorsa. Non usare l'endpoint progetto per CU. Verifica `DOCUMENT_PATH`;
per ora puoi lasciare i placeholder `FOUNDRY_*`, necessari solo in 5-6.
Non incollare mai la chiave in una cella o nel suo output.

<!-- cell:env -->
```python
if ENV_PATH.exists():
    print(".env gia presente: non e stato sovrascritto.")
else:
    ENV_PATH.write_text(
        (ROOT / ".env.example").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    print(".env creato. Compilalo nell'editor prima della prossima cella.")
```

## 3. Carica e verifica la configurazione

`override=True` rende `.env` la fonte esplicita del laboratorio, anche dopo
una modifica nello stesso kernel. La funzione segnala valori mancanti o
placeholder senza stampare il contenuto della chiave.

<!-- cell:settings -->
```python
from dotenv import load_dotenv

if not ENV_PATH.is_file():
    raise FileNotFoundError("Manca .env: completa l'esercizio 1.")
load_dotenv(ENV_PATH, override=True)

def required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value or "<" in value or ">" in value:
        raise ValueError(f"Compila {name} in .env, poi riesegui questa cella.")
    return value

CU_ENDPOINT = required_env("AZURE_CONTENTUNDERSTANDING_ENDPOINT")
CU_KEY = required_env("AZURE_CONTENTUNDERSTANDING_API_KEY")
if not CU_ENDPOINT.startswith("https://") or "/api/projects/" in CU_ENDPOINT:
    raise ValueError("CU richiede l'endpoint HTTPS della risorsa, non del progetto.")
print("Configurazione CU caricata; chiave non visualizzata.")
```

## 4. Crea il client

La costruzione del client **non effettua chiamate Azure** e non dimostra ancora
che la chiave sia valida. Il context manager chiude il trasporto; negli esercizi
successivi ricreerai un client con gli stessi due argomenti.

<!-- cell:client -->
```python
from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.core.credentials import AzureKeyCredential

with ContentUnderstandingClient(
    endpoint=CU_ENDPOINT,
    credential=AzureKeyCredential(CU_KEY),
) as client:
    print("Client creato:", type(client).__name__)
```

## Cosa verificare

- `.env` esiste e non compare in `git status`.
- La cella 3 fallisce con un messaggio esplicito se lasci un placeholder CU.
- La cella 4 stampa `ContentUnderstandingClient`, mai la chiave.
- Sai distinguere endpoint risorsa CU, endpoint progetto e deployment chat.
