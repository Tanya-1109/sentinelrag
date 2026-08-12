from sentinelrag.cli import SYSTEM_PROMPT, run


class FakeClient:
    def chat(self, prompt: str, system_prompt: str | None = None) -> str:
        assert prompt == "What is phishing?"
        assert system_prompt == SYSTEM_PROMPT
        return "Phishing is a social-engineering attack."


def test_run_returns_client_answer() -> None:
    result = run("What is phishing?", client=FakeClient())

    assert result == "Phishing is a social-engineering attack."
