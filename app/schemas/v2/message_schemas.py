from pydantic import BaseModel
from typing import Any


class MessageCreate(BaseModel):
    content: Any
    sender: str
