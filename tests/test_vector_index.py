import pytest
import json
from pathlib import Path
from pydantic import ValidationError

from sentinelrag.chunks import DocumentChunk
from sentinelrag.vector_index import (
    VectorRecord,
    build_vector_records,
    save_vector_index,
)


def create_test_chunk() -> DocumentChunk:
    return DocumentChunk(
        chunk_id="example-source::0000",
        source_id="example-source",
        chunk_index=0,
        content="Access control prevents unauthorized actions.",
        content_hash="a" * 64,
        document_hash="b" * 64,
        start_char=0,
        end_char=45,
        title="Example Security Guide",
        publisher="Example Publisher",
        source_url="https://example.com/security",
        topics=["application-security"],
    )


def test_vector_record_preserves_chunk_and_embedding_metadata() -> None:
    record = VectorRecord(
        chunk=create_test_chunk(),
        embedding_model="nomic-embed-text",
        embedding_dimensions=3,
        embedding=[0.1, 0.2, 0.3],
    )

    assert record.chunk.chunk_id == "example-source::0000"
    assert record.embedding_model == "nomic-embed-text"
    assert record.embedding_dimensions == 3
    assert record.embedding == [0.1, 0.2, 0.3]


def test_vector_record_rejects_dimension_mismatch() -> None:
    with pytest.raises(
        ValidationError,
        match="Embedding dimensions do not match",
    ):
        VectorRecord(
            chunk=create_test_chunk(),
            embedding_model="nomic-embed-text",
            embedding_dimensions=3,
            embedding=[0.1, 0.2],
        )


class FakeEmbeddingClient:
    """Predictable embedding client used only by tests."""

    def __init__(self) -> None:
        self.received_texts: list[str] = []

    def embed(self, texts: list[str]) -> list[list[float]]:
        self.received_texts = texts

        return [[float(index), 0.5, 0.25] for index, _ in enumerate(texts)]


def test_build_vector_records_embeds_chunk_content() -> None:
    first_chunk = create_test_chunk()
    second_chunk = first_chunk.model_copy(
        update={
            "chunk_id": "example-source::0001",
            "chunk_index": 1,
            "content": "Authorization should be checked on every request.",
            "content_hash": "c" * 64,
            "start_char": 30,
            "end_char": 83,
        }
    )
    client = FakeEmbeddingClient()

    records = build_vector_records(
        chunks=[first_chunk, second_chunk],
        embedding_client=client,
        embedding_model="nomic-embed-text",
    )

    assert client.received_texts == [
        first_chunk.content,
        second_chunk.content,
    ]
    assert len(records) == 2
    assert records[0].chunk.chunk_id == "example-source::0000"
    assert records[1].chunk.chunk_id == "example-source::0001"
    assert records[0].embedding_dimensions == 3
    assert records[1].embedding == [1.0, 0.5, 0.25]


def test_save_vector_index_writes_records_and_metadata(
    tmp_path: Path,
) -> None:
    record = VectorRecord(
        chunk=create_test_chunk(),
        embedding_model="nomic-embed-text",
        embedding_dimensions=3,
        embedding=[0.1, 0.2, 0.3],
    )
    output_path = tmp_path / "security-index.json"

    saved_path = save_vector_index(
        records=[record],
        output_path=output_path,
    )

    saved_index = json.loads(saved_path.read_text(encoding="utf-8"))

    assert saved_path == output_path
    assert saved_index["schema_version"] == 1
    assert saved_index["embedding_model"] == "nomic-embed-text"
    assert saved_index["embedding_dimensions"] == 3
    assert saved_index["record_count"] == 1
    assert saved_index["records"][0]["chunk"]["chunk_id"] == ("example-source::0000")
    assert saved_index["records"][0]["embedding"] == [0.1, 0.2, 0.3]
