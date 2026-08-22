import json

import httpx

from sentinelrag.config import Settings
import pytest

from sentinelrag.embeddings import (
    OllamaEmbeddingClient,
    OllamaEmbeddingError,
)


def test_ollama_embedding_client_returns_vectors() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content)

        assert request.url.path == "/api/embed"
        assert payload["model"] == "nomic-embed-text"
        assert payload["input"] == [
            "Broken access control allows unauthorized actions.",
            "Log authorization failures for investigation.",
        ]

        return httpx.Response(
            200,
            json={
                "embeddings": [
                    [0.1, 0.2, 0.3],
                    [0.4, 0.5, 0.6],
                ]
            },
        )

    settings = Settings(_env_file=None)
    transport = httpx.MockTransport(handler)
    client = OllamaEmbeddingClient(
        settings=settings,
        transport=transport,
    )

    vectors = client.embed(
        [
            "Broken access control allows unauthorized actions.",
            "Log authorization failures for investigation.",
        ]
    )

    assert vectors == [
        [0.1, 0.2, 0.3],
        [0.4, 0.5, 0.6],
    ]


def test_embedding_client_rejects_empty_input() -> None:
    settings = Settings(_env_file=None)
    client = OllamaEmbeddingClient(settings=settings)

    with pytest.raises(ValueError, match="At least one text is required"):
        client.embed([])

    with pytest.raises(ValueError, match="Embedding text cannot be empty"):
        client.embed(["   "])


def test_embedding_client_converts_http_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            503,
            json={"error": "embedding model unavailable"},
        )

    settings = Settings(_env_file=None)
    client = OllamaEmbeddingClient(
        settings=settings,
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(
        OllamaEmbeddingError,
        match="Unable to communicate with Ollama",
    ):
        client.embed(["Explain access control."])


def test_embedding_client_rejects_wrong_vector_count() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "embeddings": [
                    [0.1, 0.2, 0.3],
                ]
            },
        )

    settings = Settings(_env_file=None)
    client = OllamaEmbeddingClient(
        settings=settings,
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(
        OllamaEmbeddingError,
        match="unexpected number of embeddings",
    ):
        client.embed(
            [
                "First security text.",
                "Second security text.",
            ]
        )
