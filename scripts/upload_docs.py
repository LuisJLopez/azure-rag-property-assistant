"""Download source PDFs and upload them to the property-docs blob container.

Usage:
    uv run upload_docs.py
"""

import sys
from pathlib import Path

import requests
from azure.identity import AzureCliCredential
from azure.storage.blob import BlobServiceClient

STORAGE_ACCOUNT = "stpropertykb001"
CONTAINER = "property-docs"
DOWNLOAD_DIR = Path(__file__).parent / "downloads"

DOCUMENTS = {
    "how-to-buy-a-home.pdf": (
        "https://assets.publishing.service.gov.uk/media/5d72293340f0b60926ca4cfc/"
        "6.5492_-_MHCLG_-_How_to_Buy_Guide_WEB.PDF"
    ),
    "how-to-lease.pdf": (
        "https://assets.publishing.service.gov.uk/media/62b2f1b1e90e0765cecebb70/"
        "How_to_Lease_July_2022.pdf"
    ),
    "commonhold-leasehold-reform-bill-guide.pdf": (
        "https://assets.publishing.service.gov.uk/media/69779a943fd50ac304b79778/"
        "Guide_to_the_draft_Commonhold_and_Leasehold_Reform_Bill.pdf"
    ),
    "leasehold-commonhold-reform-briefing.pdf": (
        "https://researchbriefings.files.parliament.uk/documents/CBP-8047/CBP-8047.pdf"
    ),
}


HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; property-kb-prototype/1.0)"}


def download(name: str, url: str) -> Path:
    dest = DOWNLOAD_DIR / name
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    dest.write_bytes(response.content)
    print(f"downloaded {name} ({len(response.content) / 1024:.0f} KB)")
    return dest


def upload(container_client, path: Path) -> None:
    with path.open("rb") as f:
        container_client.upload_blob(name=path.name, data=f, overwrite=True)
    print(f"uploaded {path.name}")


def main() -> None:
    DOWNLOAD_DIR.mkdir(exist_ok=True)

    account_url = f"https://{STORAGE_ACCOUNT}.blob.core.windows.net"
    credential = AzureCliCredential()
    service_client = BlobServiceClient(account_url=account_url, credential=credential)
    container_client = service_client.get_container_client(CONTAINER)

    for name, url in DOCUMENTS.items():
        path = download(name, url)
        upload(container_client, path)

    print(f"\ndone: {len(DOCUMENTS)} documents uploaded to '{CONTAINER}'")


if __name__ == "__main__":
    try:
        main()
    except requests.HTTPError as exc:
        print(f"download failed: {exc}", file=sys.stderr)
        sys.exit(1)
