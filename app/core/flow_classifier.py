import boto3
import time
async def flow_check(msg: str):    
    starttime=time.time()
    client = boto3.client("bedrock-runtime")

    model_id = "anthropic.claude-3-haiku-20240307-v1:0"

    system_instruction = (
        "You are a classifier. "
        "if the user talks about loan or emi options or any money or bank  related things then classify it as loan_and_emi"
        "if the user talks about ivf calculation then also ivf_success_calculation should be given but if the user talks about IVF or Indira IVF Success Rate then give success_rate"
        "if the user talks about improvement of anything related ivf and it impacts lifetyle then call the class Lifestyle_and_Preparations"
        "if the user asks any question not related to ivf or Indira ivf then return out_of_context. it can be like 'What’s the weather today' or 'who will win today's match etc' "
    "If the input contains a name, number, pincode, date ,address,time slots, or is just random meaningless text (like 'ewiufhifehiuwehfib'), then return None. "
        "Return ONLY one word exactly from this list: "
        "book_appointment, ivf_success_calculator,Lifestyle_and_Preparations,cost_and_package,loan_and_emi,emergency_contact,success_rate,out_of_context,None. "
        "If the question contains a name, number,timeslots, date ,pincode, or address → return None. "
        "No explanation, no extra text."
    )

    messages = [
        {
            "role": "user",
            "content": [
                {"text": f"{system_instruction}\n\nQuestion: {msg}"}
            ],
        }
    ]

    response = client.converse(
        modelId=model_id,
        messages=messages,
        inferenceConfig={
            "maxTokens": 10,   
            "temperature": 0.0,
        },
    )

    answer = response["output"]["message"]["content"][0]["text"].strip()
    print(time.time()-starttime)
    print("flow change",answer)
    return answer