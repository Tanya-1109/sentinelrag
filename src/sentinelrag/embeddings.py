"""Embedding clients used by SentinelRAG."""

import httpx

from sentinelrag.config import Settings


class OllamaEmbeddingError(RuntimeError):
    """Raised when Ollama cannot generate valid embeddings."""


class OllamaEmbeddingClient:
    """Small client for Ollama's local embedding API."""

    def __init__(
        self,
        settings: Settings,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._settings = settings
        self._transport = transport

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate one embedding vector for each input text."""

        if not texts:
            raise ValueError("At least one text is required.")

        if any(not text.strip() for text in texts):
            raise ValueError("Embedding text cannot be empty.")

        payload = {
            "model": self._settings.ollama_embedding_model,
            "input": [text.strip() for text in texts],
        }

        try:
            with httpx.Client(
                base_url=str(self._settings.ollama_base_url),
                timeout=120.0,
                transport=self._transport,
            ) as client:
                response = client.post("/api/embed", json=payload)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError as exc:
            raise OllamaEmbeddingError("Unable to communicate with Ollama.") from exc

        embeddings = data.get("embeddings")

        if not isinstance(embeddings, list):
            raise OllamaEmbeddingError("Ollama returned an invalid embedding response.")

        if len(embeddings) != len(texts):
            raise OllamaEmbeddingError("Ollama returned an unexpected number of embeddings.")

        dimensions = set()

        for vector in embeddings:
            if not isinstance(vector, list) or not vector:
                raise OllamaEmbeddingError("Ollama returned an invalid embedding vector.")

            if any(
                isinstance(value, bool) or not isinstance(value, (int, float)) for value in vector
            ):
                raise OllamaEmbeddingError("Ollama returned a non-numeric embedding.")

            dimensions.add(len(vector))

        if len(dimensions) != 1:
            raise OllamaEmbeddingError("Ollama returned inconsistent embedding dimensions.")

        return [[float(value) for value in vector] for vector in embeddings]
