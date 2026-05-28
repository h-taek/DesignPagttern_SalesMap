from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# 실행 위치(CWD)와 무관하게 저장소 루트의 .env 를 찾도록 절대경로로 고정.
_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=_ENV_FILE, extra="ignore")

    database_url: str = Field(
        default="postgresql+psycopg://salesmap:salesmap@localhost:5432/salesmap",
        alias="DATABASE_URL",
    )
    internal_token: str = Field(default="dev-internal-token", alias="INTERNAL_TOKEN")
    predictor: str = Field(default="lr", alias="PREDICTOR")


settings = Settings()
