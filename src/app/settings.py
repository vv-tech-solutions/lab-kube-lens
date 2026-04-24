from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ollama_url: str = Field("http://localhost:11434/api", env="OLLAMA_URL")
    qdrant_host: str = Field("localhost", alias="QDRANT_HOST")
    qdrant_port: int = Field(6333, alias="QDRANT_PORT")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

settings = Settings()