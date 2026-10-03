# Esercizio 3 - Analizzare il conto hotel

**Obiettivo:** inviare il documento locale al tuo analyzer e leggere il risultato
tipizzato, il Markdown e i campi con confidence/source.
Prepara un nuovo notebook con i blocchi **1 e 3 di 1**, poi il blocco **3 di 2**.
La soluzione include tutta questa preparazione.

## 1. Leggi il documento e registra la sua impronta

Usiamo solo PDF/PNG/JPEG in questo laboratorio: lo SDK supporta altri formati,
ma qui il MIME e esplicito anche per l'allegato MAF. Il file non viene reso
pubblico ne caricato su un URL esterno. L'impronta evita di usare in 4 i risultati
di un documento diverso con lo stesso nome.

<!-- cell:document -->
```python
DOCUMENT_PATH = Path(required_env("DOCUMENT_PATH")).expanduser()
if not DOCUMENT_PATH.is_absolute():
    DOCUMENT_PATH = ROOT / DOCUMENT_PATH
DOCUMENT_PATH = DOCUMENT_PATH.resolve()
if not DOCUMENT_PATH.is_file():
    raise FileNotFoundError(f"Documento non trovato: {DOCUMENT_PATH}")

MEDIA_TYPES = {
    ".pdf": "application/pdf", ".png": "image/png",
    ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
}
if DOCUMENT_PATH.suffix.lower() not in MEDIA_TYPES:
    raise ValueError("Per questo laboratorio usa PDF, PNG o JPEG.")
MEDIA_TYPE = MEDIA_TYPES[DOCUMENT_PATH.suffix.lower()]
document_bytes = DOCUMENT_PATH.read_bytes()
if not document_bytes:
    raise ValueError("Il documento e vuoto.")
DOCUMENT_SHA256 = hashlib.sha256(document_bytes).hexdigest()
print("Documento:", DOCUMENT_PATH.name, "-", len(document_bytes), "byte")
```

## 2. Analizza e salva il risultato originale

Questa cella **invia il documento ad Azure**. Ripeterla genera una nuova analisi.
Per un PDF multipagina vengono analizzate tutte le pagine. Non usiamo `requests`
o wrapper inventati: `begin_analyze_binary` appartiene allo SDK ufficiale.
I dettagli OCR e i valori estratti rimangono nel JSON, quindi non committarlo.

<!-- cell:analyze -->
```python
from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.core.credentials import AzureKeyCredential

with ContentUnderstandingClient(
    endpoint=CU_ENDPOINT, credential=AzureKeyCredential(CU_KEY)
) as client:
    poller = client.begin_analyze_binary(
        analyzer_id=ANALYZER_ID,
        binary_input=document_bytes,
    )
    result = poller.result()

if not result.contents:
    raise RuntimeError("Il servizio non ha restituito contenuti.")

(OUTPUT / "analisi.json").write_text(
    json.dumps(result.as_dict(), ensure_ascii=False, indent=2), encoding="utf-8"
)
(OUTPUT / "analisi-input.json").write_text(
    json.dumps({
        "filename": DOCUMENT_PATH.name,
        "sha256": DOCUMENT_SHA256,
        "analyzer_id": ANALYZER_ID,
        "endpoint": CU_ENDPOINT.rstrip("/"),
    }, indent=2),
    encoding="utf-8",
)
print("Analisi salvata. Contenuti restituiti:", len(result.contents))
```

## 3. Leggi Markdown e campi senza perdere source/confidence

`as_dict()` mantiene il formato JSON del servizio (`valueString`, `valueNumber`,
`valueDate`, `valueArray`...). Non assumere che ogni campo abbia un valore o una
confidence: un campo assente va distinto da zero. Stampiamo testo, non HTML
eseguibile proveniente dal documento.

<!-- cell:inspect -->
```python
for index, content in enumerate(result.contents, start=1):
    print(f"\n--- Contenuto {index} ---")
    print(content.markdown or "(Markdown non presente)")
    print(json.dumps(
        {name: field.as_dict() for name, field in (content.fields or {}).items()},
        ensure_ascii=False, indent=2,
    ))
```

## Cosa verificare sul PDF del laboratorio

Confronta il risultato con il documento, **non con un output precostituito**:

| Campo | Valore da confrontare nella copia Mario Rossi |
|---|---|
| Ospite | Mario Rossi |
| Arrivo / Partenza | 2026-02-08 / 2026-02-13 |
| Movimenti | 15 addebiti (5 pernottamenti e 10 imposte) e 1 accredito |
| TotaleAddebiti | 1587.10 |
| TotaleAccrediti | 1587.10 |
| Saldo | 0.00, **non** 1587.10 |

La seconda pagina ripete l'intestazione: non e un secondo soggiorno e non deve
raddoppiare gli importi. Se i campi non corrispondono, osserva source/confidence,
migliora lo schema in 2 e ripeti l'analisi. Questi valori di confronto non vengono
inseriti nel prompt dell'analyzer o dell'agente.
