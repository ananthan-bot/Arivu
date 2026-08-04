"""
Application configuration.

Loaded once at startup from environment variables (see .env.example).
Using pydantic-settings so config is validated at boot, not discovered
via a KeyError three requests into production.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    app_name: str = "Arivu"
    environment: str = "development"

    # Database
    database_url: str = "postgresql://arivu:arivu@localhost:5432/arivu"

    # Auth
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Embeddings
    embedding_model_name: str = "BAAI/bge-small-en-v1.5"
    embedding_dim: int = 384

    # LLM
    anthropic_api_key: str = ""
    llm_model: str = "claude-sonnet-4-6"

    # Retrieval
    top_k_candidates: int = 50
    top_k_final: int = 5
    hallucination_confidence_threshold: float = 0.35

    # Chunking
    chunk_size_tokens: int = 400
    chunk_overlap_tokens: int = 60


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance, so we parse env vars once per process."""
    return Settings()
