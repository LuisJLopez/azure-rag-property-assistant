# Learning outcomes

What each concept from [01-property-assistant-idea-and-goal.md](01-property-assistant-idea-and-goal.md)
actually meant in this project, tied to what we built and observed rather
than textbook definitions.

## Blob Storage

Where the 4 source PDFs live, unmodified, as-is (`stpropertykb001`, container
`property-docs`). Nothing else in the pipeline reads the original files
directly — Search's indexer is the only thing that touches them. Access to
blob *data* (not just the resource) needed its own RBAC grant
(`Storage Blob Data Contributor` for uploading, `Storage Blob Data Reader`
for the Search service to read) — resource-level access and data-level
access are separate permission layers in Azure.

## Indexer

The thing that actually pulls documents out of Blob Storage and runs the
pipeline that populates the index. We didn't write it — the "Import and
vectorize data" wizard generated `property-kb-indexer` for us, along with a
matching data source and skillset. Its execution history (visible under
Search → Indexers) is the ground truth for whether indexing worked: it shows
every run, how many documents succeeded/failed, and the exact error for each
failure — this is where almost all of today's debugging actually happened.

## Chunking

Splitting each PDF into smaller passages before embedding, done here by the
`SplitSkill` (`textSplitMode: pages`, ~2000 characters per chunk, 500
characters of overlap between chunks). Each chunk becomes its own row in the
index. The 4 PDFs produced 390 chunks — a single flat "document" would be
too large and too unfocused to embed meaningfully or cite precisely; a
citation needs to point at a specific passage, not an entire 20-page guide.

## Embedding

Converting a chunk of text into a fixed-length vector (1536 numbers for
`text-embedding-3-small`) that captures its meaning. Confirmed hands-on with
`embed.py` — the same sentence always produces the same vector, and
semantically similar sentences produce vectors that are numerically close
(cosine similarity), even with no words in common. This is the property that
makes retrieval-by-meaning possible instead of retrieval-by-exact-keyword.

## Search index

The actual searchable object (`property-kb`) — not the PDFs, not the
container, the index. Each of its 391 rows holds a chunk's text, its vector,
and metadata (source file, chunk id). This is what every query actually
touches. Inspected directly via Search Explorer and the REST `$count`
endpoint throughout the session.

## Vector search

Finding chunks whose *meaning* is close to a question's meaning, via cosine
similarity between the question's embedding and every stored chunk's
embedding. Proved this manually before the real index existed:
`mini_rag_demo.py` embedded 4 hardcoded facts, ranked them by similarity to
"My name is Luis, what is my favourite colour?", and correctly ranked the
colour fact highest (0.70) over an unrelated leasehold fact (0.03) — despite
zero shared keywords.

## Keyword search

Finding chunks by literal word/phrase overlap (this is what a search engine
did before embeddings existed). Azure AI Search still supports this
alongside vector search — it's not replaced by vectors, it's complementary
(exact terms like "LPE1" or a specific act name are things keyword search
is precise for, that vector search would only approximate).

## Hybrid search

Running both keyword and vector search on the same query and merging the
results. Azure AI Search does this by default once both fields exist in the
index. We enabled semantic ranking on top of that — an extra AI re-scoring
pass over the combined results, visible as "Enable semantic ranker" in the
index config.

## RAG (retrieval-augmented generation)

The full loop: embed the question → retrieve the closest chunks from the
index → hand those chunks to the chat model as evidence → the model
generates an answer grounded in that evidence rather than its own training
data. Built and watched this work twice: once by hand in
`mini_rag_demo.py` (retrieve → construct a prompt → call `gpt-5-mini`), and
once for real through Foundry's `property-kb-knowledge` knowledge base
attached to `property-agent`. The real version does the same loop, just
managed for us — visible directly in the agent's Traces as a distinct
`knowledge_base_retrieve` tool call happening before the model's response.

## Citation

A link from a specific claim in the answer back to the specific chunk it
came from. In the Foundry agent's answers this showed up as inline numbered
references (e.g. `【10:14†leasehold-commonhold-reform-briefing.pdf】`) that
resolve to an actual document URL in the index
(`srch-property-kb.search.windows.net/indexes/property-kb/docs/...`) — not
just "trust me," an actual pointer to the retrieved evidence.

## Evaluation

Checking three separate things, not just "does it work":

1. **Retrieval relevance** — does the right chunk get retrieved for a given
   question? (proved with the cosine-similarity ranking in
   `mini_rag_demo.py`, and confirmed for real via Traces showing
   `knowledge_base_retrieve` being called)
2. **Groundedness** — does the generated answer only state what the
   retrieved evidence supports, with citations? (the leasehold/freehold and
   flats/houses comparison answers both did this correctly)
3. **Behaviour when evidence is absent** — does it say so, instead of
   guessing? This is where we found a real gap: asking about Japanese
   mortgage rates got a hedge about lacking live web access rather than the
   spec's required "not found in the supplied sources." A working system
   still needs this kind of adversarial testing to find where it quietly
   drifts from spec — see [learning_plan_status.md](learning_plan_status.md)
   Step 5 for the detail.

## One thing that surprised me

Agentic retrieval doesn't always search the knowledge base — it decides
per-question whether retrieval is warranted, based on the system
instructions. The default instructions ("You are an AI assistant that helps
people find information") weren't strong enough to force a search on every
question; a vague-sounding personal question skipped retrieval entirely and
got answered from the model's own guesswork. This only became visible by
checking the Traces tab and seeing which tools actually ran — the chat
output alone didn't make it obvious. Fixed by making the instructions
explicit: always search first, answer only from what's retrieved, say so
when nothing relevant comes back.
