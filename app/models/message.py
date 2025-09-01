from pydantic import BaseModel, Field
from datetime import datetime,timezone
from typing import List, Optional, Union
from beanie import Document


class Message(Document, BaseModel):
    content: Union[str, List[str]]
    role: str
    timestamp: datetime = Field(default_factory=datetime.now(timezone.utc))
    feedback: Optional[int] = -1
    sender: str
    thread_id: str

    class Settings:
        collection = "messages"
