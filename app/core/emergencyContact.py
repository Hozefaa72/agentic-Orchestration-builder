from app.core.boto3client import bot_generate
import json


async def EmergencyContact(user_message, language: str):

    # Explicitly keep messages as a list of separate strings
    messages = [
        {
            "heading": "EMERGENCY NUMBER",
            "phone_number": "1800 3092429",
            "text": "In case of any emergency, feel free to call this number between 9 AM and 6 PM.",
        },
        "Alternatively, you can also reach out to us on WhatsApp for quick support",
    ]

    prompt = f"""
                You are a helpful assistant.  
                user message = {user_message}  

                Your task:  
                - If the user asks about emergency contacts, translate the messages into {language}.  
                - In the dictionary, translate only the `heading` and `text` fields into {language},  
                but keep the `phone_number` exactly the same.  
                - Translate the second string in the list into {language}.  
                - If the user asks irrelevant or unwanted questions not related to emergency contact, return:  
                ["Please call on the emergency number provided above. Is there anything else I can do?"]  

                Return the result strictly as a JSON list,  
                keeping the same structure (dict + string).  

                Input Messages:  
                {messages}  

                Output Format Example:  
                [{{"heading":"<translated heading>", "phone_number":"1800 3092429", "text":"<translated text>"}}, "<translated string>"]  
            """

    answer = await bot_generate(prompt, 500)

    try:
        answer = json.loads(answer)  # will give list
    except:
        answer = [answer]

    print("Bedrock Response:", answer)
    return answer
