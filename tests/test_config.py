from sentinelrag.config import Settings


def test_settings_load_from_environment(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://localhost:11434")
    monkeypatch.setenv("OLLAMA_MODEL", "qwen2.5:1.5b")

    settings = Settings(_env_file=None)

    assert settings.llm_provider == "ollama"
    assert str(settings.ollama_base_url) == "http://localhost:11434/"
    assert settings.ollama_model == "qwen2.5:1.5b"
