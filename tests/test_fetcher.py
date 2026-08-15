from pathlib import Path

import httpx
import pytest

from sentinelrag.fetcher import SourceFetcher, SourceFetchError
from sentinelrag.sources import load_source_manifest


def test_fetcher_downloads_enabled_html_source() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url == "https://owasp.org/Top10/2021/A00_2021_Introduction/"
        assert request.headers["accept"] == "text/html"
        assert request.headers["user-agent"].startswith("SentinelRAG/")

        return httpx.Response(
            200,
            headers={"content-type": "text/html; charset=utf-8"},
            text="<main><h1>OWASP Top 10</h1></main>",
        )

    manifest = load_source_manifest(Path("data/sources.yaml"))
    source = manifest.sources[0]
    fetcher = SourceFetcher(transport=httpx.MockTransport(handler))

    html = fetcher.fetch(source)

    assert "OWASP Top 10" in html


def test_fetcher_rejects_disabled_source() -> None:
    manifest = load_source_manifest(Path("data/sources.yaml"))
    disabled_source = manifest.sources[2]
    fetcher = SourceFetcher()

    with pytest.raises(ValueError, match="Source is disabled"):
        fetcher.fetch(disabled_source)


def test_fetcher_rejects_non_html_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"content-type": "application/pdf"},
            content=b"%PDF",
        )

    manifest = load_source_manifest(Path("data/sources.yaml"))
    source = manifest.sources[0]
    fetcher = SourceFetcher(transport=httpx.MockTransport(handler))

    with pytest.raises(SourceFetchError, match="unsupported content type"):
        fetcher.fetch(source)
