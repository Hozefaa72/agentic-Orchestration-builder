from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str ="mongodb+srv://developer:developer@cluster0.iexuetn.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    SECRET_KEY: str
    OPENAI_API_KEY: str
    FAQ_FILE_ID:str
    CENTER_FILE_ID:str
    NEED_FILE_ID:str
    GUEST_TOKEN_EXPIRY_SECONDS:int
    GUEST_TOKEN_EXPIRY_DAYS:int
    

    class Config:
        env_file = ".env" 

settings = Settings()
