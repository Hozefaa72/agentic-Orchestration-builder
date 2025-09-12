from app.core.boto3client import bot_generate
import json
import ast

async def clean_model_output(answer: str):
    try:
        # Try to load directly as JSON
        return json.loads(answer)
    except json.JSONDecodeError:
        try:
            # If it's wrapped as a string in a list, unwrap with ast.literal_eval
            parsed = ast.literal_eval(answer)
            if isinstance(parsed, list) and len(parsed) == 1 and isinstance(parsed[0], str):
                return json.loads(parsed[0])
            return parsed
        except Exception:
            return answer

async def lifestyleAndPreparations(language: str):
    print("user language", language)

    # Explicitly keep messages as a list of separate strings
    messages = [
        {"heading":"Things to Consider ",
         "alcohol":"Avoid Alcohol",
         "Smoking":"Avoid Smoking",
         "hydration":"Stay Hydrated",
         "stress":"Avoid Stress"},
        "Apart from this, you can adopt a protein-rich diet to support fertility",
        "For more personalized guidance, schedule a free consultation with our fertility expert today!",
    ]

    # No need to join — instead pass list directly in prompt
    prompt = f"""
You are a helpful assistant.  
Translate each of the following items into {language}.
in the dictionary change the language of only vales not keys and return dict as dict not string  
Return the result strictly as a JSON message given below ,  
keeping the same number of items as input.
and don't add anything from your side
output should be list only not other than anything

Input Messages:
{messages}

Output Format Example:
[dict,"<translated message 1>", "<translated message 2>"]
"""


    answer = await bot_generate(prompt,500)
    
    # try:
    #     answer = json.loads(answer)  # will give list
    # except:
    #     answer = [answer] 
    answer= await clean_model_output(answer)
    print("Bedrock Response:", answer)
    return answer
