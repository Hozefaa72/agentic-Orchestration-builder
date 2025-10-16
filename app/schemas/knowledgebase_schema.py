from pydantic import BaseModel
from typing import Optional
from app.models.llmmodels_models import llmcompany


class knowledgebase(BaseModel):

    KBName: str
    KBDecription:Optional[str]=None
    KBEmbeddingModelcompany:llmcompany
    KBEmbeddingModelname:str
    KBMetadata:Optional[str]=None
    chunksize:Optional[int]=1000
    chunkoverlap:Optional[int]=200

