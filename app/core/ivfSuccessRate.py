from app.core.boto3client import bot_generate
import json


async def IVFSuccessRate(user_message, language: str):

    # Explicitly keep messages as a list of separate strings
    messages = [
        {
            "first_text": "We report a success rate of around 70-75% per cycle",
            "second_heading": "1.75 Lakh +",
            "second_text": "Couples found happiness",
        },
        "You can also get a personalized estimate  with our Success Calculator",
    ]

    prompt = f"""
                You are a helpful assistant. 
                User message: {user_message}  

                Your task:  

                - CASE 1: If the user asks about success rate, successful cases, couples, or related information:  
                • Translate the given `messages` list into {language}.  
                • Only translate the values of `first_text`, `second_heading`, `second_text`, and the second string in the list.  
                • Keep numbers/digits exactly the same.  
                • Keep the structure **identical** to {messages}.  

                - CASE 2: If the user asks about failure rate, failures, or anything irrelevant about Indira IVF:  
                • Return exactly this JSON (not merged with messages):  
                ["I can't help you on this. Is there anything else I can do?"]

                ⚠️ STRICT RULES:  
                - Output must be **only valid JSON**.  
                - Do not add explanations, labels, or extra text.  
                - The output must be **either** the translated `messages` list **or** the failure JSON, nothing else.  

                Input Messages:  
                {messages}  

                Output Format Example (CASE 1):
                [{{"first_text": "...", "second_heading": "...", "second_text": "..."}}, "<translated message>"]

                Output Format Example (CASE 2):
                ["I can't help you on this. Is there anything else I can do?"]
            """
    answer = await bot_generate(prompt, 500)

    try:
        answer = json.loads(answer)  # will give list
    except:
        answer = [answer]

    print("Bedrock Response:", answer)
    return answer
