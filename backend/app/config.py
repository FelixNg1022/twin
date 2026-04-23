from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    anthropic_api_key: str
    anthropic_turn_model: str = "claude-haiku-4-5-20251001"
    anthropic_synthesis_model: str = "claude-opus-4-7"
    database_url: str = "sqlite:///./twin.db"
    cors_origins: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
