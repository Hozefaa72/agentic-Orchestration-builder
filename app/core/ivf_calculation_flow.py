from app.core.boto3client import bot_generate
import json


async def ivf_success_calculation_flow(language: str):
    print("user language", language)

    # Explicitly keep messages as a list of separate strings
    messages = [
        "Yes, Sure. We have devised an IVF Success Calculator which gives success rate based on historical data of Indira IVF.",
        "This is how our IVF Success Calculator works.\n1 Share details and reports\n2 We analyze key fertility factors\n3 Know success rate for each cycle",
    ]

    # No need to join — instead pass list directly in prompt
    prompt = f"""
You are a helpful assistant.  
Translate each of the following items into {language}.  
Return the result strictly as a JSON list of strings,  
keeping the same number of items as input.
and don't add anything from your side

Input Messages:
{messages}

Output Format Example:
["<translated message 1>", "<translated message 2>"]
"""


    answer = bot_generate(prompt,500)
    
    try:
        answer = json.loads(answer)  # will give list
    except:
        answer = [answer] 

    print("Bedrock Response:", answer)
    return answer
