"""Command-line ingestion of approved security sources."""

import sys
from pathlib import Path

from sentinelrag.fetcher import SourceFetchError, SourceFetcher
from sentinelrag.ingestion import ingest_web_source, save_normalized_document
from sentinelrag.sources import load_source_manifest

MANIFEST_PATH = Path("data/sources.yaml")
OUTPUT_DIRECTORY = Path("data/processed")


def find_source(source_id: str):
    """Find one source by its stable manifest identifier."""

    manifest = load_source_manifest(MANIFEST_PATH)

    for source in manifest.sources:
        if source.id == source_id:
            return source

    raise ValueError(f"Unknown source ID: {source_id}")


def ingest_source(source_id: str) -> Path:
    """Fetch, normalize, and save one approved source."""

    source = find_source(source_id)
    document = ingest_web_source(
        source=source,
        fetcher=SourceFetcher(),
    )

    return save_normalized_document(
        document=document,
        output_directory=OUTPUT_DIRECTORY,
    )


def main() -> int:
    """Run one-source ingestion from the terminal."""

    if len(sys.argv) != 2:
        print("Usage: sentinelrag-ingest <source-id>")
        return 2

    try:
        output_path = ingest_source(sys.argv[1])
    except (FileNotFoundError, SourceFetchError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Saved normalized document: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
