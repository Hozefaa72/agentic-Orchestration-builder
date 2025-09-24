from app.core.boto3client import bot_generate
import json


async def greetingsFlow(user_message, language: str):
    print("in loan emi flow")

    # Explicitly keep messages as a list of separate strings
    messages = ["Hello 👋 I’m here to help you with all your queries and tasks"]
    another_message=["I am Fine How can I help you today!"]

    prompt = f"""
You are a helpful assistant.
User message: {user_message}

Guidelines:
- If the user greets you with words like "hi", "hello", "hey", "good morning", "good evening", or similar greetings in any language, respond only with {messages}. Do not add any extra text.
- If the user asks "how are you", "how’s it going", "how do you do", or similar well-being questions in any language, respond with {another_message}.
- The response must always be in {language}.
- Do not confuse a well-being question ("how are you") with a simple greeting ("hello").
- Output must strictly follow the format below.

Output format:
[ "<translated_message>" ]
"""

    answer = await bot_generate(prompt, 200)

    try:
        answer = json.loads(answer)  # will give list
    except:
        answer = [answer]

    print("Bedrock Response:", answer)
    return answer
