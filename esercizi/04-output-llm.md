# Esercizio 4 - Output piu adatto a un LLM

**Obiettivo:** convertire lo stesso `AnalysisResult` con il metodo ufficiale
`to_llm_input`, senza appiattire a mano campi, pagine e tabelle.
Prepara i blocchi **1 e 3 di 1**, **3 di 2**, **1 di 3**.

## 1. Riusa l'analisi dello stesso documento

Ricarichiamo 3 dal disco: l'analisi e gia stata eseguita, questa trasformazione
non richiede un'altra chiamata Azure. Verifichiamo hash, analyzer ed endpoint.

<!-- cell:reload -->
```python
from azure.ai.contentunderstanding.models import AnalysisResult

result_path = OUTPUT / "analisi.json"
input_path = OUTPUT / "analisi-input.json"
if not result_path.is_file() or not input_path.is_file():
    raise FileNotFoundError("Esegui prima l'esercizio 3.")
analyzed_input = json.loads(input_path.read_text(encoding="utf-8"))
expected_input = {
    "sha256": DOCUMENT_SHA256,
    "analyzer_id": ANALYZER_ID,
    "endpoint": CU_ENDPOINT.rstrip("/"),
}
if any(analyzed_input.get(key) != value for key, value in expected_input.items()):
    raise ValueError("Documento, analyzer o endpoint cambiato: riesegui 3.")
result = AnalysisResult(json.loads(result_path.read_text(encoding="utf-8")))
if not result.contents:
    raise ValueError("Il risultato salvato non contiene contenuti.")
```

## 2. Facoltativo: ripeti davvero la chiamata di analisi

Lascia `False` per riusare il risultato di 3. Impostalo a `True` solo se vuoi
rianalizzare lo stesso file **con ulteriori costi CU** e confrontare eventuali
variazioni. Il risultato nuovo resta in memoria e non sovrascrive l'originale di 3.

<!-- cell:reanalyze -->
```python
RIPETI_ANALISI = False
if RIPETI_ANALISI:
    from azure.ai.contentunderstanding import ContentUnderstandingClient
    from azure.core.credentials import AzureKeyCredential
    with ContentUnderstandingClient(
        endpoint=CU_ENDPOINT, credential=AzureKeyCredential(CU_KEY)
    ) as client:
        result = client.begin_analyze_binary(
            analyzer_id=ANALYZER_ID, binary_input=document_bytes,
        ).result()
    if not result.contents:
        raise RuntimeError("La nuova analisi non contiene contenuti.")
```

## 3. Converti con to_llm_input

Il risultato e una **stringa** con front matter YAML (campi e metadati) e corpo
Markdown (testo, tabelle, riferimenti alle pagine). Non e una risposta di un LLM,
non esegue inferenza e non garantisce automaticamente un limite di token.
Il JSON dettagliato di 3 resta la fonte per confidence, coordinate e debugging.

<!-- cell:convert -->
```python
from azure.ai.contentunderstanding import to_llm_input

llm_text = to_llm_input(result)
fields_only = to_llm_input(result, include_markdown=False)
markdown_only = to_llm_input(result, include_fields=False)
if not llm_text.strip():
    raise RuntimeError("Conversione LLM vuota.")

(OUTPUT / "contesto-llm.md").write_text(llm_text, encoding="utf-8")
print(llm_text)
print("\nCaratteri (NON token):", {
    "json": len(json.dumps(result.as_dict(), ensure_ascii=False)),
    "llm_completo": len(llm_text),
    "solo_campi": len(fields_only),
    "solo_markdown": len(markdown_only),
})
```

## Cosa verificare

- Il testo mantiene `Ospite`, totali e saldo senza confonderli.
- `fields_only` esclude il corpo Markdown; `markdown_only` esclude i campi.
- La conversione e diversa da `json.dumps(result.as_dict())` o da
  `result.contents[0].markdown`: questi due approcci non fanno lo stesso lavoro.
- Nell'esercizio 6 sara il provider a fare questa preparazione automaticamente;
  non incolleremo a mano `contesto-llm.md` nel prompt.
