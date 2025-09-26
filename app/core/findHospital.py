from app.utils.llm_utils import ask_openai_validation_assistant
from app.models.threads import Thread
from app.models.user_info import User_Info
from app.core.ivf_centers import find_nearest_by_postal
from bson import ObjectId
import json
import re
from app.core.existingUser import step_check
from app.schemas.otp_verification import OtpRequest,OtpVerify
from app.cruds.otp_verification import create_or_update_otp_entry,send_indira_otp,verify_otp_entry,call_ivf_lead_creation_api




async def FindHospital(
    thread_id: str, flow_id: str, step_id: str, language: str, user_message: str ):
    find_hospital_flow = {
        "flow_id": "cost_and_package",
        "steps": {
            "1": {
                "step_id": "1",
                "message": ["To share the IVF Centers details, I’ll need a few quick details from you","Please share your pincode"],
                "expected_input": "user wants to find nearby ivf or indira ivf centers",
                "valid_condition": "",
                "action": None,
                "other_text": "",
                "final_text": "",
                "next_step": "2",
            },
            "2": {
                "step_id": "2",
                "message": "",
                "expected_input": "pincode or city or area name",
                "valid_condition": r"^[A-Za-z\s]{2,50}$",
                "action": "send_center details",
                "other_text": [
                    "Sorry, the Pincode is invalid",
                    " Please enter a valid pincode to check clinic availability near you",
                ],  # "Please share your name it is important for appointment booking step",
                "final_text": [
                    "We cannot proceed with the booking process without these details. Please share your pincode to continue",
                    "You can enter your city or area name instead",
                ],
                "next_step": "3",
            },
            "3": {
                "step_id": "3",
                "message": ["", "Hope this was helpful. Let me know if you need more info"],
                "expected_input": "center_selection",
                "valid_condition": r".+",
                "action": None,
                "other_text": "",
                "final_text": "",
                "next_step": None,
                
            }
        },
    }

    thread_obj_id = ObjectId(thread_id)
    thread = await Thread.find_one(Thread.id == thread_obj_id)
    step_count = thread.step_count
    print("step_count", step_count)

    if thread and thread.step_id:
        step_id = thread.step_id
    elif not step_id:
        step_id = "1"
        user_message = "Find Indira IVF Centers near me?"

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


    step = find_hospital_flow["steps"].get(step_id)
    if not step:
        return {"error": "Invalid step"}

    if not user_message or user_message.strip() == "":
        user_message = ""

    if step["step_id"] == "2":
        match = re.search(r"\b\d{6}\b", user_message)
        if match:
            pincode = match.group(0)  # the actual 6-digit code
            response = find_nearest_by_postal(pincode)
          # pass only the pincode
        else:
            response = None
        print("response", response)
        if response:
            user = await User_Info.find_one(User_Info.thread_id == thread_id)
            if user:
                user.preffered_center = response
                user.pincode = pincode
                await user.save()
            else:
                user_info = User_Info(preffered_center=response,pincode=pincode, thread_id=thread_id)
                await user_info.insert()
            next_step = step["next_step"]
            user = await User_Info.find_one(User_Info.thread_id == thread_id)
            if thread:
                thread.flow_id = flow_id
                thread.step_id = next_step
                await thread.save()
                return response, "centers"
        # else:
        # return ["Sorry, the Pincode is invalid"," Please enter a valid pincode to check clinic availability near you"], None
    if step["step_id"] == "3":
        user = await User_Info.find_one(User_Info.thread_id == thread_id)
        for c in user.preffered_center:
            if (c["Clinic Name"].strip().lower() == user_message.strip().lower()) or (
                c["Clinic Name"].strip().lower().split("-")[1].strip()
                == user_message.strip().lower()
            ):
                user.preffered_center_address = c["Address"]
                user.City = c["City"]
                user.State = c["State"]
                await user.save()
                step["message"][0] = c["Address"]
        if step["message"][0] == "":
            return "Please enter a valid city", None
    prompt = f"""
You are a validation assistant.
Conversation language = {language}.
Step: {step_id}, Expecting: {step['expected_input']}
the expected input can also be in user selected language also 
User input: "{user_message}"
Valid condition (regex): {step['valid_condition']}
bot_response must ALWAYS be written in {language}, regardless of input language or system language.



Instructions:
1. Refusal detection:
   - If the {user_message} intent states that it dosen't want to share information then return only {step['final_text']} (translated into {language}), with status = "INVALID".
   - If user input clearly expresses **refusal** (like "I don’t want to give", "skip", "no", "nahi batana", "not sharing", "prefer not to say"),
     then → return only {step['final_text']} (translated into {language}), with status = "INVALID".
   - Do NOT treat unrelated or invalid inputs as refusal.
2. Regex + meaning validation:
   - If the input matches {step['valid_condition']} (regex + meaning check), 
     then → return status = "VALID" and bot_response = {step['message']} (translated into {language}).
3. Otherwise:
   - If input is not refusal and does not match regex, 
     then → return status = "INVALID" and bot_response = {step['other_text']} (translated into {language}).

- ** and also in same the format if it is string then string and if its is list of string then list of string

Format:
{{
  "status": "VALID" or "INVALID",
  "bot_response": "string or list of string  (next message to show the user in {language})"
}}

Rules:
- If regex + meaning are correct → status = "VALID" and bot_response = next step message (filled with variables if available).
- If not valid → status = "INVALID" and bot_response = re-ask current step politely in {language}.
"""


    llm_answer = await ask_openai_validation_assistant(prompt)
    print("raw llm answer:", llm_answer)

    try:
        llm_json = json.loads(llm_answer)
    except Exception:
        # fallback if model doesn't output strict JSON
        llm_json = {"status": "INVALID", "bot_response": step["message"]}

    # Final decision
    if llm_json.get("status") == "INVALID":
        if thread:
            thread.step_count += 1
            await thread.save()

    if llm_json.get("status") == "VALID":
        next_step = step["next_step"]
        print(next_step)

        # Save thread
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
