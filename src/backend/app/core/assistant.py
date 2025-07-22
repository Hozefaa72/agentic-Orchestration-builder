from openai import AsyncOpenAI
from backend.app.core.assistant_init import IVFChatbot
from backend.app.config import Settings

client = AsyncOpenAI(
    api_key=Settings().OPENAI_API_KEY, default_headers={"OpenAI-Beta": "assistants=v2"}
)

manager = IVFChatbot(client)
