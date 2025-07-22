from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    OPENAI_API_KEY: str
    FAQ_FILE_ID:str
    CENTER_FILE_ID:str
    NEED_FILE_ID:str
    

    class Config:
        env_file = ".env" 

settings = Settings()
