from app.core.boto3client import bot_generate
import json


async def loan_emi_option(user_message,language: str):
    print("user language", language)

    # Explicitly keep messages as a list of separate strings
    messages = [
        "Yes, we have tie-ups with banks that offer easy loan and EMI options to make IVF treatment more affordable",
        "To check your eligibility or know more simply click on apply now below",
        {"content":"Bringing your parenthood dream closer"}
    ]

    prompt = f"""
You are a helpful assistant. 
user message={user_message} 
If the input messages are about loan or EMI options, translate each of them into {language}.  
Otherwise, instead of translation, return the fixed response:
["I can't help you on this. Is there anything else I can do?"]

Return the result strictly as a JSON list of strings,  
keeping the same number of items as input.

Input Messages:
{messages}

Output Format Example:
["<translated message 1>", "<translated message 2>,"dict"]
"""


    answer = await bot_generate(prompt,500)
    
    try:
        answer = json.loads(answer)  # will give list
    except:
        answer = [answer] 

    print("Bedrock Response:", answer)
    return answer
