from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SECRET_KEY: str
    OPENAI_API_KEY: str

    FAQ_FILE_ID: str
    CENTER_FILE_ID: str
    NEED_FILE_ID: str

    GUEST_TOKEN_EXPIRY_SECONDS: int
    GUEST_TOKEN_EXPIRY_DAYS: int

    DATABASE_URL: str
    PORT: int

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


ENV_PROJECT = Settings()
