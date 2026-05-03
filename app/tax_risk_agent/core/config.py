from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "local"
    database_url: Path = Path("data/tax_risk_demo.sqlite")
    report_dir: Path = Path("reports_output")
    llm_provider: str = "offline"
    llm_base_url: str = "http://127.0.0.1:8001/v1"
    llm_model: str = "Qwen2.5-14B-Instruct"
    llm_api_key: str = Field(default="local-key", repr=False)
    milvus_uri: str = "http://127.0.0.1:19530"
    milvus_collection: str = "tax_rules"
    max_tool_rounds: int = 8


@lru_cache
def get_settings() -> Settings:
    return Settings()

