"""Models and utilities for retrievable document chunks."""

import hashlib
import json
from pathlib import Path

from sentinelrag.documents import NormalizedDocument

from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator


@dataclass(frozen=True)
class ChunkSpan:
    """A character range selected from normalized document content."""

    start_char: int
    end_char: int
    content: str


class DocumentChunk(BaseModel):
    """A retrievable section with document provenance."""

    model_config = ConfigDict(extra="forbid")

    chunk_id: str = Field(pattern=r"^[a-z0-9-]+::[0-9]{4}$")
    source_id: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    chunk_index: int = Field(ge=0)
    content: str = Field(min_length=1)
    content_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    document_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    start_char: int = Field(ge=0)
    end_char: int = Field(gt=0)
    title: str = Field(min_length=1)
    publisher: str = Field(min_length=1)
    source_url: HttpUrl
    topics: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def end_must_follow_start(self) -> "DocumentChunk":
        """Ensure character offsets describe a valid range."""

        if self.end_char <= self.start_char:
            raise ValueError("Chunk end must be greater than its start.")

        return self


def split_content(
    content: str,
    max_chars: int = 1_000,
    overlap_chars: int = 150,
) -> list[ChunkSpan]:
    if max_chars <= 0:
        raise ValueError("Maximum chunk size must be positive.")
    if overlap_chars < 0:
        raise ValueError("Chunk overlap cannot be negative.")

    if overlap_chars >= max_chars:
        raise ValueError("Chunk overlap must be smaller than chunk size.")

    if not content.strip():
        raise ValueError("Content cannot be empty.")

    spans: list[ChunkSpan] = []
    cursor = 0

    while cursor < len(content):
        proposed_end = min(cursor + max_chars, len(content))
        end = proposed_end

        if proposed_end < len(content):
            minimum_boundary = cursor + (max_chars // 2)
            newline = content.rfind("\n", minimum_boundary, proposed_end)
            space = content.rfind(" ", minimum_boundary, proposed_end)
            boundary = max(newline, space)

            if boundary > cursor:
                end = boundary

        raw_segment = content[cursor:end]
        segment = raw_segment.strip()

        if segment:
            leading_whitespace = len(raw_segment) - len(raw_segment.lstrip())
            start_char = cursor + leading_whitespace
            end_char = start_char + len(segment)

            spans.append(
                ChunkSpan(
                    start_char=start_char,
                    end_char=end_char,
                    content=segment,
                )
            )

        if end == len(content):
            break

        next_cursor = end - overlap_chars

        # Move forward to the beginning of a word rather than starting midway
        # through a word contained in the overlapping region.
        while next_cursor < end and next_cursor > 0 and not content[next_cursor - 1].isspace():
            next_cursor += 1

        while next_cursor < len(content) and content[next_cursor].isspace():
            next_cursor += 1

        # Defensive guarantee that every iteration advances.
        if next_cursor <= cursor:
            next_cursor = end

        cursor = next_cursor

    return spans


def build_document_chunks(
    document: NormalizedDocument,
    max_chars: int = 1_000,
    overlap_chars: int = 150,
) -> list[DocumentChunk]:
    """Split a normalized document into validated retrievable chunks."""

    spans = split_content(
        document.content,
        max_chars=max_chars,
        overlap_chars=overlap_chars,
    )

    chunks: list[DocumentChunk] = []

    for index, span in enumerate(spans):
        chunk_hash = hashlib.sha256(span.content.encode("utf-8")).hexdigest()

        chunks.append(
            DocumentChunk(
                chunk_id=f"{document.source_id}::{index:04d}",
                source_id=document.source_id,
                chunk_index=index,
                content=span.content,
                content_hash=chunk_hash,
                document_hash=document.content_hash,
                start_char=span.start_char,
                end_char=span.end_char,
                title=document.title,
                publisher=document.publisher,
                source_url=document.source_url,
                topics=document.topics,
            )
        )

    return chunks


def save_document_chunks(
    chunks: list[DocumentChunk],
    output_directory: Path,
) -> Path:
    """Save one document's chunks as readable JSON."""

    if not chunks:
        raise ValueError("At least one chunk is required.")

    source_ids = {chunk.source_id for chunk in chunks}

    if len(source_ids) != 1:
        raise ValueError("All chunks must belong to the same source.")

    source_id = chunks[0].source_id
    output_directory.mkdir(parents=True, exist_ok=True)
    output_path = output_directory / f"{source_id}.chunks.json"

    serialized_chunks = [chunk.model_dump(mode="json") for chunk in chunks]

    output_path.write_text(
        json.dumps(serialized_chunks, indent=2),
        encoding="utf-8",
    )

    return output_path
