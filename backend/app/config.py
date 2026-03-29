from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_title: str = "재단 규정 상담봇"
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-4o-mini"
    embedding_model: str = "nlpai-lab/KoE5"
    reranker_model: str = "BAAI/bge-reranker-v2-m3"
    law_oc: str = "dhl"
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_timeout: int = 120
    collection_name: str = "foundation_docs"
    chunk_size: int = 800
    chunk_overlap: int = 200
    top_k: int = 5
    rerank_candidates: int = 12
    upload_dir: Path = Path("/app/uploads")
    data_dir: Path = Path("/app/data")
    allowed_origins: list[str] = Field(default_factory=lambda: ["*"])

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def split_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    def ensure_storage(self) -> None:
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        (self.data_dir / "law_md").mkdir(parents=True, exist_ok=True)
        (self.data_dir / "feedback").mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_storage()
    return settings
