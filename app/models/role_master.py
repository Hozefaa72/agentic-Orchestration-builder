from beanie import Document
from typing import Optional

class Role(Document):
    rolename: str
    roledescription: Optional[str] = None

    class Settings:
        name = "RoleMaster"
