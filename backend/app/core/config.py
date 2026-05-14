import logging
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# 실행 위치(CWD)와 무관하게 backend/.env 를 찾도록 절대경로로 고정.
_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=_ENV_FILE, extra="ignore")

    database_url: str = Field(
        default="postgresql+psycopg://salesmap:salesmap@localhost:5432/salesmap",
        alias="DATABASE_URL",
    )
    cors_origins: str = Field(default="http://localhost:5173", alias="CORS_ORIGINS")
    internal_token: str = Field(default="dev-internal-token", alias="INTERNAL_TOKEN")
    open_api_key: str = Field(default="", alias="OPEN_API_KEY")
    open_api_base: str = Field(
        default="http://openapi.seoul.go.kr:8088", alias="OPEN_API_BASE"
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()

# 서버 기동 시 키 로드 여부 확인 (마스킹 처리)
if settings.open_api_key:
    masked = settings.open_api_key[:4] + "****" if len(settings.open_api_key) > 4 else "****"
    logging.info(f"Loaded OPEN_API_KEY: {masked}")
else:
    logging.warning("OPEN_API_KEY is NOT loaded (empty or missing in .env)")
