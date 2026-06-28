from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql://postgres:postgres@postgres:5432/research"
    redis_url: str = "redis://redis:6379"
    ml_site_id: str = "MLM"


settings = Settings()
