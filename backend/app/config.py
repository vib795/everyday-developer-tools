from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    log_directory: str = "logs/"
    redis_url: str | None = None
    spa_dist: str = str(Path(__file__).resolve().parents[2] / "frontend" / "dist")
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    app_name: str = "Developer Tools"
    rate_limit_default: str = "60/minute"
    rate_limit_regex_check: str = "15/minute"
    rate_limit_json_sample: str = "30/minute"


settings = Settings()
