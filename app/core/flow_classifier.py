# import boto3
# import time
# async def flow_check(msg: str):    
#     starttime=time.time()
#     client = boto3.client("bedrock-runtime")

#     model_id = "anthropic.claude-3-haiku-20240307-v1:0"

#     system_instruction = (
#         "You are a classifier. "
#         "if the user talks about ivf calculation then also ivf_success_calculation should be given"
#         "if the user talks about improvement of anything related ivf and it impacts lifetyle then call the class Lifestyle_and_Preparations"
#         "if the user talks about loan or emi options then classify it as loan_and_emi "
#         "Return ONLY one word exactly from this list: "
#         "book_appointment, ivf_success_calculator,Lifestyle_and_Preparations,cost_and_package,loan_and_emi,emergency_contact,None. "
#         "If the question contains a name, number, pincode, or address → return None. "
#         "No explanation, no extra text."
#     )

#     messages = [
#         {
#             "role": "user",
#             "content": [
#                 {"text": f"{system_instruction}\n\nQuestion: {msg}"}
#             ],
#         }
#     ]

#     response = client.converse(
#         modelId=model_id,
#         messages=messages,
#         inferenceConfig={
#             "maxTokens": 10,   
#             "temperature": 0.0,
#         },
#     )

#     answer = response["output"]["message"]["content"][0]["text"].strip()
#     print(time.time()-starttime)
#     print("flow change",answer)
#     return answer

import time
from app.llm_utils import ask_openai_validation_assistant

async def flow_check(msg: str):
    starttime = time.time()

    system_instruction = (
        "You are a classifier. "
        "if the user talks about ivf calculation then also ivf_success_calculator should be given. "
        "if the user talks about improvement of anything related to ivf and it impacts lifestyle then call the class Lifestyle_and_Preparations. "
        "if the user talks about loan or emi options then classify it as loan_and_emi. "
        "Return ONLY one word exactly from this list: "
        "book_appointment, ivf_success_calculator, Lifestyle_and_Preparations, cost_and_package, loan_and_emi, emergency_contact, None. "
        "If the question contains a name, number, pincode, or address → return None. "
        "No explanation, no extra text."
    )

    prompt = f"{system_instruction}\n\nQuestion: {msg}"

    answer, _ = await ask_openai_validation_assistant(
        prompt=prompt,
        model="gpt-3.5-turbo",  # or "gpt-4o" for better quality
        max_tokens=10,
        temperature=0
    )

    print(f"[Flow Check Response Time] {time.time() - starttime:.2f} sec")
    print("flow change:", answer)
    return answer
