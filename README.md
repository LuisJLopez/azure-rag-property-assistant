# Property Knowledge Assistant

A one-day learning prototype: a RAG assistant that answers questions about UK
property documents, with citations, using Azure AI Search and Microsoft
Foundry. Built to learn Blob Storage, indexing, embeddings, vector/hybrid
retrieval, and grounded generation hands-on — not a production system, and
not financial or property advice.

Full spec: [01-property-assistant-idea-and-goal.md](01-property-assistant-idea-and-goal.md).

## What this does

1. Uploads 4 public UK property PDFs to Blob Storage.
2. Azure AI Search chunks each PDF (~2000 chars/chunk, 500 overlap) and
   generates a 1536-dim embedding per chunk via a deployed `text-embedding-3-small` model.
3. Chunks, vectors, and source metadata land in a hybrid (keyword + vector)
   search index — 391 chunks total.
4. A Foundry agent (`gpt-5-mini`) queries that index at chat time and
   generates answers grounded only in retrieved chunks, with inline
   citations back to the source document.
5. Along the way: deployed two separate OpenAI-family resources after
   discovering Azure AI Search's embedding skill doesn't reliably call a
   deployment hosted on the newer `AIServices` resource kind — see
   [04-indexing-fix-notes.md](04-indexing-fix-notes.md).

## Architecture

```text
Public UK property PDFs (gov.uk, parliament.uk)
                  |
                  v
      Azure Blob Storage container
                  |
                  v
 Azure AI Search indexer + skillset
   chunking -> embedding -> vectors
                  |
                  v
        Azure AI Search index
  text + metadata + source URL + vectors
                  |
       keyword / vector / hybrid search
                  |
                  v
     Microsoft Foundry agent (gpt-5-mini)
                  |
          grounded answer + citations
```

## Azure resources

| Resource | Name | Purpose |
|---|---|---|
| Resource group | `rg-property-kb` | uksouth |
| Storage account | `stpropertykb001` | source PDFs, container `property-docs` |
| Azure AI Search | `srch-property-kb` | index, indexer, skillset, data source |
| Search index | `property-kb` | chunked text + vectors + metadata |
| Foundry resource | `luisjlop-1485-resource` | kind AIServices, swedencentral — hosts the chat model |
| Chat deployment | `gpt-5-mini` | generates grounded answers |
| OpenAI resource | `property-kb-openai` | kind OpenAI, uksouth — hosts the embedding model used by the indexer |
| Embedding deployment | `text-embedding-3-small` | 1536-dim vectors, used at index and query time |
| Foundry knowledge base | `property-kb-knowledge` | Foundry IQ, connects the agent to the index |
| Foundry agent | `property-agent` | `gpt-5-mini` + `property-kb-knowledge` |

Why two OpenAI-family resources: see
[04-indexing-fix-notes.md](04-indexing-fix-notes.md) — Azure AI Search's
embedding skill didn't reliably call a deployment hosted on an
`AIServices`-kind resource, so the embedding model was moved to a dedicated
`OpenAI`-kind resource.

## Repo layout

- [scripts/](scripts/) — downloads the source PDFs and uploads them to Blob Storage
- [azure_model_deployment/](azure_model_deployment/) — sanity-check scripts for both model deployments, plus a hand-rolled RAG loop (embed → cosine similarity retrieval → generate) that proves the concept before the real index exists
- [screenshots/](screenshots/) — evidence of the working pipeline

## Setup

Requires [uv](https://docs.astral.sh/uv/) and `az login`.

```bash
cd scripts && uv sync && uv run upload_docs.py
cd ../azure_model_deployment && uv sync && uv run chat.py "your question"
```

## Docs

| Doc | Contents |
|---|---|
| [01-property-assistant-idea-and-goal.md](01-property-assistant-idea-and-goal.md) | Scope, goals, definition of done |
| [02-getting-started-plan.md](02-getting-started-plan.md) | Step-by-step build plan |
| [03-embeddings-explained.md](03-embeddings-explained.md) | How embeddings and vector search work |
| [04-indexing-fix-notes.md](04-indexing-fix-notes.md) | A real indexing bug and its root cause |
| [05-learning-outcomes.md](05-learning-outcomes.md) | What was learned, tied to concrete evidence |
| [learning_plan_status.md](learning_plan_status.md) | Progress against the plan, resource inventory |

## Status

Working end to end: 4 documents indexed (391 chunks), grounded answers with
inline citations, sourced-vs-general distinction, and knowledge-base
retrieval confirmed via traces. Full detail in
[learning_plan_status.md](learning_plan_status.md).
