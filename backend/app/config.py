from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:postgres@postgres:5432/research"
    redis_url: str = "redis://redis:6379"
    ml_site_id: str = "MLM"

    class Config:
        env_file = ".env"


settings = Settings()
