from pydantic import BaseModel
from typing import Optional

class permission(BaseModel):
    permissionname :str
    description:Optional[str]=None 
    ispublic :bool=False