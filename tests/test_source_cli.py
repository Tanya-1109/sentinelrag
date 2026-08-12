from pathlib import Path

from sentinelrag.source_cli import validate_manifest


def test_validate_manifest_returns_summary() -> None:
    summary = validate_manifest(Path("data/sources.yaml"))

    assert summary == "Valid manifest: 4 sources, 3 enabled."
