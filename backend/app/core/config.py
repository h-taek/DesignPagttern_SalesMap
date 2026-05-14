from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

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
