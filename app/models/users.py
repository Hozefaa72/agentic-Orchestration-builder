from beanie import Document
from pydantic import EmailStr, Field
from datetime import datetime,timezone
from typing import Optional


class User(Document):

    name: str
    email: EmailStr
    phone: Optional[str] = None
    password_hash: str
    signup_platform: str = "web"
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))
    last_login: datetime = Field(default_factory=datetime.now(timezone.utc))
    active: bool = True
    is_verified: bool = False
    location: Optional[str] = None
    preferred_city: Optional[str] = None

    class Settings:
        name = "users"
