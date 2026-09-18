# Embeddings: how they work and why we need two models

## What an embedding model does

A chat model takes text in and produces more text out. An embedding model takes
text in and produces a **vector** out — a fixed-length list of numbers, e.g.
1536 floating-point values for `text-embedding-3-small`.

```
"leasehold flats often have ground rent" -> [0.0123, -0.0456, 0.0788, ...]  (1536 numbers)
```

That vector is a coordinate in a very high-dimensional space. The model is
trained so that text with **similar meaning lands near similar coordinates**,
regardless of the exact words used. This is the key property RAG depends on.

## Why "nearby" is useful: semantic similarity

Two pieces of text about the same idea, phrased differently, produce vectors
that sit close together in that space. Text about unrelated ideas produces
vectors that sit far apart.

```
"ground rent obligations for leaseholders"      -> vector A
"charges a leaseholder must pay to the landlord" -> vector B   (close to A — same meaning)
"how to fit a kitchen sink"                      -> vector C   (far from A and B)
```

"Close" and "far" are measured mathematically — usually with **cosine
similarity**, which checks the angle between two vectors rather than their
raw distance. A search query gets embedded into a vector the same way, and
Azure AI Search finds the document chunks whose vectors have the smallest
angle to the query vector. That's vector search.

This is a big upgrade over keyword search: a keyword search for "ground rent"
won't match a chunk that says "annual charge payable to the freeholder" even
though it's the right answer. Vector search finds it because the *meaning* is
close, even though not one word overlaps. (Azure AI Search's hybrid mode runs
both keyword and vector search and merges the results, so you get the best
of each.)

## Why two separate model deployments

| | Chat model (e.g. `gpt-5-mini`) | Embedding model (e.g. `text-embedding-3-small`) |
|---|---|---|
| Input | Text (+ retrieved chunks) | Text |
| Output | Generated text (an answer) | A fixed-length numeric vector |
| Job in this project | Reads retrieved evidence and writes the final answer, with citations | Converts every document chunk — and every incoming question — into a vector so they can be compared |
| Runs | Once per question, at answer time | Once per chunk at indexing time, and once per question at query time |

They are architecturally different models doing different jobs — one
understands and generates language, the other measures semantic distance.
You can't substitute one for the other: a chat model doesn't output a
comparable numeric vector, and an embedding model can't write a fluent
answer. Foundry deploys them separately because they're billed and scaled
independently, and a RAG pipeline always uses both:

1. **Indexing time** (once, when documents are loaded): the embedding model
   converts every chunk of every PDF into a vector. Azure AI Search stores
   each chunk's text, metadata, and vector together in the index.
2. **Query time** (every question): the embedding model converts your
   *question* into a vector, using the exact same model — vectors from
   different embedding models aren't comparable to each other.
3. **Retrieval**: Azure AI Search compares the question vector to all the
   stored chunk vectors and returns the closest ones.
4. **Generation**: those retrieved chunks are inserted into the chat model's
   input alongside your question. The chat model writes an answer grounded
   in that evidence and can cite which chunk it came from.

## What the response actually looks like

Calling an embedding deployment (via the OpenAI-compatible endpoint, same
pattern as [chat.py](azure_model_deployment/chat.py)) returns JSON shaped
roughly like this:

```json
{
  "data": [
    {
      "embedding": [0.0123, -0.0456, 0.0788, "...", 1536 numbers total],
      "index": 0,
      "object": "embedding"
    }
  ],
  "model": "text-embedding-3-small",
  "object": "list",
  "usage": {
    "prompt_tokens": 8,
    "total_tokens": 8
  }
}
```

There's no "answer" to read — the useful output is purely the `embedding`
array. That array is meaningless on its own; it only becomes useful when
compared against other vectors, which is exactly what Azure AI Search's
vector index does for you automatically once it's wired up.

## Where this fits in the plan

This is Step 2 of [02-getting-started-plan.md](02-getting-started-plan.md).
With the embedding deployment created, the next step (Step 3) is the Azure
AI Search "Import and vectorize data" wizard, which calls this embedding
model once per document chunk to build the vector index — the manual version
of the loop described above.
