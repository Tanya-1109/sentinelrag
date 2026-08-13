"""Controlled downloading of approved web sources."""

import httpx

from sentinelrag.sources import SecuritySource


class SourceFetchError(RuntimeError):
    """Raised when an approved source cannot be downloaded."""


class SourceFetcher:
    """Download enabled web sources from their manifest URLs."""

    def __init__(
        self,
        transport: httpx.BaseTransport | None = None,
        timeout: float = 30.0,
    ) -> None:
        self._transport = transport
        self._timeout = timeout

    def fetch(self, source: SecuritySource) -> str:
        """Download HTML for one enabled web source."""

        if not source.enabled:
            raise ValueError(f"Source is disabled: {source.id}")

        if source.source_type != "web":
            raise ValueError(f"Source is not a web document: {source.id}")

        if source.url.scheme != "https":
            raise ValueError("Source URL must use HTTPS.")

        try:
            with httpx.Client(
                timeout=self._timeout,
                follow_redirects=True,
                transport=self._transport,
                headers={
                    "User-Agent": "SentinelRAG/0.1 educational-security-rag",
                    "Accept": "text/html",
                },
            ) as client:
                response = client.get(str(source.url))
                response.raise_for_status()
        except httpx.HTTPError as exc:
            raise SourceFetchError(f"Unable to fetch source: {source.id}") from exc

        content_type = response.headers.get("content-type", "").lower()

        if "text/html" not in content_type:
            raise SourceFetchError(
                f"Source returned unsupported content type: {content_type or 'unknown'}"
            )

        if not response.text.strip():
            raise SourceFetchError(f"Source returned empty content: {source.id}")

        return response.text
