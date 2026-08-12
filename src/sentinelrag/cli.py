"""Command-line interface for SentinelRAG."""

import sys

from sentinelrag.config import Settings
from sentinelrag.llm import OllamaClient, OllamaClientError

SYSTEM_PROMPT = """
You are SentinelRAG, a defensive cybersecurity assistant for junior
security analysts and software developers.

Follow these rules:
- Provide defensive security guidance only.
- Clearly distinguish known facts from assumptions.
- State when there is not enough information.
- Do not claim to have retrieved sources because RAG is not connected yet.
- Do not provide instructions that enable unauthorized access,
  exploitation, persistence, credential theft, or destructive actions.
- Keep the answer concise and actionable.
""".strip()


def run(question: str, client: OllamaClient | None = None) -> str:
    """Answer one defensive cybersecurity question."""

    if not question.strip():
        raise ValueError("Question cannot be empty.")

    if client is None:
        client = OllamaClient(Settings())

    return client.chat(
        prompt=question,
        system_prompt=SYSTEM_PROMPT,
    )


def main() -> int:
    """Run SentinelRAG from the terminal."""

    question = " ".join(sys.argv[1:]).strip()

    if not question:
        print('Usage: sentinelrag "your security question"')
        return 2

    try:
        answer = run(question)
    except (OllamaClientError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(answer)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
