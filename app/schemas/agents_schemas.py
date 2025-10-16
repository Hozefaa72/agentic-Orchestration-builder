from pydantic import BaseModel
from app.models.llmmodels_models import llmcompany
from typing import Optional

class Agent_info(BaseModel):
    agentName: str
    agentPrompt:str
    agentLLMModelcompany:llmcompany
    agentLLMModelname:str
    agentKBID:Optional[list[str]]=None