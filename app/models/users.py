from beanie import Document
from pydantic import EmailStr, Field
from datetime import datetime, timezone
from typing import Optional


class User(Document):
    name: str
    email: EmailStr
    password_hash: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    role_id: str
    orchestration_id: Optional[list[str]] = Field(default_factory=list)
    agent_id: Optional[list[str]] = Field(default_factory=list)
    knowledgebase_id: Optional[list[str]] = Field(default_factory=list)
    step_id: Optional[list[str]] = Field(default_factory=list)
    secretkey: Optional[str] = None

    class Settings:
        name = "users"
