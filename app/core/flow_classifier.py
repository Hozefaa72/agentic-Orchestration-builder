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
    print(msg)
    system_instruction = (
        "You are a classifier. Follow these rules strictly in order of priority:\n"
        "1. If the input is a name, number, pincode,indira_ivf center name,city name, state name, country name, date, address, time slots, "
        "or just random meaningless text (like 'ewiufhifehiuwehfib') or the user donse't want to give his/her information, then return None.\n"
        "2. If the user talks about loan or emi options or any money or  any bank related things then classify as loan_and_emi.\n"
        "3. If the user talks about ivf calculation or wants to know his or her successful chances of ivf then classify as ivf_success_calculator.\n"
        "4. If the user talks about IVF or Indira IVF Success Rate then classify as success_rate.\n"
        "5. If the user talks about improvement of anything related to ivf lifestyle then classify as Lifestyle_and_Preparations.\n"
        "6. If the user message contains signing legal consent before ivf or anything about legal consent or bond or content in bod or agreement or anything realted to consent form then classify as legal_consent.\n"
        "7. If the user asks any question not related to ivf or Indira ivf or anything irrelevant to indira ivf then return out_of_context.\n\n"
        "Return ONLY one word exactly from this list:\n"
        "book_appointment, ivf_success_calculator, Lifestyle_and_Preparations, cost_and_package, loan_and_emi, "
        "emergency_contact, success_rate, legal_consent, out_of_context, None.\n"
        "No explanation. No extra text."
    )

    prompt = f"{system_instruction}\n\nQuestion: {msg}"

    answer = await ask_openai_validation_assistant(
        prompt=prompt,
        max_tokens=10,
    )

    print(f"[Flow Check Response Time] {time.time() - starttime:.2f} sec")
    print("flow change:", answer)
    return answer
