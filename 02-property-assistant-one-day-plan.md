# Property Knowledge Assistant: One-Day Build Plan

## Target architecture

```text
Public or self-authored property documents
                  |
                  v
      Azure Blob Storage container
                  |
                  v
 Azure AI Search data source + indexer
                  |
           document extraction
           chunking / enrichment
           embedding generation
                  |
                  v
        Azure AI Search index
  text + metadata + source URL + vectors
                  |
       keyword / vector / hybrid search
                  |
                  v
 Microsoft Foundry project and model/agent
                  |
          grounded answer + citations
                  |
                  v
       Foundry playground test session
```

## Resource responsibilities

- **Blob Storage:** original source documents.
- **Azure AI Search data source:** connection from Search to the Blob container.
- **Indexer:** imports and periodically refreshes content.
- **Skillset or integrated vectorisation path:** extraction, chunking and embedding steps where configured.
- **Azure AI Search index:** searchable chunks, metadata and vectors.
- **Embedding deployment:** generates vectors for document chunks and vector queries.
- **Chat model deployment:** generates grounded responses.
- **Microsoft Foundry project:** model, connection, agent/playground and evaluation experience.

## Before starting

- [ ] Use a personal or approved sandbox Azure subscription.
- [ ] Confirm that creating Foundry, model, Storage and Search resources is permitted.
- [ ] Check model availability in the chosen Azure region.
- [ ] Set a small budget or cost alert.
- [ ] Prepare several public, synthetic or self-authored documents.
- [ ] Do not use work IP, customer information or personal data.
- [ ] Prefer Microsoft Entra ID and managed identities over embedded keys where the selected wizard supports them.

Resource names vary by portal experience and evolve over time. Follow the current Microsoft Learn instructions linked below if a label differs.

# Phase 1: Define the experiment

## 1. Write five questions before building

Choose questions whose answers you can locate manually in the documents. For example:

1. What concerns are mentioned for leasehold buyers?
2. What maintenance costs should a buyer investigate?
3. What does the source say about energy efficiency?
4. Which documents discuss rental demand?
5. What evidence is provided for the answer?

Also add two negative tests:

- A question unrelated to the documents
- A question requesting a recommendation unsupported by the documents

## 2. Prepare a small, clean corpus

Use documents with varied but clear content. Give each file a useful name. For example:

```text
property-buying-checklist.md
leasehold-guide.pdf
epc-explainer.pdf
rental-market-summary.md
home-maintenance-guide.pdf
```

Keep a note of document title, publisher, date, source link and allowed usage. If downloading public material, retain links rather than redistributing copyrighted documents unnecessarily.

# Phase 2: Provision the Azure resources

## 3. Create a resource group

Create one temporary resource group so all prototype resources can be identified and removed together.

Suggested logical contents:

```text
rg-property-rag-lab
  storage account
  Azure AI Search service
  Microsoft Foundry resource/project
  model deployments
```

Use the same suitable region where possible, subject to model and service availability.

## 4. Create Blob Storage

1. Create a general-purpose v2 Storage account.
2. Create a private container called `property-docs`.
3. Upload the prepared files.
4. Record the container and storage account names.
5. Verify the uploaded documents open correctly.

Do not place secrets or private documents in the container.

## 5. Create Azure AI Search

1. Create an Azure AI Search service suitable for a small experiment.
2. Open the service in the Azure portal.
3. Note where indexes, indexers, data sources, skillsets and Search Explorer are shown.
4. Confirm the selected tier supports the features used by the chosen indexing wizard.

## 6. Create a Microsoft Foundry project and models

1. Create or open a Microsoft Foundry project.
2. Deploy an available chat model.
3. Deploy a compatible embedding model.
4. Record the deployment names, not credentials.
5. Connect the project to the Azure AI Search service if the workflow requires an explicit connection.

Do not hard-code API keys in source files. For a first portal-only prototype, use the authentication options offered by the current guided experience.

# Phase 3: Build and inspect the index

## 7. Import the Blob documents

Use the current Azure AI Search import and vectorisation experience, or the equivalent Foundry data/index flow:

1. Select Azure Blob Storage as the data source.
2. Select the storage account and `property-docs` container.
3. Configure document extraction.
4. Enable chunking if offered.
5. Select the embedding deployment for vectorisation.
6. Include source metadata needed for citations, such as file name, title or source URL.
7. Create the search index, indexer and any associated skillset.
8. Run the indexer.

## 8. Inspect the generated objects

Open each object and identify:

- **Data source:** points to the Blob container.
- **Indexer:** controls ingestion and refresh.
- **Skillset:** enrichment pipeline, if created.
- **Index:** field schema and retrieval configuration.
- **Text field:** contains the chunk or extracted content.
- **Vector field:** contains the chunk embedding.
- **Metadata fields:** identify the source document and support citations.
- **Key field:** uniquely identifies each indexed record.

Write down the vector dimensions and ensure they match the selected embedding model's configuration.

## 9. Validate in Search Explorer

Run several searches directly against the index before involving a chat model:

- Keyword query using an exact term from a document
- Semantic or natural-language query
- Vector or hybrid query if exposed by the portal workflow
- Query with selected fields so you can inspect content and source metadata

For every test, record:

```text
Question:
Expected document:
Top result:
Relevant? yes/no
Useful source metadata present? yes/no
```

If retrieval is poor, fix ingestion or metadata before tuning the prompt.

# Phase 4: Connect the index to Foundry

## 10. Create the chat experience

Use a Foundry playground or agent experience that supports Azure AI Search:

1. Select the deployed chat model.
2. Add the Azure AI Search index as the knowledge source or tool.
3. Map the content field used for grounding.
4. Map the source URL/title fields used for citations.
5. Configure retrieval settings conservatively for the small corpus.
6. Add a system instruction similar to the one below.

```text
You are an educational property knowledge assistant.
Answer only from the retrieved sources.
Cite the source for each material factual claim.
If the indexed sources do not contain enough evidence, say so clearly.
Do not provide personalised financial, mortgage, legal or investment advice.
Distinguish sourced facts from general explanation.
```

## 11. Run the test set

For each predefined question, check:

- Was the expected document retrieved?
- Is the answer supported by the retrieved text?
- Are citations present and useful?
- Does the assistant combine sources without misrepresenting them?
- Does it refuse to invent missing information?

Test wording variations to see the difference between lexical and semantic retrieval.

# Phase 5: Learn deliberately

## 12. Perform three controlled experiments

### Experiment A: Remove vector retrieval

Run a paraphrased question using keyword-only retrieval if the interface permits it. Compare recall with vector or hybrid retrieval.

### Experiment B: Change chunking

If practical, create a second small index with different chunk sizing or overlap. Compare whether retrieved passages contain enough surrounding context.

### Experiment C: Ask an unanswerable question

Confirm the model states that the indexed sources do not contain sufficient evidence. If it guesses, strengthen the system instruction and inspect retrieved content.

## 13. Document the end-to-end request flow

Be able to describe this sequence:

```text
1. User submits a question.
2. The question is represented for retrieval.
3. Azure AI Search retrieves relevant indexed chunks.
4. Retrieved text and metadata are added to the model input.
5. The chat model generates a grounded response.
6. Citation metadata links the answer to its source.
```

Also document the storage distinction:

```text
Blob Storage: original files
Azure AI Search index: searchable text, metadata and vector fields
Foundry/model: orchestration and response generation, not the source-document store
```

# Phase 6: Wrap up

## 14. Capture evidence of learning

Save:

- Architecture diagram
- Resource inventory without secrets
- Index field schema
- One keyword-search result
- One vector or hybrid-search result
- Five chat questions and answers
- One successful negative test
- Notes on what was confusing or surprising

## 15. Clean up

- Remove any downloaded material that should not be retained.
- Delete the prototype resource group if it is no longer needed.
- Otherwise disable unnecessary resources and review costs.
- Remove unused keys and local `.env` files.

# Troubleshooting order

When the assistant gives a bad answer, debug in this order:

1. **Source quality:** Does the answer exist in the corpus?
2. **Ingestion:** Was the relevant document indexed successfully?
3. **Text extraction:** Is the extracted content readable?
4. **Chunking:** Does a retrieved chunk contain sufficient context?
5. **Metadata:** Can the result identify and cite the source?
6. **Retrieval:** Does Search Explorer return the correct chunk?
7. **Prompt grounding:** Is the model instructed to use only retrieved evidence?
8. **Generation:** Is the final response faithful to the evidence?

Do not start by changing the chat prompt if the right chunk is not being retrieved.

# Optional code stretch goal

Only after the portal flow works, create a tiny Python script that:

1. Authenticates with `DefaultAzureCredential`.
2. Sends a query to Azure AI Search.
3. Prints the top chunks and source metadata.
4. Sends those chunks to the chat model as grounding context.
5. Prints the response and citations.

This is optional. The primary goal is to understand and inspect the managed Foundry and Azure AI Search workflow.

# Final checklist

- [ ] Safe corpus selected
- [ ] Blob container populated
- [ ] Search service created
- [ ] Chat and embedding models deployed
- [ ] Indexer completed successfully
- [ ] Index fields inspected
- [ ] Search Explorer tests passed
- [ ] Foundry connected to the index
- [ ] Grounded answers returned
- [ ] Citations checked
- [ ] Negative tests passed
- [ ] Architecture and findings documented
- [ ] Costs reviewed and resources cleaned up

# Reference documentation

- [RAG and indexes in Microsoft Foundry](https://learn.microsoft.com/en-us/azure/foundry/concepts/retrieval-augmented-generation)
- [RAG in Azure AI Search](https://learn.microsoft.com/en-us/azure/search/retrieval-augmented-generation-overview)
- [Index data from Azure Blob Storage](https://learn.microsoft.com/en-us/azure/search/search-how-to-index-azure-blob-storage)
- [Search over Blob Storage content](https://learn.microsoft.com/en-us/azure/search/search-blob-storage-integration)
- [Connect an Azure AI Search index to Foundry agents](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/ai-search)
