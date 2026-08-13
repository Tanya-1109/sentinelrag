from datetime import UTC, datetime
from pathlib import Path

import httpx

from sentinelrag.fetcher import SourceFetcher
from sentinelrag.ingestion import ingest_web_source, save_normalized_document
from sentinelrag.sources import load_source_manifest


def test_ingest_web_source_builds_normalized_document() -> None:
    html = Path("tests/fixtures/owasp_sample.html").read_text(encoding="utf-8")

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "text/html; charset=utf-8"},
            text=html,
        )

    manifest = load_source_manifest(Path("data/sources.yaml"))
    source = manifest.sources[0]
    fetcher = SourceFetcher(transport=httpx.MockTransport(handler))
    retrieved_at = datetime(2026, 8, 13, tzinfo=UTC)

    document = ingest_web_source(
        source=source,
        fetcher=fetcher,
        retrieved_at=retrieved_at,
    )

    assert document.source_id == "owasp-top-10-2021"
    assert document.retrieved_at == retrieved_at
    assert "A01: Broken Access Control" in document.content
    assert "OWASP website header" not in document.content
    assert len(document.content_hash) == 64


def test_save_normalized_document_writes_json(tmp_path: Path) -> None:
    html = Path("tests/fixtures/owasp_sample.html").read_text(encoding="utf-8")

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "text/html; charset=utf-8"},
            text=html,
        )

    manifest = load_source_manifest(Path("data/sources.yaml"))
    source = manifest.sources[0]
    fetcher = SourceFetcher(transport=httpx.MockTransport(handler))
    document = ingest_web_source(source=source, fetcher=fetcher)

    output_path = save_normalized_document(
        document=document,
        output_directory=tmp_path,
    )

    saved_document = output_path.read_text(encoding="utf-8")

    assert output_path.name == "owasp-top-10-2021.json"
    assert '"source_id": "owasp-top-10-2021"' in saved_document
    assert '"content_hash":' in saved_document
    assert "A01: Broken Access Control" in saved_document
