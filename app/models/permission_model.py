from beanie import Document
from typing import Optional


class Permissions(Document):
    permissionname: str
    description: Optional[str] = None
    ispublic: bool = False

    class Settings:
        name = "Permissions"
