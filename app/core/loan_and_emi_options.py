from app.core.boto3client import bot_generate
import json


async def loan_emi_option(user_message, language: str):
    print("in loan emi flow")

    # Explicitly keep messages as a list of separate strings
    messages = [
        "Yes, we have tie-ups with banks that offer easy loan and EMI options to make IVF treatment more affordable",
        "To check your eligibility or know more simply click on apply now below",
        {"content": "Bringing your parenthood dream closer"},
    ]

    prompt = f"""
You are a helpful assistant.
user message = {user_message}

Rules (apply in order, highest priority first):

1. If the user provides incorrect, misleading, accusatory, or negative statements about IVF loans/EMIs  
   OR if the user expresses complaints, suspicion, or negative sentiment about IVF loans/EMIs,  
   → Then IGNORE input messages and return exactly:
   ["I can't help you on this. Is there anything else I can do?"]

2. If the user shows genuine informational intent about IVF loan or EMI options or loan policy then 
   (even if grammar is broken, phrasing is casual, or in any language)
   → Then translate EACH input message into {language}.  
   (Keep the same number of items. Dicts must remain dicts, only values translated.)

3. If the user message is not about loan/EMI at all,  
   → Return exactly:
   ["I can't help you on this. Is there anything else I can do?"]

Input Messages:
{messages}

Output Format Example:
["<translated message 1>", "<translated message 2>", {{ "content": "<translated content>" }}]
"""

    answer = await bot_generate(prompt, 500)

    try:
        answer = json.loads(answer)  # will give list
    except:
        answer = [answer]

    print("Bedrock Response:", answer)
    return answer
