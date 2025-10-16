from typing import Optional
from app.models.llmmodels_models import llmcompany
from pydantic import BaseModel
from app.models.llmmodels_models import ModelType

class llmmodel(BaseModel):

    llmcompanyname: llmcompany 
    basemodelname: str
    llmapikey: Optional[str]=None
    model_type:ModelType
    isapiexpired: Optional[bool]=False
    tokenused: Optional[int]=0


class llmmodelfilter(BaseModel):
    llmcompanyname: Optional[llmcompany]=None
    model_type:Optional[ModelType]=None
