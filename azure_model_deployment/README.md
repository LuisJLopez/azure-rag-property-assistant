# azure_model_deployment

Sanity-check script for a deployed Foundry chat model.

## Install

Requires [uv](https://docs.astral.sh/uv/).

```bash
cd azure_model_deployment
uv sync
cp .env.example .env   # then edit with your endpoint + deployment name
```

## Run

Requires `az login` (auth uses your CLI credentials, no API key stored).

```bash
uv run chat.py "What is the capital of France?"
```
