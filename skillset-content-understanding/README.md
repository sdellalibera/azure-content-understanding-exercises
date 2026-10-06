# Azure AI Search con Content Understanding

Questa cartella contiene una pipeline completa di indicizzazione per Azure AI
Search. Lo skillset usa **Azure Content Understanding** per trasformare ogni
documento in chunk Markdown, conserva i riferimenti alle pagine e alle immagini
e usa Azure OpenAI per creare il vettore di ogni chunk.

Il flusso è:

```text
Blob Storage -> indexer -> Content Understanding -> chunk Markdown
                                           |
                                           +-> Azure OpenAI -> embedding
                                           |
                                           +-> index projection -> indice Search
```

> [!IMPORTANT]
> L'esempio usa l'API preview `2026-08-01-preview` perché abilita chunking
> semantico e descrizioni delle immagini. Le funzionalità preview non hanno SLA
> e possono cambiare. Per usare solo funzionalità GA, consulta la sezione
> [Variante GA](#variante-ga).

## File

| File | Risorsa Azure AI Search | Scopo |
| --- | --- | --- |
| `01-data-source.json` | Data source | Collega il container Blob |
| `02-index.json` | Index | Definisce campi testuali, metadati e vettori |
| `03-skillset.json` | Skillset | Estrae, suddivide, vettorializza e proietta i contenuti |
| `04-indexer.json` | Indexer | Coordina origine, skillset e indice |

I file contengono segnaposto tra parentesi angolari. Non inserire chiavi reali
nel controllo versione.

## Prerequisiti

Servono:

1. un servizio Azure AI Search;
2. un account Storage con un container Blob contenente PDF o altri formati
   supportati;
3. una risorsa Microsoft Foundry in una regione supportata da Content
   Understanding;
4. nella risorsa Foundry:
   - un deployment chat, per esempio `gpt-4.1`, per descrivere figure e grafici;
   - un deployment embedding `text-embedding-3-small`;
5. autorizzazioni per creare data source, indice, skillset e indexer.

La risorsa Search può essere in una regione diversa dalla risorsa Foundry, ma
la latenza tra regioni può rallentare l'indexer.

## Segnaposto da sostituire

| Segnaposto | Valore |
| --- | --- |
| `<storage-connection-string>` | Connection string dell'account Storage |
| `<blob-container-name>` | Nome del container con i documenti |
| `<chat-model-deployment>` | Nome del deployment chat nella risorsa Foundry |
| `<azure-openai-subdomain>` | Sottodominio dell'endpoint Azure OpenAI |
| `<azure-openai-api-key>` | Chiave usata dalla skill di embedding |
| `<foundry-resource-name>` | Nome della risorsa Foundry associata allo skillset |
| `<foundry-resource-key>` | Chiave della risorsa Foundry associata allo skillset |

Per una demo sono pratiche le chiavi. In produzione è preferibile usare
un'identità gestita e ruoli Azure; vedi
[Autenticazione con identità gestita](#autenticazione-con-identita-gestita).

## Creazione dal portale

Nel portale Azure apri il servizio **Azure AI Search**. Crea le risorse
nell'ordine seguente, usando l'editor JSON disponibile nelle rispettive sezioni:

1. **Data sources**: contenuto di `01-data-source.json`;
2. **Indexes**: contenuto di `02-index.json`;
3. **Skillsets**: contenuto di `03-skillset.json`;
4. **Indexers**: contenuto di `04-indexer.json`.

I nomi sono già coerenti tra i quattro file. Se rinomini una risorsa, aggiorna
anche tutti i riferimenti:

- `targetIndexName` nello skillset;
- `dataSourceName`, `targetIndexName` e `skillsetName` nell'indexer.

Avvia quindi l'indexer e controlla **Execution history**. Al termine usa
**Search explorer** sull'indice `cu-documents-index`.

## Creazione con REST

Gli stessi JSON possono essere inviati alle API REST di Search:

```http
POST https://<search-service>.search.windows.net/datasources?api-version=2026-08-01-preview
api-key: <search-admin-key>
Content-Type: application/json

<contenuto di 01-data-source.json>
```

Ripeti la richiesta sugli endpoint `indexes`, `skillsets` e `indexers`,
mantenendo l'ordine indicato sopra.

## Parametri dello skillset

### Proprietà generali

| Parametro | Valore nell'esempio | Significato |
| --- | --- | --- |
| `name` | `cu-documents-skillset` | Nome univoco dello skillset |
| `description` | Testo descrittivo | Scopo leggibile della pipeline |
| `skills` | Due elementi | Sequenza delle trasformazioni |
| `cognitiveServices` | Risorsa Foundry con endpoint e chiave | Risorsa fatturata per Content Understanding |
| `indexProjections` | Una proiezione | Crea un documento Search per ogni chunk |

### Content Understanding skill

La prima skill ha tipo
`#Microsoft.Skills.Util.ContentUnderstandingSkill`.

| Parametro | Valore nell'esempio | Significato |
| --- | --- | --- |
| `name` | `content-understanding` | Nome interno della skill |
| `context` | `/document` | La skill viene eseguita una volta per file |
| `modelName` | `gpt-4.1` | Nome del modello chat per descrivere le immagini |
| `modelDeployment` | Segnaposto | Nome del relativo deployment nella risorsa Foundry |
| `extractionOptions` | `images`, `locationMetadata` | Estrae immagini e coordinate/pagine |
| `inputs[0].name` | `file_data` | Input binario richiesto dalla skill |
| `inputs[0].source` | `/document/file_data` | Percorso creato dall'indexer |
| `text_sections` | Output principale | Chunk Markdown del documento |
| `normalized_images` | Output immagini | Immagini estratte in formato normalizzato |

`modelName` e `modelDeployment` sono facoltativi, ma devono essere presenti o
assenti insieme. Servono per generare descrizioni testuali di figure, diagrammi
e grafici. Questa funzione è indipendente da `extractionOptions`: è possibile
descrivere le immagini senza esportarle.

I valori consentiti per `extractionOptions` sono:

- `["images"]`;
- `["locationMetadata"]`;
- `["images", "locationMetadata"]`.

Se non servono immagini né riferimenti di pagina, ometti la proprietà.

### `chunkingProperties`

| Parametro | Valore nell'esempio | Regole |
| --- | --- | --- |
| `method` | `semantic` | `semantic` oppure `fixedSize` |
| `unit` | `tokens` | `tokens` con `semantic`; `characters` con `fixedSize` |
| `maximumLength` | `500` | 100-8.000 token oppure 300-50.000 caratteri |
| `overlapLength` | omesso | Solo per `fixedSize`; deve essere minore di metà `maximumLength` |

Il chunking `semantic` rispetta titoli e paragrafi e gestisce meglio le tabelle
lunghe. Non richiede una Text Split skill separata. Per il chunking
`fixedSize`, un esempio valido è:

```json
"chunkingProperties": {
  "method": "fixedSize",
  "unit": "characters",
  "maximumLength": 2000,
  "overlapLength": 200
}
```

### Output `text_sections`

Ogni elemento può contenere:

| Campo | Contenuto |
| --- | --- |
| `id` | Identificatore univoco del chunk |
| `content` | Contenuto Markdown |
| `locationMetadata.pageNumberFrom` | Prima pagina del chunk |
| `locationMetadata.pageNumberTo` | Ultima pagina del chunk |
| `locationMetadata.ordinalPosition` | Posizione del chunk |
| `locationMetadata.source` | Informazioni geometriche di origine |
| `imagePath` | Percorsi delle immagini che intersecano il chunk |

### Azure OpenAI Embedding skill

La seconda skill viene eseguita nel contesto
`/document/text_sections/*`, quindi una volta per ogni chunk.

| Parametro | Valore nell'esempio | Significato |
| --- | --- | --- |
| `resourceUri` | Endpoint Azure OpenAI | Risorsa che ospita il deployment |
| `deploymentId` | `text-embedding-3-small` | Nome del deployment |
| `modelName` | `text-embedding-3-small` | Nome del modello |
| `dimensions` | `1536` | Dimensione del vettore prodotto |
| input `text` | `.../content` | Markdown del chunk |
| output `embedding` | `text_vector` | Vettore passato alla proiezione |

`dimensions` deve coincidere con `dimensions` del campo `text_vector`
nell'indice. Se cambi modello o dimensione, aggiorna entrambi.

### `indexProjections`

La proiezione converte la relazione uno-a-molti in documenti separati:

- `sourceContext` seleziona ogni elemento di `text_sections`;
- `targetIndexName` indica l'indice di destinazione;
- `parentKeyFieldName` conserva l'identificatore del file sorgente;
- `mappings` associa output e metadati ai campi dell'indice;
- `skipIndexingParentDocuments` impedisce di aggiungere anche un documento
  padre privo di contenuto chunk.

Il campo chiave `chunk_id` non compare nei mapping: Azure AI Search lo genera
per ogni proiezione.

## Parametri dell'indexer

| Parametro | Valore | Motivo |
| --- | --- | --- |
| `batchSize` | `1` | Limita il lavoro concorrente per documenti costosi |
| `dataToExtract` | `contentAndMetadata` | Rende disponibili contenuto e metadati |
| `parsingMode` | `default` | Tratta ogni blob come un documento |
| `allowSkillsetToReadFileData` | `true` | Crea `/document/file_data`; è obbligatorio per questa skill con Blob Storage |

Non servono `outputFieldMappings`: i chunk vengono scritti tramite
`indexProjections`.

## Autenticazione con identità gestita

Per evitare segreti:

1. abilita l'identità gestita del servizio Search;
2. assegna **Cognitive Services User** alla sua identità sulla risorsa Foundry;
3. assegna alla stessa identità i ruoli richiesti su Storage e Azure OpenAI;
4. usa una connessione gestita nel data source;
5. rimuovi `apiKey` dalla skill di embedding;
6. sostituisci il blocco `cognitiveServices` con:

```json
"cognitiveServices": {
  "@odata.type": "#Microsoft.Azure.Search.AIServicesByIdentity",
  "description": "Fatturazione Content Understanding con identità gestita",
  "subdomainUrl": "https://<foundry-resource-name>.services.ai.azure.com",
  "identity": null
}
```

`identity: null` seleziona l'identità gestita assegnata dal sistema. Per
un'identità assegnata dall'utente occorre invece indicarne il resource ID con
il tipo `#Microsoft.Azure.Search.DataUserAssignedIdentity`.

I ruoli esatti dipendono dal tipo di risorsa e dall'accesso a rete. Configura
anche firewall, endpoint privati e DNS prima di disabilitare l'accesso tramite
rete pubblica.

## Variante GA

La Content Understanding skill è disponibile nella REST API stabile
`2026-04-01`. Per evitare le due funzioni preview:

1. usa `api-version=2026-04-01`;
2. rimuovi `modelName` e `modelDeployment`;
3. sostituisci il chunking semantico con `fixedSize` e `characters`;
4. mantieni la skill di embedding e le proiezioni, adattandole alla versione
   REST scelta.

## Verifica e diagnostica

Controlla nello storico dell'indexer:

- `status`: deve essere `success`;
- `itemsProcessed`: deve essere maggiore di zero;
- `itemsFailed`: deve essere zero;
- warning relativi a documenti troppo grandi o formati non supportati.

La skill può andare in timeout per documenti che richiedono più di cinque
minuti di elaborazione e i costi possono comunque essere applicati. La
dimensione massima lato Content Understanding è 200 MB, ma valgono anche i
limiti specifici del tier Search. I PDF protetti da password non sono
supportati.

Una query di controllo in Search explorer:

```json
{
  "search": "*",
  "select": "title,chunk,page_number_from,page_number_to,image_path",
  "top": 5
}
```

## Riferimenti

- [Azure Content Understanding skill](https://learn.microsoft.com/azure/search/cognitive-search-skill-content-understanding)
- [Chunk e vettori con Content Understanding](https://learn.microsoft.com/azure/search/search-how-to-semantic-chunking-content-understanding)
- [Creare uno skillset](https://learn.microsoft.com/azure/search/cognitive-search-defining-skillset)
- [Collegare una risorsa Azure AI allo skillset](https://learn.microsoft.com/azure/search/cognitive-search-attach-cognitive-services)
- [Configurare identità gestite in Azure AI Search](https://learn.microsoft.com/azure/search/search-how-to-managed-identities)
