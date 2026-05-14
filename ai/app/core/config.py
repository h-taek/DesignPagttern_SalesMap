from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = Field(
        default="postgresql+psycopg://salesmap:salesmap@localhost:5432/salesmap",
        alias="DATABASE_URL",
    )
    internal_token: str = Field(default="dev-internal-token", alias="INTERNAL_TOKEN")
    predictor: str = Field(default="lr", alias="PREDICTOR")


settings = Settings()
