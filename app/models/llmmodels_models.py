from beanie import Document
from pydantic import Field
from datetime import datetime, timezone
from typing import Optional
from enum import Enum


class llmcompany(str, Enum):
    GoogleGemini = "GoogleGemini"
    OpenAI = "OpenAI"


# class OpenAIModels(str, Enum):
#     OpenAIGPT4Nano="gpt-4.1-nano"
#     OpenAIGPT5Nano="gpt-5-nano"
#     OpenAIGPT5Mini="gpt-5-mini"
#     OpenAIGPT5="gpt-5"
#     OpenAIGPTurbo="gpt-3.5-turbo"
#     OpenAIGPT4="gpt-4"

# class GeminiModels(str, Enum):
#     GeminiPro = "Gemini 2.5 Pro"
#     GeminiFlash = "Gemini 2.5 Flash"
#     GeminiFlashLite = "Gemini 2.5 Flash-Lite"


class ModelType(str, Enum):
    Chat = "Chat"
    Embedding = "Embedding"


class LLMModel(Document):

    llmcompanyname: llmcompany
    basemodelname: str
    llmapikey: Optional[str] = None
    model_type: ModelType
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    isapiexpired: Optional[bool] = False
    tokenused: Optional[int] = 0

    class Settings:
        name = "LLMModels"

    class Config:
        use_enum_values = True
