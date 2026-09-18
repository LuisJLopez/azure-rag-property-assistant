# scripts

Utility scripts for the Property Knowledge Assistant prototype.

## Install

Requires [uv](https://docs.astral.sh/uv/).

```bash
cd scripts
uv sync
```

## Run

Requires `az login` to have been run first (scripts use your CLI credentials, no keys stored).

```bash
uv run upload_docs.py
```

Downloads the source PDFs into `downloads/` and uploads them to the `property-docs` blob container.
