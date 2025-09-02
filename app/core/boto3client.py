import boto3
import time
async def bot_generate(msg: str,max_token:int=10):    
    starttime=time.time()
    client = boto3.client("bedrock-runtime")

    model_id = "anthropic.claude-3-haiku-20240307-v1:0"

    messages = [
        {
            "role": "user",
            "content": [
                {"text": f"{msg}"}
            ],
        }
    ]

    response = client.converse(
        modelId=model_id,
        messages=messages,
        inferenceConfig={
            "maxTokens": max_token,   
            "temperature": 0.0,
        },
    )

    answer = response["output"]["message"]["content"][0]["text"].strip()
    print(time.time()-starttime)
    return answer