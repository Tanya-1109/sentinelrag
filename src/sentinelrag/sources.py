"""Validation and loading for trusted security sources."""

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator


class SourceLicense(BaseModel):
    """Licensing information for a source."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    url: HttpUrl
    attribution_required: bool


class SecuritySource(BaseModel):
    """One trusted cybersecurity source."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    title: str = Field(min_length=1)
    publisher: str = Field(min_length=1)
    source_type: Literal["web", "pdf", "collection"]
    url: HttpUrl
    topics: list[str] = Field(min_length=1)
    license: SourceLicense
    trust_tier: int = Field(ge=1, le=3)
    enabled: bool
    notes: str = ""


class SourceManifest(BaseModel):
    """Versioned collection of security sources."""

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal[1]
    sources: list[SecuritySource] = Field(min_length=1)

    @model_validator(mode="after")
    def source_ids_must_be_unique(self) -> "SourceManifest":
        """Reject manifests containing duplicate source identifiers."""

        source_ids = [source.id for source in self.sources]

        if len(source_ids) != len(set(source_ids)):
            raise ValueError("Source IDs must be unique.")

        return self


def load_source_manifest(path: Path) -> SourceManifest:
    """Load and validate a YAML source manifest."""

    with path.open(encoding="utf-8") as manifest_file:
        raw_manifest = yaml.safe_load(manifest_file)

    return SourceManifest.model_validate(raw_manifest)
