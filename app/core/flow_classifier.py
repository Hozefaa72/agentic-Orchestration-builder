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
from app.utils.llm_utils import ask_openai_validation_assistant


async def flow_check(msg: str):
    starttime = time.time()
    print(msg)
    system_instruction = (
    "You are a strict classifier. Follow these rules in EXACT priority order:\n"
    "RULE 1 (highest priority, must override all others):\n"
    "- If the input is ONLY a name, a number (like phone number), pincode, Indira IVF center name, city, state, country, date, address, time slot, "
    "or meaningless random text (like 'ewiufhifehiuwehfib'), OR if the user refuses to provide information → RETURN None immediately. "
    "Do not check other rules if this condition is true.\n\n"
    "RULE 2: If the user talks about loan, EMI, money, or bank-related things → loan_and_emi.\n"
    "RULE 3: If the user talks about IVF calculation or wants to know their chances of IVF success → ivf_success_calculator.\n"
    "RULE 4: If the user talks about IVF or Indira IVF success rate or ivf successful cases → success_rate.\n"
    "RULE 5: If the user talks about improving fertility, IVF lifestyle, preparations, or wants to improve chances of successful IVF → Lifestyle_and_Preparations.\n"
    "RULE 6: If the user mentions signing legal consent before IVF, or anything about consent forms, bonds, agreements → legal_consent.\n"
    "RULE 7: If the user asks about the different steps in ivf cycle or steps in ivf cycle or steps in Self Oocyte cycle then return ivf_steps"
    "RULE 8: If the user asks about the costs of the ivf cycle or different packages in an ivf cycle or packages in ivf cycle then return cost_and_package"
    "RULE 9: If the user asks any question unrelated to IVF or Indira IVF or fertility or like who is rahul? etc → out_of_context.\n"
    "RULE 10: If the user wants to contact Indira IVF or asks for contact number / emergency contact → emergency_contact.\n\n"
    "Return ONLY one exact word from this list:\n"
    "book_appointment, ivf_success_calculator, Lifestyle_and_Preparations, cost_and_package, loan_and_emi, "
    "emergency_contact, success_rate, legal_consent,ivf_steps,out_of_context, None\n"
    "(case-sensitive, no quotes, no explanations)."
)

    prompt = f"{system_instruction}\n\nQuestion: {msg}"

    answer = await ask_openai_validation_assistant(
        prompt=prompt,
        max_tokens=10,
    )

    print(f"[Flow Check Response Time] {time.time() - starttime:.2f} sec")
    print("flow change:", answer)
    return answer
