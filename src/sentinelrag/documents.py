"""Normalized documents produced by the ingestion pipeline."""

import hashlib
import re
from datetime import UTC, datetime

from bs4 import BeautifulSoup
from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from sentinelrag.sources import SecuritySource, SourceLicense


class NormalizedDocument(BaseModel):
    """Clean document with enough provenance for citation and auditing."""

    model_config = ConfigDict(extra="forbid")

    source_id: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    title: str = Field(min_length=1)
    publisher: str = Field(min_length=1)
    source_url: HttpUrl
    retrieved_at: datetime
    content_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    content: str = Field(min_length=1)
    topics: list[str] = Field(min_length=1)
    license: SourceLicense


REMOVABLE_ELEMENTS = (
    "script",
    "style",
    "noscript",
    "nav",
    "header",
    "footer",
    "aside",
)


def normalize_html(html: str) -> str:
    """Extract readable main content from an HTML document."""

    soup = BeautifulSoup(html, "html.parser")

    for element in soup.select(",".join(REMOVABLE_ELEMENTS)):
        element.decompose()

    content_root = soup.find("main") or soup.find("article") or soup.body

    if content_root is None:
        raise ValueError("HTML document has no readable content.")

    text = content_root.get_text(separator="\n", strip=True)
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
    clean_lines = [line for line in lines if line]

    if not clean_lines:
        raise ValueError("HTML document has no readable content.")

    return "\n".join(clean_lines)


def build_normalized_document(
    source: SecuritySource,
    html: str,
    retrieved_at: datetime | None = None,
) -> NormalizedDocument:
    """Normalize HTML and combine it with source provenance."""

    if source.source_type != "web":
        raise ValueError("Only web sources are supported by the HTML parser.")

    content = normalize_html(html)
    content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

    return NormalizedDocument(
        source_id=source.id,
        title=source.title,
        publisher=source.publisher,
        source_url=source.url,
        retrieved_at=retrieved_at or datetime.now(UTC),
        content_hash=content_hash,
        content=content,
        topics=source.topics,
        license=source.license,
    )
