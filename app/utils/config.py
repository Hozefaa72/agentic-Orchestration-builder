from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SECRET_KEY: str
    OPENAI_API_KEY: str
    GUEST_TOKEN_EXPIRY_SECONDS: int
    GUEST_TOKEN_EXPIRY_DAYS: int
    DATABASE_URL: str
    PORT: int
    UPLOAD_DIR: str = "app/datasets"
    CHROMA_DB_KEY: str
    CHROMA_DB_TENANT: str
    GEMINI_API_KEY:str
    SUPERADMIN_EMAILID:str
    MAIL_PASSWORD:str
    MAIL_PORT:int
    EMAIL_SECRET_KEY:str
    model_config = SettingsConfigDict(env_file=".env", extra="allow")


ENV_PROJECT = Settings()
