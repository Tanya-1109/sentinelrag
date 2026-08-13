import pytest

from sentinelrag.ingest_cli import find_source


def test_find_source_returns_manifest_source() -> None:
    source = find_source("owasp-top-10-2021")

    assert source.publisher == "OWASP Foundation"
    assert source.enabled is True


def test_find_source_rejects_unknown_id() -> None:
    with pytest.raises(ValueError, match="Unknown source ID"):
        find_source("unknown-source")
