"""Sanity-check script for a deployed Foundry embedding model.

Usage:
    uv run embed.py "ground rent obligations for leaseholders"
"""

import os
import sys

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

DEFAULT_TEXT = "ground rent obligations for leaseholders"


def main() -> None:
    endpoint = os.environ["AZURE_MODEL_ENDPOINT"]
    deployment_name = os.environ["AZURE_EMBEDDING_DEPLOYMENT"]
    text = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_TEXT

    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(), "https://ai.azure.com/.default"
    )
    client = OpenAI(base_url=endpoint, api_key=token_provider)

    response = client.embeddings.create(model=deployment_name, input=text)
    vector = response.data[0].embedding

    print(f"model: {response.model}")
    print(f"dimensions: {len(vector)}")
    print(f"tokens used: {response.usage.total_tokens}")
    print(f"first 10 values: {vector[:10]}")


if __name__ == "__main__":
    main()



### Real Example Output:

# model: text-embedding-3-small
# dimensions: 1536
# tokens used: 6
# first 10 values: [-0.019195556640625, 0.042236328125, 0.07928466796875, -0.00049591064453125, -0.03765869140625, 0.0158233642578125, 0.0184326171875, -0.01282501220703125, 0.0205078125, -0.005863189697265625]
# model: text-embedding-3-small
# dimensions: 1536
# tokens used: 9
# first 10 values: [0.00426483154296875, 0.0159759521484375, 0.043609619140625, -0.007297515869140625, -0.01232147216796875, 0.007110595703125, -0.004161834716796875, -0.020721435546875, 0.004550933837890625, -0.0223236083984375]
# model: text-embedding-3-small
# dimensions: 1536
# tokens used: 6
# first 10 values: [-0.0428466796875, 0.01568603515625, 0.0030765533447265625, -0.049835205078125, 0.004909515380859375, -0.03424072265625, 0.0025634765625, 0.0379638671875, -0.05169677734375, -0.00942230224609375]

### Explanation of the RAG demo output:

# The embedding model correctly ranked the yellow-house fact highest (0.70 similarity), well ahead of unrelated leasehold facts (~0.03–0.04)
# Even the pizza fact scored lower despite also being "about Luis." Then the chat model generated "Yellow" using only that retrieved sentence as evidence, not its own general knowledge.

# That's the whole RAG loop, end to end, in ~70 lines: embed → rank by similarity → retrieve top match → feed as evidence → generate grounded answer. 