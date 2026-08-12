import json

import httpx
import pytest

from sentinelrag.config import Settings
from sentinelrag.llm import OllamaClient, OllamaClientError


def test_ollama_client_returns_assistant_content() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content)

        assert request.url.path == "/api/chat"
        assert payload["model"] == "qwen2.5:1.5b"
        assert payload["stream"] is False
        assert payload["messages"][0]["content"] == "What is phishing?"

        return httpx.Response(
            200,
            json={
                "message": {
                    "role": "assistant",
                    "content": "Phishing is a social-engineering attack.",
                }
            },
        )

    settings = Settings(_env_file=None)
    transport = httpx.MockTransport(handler)
    client = OllamaClient(settings=settings, transport=transport)

    result = client.chat("What is phishing?")

    assert result == "Phishing is a social-engineering attack."


def test_ollama_client_rejects_empty_prompt() -> None:
    settings = Settings(_env_file=None)
    client = OllamaClient(settings=settings)

    with pytest.raises(ValueError, match="Prompt cannot be empty"):
        client.chat("   ")


def test_ollama_client_converts_http_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            503,
            json={"error": "model unavailable"},
        )

    settings = Settings(_env_file=None)
    transport = httpx.MockTransport(handler)
    client = OllamaClient(settings=settings, transport=transport)

    with pytest.raises(
        OllamaClientError,
        match="Unable to communicate with Ollama",
    ):
        client.chat("Explain phishing.")


def test_ollama_client_sends_system_prompt() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content)

        assert payload["messages"] == [
            {
                "role": "system",
                "content": "Answer only defensive security questions.",
            },
            {
                "role": "user",
                "content": "Explain credential stuffing.",
            },
        ]

        return httpx.Response(
            200,
            json={
                "message": {
                    "role": "assistant",
                    "content": "Credential stuffing reuses stolen credentials.",
                }
            },
        )

    settings = Settings(_env_file=None)
    transport = httpx.MockTransport(handler)
    client = OllamaClient(settings=settings, transport=transport)

    result = client.chat(
        "Explain credential stuffing.",
        system_prompt="Answer only defensive security questions.",
    )

    assert result == "Credential stuffing reuses stolen credentials."
