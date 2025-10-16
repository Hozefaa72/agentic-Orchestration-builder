from beanie import Document
from pydantic import Field
from datetime import datetime, timezone
from typing import Optional, Any
from enum import Enum


class StepsStatus(str, Enum):
    NOTSTARTED = "not_started"
    PENDING = "pending"
    INPROGRESS = "inprogress"
    COMPLETED = "completed"
    FAILED = "failed"


class OrchestrationInstance(Document):
    orchestration_id: str
    user_id: str
    previousstep: Optional[str] = None
    currentstep: Optional[str] = None
    triggerevent: Optional[str] = None
    lastupdatedat: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    isactivestep: Optional[bool] = False
    stepinput: Optional[Any] = None
    stepoutput: Optional[Any] = None
    approvalsentat: Optional[datetime] = None
    status: Optional[StepsStatus] = StepsStatus.NOTSTARTED

    class Settings:
        name = "OrchestrationInstance"

    class Config:
        use_enum_values = True
