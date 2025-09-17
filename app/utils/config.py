from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SECRET_KEY: str
    OPENAI_API_KEY: str

    GUEST_TOKEN_EXPIRY_SECONDS: int
    GUEST_TOKEN_EXPIRY_DAYS: int

    DATABASE_URL: str
    PORT: int
    
    USE_SSH_TUNNEL: bool
    SSH_USER: str
    SSH_HOST: str
    SSH_PORT: str
    SSH_KEY_PATH: str
    MONGO_CA_FILE: str
    MONGO_SECRET_NAME: str
    MONGO_DB_NAME: str
    MONGO_PORT: int
    MONGO_HOST: str
    AWS_ACCESS_KEY_ID:str
    AWS_SECRET_ACCESS_KEY:str
    AWS_REGION: str
    REPO_NAME: str

    # New fields for TLS
    MONGO_TLS_CA_FILE: str  # Path to the CA certificate file
    MONGO_TLS_CERT_FILE: str  # Path to the client certificate file (optional)
    MONGO_TLS_ALLOW_INVALID_HOSTNAMES: bool = True 

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


ENV_PROJECT = Settings()
