import hashlib
from datetime import UTC, datetime

from pydantic import ValidationError
import pytest
import json
from pathlib import Path
from sentinelrag.chunks import (
    DocumentChunk,
    build_document_chunks,
    load_document_chunks,
    save_document_chunks,
    split_content,
)
from sentinelrag.documents import NormalizedDocument
from sentinelrag.sources import SourceLicense


def test_document_chunk_preserves_provenance() -> None:
    chunk = DocumentChunk(
        chunk_id="owasp-top-10-2021::0000",
        source_id="owasp-top-10-2021",
        chunk_index=0,
        content="Broken access control allows unauthorized actions.",
        content_hash="a" * 64,
        document_hash="b" * 64,
        start_char=0,
        end_char=50,
        title="OWASP Top 10:2021",
        publisher="OWASP Foundation",
        source_url="https://owasp.org/Top10/2021/A00_2021_Introduction/",
        topics=["application-security"],
    )

    assert chunk.chunk_index == 0
    assert chunk.document_hash == "b" * 64
    assert chunk.end_char > chunk.start_char


def test_document_chunk_rejects_invalid_range() -> None:
    with pytest.raises(
        ValidationError,
        match="Chunk end must be greater than its start",
    ):
        DocumentChunk(
            chunk_id="example-source::0000",
            source_id="example-source",
            chunk_index=0,
            content="Example content",
            content_hash="a" * 64,
            document_hash="b" * 64,
            start_char=20,
            end_char=10,
            title="Example",
            publisher="Example Publisher",
            source_url="https://example.com/security",
            topics=["security"],
        )


def test_split_content_preserves_offsets() -> None:
    content = (
        "Broken access control permits unauthorized actions.\n"
        "Use deny-by-default authorization policies.\n"
        "Log access-control failures for investigation."
    )

    spans = split_content(content, max_chars=80, overlap_chars=0)

    assert len(spans) > 1

    for span in spans:
        assert span.content == content[span.start_char : span.end_char]
        assert len(span.content) <= 80


def test_split_content_is_deterministic() -> None:
    content = "First security paragraph.\nSecond security paragraph."

    first_result = split_content(content, max_chars=30, overlap_chars=0)
    second_result = split_content(content, max_chars=30, overlap_chars=0)

    assert first_result == second_result


def test_split_content_rejects_invalid_arguments() -> None:
    with pytest.raises(ValueError, match="Maximum chunk size must be positive"):
        split_content("Security content", max_chars=0, overlap_chars=0)

    with pytest.raises(ValueError, match="Content cannot be empty"):
        split_content("   ")


def test_split_content_creates_word_aligned_overlap() -> None:
    content = (
        "Access control prevents unauthorized actions. "
        "Authorization must be checked on every request. "
        "Failures should be logged for investigation. "
        "Deny access when authorization cannot be verified."
    )

    spans = split_content(
        content,
        max_chars=90,
        overlap_chars=25,
    )

    assert len(spans) > 1

    for previous, current in zip(spans, spans[1:]):
        assert current.start_char < previous.end_char
        assert current.start_char > previous.start_char
        assert current.content == content[current.start_char : current.end_char]
        assert content[current.start_char - 1].isspace()


def test_split_content_rejects_invalid_overlap() -> None:
    with pytest.raises(ValueError, match="overlap cannot be negative"):
        split_content("Security content", overlap_chars=-1)

    with pytest.raises(ValueError, match="overlap must be smaller"):
        split_content(
            "Security content",
            max_chars=100,
            overlap_chars=100,
        )


def test_build_document_chunks_adds_metadata_and_hashes() -> None:
    content = (
        "Access control prevents unauthorized actions. "
        "Authorization must be checked on every request. "
        "Failures should be logged for investigation."
    )
    document_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

    document = NormalizedDocument(
        source_id="example-source",
        title="Example Security Guide",
        publisher="Example Publisher",
        source_url="https://example.com/security",
        retrieved_at=datetime.now(UTC),
        content_hash=document_hash,
        content=content,
        topics=["application-security"],
        license=SourceLicense(
            name="Public Domain",
            url="https://creativecommons.org/publicdomain/mark/1.0/",
            attribution_required=False,
        ),
    )

    chunks = build_document_chunks(
        document,
        max_chars=80,
        overlap_chars=20,
    )

    assert len(chunks) > 1

    for index, chunk in enumerate(chunks):
        assert chunk.chunk_id == f"example-source::{index:04d}"
        assert chunk.chunk_index == index
        assert chunk.document_hash == document_hash
        assert chunk.content_hash == hashlib.sha256(chunk.content.encode("utf-8")).hexdigest()
        assert chunk.content == content[chunk.start_char : chunk.end_char]
        assert chunk.title == document.title
        assert chunk.publisher == document.publisher
        assert chunk.source_url == document.source_url
        assert chunk.topics == document.topics


def test_save_document_chunks_writes_json(
    tmp_path: Path,
) -> None:
    chunk = DocumentChunk(
        chunk_id="example-source::0000",
        source_id="example-source",
        chunk_index=0,
        content="Access control prevents unauthorized actions.",
        content_hash=hashlib.sha256(b"Access control prevents unauthorized actions.").hexdigest(),
        document_hash="b" * 64,
        start_char=0,
        end_char=45,
        title="Example Security Guide",
        publisher="Example Publisher",
        source_url="https://example.com/security",
        topics=["application-security"],
    )

    output_path = save_document_chunks(
        chunks=[chunk],
        output_directory=tmp_path,
    )

    saved_chunks = json.loads(output_path.read_text(encoding="utf-8"))

    assert output_path.name == "example-source.chunks.json"
    assert len(saved_chunks) == 1
    assert saved_chunks[0]["chunk_id"] == "example-source::0000"
    assert saved_chunks[0]["content"] == chunk.content
    assert saved_chunks[0]["document_hash"] == "b" * 64


def test_load_document_chunks_validates_saved_json(
    tmp_path: Path,
) -> None:
    chunk = DocumentChunk(
        chunk_id="example-source::0000",
        source_id="example-source",
        chunk_index=0,
        content="Access control prevents unauthorized actions.",
        content_hash=hashlib.sha256(b"Access control prevents unauthorized actions.").hexdigest(),
        document_hash="b" * 64,
        start_char=0,
        end_char=45,
        title="Example Security Guide",
        publisher="Example Publisher",
        source_url="https://example.com/security",
        topics=["application-security"],
    )

    output_path = save_document_chunks(
        chunks=[chunk],
        output_directory=tmp_path,
    )

    loaded_chunks = load_document_chunks(output_path)

    assert loaded_chunks == [chunk]
    assert isinstance(loaded_chunks[0], DocumentChunk)
