from datetime import UTC, datetime
from pathlib import Path

import pytest

from sentinelrag.documents import (
    NormalizedDocument,
    build_normalized_document,
    normalize_html,
)
from sentinelrag.sources import load_source_manifest


def test_normalized_document_preserves_provenance() -> None:
    document = NormalizedDocument(
        source_id="owasp-top-10-2021",
        title="OWASP Top 10:2021",
        publisher="OWASP Foundation",
        source_url="https://owasp.org/Top10/2021/A00_2021_Introduction/",
        retrieved_at=datetime(2026, 8, 13, tzinfo=UTC),
        content_hash="a" * 64,
        content="The OWASP Top 10 is an application-security awareness document.",
        topics=["application-security"],
        license={
            "name": "Creative Commons Attribution 3.0 Unported",
            "url": "https://creativecommons.org/licenses/by/3.0/",
            "attribution_required": True,
        },
    )

    assert document.source_id == "owasp-top-10-2021"
    assert document.retrieved_at.tzinfo is UTC
    assert len(document.content_hash) == 64


def test_normalize_html_removes_page_chrome() -> None:
    html = Path("tests/fixtures/owasp_sample.html").read_text(encoding="utf-8")

    content = normalize_html(html)

    assert "OWASP Top 10" in content
    assert "A01: Broken Access Control" in content
    assert "Access control enforces policy" in content
    assert "OWASP website header" not in content
    assert "Home" not in content
    assert "Privacy policy" not in content
    assert "console.log" not in content


def test_normalize_html_rejects_empty_document() -> None:
    with pytest.raises(ValueError, match="no readable content"):
        normalize_html("<html><body><script>ignored()</script></body></html>")


def test_build_normalized_document_uses_manifest_metadata() -> None:
    html = Path("tests/fixtures/owasp_sample.html").read_text(encoding="utf-8")
    manifest = load_source_manifest(Path("data/sources.yaml"))
    source = manifest.sources[0]
    retrieved_at = datetime(2026, 8, 13, tzinfo=UTC)

    document = build_normalized_document(
        source=source,
        html=html,
        retrieved_at=retrieved_at,
    )

    assert document.source_id == source.id
    assert document.title == source.title
    assert document.publisher == source.publisher
    assert document.source_url == source.url
    assert document.topics == source.topics
    assert document.license == source.license
    assert document.retrieved_at == retrieved_at
    assert len(document.content_hash) == 64
    assert "A01: Broken Access Control" in document.content


def test_content_hash_ignores_navigation_changes() -> None:
    manifest = load_source_manifest(Path("data/sources.yaml"))
    source = manifest.sources[0]

    first_html = """
    <html>
      <body>
        <nav>Original navigation</nav>
        <main>
          <h1>Security Guidance</h1>
          <p>Use access controls to restrict unauthorized actions.</p>
        </main>
      </body>
    </html>
    """

    second_html = """
    <html>
      <body>
        <nav>Completely different navigation</nav>
        <main>
          <h1>Security Guidance</h1>
          <p>Use access controls to restrict unauthorized actions.</p>
        </main>
      </body>
    </html>
    """

    first_document = build_normalized_document(source, first_html)
    second_document = build_normalized_document(source, second_html)

    assert first_document.content == second_document.content
    assert first_document.content_hash == second_document.content_hash


def test_content_hash_changes_when_evidence_changes() -> None:
    manifest = load_source_manifest(Path("data/sources.yaml"))
    source = manifest.sources[0]

    first_document = build_normalized_document(
        source,
        "<main><p>Enable multifactor authentication.</p></main>",
    )
    second_document = build_normalized_document(
        source,
        "<main><p>Disable multifactor authentication.</p></main>",
    )

    assert first_document.content_hash != second_document.content_hash
