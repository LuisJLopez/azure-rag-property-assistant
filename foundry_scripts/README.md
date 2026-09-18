# foundry_scripts

Sanity-check script for a deployed Foundry chat model.

## Install

Requires [uv](https://docs.astral.sh/uv/).

```bash
cd foundry_scripts
uv sync
cp .env.example .env   # then edit with your endpoint + deployment name
```

## Run

Requires `az login` (auth uses your CLI credentials, no API key stored).

```bash
uv run chat.py "What is the capital of France?"
```
