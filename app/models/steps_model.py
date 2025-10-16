from beanie import Document
from pydantic import Field
from datetime import datetime, timezone
from typing import Optional, Any
from enum import Enum
from pydantic import BaseModel


class TimeOutAction(str, Enum):
    ROLLBACK = "roll_back"
    SKIP = "skip"
    NOTIFY = "notify"


class Customer(str, Enum):
    USER = "user"
    ADMIN = "admin"


class ConditionRule(BaseModel):
    approvedby: Optional[Customer] = None
    next_step: Optional[str] = None
    rollback_step: Optional[str] = None


class Steps(Document):
    StepName: str
    StepDescription: Optional[str] = None
    PreviousStep: Optional[str] = None
    NextStep: Optional[str] = None
    AgentID: Optional[str] = None
    canhumanintrupt: Optional[bool] = False
    expectedinput: list[str]
    expectedoutput: list[str]
    ispriorstep: Optional[bool] = False
    validconditions: Optional[list[str]] = None
    stepcreatedat: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    adminid: Optional[str] = None
    user_ids: Optional[list[str]] = Field(default_factory=list)
    isinitialstep: Optional[bool] = False
    isfinalstep: Optional[bool] = False
    canrollback_agent: Optional[bool] = False
    rollbackstep_agent: Optional[str] = None
    userapprovalrequired: Optional[bool] = False
    adminapprovalrequired: Optional[bool] = False
    conditionmap: Optional[ConditionRule] = None
    approvaltimeoutdays: Optional[int] = 7
    timeoutaction: Optional[TimeOutAction] = TimeOutAction.ROLLBACK

    class Settings:
        name = "Steps"

    class Config:
        use_enum_values = True
