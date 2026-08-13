"""Orchestration for downloading and normalizing approved sources."""

from datetime import datetime
from pathlib import Path

from sentinelrag.documents import NormalizedDocument, build_normalized_document
from sentinelrag.fetcher import SourceFetcher
from sentinelrag.sources import SecuritySource


def ingest_web_source(
    source: SecuritySource,
    fetcher: SourceFetcher,
    retrieved_at: datetime | None = None,
) -> NormalizedDocument:
    """Fetch and normalize one approved web source."""

    html = fetcher.fetch(source)

    return build_normalized_document(
        source=source,
        html=html,
        retrieved_at=retrieved_at,
    )


def save_normalized_document(
    document: NormalizedDocument,
    output_directory: Path,
) -> Path:
    """Write a normalized document as readable JSON."""

    output_directory.mkdir(parents=True, exist_ok=True)
    output_path = output_directory / f"{document.source_id}.json"

    output_path.write_text(
        document.model_dump_json(indent=2),
        encoding="utf-8",
    )

    return output_path
