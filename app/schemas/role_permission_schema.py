from pydantic import BaseModel

class rolepermissionmapping(BaseModel):
    role_id: str
    permission_id: str