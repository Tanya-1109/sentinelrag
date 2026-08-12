from pathlib import Path

import pytest
from pydantic import ValidationError

from sentinelrag.sources import SourceManifest, load_source_manifest


def make_source(source_id: str = "example-source") -> dict:
    """Create valid source data for focused validation tests."""

    return {
        "id": source_id,
        "title": "Example Security Source",
        "publisher": "Example Publisher",
        "source_type": "web",
        "url": "https://example.com/security",
        "topics": ["security"],
        "license": {
            "name": "Example License",
            "url": "https://example.com/license",
            "attribution_required": True,
        },
        "trust_tier": 1,
        "enabled": True,
        "notes": "",
    }


def test_load_source_manifest() -> None:
    manifest = load_source_manifest(Path("data/sources.yaml"))

    assert manifest.schema_version == 1
    assert len(manifest.sources) == 4
    assert len([source for source in manifest.sources if source.enabled]) == 3
    assert manifest.sources[0].id == "owasp-top-10-2021"


def test_manifest_rejects_duplicate_source_ids() -> None:
    source = make_source()

    with pytest.raises(
        ValidationError,
        match="Source IDs must be unique",
    ):
        SourceManifest.model_validate(
            {
                "schema_version": 1,
                "sources": [source, source.copy()],
            }
        )


def test_manifest_rejects_unexpected_fields() -> None:
    source = make_source()
    source["publsher"] = source.pop("publisher")

    with pytest.raises(ValidationError, match="publisher"):
        SourceManifest.model_validate(
            {
                "schema_version": 1,
                "sources": [source],
            }
        )
