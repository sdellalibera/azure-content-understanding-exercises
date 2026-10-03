# Esercizio 6 - Esegui l'agente e osserva il context provider

**Obiettivo:** allegare il PDF, interrogare l'agente e osservare la prova
dell'estrazione nel provider, non soltanto una risposta plausibile del modello.
Prepara **1 e 3 di 1**, **3 di 2**, **1 di 3**, **1 e 2 di 5**.
La soluzione contiene gia tutti questi blocchi ed e indipendente dal kernel di 5.

## 1. Esegui due turni nella stessa sessione

La prima chiamata invia un vero allegato con `Content.from_data`; una stringa
contenente il percorso locale **non** consentirebbe al servizio di leggere il
file. Non chiamiamo `begin_analyze_binary` e non iniettiamo manualmente il testo
prodotto da 4: e il provider registrato a farlo.

Il secondo turno non allega nuovamente il file e riusa la stessa `AgentSession`.
Lo storico configurato in 5 conserva anche il contesto aggiunto da CU, non solo
la prima risposta del modello.
Una nuova sessione o un nuovo kernel non conserva questo stato.
Rieseguire l'intera cella crea una sessione nuova e comporta nuovi costi CU/LLM.

<!-- cell:run -->
```python
from agent_framework import AgentSession, Content, Message

session = AgentSession()
async with hotel_agent() as (agent, provider):
    response = await agent.run(
        Message(role="user", contents=[
            Content.from_text(
                "Analizza il conto hotel allegato. Indica ospite, hotel, arrivo, "
                "partenza, notti, totale addebiti, totale pagamenti e saldo. "
                "Spiega se resta qualcosa da pagare e cita le pagine disponibili."
            ),
            Content.from_data(
                document_bytes,
                media_type=MEDIA_TYPE,
                additional_properties={"filename": DOCUMENT_PATH.name},
            ),
        ]),
        session=session,
    )

    provider_state = session.state.get(provider.source_id, {})
    documents = provider_state.get("documents", {})
    if DOCUMENT_PATH.name not in documents:
        raise RuntimeError("Il provider non ha registrato l'allegato.")
    document_state = documents[DOCUMENT_PATH.name]
    if document_state["status"] != "ready" or not document_state.get("result"):
        raise RuntimeError(
            f"Analisi CU non riuscita: {document_state['status']}; "
            f"dettaglio: {document_state.get('error')}"
        )

    print("Stato CU:", document_state["status"])
    print("Analyzer usato:", document_state["analyzer_id"])
    print("Secondi di analisi:", document_state.get("analysis_duration_s"))
    print("\nRisposta primo turno:\n", response.text)
    print("\nContesto preparato dal provider (anteprima):\n",
          document_state["result"][:2500])
    (OUTPUT / "contesto-provider.md").write_text(
        document_state["result"], encoding="utf-8"
    )
    first_analysis_time = document_state.get("analyzed_at")

    follow_up = await agent.run(
        "Senza un nuovo allegato, separa pernottamenti e imposte. "
        "Spiega come riconcili gli addebiti con il pagamento e il saldo, "
        "senza ripetere i riferimenti della carta.",
        session=session,
    )
    after_documents = session.state[provider.source_id]["documents"]
    if set(after_documents) != {DOCUMENT_PATH.name}:
        raise RuntimeError("Numero di documenti inatteso dopo il secondo turno.")
    if after_documents[DOCUMENT_PATH.name].get("analyzed_at") != first_analysis_time:
        raise RuntimeError("L'analisi del documento e cambiata nel secondo turno.")
    print("\nRisposta secondo turno:\n", follow_up.text)
    print("\nStato riutilizzato: stesso documento e timestamp di analisi.")
```

## 2. Interpreta quello che hai osservato

`session.state[provider.source_id]["documents"]` e lo stato diagnostico della
versione del provider fissata nei requirements. Non e un formato di business
stabile da usare al posto del risultato CU. Un errore del provider puo essere
convertito in un messaggio per il modello: per questo controlliamo `ready` e
`result` **prima di presentare la risposta come un'analisi riuscita**.

Apri `soluzioni/output/contesto-provider.md` per leggere l'intero contesto.
Confrontalo con `contesto-llm.md` di 4: entrambi derivano dalla conversione
`to_llm_input`, ma 6 effettua una nuova analisi, quindi non promettiamo identita
testuale. La verifica di timestamp e stato e diagnostica, non un contatore di
richieste HTTP; per audit di fatturazione servono metriche del servizio.

## Cosa verificare sul conto Mario Rossi

- Il primo turno riconosce Mario Rossi e un soggiorno di **5 notti**.
- Pernottamenti **1345.00**, room tax **211.15**, tourism assessment **30.95**:
  totale addebiti **1587.10**, pagamento **1587.10**, saldo **0.00**.
- Non somma una seconda volta la seconda pagina e non presenta il totale come
  importo ancora da pagare.
- Il secondo turno risponde senza un nuovo allegato; lo stato CU rimane invariato.
- Le cifre sopra sono criteri umani di confronto, non risposte da passare al
  modello. Se la risposta e errata, verifica prima i campi e poi le istruzioni.
- Elimina tutti gli output delle celle prima di condividere il notebook.
