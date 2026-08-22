import hashlib
import json
from pathlib import Path

import sys

from sentinelrag import index_cli
from sentinelrag.chunks import DocumentChunk, save_document_chunks
from sentinelrag.index_cli import build_index_file


class FakeEmbeddingClient:
    """Deterministic embedding provider for the index workflow test."""

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [[float(index), 0.5, 0.25] for index, _ in enumerate(texts)]


def test_build_index_file_embeds_persisted_chunks(
    tmp_path: Path,
) -> None:
    content = "Access control prevents unauthorized actions."
    chunk = DocumentChunk(
        chunk_id="example-source::0000",
        source_id="example-source",
        chunk_index=0,
        content=content,
        content_hash=hashlib.sha256(content.encode("utf-8")).hexdigest(),
        document_hash="b" * 64,
        start_char=0,
        end_char=len(content),
        title="Example Security Guide",
        publisher="Example Publisher",
        source_url="https://example.com/security",
        topics=["application-security"],
    )

    chunk_path = save_document_chunks(
        chunks=[chunk],
        output_directory=tmp_path / "chunks",
    )
    index_path = tmp_path / "index" / "security-index.json"

    saved_path = build_index_file(
        chunk_path=chunk_path,
        output_path=index_path,
        embedding_client=FakeEmbeddingClient(),
        embedding_model="nomic-embed-text",
        batch_size=16,
    )

    saved_index = json.loads(saved_path.read_text(encoding="utf-8"))

    assert saved_path == index_path
    assert saved_index["record_count"] == 1
    assert saved_index["embedding_model"] == "nomic-embed-text"
    assert saved_index["embedding_dimensions"] == 3
    assert saved_index["records"][0]["chunk"]["chunk_id"] == ("example-source::0000")


def test_main_parses_index_arguments(
    monkeypatch,
    tmp_path: Path,
    capsys,
) -> None:
    chunk_path = tmp_path / "chunks.json"
    output_path = tmp_path / "security-index.json"
    fake_client = object()
    received: dict[str, object] = {}

    class FakeSettings:
        ollama_embedding_model = "nomic-embed-text"

    def fake_build_index_file(
        chunk_path: Path,
        output_path: Path,
        embedding_client: object,
        embedding_model: str,
        batch_size: int,
    ) -> Path:
        received["chunk_path"] = chunk_path
        received["output_path"] = output_path
        received["embedding_client"] = embedding_client
        received["embedding_model"] = embedding_model
        received["batch_size"] = batch_size
        return output_path

    monkeypatch.setattr(
        index_cli,
        "Settings",
        lambda: FakeSettings(),
        raising=False,
    )
    monkeypatch.setattr(
        index_cli,
        "OllamaEmbeddingClient",
        lambda settings: fake_client,
        raising=False,
    )
    monkeypatch.setattr(
        index_cli,
        "build_index_file",
        fake_build_index_file,
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "sentinelrag-index",
            str(chunk_path),
            "--output",
            str(output_path),
            "--batch-size",
            "8",
        ],
    )

    exit_code = index_cli.main()

    assert exit_code == 0
    assert received == {
        "chunk_path": chunk_path,
        "output_path": output_path,
        "embedding_client": fake_client,
        "embedding_model": "nomic-embed-text",
        "batch_size": 8,
    }
    assert f"Saved vector index: {output_path}" in capsys.readouterr().out
