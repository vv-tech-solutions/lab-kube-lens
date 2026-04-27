"""Application configuration.

This module uses :class:`pydantic_settings.BaseSettings` to load environment
variables from ``.env`` (or the system environment).  The resulting ``settings``
object is imported by other modules.

Available settings:
- ``ollama_url`` – base URL for the Ollama API.
- ``qdrant_host`` – host for the Qdrant vector database.
- ``qdrant_port`` – port for Qdrant.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed settings container for the application."""

    # Base URL for Ollama (default to local dev instance)
    ollama_url: str = Field("http://localhost:11434/api", env="OLLAMA_URL")

    # Qdrant connection details
    qdrant_host: str = Field("localhost", alias="QDRANT_HOST")
    qdrant_port: int = Field(6333, alias="QDRANT_PORT")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

# Instantiate the settings for use throughout the project
settings = Settings()
