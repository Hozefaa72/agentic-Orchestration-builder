from pydantic import BaseModel, Field
from typing import Any, Optional


class responsemodel(BaseModel):
    success: bool
    result: Optional[Any] = None
    error_message: Optional[str] = Field(None, alias="message")
    error_detail: Optional[str] = Field(None, alias="detail")
    status_code: int

    class Config:
        from_attributes = True
