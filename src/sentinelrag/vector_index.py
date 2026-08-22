"""Validated vector records and semantic index utilities."""

import json
from pathlib import Path

import math

from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field, model_validator

from sentinelrag.chunks import DocumentChunk


class EmbeddingClient(Protocol):
    """Interface required from an embedding provider."""

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate one vector per input text."""


class VectorRecord(BaseModel):
    """One document chunk paired with its embedding vector."""

    model_config = ConfigDict(extra="forbid")

    chunk: DocumentChunk
    embedding_model: str = Field(min_length=1)
    embedding_dimensions: int = Field(gt=0)
    embedding: list[float] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_embedding(self) -> "VectorRecord":
        """Ensure vector dimensions and values are valid."""

        if len(self.embedding) != self.embedding_dimensions:
            raise ValueError("Embedding dimensions do not match the vector length.")

        if not all(math.isfinite(value) for value in self.embedding):
            raise ValueError("Embedding values must be finite numbers.")

        return self


def build_vector_records(
    chunks: list[DocumentChunk],
    embedding_client: EmbeddingClient,
    embedding_model: str,
    batch_size: int = 16,
) -> list[VectorRecord]:
    """Embed document chunks in batches and create validated records."""

    if not chunks:
        raise ValueError("At least one chunk is required.")

    if not embedding_model.strip():
        raise ValueError("Embedding model cannot be empty.")

    if batch_size <= 0:
        raise ValueError("Batch size must be positive.")

    records: list[VectorRecord] = []

    for batch_start in range(0, len(chunks), batch_size):
        batch = chunks[batch_start : batch_start + batch_size]
        vectors = embedding_client.embed([chunk.content for chunk in batch])

        if len(vectors) != len(batch):
            raise ValueError("Embedding count does not match the chunk count.")

        for chunk, vector in zip(batch, vectors, strict=True):
            records.append(
                VectorRecord(
                    chunk=chunk,
                    embedding_model=embedding_model.strip(),
                    embedding_dimensions=len(vector),
                    embedding=vector,
                )
            )

    return records


def save_vector_index(
    records: list[VectorRecord],
    output_path: Path,
) -> Path:
    """Save vector records with auditable index metadata."""

    if not records:
        raise ValueError("At least one vector record is required.")

    embedding_models = {record.embedding_model for record in records}
    embedding_dimensions = {record.embedding_dimensions for record in records}
    chunk_ids = [record.chunk.chunk_id for record in records]

    if len(embedding_models) != 1:
        raise ValueError("All vector records must use the same embedding model.")

    if len(embedding_dimensions) != 1:
        raise ValueError("All vector records must have the same dimensions.")

    if len(chunk_ids) != len(set(chunk_ids)):
        raise ValueError("Vector index cannot contain duplicate chunk IDs.")

    payload = {
        "schema_version": 1,
        "embedding_model": records[0].embedding_model,
        "embedding_dimensions": records[0].embedding_dimensions,
        "record_count": len(records),
        "records": [record.model_dump(mode="json") for record in records],
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )

    return output_path
