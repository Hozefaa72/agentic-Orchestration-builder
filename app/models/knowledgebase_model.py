from beanie import Document
from pydantic import Field
from datetime import datetime, timezone
from typing import Optional
from enum import Enum
from app.models.llmmodels_models import llmcompany


class KnowledgeBase(Document):

    KBName: str
    KbFilename: Optional[list[str]] = None
    KBDecription: Optional[str] = None
    KBEmbeddingModelcompany: llmcompany
    KBEmbeddingModelname: str
    KBCreatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    KBMetadata: Optional[str] = None
    KBVectorDatabsepath: Optional[str] = None
    chunksize: Optional[int] = 1000
    chunkoverlap: Optional[int] = 200

    class Settings:
        name = "KnowledgeBase"

    class Config:
        use_enum_values = True
