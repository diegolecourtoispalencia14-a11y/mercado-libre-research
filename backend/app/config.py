from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql://postgres:postgres@postgres:5432/research"
    redis_url: str = "redis://redis:6379"
    ml_site_id: str = "MLM"
    ml_access_token: str = ""
    ml_refresh_token: str = ""
    ml_client_id: str = ""
    ml_client_secret: str = ""

    # Security & Auth Settings
    auth_enabled: bool = True
    secret_key: str = "e98c9fc1-flamante-lab-secret-key-riviera-maya-2026-auth"
    admin_username: str = "admin"
    admin_password: str = "Admin!Riviera2026"
    admin_email: str = "admin@flamante.lab"
    token_expire_hours: int = 8
    max_login_attempts: int = 5
    lockout_duration_seconds: int = 60
    rate_limit_per_minute: int = 60


settings = Settings()
