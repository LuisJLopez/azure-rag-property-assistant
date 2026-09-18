# Property Knowledge Assistant: Idea and Goal

## One-day learning objective

Build a small, non-work prototype that answers questions about a set of public UK property documents. The purpose is to gain hands-on exposure to Microsoft Foundry, Azure AI Search, Blob Storage, indexing, embeddings, vector retrieval, RAG, grounding and citations.

This is a learning prototype, not a production service and not a system that gives financial or property-investment advice.

## The idea

Create a **Property Knowledge Assistant** that can answer questions such as:

- What risks do these documents identify for buyers?
- What do the documents say about leasehold properties?
- Compare the reported considerations for flats and houses.
- What evidence supports the answer?

The assistant must answer only from the documents uploaded for the prototype, show citations, distinguish sourced facts from general explanation, and say when the indexed material does not contain the answer.

## Why this is a good substitute for a portfolio assistant

It exercises the same core technical pattern without using company intellectual property:

1. Source documents represent domain knowledge.
2. Blob Storage holds the originals.
3. Azure AI Search extracts and indexes searchable content.
4. An embedding model creates vectors for semantic similarity.
5. The search index stores chunks, metadata and vector fields.
6. Microsoft Foundry connects a model or agent to the index.
7. The model generates an answer from retrieved evidence and returns citations.

The domain is intentionally simpler. The first version is a **knowledge assistant**, not an analytics or recommendation engine.

## Scope

### In scope

- A small collection of public or self-authored property documents
- PDF, Markdown or text content
- One Blob Storage container
- One Azure AI Search service and index
- Keyword, vector and preferably hybrid retrieval
- One chat model deployment
- One embedding model deployment
- A Foundry playground or agent connected to the search index
- A short test set with expected source documents
- Grounded answers with citations

### Out of scope

- Scraping live property listings
- Personal financial recommendations
- Mortgage eligibility decisions
- House-price prediction
- Production UI
- Multi-agent orchestration
- Infrastructure-as-code
- Private networking and full production hardening
- Work or client data

## Definition of done

The prototype is complete when:

- [ ] Several permitted documents are present in Blob Storage.
- [ ] An Azure AI Search index contains retrievable text, source metadata and vector data.
- [ ] A search query returns relevant chunks from the expected documents.
- [ ] A Foundry chat experience uses the index as its knowledge source.
- [ ] At least five representative questions have been tested.
- [ ] Answers contain citations to indexed sources.
- [ ] An unanswerable question produces an explicit “not found in the supplied sources” response.
- [ ] Notes capture the roles of Blob Storage, the indexer, the index, embeddings, retrieval and generation.

## Expected learning outcomes

By the end, you should be able to explain:

- **Blob Storage:** stores the source files.
- **Indexer:** reads source files and populates the search index.
- **Chunking:** splits long documents into retrievable passages.
- **Embedding:** converts the semantic meaning of text into a numeric vector.
- **Search index:** stores searchable fields, metadata and vector fields optimised for retrieval.
- **Vector search:** finds semantically similar chunks.
- **Keyword search:** finds lexical matches.
- **Hybrid search:** combines keyword and vector retrieval.
- **RAG:** retrieves evidence, adds it to the model input, and generates a grounded answer.
- **Citation:** links an answer back to the source metadata stored in the index.
- **Evaluation:** checks retrieval relevance, groundedness and behaviour when evidence is absent.

## Success criteria

A successful one-day prototype is deliberately small:

- It works end to end.
- You can inspect the indexed documents and retrieved chunks.
- You understand where the original files and searchable vectors live.
- You can explain why a particular source was retrieved.
- The assistant does not invent an answer when evidence is missing.

## Safe data rules

- Use public, synthetic or self-authored documents only.
- Do not upload Brit, client, employee or commercially sensitive material.
- Do not include personal data, credentials, connection strings or secrets.
- Treat all outputs as educational and verify any property or financial facts at source.

## Possible follow-on experiment

After the basic RAG path works, add a deterministic calculator such as rental yield or monthly mortgage repayment. Keep calculations in normal code and let the model explain the result. This demonstrates the distinction between document retrieval and an analytics/tool layer, which is directly relevant to a future portfolio-management assistant.

## Reference documentation

- [RAG and indexes in Microsoft Foundry](https://learn.microsoft.com/en-us/azure/foundry/concepts/retrieval-augmented-generation)
- [RAG in Azure AI Search](https://learn.microsoft.com/en-us/azure/search/retrieval-augmented-generation-overview)
- [Index data from Azure Blob Storage](https://learn.microsoft.com/en-us/azure/search/search-how-to-index-azure-blob-storage)
- [Connect an Azure AI Search index to Foundry agents](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/ai-search)
