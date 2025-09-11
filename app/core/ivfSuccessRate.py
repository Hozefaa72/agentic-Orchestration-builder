from app.core.boto3client import bot_generate
import json


async def IVFSuccessRate(user_message, language: str):

    # Explicitly keep messages as a list of separate strings
    messages = [
        {"first_text":"We report a success rate of around 70-75% per cycle",
         "second_heading":"1.75 Lakh +",
         "second_text":"Couples found happiness"
        },
        "You can also get a personalized estimate  with our Success Calculator",
    ]

    prompt = f"""
                You are a helpful assistant. 
                User message: {user_message}  

                Your task:  
                - If the user asks about success rate, couples, or related information, translate the messages into {language}.  
                - Translate only the text fields (`first_text`, `second_heading`, `second_text`) into {language},  
                but keep all numbers/digits exactly the same.  
                - Translate the second string in the list into {language}.  
                - If the user asks irrelevant or unwanted questions, return:  
                ["This question is not related. Is there anything else I can do?"]  

                ⚠️ IMPORTANT:  
                - Do not add explanations, introductions, or extra text.  
                - Return **only valid JSON** in the exact same structure.  

                Input Messages:  
                {messages}  

                Expected Output Example:  
                [
                {{
                    "first_text": "We report a success rate of around 70-75% per cycle",
                    "second_heading": "1.75 Lakh +",
                    "second_text": "Couples found happiness"
                }},
                "This is a translated second string"
                ]
            """


    answer = await bot_generate(prompt, 500)

    try:
        answer = json.loads(answer)  # will give list
    except:
        answer = [answer]

    print("Bedrock Response:", answer)
    return answer
