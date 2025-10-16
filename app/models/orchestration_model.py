from beanie import Document
from pydantic import Field
from datetime import datetime, timezone
from typing import Optional
from enum import Enum


class Orchestration(Document):

    orchestrationName: str
    orchestrationDescription: Optional[str] = None
    orchestrationCreatedAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    orchestrationAgentsID: Optional[list[str]] = None
    adminids: Optional[list[str]] = Field(default_factory=list)
    stepids: Optional[list[str]] = Field(default_factory=list)
    agentids: Optional[list[str]] = Field(default_factory=list)
    kbids: Optional[list[str]] = Field(default_factory=list)
    no_of_steps: Optional[int] = 0
    isactive: Optional[bool] = False
    intialstep: Optional[str] = None
    finalstep: Optional[str] = None
    triggerevent: Optional[str] = None
    lastupdatedat: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "Orchestration"

    class Config:
        use_enum_values = True
