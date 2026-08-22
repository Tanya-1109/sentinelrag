"""Application configuration loaded from environment variables."""

from typing import Literal

from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Validated settings for SentinelRAG."""

    llm_provider: Literal["ollama"] = "ollama"
    ollama_base_url: AnyHttpUrl = "http://localhost:11434"
    ollama_model: str = "qwen2.5:1.5b"
    ollama_embedding_model: str = "nomic-embed-text"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
