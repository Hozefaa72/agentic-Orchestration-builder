from openai import AsyncOpenAI
from app.core.assistant_init import IVFChatbot
from app.config import ENV_PROJECT

client = AsyncOpenAI(
    api_key=ENV_PROJECT.OPENAI_API_KEY,  # ✅ Correct
    default_headers={"OpenAI-Beta": "assistants=v2"}
)

manager = IVFChatbot(client)
