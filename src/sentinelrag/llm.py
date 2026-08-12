"""LLM clients used by SentinelRAG."""

import httpx

from sentinelrag.config import Settings


class OllamaClientError(RuntimeError):
    """Raised when communication with Ollama fails."""


class OllamaClient:
    """Small client for Ollama's local chat API."""

    def __init__(
        self,
        settings: Settings,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._settings = settings
        self._transport = transport

    def chat(self, prompt: str, system_prompt: str | None = None) -> str:
        """Send one user prompt and return the assistant's response."""

        if not prompt.strip():
            raise ValueError("Prompt cannot be empty.")
        messages = []

        if system_prompt and system_prompt.strip():
            messages.append(
                {
                    "role": "system",
                    "content": system_prompt.strip(),
                }
            )

        messages.append(
            {
                "role": "user",
                "content": prompt.strip(),
            }
        )

        payload = {
            "model": self._settings.ollama_model,
            "messages": messages,
            "stream": False,
        }

        try:
            with httpx.Client(
                base_url=str(self._settings.ollama_base_url),
                timeout=60.0,
                transport=self._transport,
            ) as client:
                response = client.post("/api/chat", json=payload)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError as exc:
            raise OllamaClientError("Unable to communicate with Ollama.") from exc

        try:
            content = data["message"]["content"]
        except (KeyError, TypeError) as exc:
            raise OllamaClientError("Ollama returned an invalid response.") from exc

        if not isinstance(content, str) or not content.strip():
            raise OllamaClientError("Ollama returned an empty response.")

        return content.strip()
