# Why indexing failed, and the fix

## The symptom

The Azure AI Search "Import and vectorize data" wizard created an indexer that
kept failing with `DeploymentNotFound` whenever it tried to call the
`text-embedding-3-small` embedding model — even though that exact deployment
worked perfectly every time it was called directly (via `embed.py`, via raw
`curl`, with both a bearer token and an API key). The failure was consistent
and specific to Azure AI Search's own internal call to the model, never to
calls made directly by us.

## Resource vs. deployment: two different things

Two separate ideas got easy to conflate here:

- A **resource** (`Microsoft.CognitiveServices/accounts`) is the Azure object
  you create — it has a region, a pricing tier, an endpoint, and keys. Think
  of it as "an account with Azure OpenAI."
- A **deployment** is a specific model made available *inside* that resource
  — e.g. `text-embedding-3-small` or `gpt-5-mini`. One resource can host
  several deployments.

A resource also has a **kind**, which is the type of resource it is:

- `OpenAI` — the original, dedicated Azure OpenAI resource type. Only hosts
  OpenAI-family models.
- `AIServices` — a newer, unified "multi-service" resource type introduced
  with Microsoft Foundry. It can host OpenAI models *and* other Azure AI
  services (vision, language, etc.) under one resource.

Your original resource, `luisjlop-1485-resource`, is kind `AIServices` — it's
what Microsoft Foundry creates by default now. It's not "wrong," and it
served your chat model (`gpt-5-mini`) fine the whole time, including every
direct API call we made to test the embedding deployment on it.

## Why it broke specifically for Azure AI Search

Azure AI Search's built-in `AzureOpenAIEmbeddingSkill` — the piece the
"Import and vectorize data" wizard wires up automatically — makes its own
internal, first-party, service-to-service call to your model resource. That
internal path has different (and less flexible) support than the general
public REST API surface every client library and `curl` call goes through.

The strongest evidence: when we created a brand-new resource of kind
`OpenAI` (`property-kb-openai`) in the same region as the Search service and
pointed the skill at it instead, its resource properties explicitly listed
`Microsoft.Search` as a **trusted service**:

```json
"capabilities": [
  {
    "name": "TrustedServices",
    "value": "Microsoft.CognitiveServices,Microsoft.MachineLearningServices,Microsoft.Search,Microsoft.VideoIndexer"
  }
]
```

That's a first-party trust relationship declared directly on the resource.
The original `AIServices`-kind resource didn't expose that same explicit
trust list for its embedding deployment — plausibly because Search's
integration with the newer unified resource kind is still catching up.
Everything else we tried first (managed identity, API keys, waiting out
possible RBAC propagation delay, checking deployment SKU) ruled itself out
one by one; the resource *kind* was the actual variable that mattered.

## The fix

1. Created a second, dedicated resource: `property-kb-openai`, kind
   `OpenAI`, in `uksouth` (same region as the Search service, removing
   region as a variable too).
2. Deployed `text-embedding-3-small` on it.
3. Updated `property-kb-skillset`'s `AzureOpenAIEmbeddingSkill` to point at
   this new resource's endpoint and key instead of the original one.

Your chat model (`gpt-5-mini`) stays on the original `AIServices` resource —
that side was never broken. Only the embedding call used by Search's
indexing pipeline needed the dedicated `OpenAI`-kind resource.

## Where things stand now

| Resource | Kind | Region | Used for |
|---|---|---|---|
| `luisjlop-1485-resource` | AIServices | swedencentral | chat model (`gpt-5-mini`) — `chat.py`, general Foundry use |
| `property-kb-openai` | OpenAI | uksouth | embedding model, called specifically by Azure AI Search's indexer |

Both resources' embedding deployments are functionally identical models —
the split exists purely to work around Azure AI Search's current
compatibility gap with the `AIServices` resource kind, not because the model
or the original resource was doing anything wrong.

## The final run

8 indexer runs total: 7 failures (`12:07` through `14:23`, each failing in
1–11 seconds at the embedding step) followed by one success once the
skillset pointed at `property-kb-openai`:

```
Status    Start time           Duration   Docs succeeded   Errors/Warnings
Success   18/09/2026, 14:30:33   3 mins   4                0/0
Failed    18/09/2026, 14:23:55   1 s      0                1/0
Failed    18/09/2026, 12:26:33   2 s      0                1/0
Failed    18/09/2026, 12:24:01   631 ms   0                1/0
Failed    18/09/2026, 12:18:55   3 s      0                1/0
Failed    18/09/2026, 12:16:00   3 s      0                1/0
Failed    18/09/2026, 12:10:43   3 s      0                1/0
Failed    18/09/2026, 12:07:55   11 s     0                1/0
```

Result: `property-kb` index holds 390 chunks across the 4 PDFs.
