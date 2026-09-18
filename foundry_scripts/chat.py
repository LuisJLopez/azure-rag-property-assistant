"""Sanity-check script for a deployed Foundry chat model.

Usage:
    uv run chat.py "What is the capital of France?"
"""

import os
import sys

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

DEFAULT_PROMPT = "What is the capital of France?"


def main() -> None:
    endpoint = os.environ["AZURE_MODEL_ENDPOINT"]
    deployment_name = os.environ["AZURE_MODEL_DEPLOYMENT"]
    prompt = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PROMPT

    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(), "https://ai.azure.com/.default"
    )
    client = OpenAI(base_url=endpoint, api_key=token_provider)

    response = client.responses.create(model=deployment_name, input=prompt)
    print(response.output_text)


if __name__ == "__main__":
    main()
