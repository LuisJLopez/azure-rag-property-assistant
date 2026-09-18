# Getting Started Plan

Step-by-step path for the one-day Property Knowledge Assistant prototype (see [01-property-assistant-idea-and-goal.md](01-property-assistant-idea-and-goal.md)).

## Step 0 — Prereqs

- Azure subscription with permission to create resources
- Azure CLI installed and `az login` done

## Step 1 — Gather documents

- Pick 3–5 public UK property docs (e.g. gov.uk leasehold guidance, a "How to buy a home" PDF, Land Registry explainer). PDF or Markdown is fine per scope.

## Step 2 — Create resources

- Resource group
- Storage account + one Blob container → upload the docs
- Azure AI Search service (Basic tier is enough for this)
- Microsoft Foundry (Azure AI Foundry) project, with a chat model deployment (e.g. gpt-4o-mini) and an embedding model deployment (e.g. text-embedding-3-small)

## Step 3 — Index the documents

- Easiest path for day one: use the **Azure AI Search "Import and vectorize data"** wizard in the portal, pointed at your blob container, with your Foundry embedding deployment selected. This auto-creates the indexer, skillset (chunking), index (text + vector fields), and vectorizer — chunking + embeddings without writing pipeline code.
- Inspect the resulting index in Search Explorer to see chunks, metadata, and vectors.

## Step 4 — Connect to Foundry

- In the Foundry playground, add the AI Search index as a data source ("Add your data" / agent knowledge tool) and chat against it. This is the RAG + citations loop with no custom orchestration code.

## Step 5 — Test

- Run five representative questions, confirm citations appear, and confirm an out-of-scope question returns "not found in the supplied sources."

## Step 6 — Notes

- Fill in the "Expected learning outcomes" section of the idea/goal doc as you go — write one line per concept in your own words right after you touch that piece (e.g. the Blob Storage note right after uploading, the chunking note right after inspecting the index).
