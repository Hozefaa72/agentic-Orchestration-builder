from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Optional, Any
from beanie import Document
from enum import Enum


class Feedack(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NOTGIVEN = "not_given"


class Message(Document, BaseModel):
    content: Any
    timestamp: datetime = Field(default_factory=datetime.now(timezone.utc))
    sender: str
    thread_id: str
    feedback: Optional[Feedack] = Feedack.NOTGIVEN

    class Settings:
        collection = "messages"
