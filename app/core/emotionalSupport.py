from app.core.boto3client import bot_generate
import json


async def EmotionalSupport(user_message, language: str):
    print("the language in emotional support is",language)
    # Explicitly keep messages as a list of separate strings
    messages = [
        "That's completely understandable, feel free to reach out to our team anytime you’re feeling unsure",
        "You can also watch videos of patients sharing their experiences",
        "Hope this was helpful. Let me know if you need more info"
    ]

    prompt = f"""
                You are a helpful assistant. 
                User message: {user_message}  

                Your task:  

                - CASE 1: If the user asks about question such that they are really nervous, depressed or frightened or if they want emotional support:  
                • Translate the given `messages` list into {language}.  
                • Keep the structure **identical** to {messages}.  
                don't give it as whole string in a list instead give the same structure as message a list and there it should have three strings in all language

                - CASE 2: If the user asks about anything unrelated to emotional support then:  
                • Return exactly this JSON (not merged with messages):  
                ["I can't help you on this. Is there anything else I can do?"]

               ⚠️ IMPORTANT:
                - Output MUST be valid JSON.
                - Use double quotes (") for strings, not single quotes (').
                - Do not wrap the whole list in quotes.
                Input Messages:  
                {messages}  

                Output Format Example (CASE 1):
                ["<translated message>","<translated message>","<translated message>"]

                Output Format Example (CASE 2):
                ["I can't help you on this. Is there anything else I can do?"]
            """
    answer = await bot_generate(prompt, 500)

    try:
        parsed = json.loads(answer)  # first decode
        if isinstance(parsed, str):  # still a JSON string
            parsed = json.loads(parsed)  # decode again
        answer = parsed  # will give list
    except:
        answer = [answer]

    print("Bedrock Response:", answer)
    return answer
