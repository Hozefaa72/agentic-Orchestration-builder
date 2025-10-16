from pydantic import BaseModel
from typing import Optional
from enum import Enum

class roles(str, Enum):
    Admin="Admin"
    User="User"
    SuperAdmin="SuperAdmin"

class role(BaseModel):
    rolename: str
    roledescription: Optional[str]=None