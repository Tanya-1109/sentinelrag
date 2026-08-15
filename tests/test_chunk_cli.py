import json
from datetime import UTC, datetime
from pathlib import Path
import sys

from sentinelrag import chunk_cli

from sentinelrag.chunk_cli import chunk_document_file
from sentinelrag.documents import NormalizedDocument
from sentinelrag.sources import SourceLicense


def test_chunk_document_file_creates_chunk_json(
    tmp_path: Path,
) -> None:
    content = (
        "Access control prevents unauthorized actions. "
        "Authorization must be checked on every request. "
        "Security failures should be logged for investigation."
    )

    document = NormalizedDocument(
        source_id="example-source",
        title="Example Security Guide",
        publisher="Example Publisher",
        source_url="https://example.com/security",
        retrieved_at=datetime.now(UTC),
        content_hash="a" * 64,
        content=content,
        topics=["application-security"],
        license=SourceLicense(
            name="Public Domain",
            url="https://creativecommons.org/publicdomain/mark/1.0/",
            attribution_required=False,
        ),
    )

    input_path = tmp_path / "example-source.json"
    output_directory = tmp_path / "chunks"

    input_path.write_text(
        document.model_dump_json(indent=2),
        encoding="utf-8",
    )

    output_path = chunk_document_file(
        input_path=input_path,
        output_directory=output_directory,
        max_chars=80,
        overlap_chars=20,
    )

    saved_chunks = json.loads(output_path.read_text(encoding="utf-8"))

    assert output_path.name == "example-source.chunks.json"
    assert len(saved_chunks) > 1
    assert saved_chunks[0]["chunk_id"] == "example-source::0000"
    assert saved_chunks[0]["source_id"] == "example-source"


def test_main_parses_chunking_arguments(
    monkeypatch,
    tmp_path: Path,
    capsys,
) -> None:
    input_path = tmp_path / "document.json"
    output_directory = tmp_path / "chunks"
    expected_output = output_directory / "example-source.chunks.json"
    received: dict[str, object] = {}

    def fake_chunk_document_file(
        input_path: Path,
        output_directory: Path,
        max_chars: int,
        overlap_chars: int,
    ) -> Path:
        received["input_path"] = input_path
        received["output_directory"] = output_directory
        received["max_chars"] = max_chars
        received["overlap_chars"] = overlap_chars
        return expected_output

    monkeypatch.setattr(
        chunk_cli,
        "chunk_document_file",
        fake_chunk_document_file,
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "sentinelrag-chunk",
            str(input_path),
            "--output",
            str(output_directory),
            "--max-chars",
            "800",
            "--overlap-chars",
            "100",
        ],
    )

    exit_code = chunk_cli.main()

    assert exit_code == 0
    assert received == {
        "input_path": input_path,
        "output_directory": output_directory,
        "max_chars": 800,
        "overlap_chars": 100,
    }
    assert f"Saved document chunks: {expected_output}" in capsys.readouterr().out
