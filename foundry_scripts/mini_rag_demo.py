"""Tiny end-to-end RAG demo: embed facts, retrieve by similarity, then
generate an answer with the chat model.

This is the same loop Azure AI Search + Foundry will run for the property
documents, just at toy scale with a few hardcoded sentences instead of a
real index.

Usage:
    uv run mini_rag_demo.py
"""

import math
import os

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

FACTS = [
    "Luis's favourite house colour is yellow.",
    "Luis's favourite food is pizza.",
    "The gov.uk How to Lease guide explains ground rent and service charges.",
    "A leasehold flat's lease can be extended by paying the freeholder a premium.",
]

QUESTION = "My name is Luis, what is my favourite colour?"


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    return dot / (norm_a * norm_b)


def main() -> None:
    endpoint = os.environ["AZURE_MODEL_ENDPOINT"]
    chat_deployment = os.environ["AZURE_MODEL_DEPLOYMENT"]
    embedding_deployment = os.environ["AZURE_EMBEDDING_DEPLOYMENT"]

    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(), "https://ai.azure.com/.default"
    )
    client = OpenAI(base_url=endpoint, api_key=token_provider)

    # 1. Embed every fact once (this is what the search index stores per chunk)
    fact_vectors = [
        client.embeddings.create(model=embedding_deployment, input=fact).data[0].embedding
        for fact in FACTS
    ]

    # 2. Embed the incoming question the same way
    question_vector = (
        client.embeddings.create(model=embedding_deployment, input=QUESTION)
        .data[0]
        .embedding
    )

    # 3. Retrieval: rank facts by cosine similarity to the question
    ranked = sorted(
        zip(FACTS, fact_vectors),
        key=lambda pair: cosine_similarity(question_vector, pair[1]),
        reverse=True,
    )
    print("\n=== RAG demo ===")
    print("Question:", QUESTION)
    print("\nRetrieval ranking (most relevant first):")
    for fact, vector in ranked:
        score = cosine_similarity(question_vector, vector)
        print(f"  {score:.4f}  {fact}")

    top_fact = ranked[0][0]

    # 4. Generation: give the chat model only the top retrieved fact as evidence
    prompt = (
        f"Answer the question using only the evidence below. "
        f"If the evidence doesn't answer it, say so.\n\n"
        f"Evidence: {top_fact}\n\n"
        f"Question: {QUESTION}"
    )
    response = client.responses.create(model=chat_deployment, input=prompt)

    print("\nRetrieved evidence:", top_fact)
    print("Generated answer:", response.output_text)


if __name__ == "__main__":
    main()

# Output:
# Question: My name is Luis, what is my favourite colour?

# Retrieval ranking (most relevant first):
#   0.6992  Luis's favourite house colour is yellow.
#   0.5679  Luis's favourite food is pizza.
#   0.0383  A leasehold flat's lease can be extended by paying the freeholder a premium.
#   0.0327  The gov.uk How to Lease guide explains ground rent and service charges.

# Retrieved evidence: Luis's favourite house colour is yellow.
# Generated answer: Yellow.
