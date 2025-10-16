from beanie import Document
from pydantic import Field
from datetime import datetime, timezone
from typing import Optional
from enum import Enum
from app.models.llmmodels_models import llmcompany


class Agents(Document):

    agentName: str
    agentPrompt: str
    agentLLMModelcompany: llmcompany
    agentLLMModelname: str
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    agentKBID: Optional[list[str]] = None

    class Settings:
        name = "Agents"

    class Config:
        use_enum_values = True
