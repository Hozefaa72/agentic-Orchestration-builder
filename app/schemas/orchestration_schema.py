from pydantic import BaseModel
from typing import Optional

class orchestration(BaseModel):
    orchestrationName: str
    orchestrationDescription:Optional[str]=None
    adminids:Optional[list[str]]=None