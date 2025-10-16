from beanie import Document
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from typing import Optional
from app.models.orchestration_instace import StepsStatus


class Thread(Document):
    thread_created_at: datetime = Field(default_factory=datetime.now(timezone.utc))
    thread_name: Optional[str] = None
    instanceid: str
    language: Optional[str] = None
    previousstepid: Optional[str] = None
    currentstepid: Optional[str] = None
    status: Optional[StepsStatus] = StepsStatus.NOTSTARTED

    class Settings:
        name = "threads"
