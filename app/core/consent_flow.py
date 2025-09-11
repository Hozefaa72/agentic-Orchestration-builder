import boto3
from app.models.threads import Thread
from app.models.user_info import User_Info, AppointmentStatus
from app.core.ivf_centers import find_nearest_by_postal
from bson import ObjectId
import json


async def ConsentFlow(
    thread_id: str, flow_id: str, step_id: str, language: str, user_message: str
):

    thread_obj_id = ObjectId(thread_id)
    thread = await Thread.find_one(Thread.id == thread_obj_id)
    step_count=thread.step_count
    print("step_count",step_count)

    if thread and thread.step_id:
        step_id = thread.step_id
    elif not step_id:
        step_id = "1"

    print(
        " Current step:",
        step_id,
        "| Thread:",
        thread_id,
        "| Flow:",
        flow_id,
        "|user message",
        user_message,
    )

    consentflow = {
        "flow_id": "legal_consent",
        "steps": {
            "1": {
                "step_id": "1",
                "message": "Yes, both partners (or the individual) must sign consent forms before starting IVF.",
                "expected_input": "",
                "action": None,
                "other_text":"",
                "next_step": "2",
            },
            "2": {
                "step_id": "2",
                "message": ["The form covers IVF steps, embryo handling, storage period, future decisions (like donation or disposal), and your right to withdraw consent anytime","Hope this was helpful. Let me know if you need more info"],
                "expected_input": "What’s included in the consent form? or what's inside the consent form?",
                "other_text":[ {"first_text":"For more specific information, please connect with our call center between 9 AM and 6 PM.","second_text":"CUSTOMER CARE NUMBER","phone_number":"1800 3092429"},
                                "Hope this helps! You can come back anytime to explore  or get more info"],
                "action": None,
                "next_step": None,
            },

        },
    }

    step = consentflow["steps"].get(step_id)
    if not step:
        return {"error": "Invalid step"}

    if not user_message or user_message.strip() == "":
        user_message = ""
   
    prompt = f"""
You are a validation assistant.
Conversation language = {language}.
Step: {step_id}, Expecting: {step['expected_input']}
the expected input can also be in user selected language also 
User input: "{user_message}"


Instructions:
- Always return ONLY {step['message']} as bot_response if the input is valid.
- If {step['message']} is a list, return that list translated into {language}.
- If the user enters an invalid response compared to the expected input:
  → return only {step['other_text']} (translated into {language}).
- Do NOT send both {step['other_text']} and {step['message']} together.
- Always respond strictly in valid JSON, no extra text.
 

Format:
{{
  "status": "VALID" or "INVALID",
  "bot_response": "string or list of string  (next message to show the user in {language})"
}}

Rules:
- If  meaning are correct → status = "VALID" and bot_response = next step message (filled with variables if available).
- If not valid → status = "INVALID" and bot_response = re-ask current step politely in {language}.
"""

    client = boto3.client("bedrock-runtime")
    model_id = "anthropic.claude-3-haiku-20240307-v1:0"

    response = client.converse(
        modelId=model_id,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"maxTokens": 500, "temperature": 0},
    )

    llm_answer = response["output"]["message"]["content"][0]["text"].strip()
    print("raw llm answer:", llm_answer)

    try:
        llm_json = json.loads(llm_answer)
    except Exception:
        # fallback if model doesn't output strict JSON
        llm_json = {"status": "INVALID", "bot_response": step["message"]}


    if llm_json.get("status") == "INVALID":
        if thread:
            thread.step_count+=1
            await thread.save()
        if step_id =="2":
            return llm_json.get("bot_response"), "out_of_context"

    if llm_json.get("status") == "VALID":
        next_step = step["next_step"]
        print("next step is",next_step)

        if thread:
            thread.flow_id = flow_id
            thread.step_id = next_step
            thread.step_count = 1
            await thread.save()

        return llm_json.get("bot_response"), None
    else:
        # stay on same step
        if thread and step["step_id"] == "1":
            next_step = step["next_step"]
            thread.flow_id = flow_id
            thread.step_id = next_step
            thread.step_count = 1
            await thread.save()
        return llm_json.get("bot_response"), None
