from pydantic import BaseModel

class ThreadEditRequest(BaseModel):
    name: str
    thread_id: str

class ChangeLangRequest(BaseModel):
    thread_id: str
    language: str