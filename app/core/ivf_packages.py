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




async def ivfPackages(
    thread_id: str, flow_id: str, step_id: str, language: str, user_message: str
):
    packages_flow = {
        "flow_id": "cost_and_package",
        "steps": {
            "1": {
                "step_id": "1",
                "message": ["To share the package details, I’ll need a few quick details from you","Please share your name"],
                "expected_input": "The user wants to know the cost of an IVF cycle or the packages available for an IVF cycle.",
                "valid_condition": "",
                "action": None,
                "other_text": "",
                "final_text": "",
                "next_step": "2",
            },
            "2": {
                "step_id": "2",
                "message": "Thanks. Please provide your mobile number",
                "expected_input": "name of the person",
                "valid_condition": r"^[A-Za-z\s]{2,50}$",
                "action": "send_otp_api",
                "other_text": "Sorry, I couldn’t recognize that as a name. Could you please re-enter your full name Let's try again",  # "Please share your name it is important for appointment booking step",
                "final_text": [
                    "We cannot continue with the booking without your name. Please enter your name to proceed",
                    "You can still explore information without giving your name. Would you like to know about topics below",
                ],
                "next_step": "3",
            },
            "3": {
                "step_id": "3",
                "message": "Please enter the OTP sent to your mobile number for verification",
                "expected_input": "only ten digit phone number",
                "valid_condition": r"^\d{10}$",
                "action": "verify_otp_api",
                "other_text": "Please enter a valid ten digit Phone Number it is important for booking an appointment",
                "final_text": [
                    "We cannot continue with the booking without your phone number. Please enter your number to proceed",
                    "You can still explore information without giving your number. Would you like to know about topics below",
                ],
                "next_step": "4",
            },
            "4": {
                "step_id": "4",
                "message": [
                    "Your mobile number is verified. Thank you for confirming!",
                    "Now please mention your preferred pin code",
                ],
                "expected_input": "6 digit otp",
                "valid_condition": r"^\d{6}$",
                "action": None,
                "other_text": "Oops! The OTP you entered doesn’t match. Please try again",
                "final_text": "You’ve reached the maximum OTP attempts. You can request a new OTP in 1 hour",
                "next_step": "5",
            },
            "5": {
                "step_id": "5",
                "message": ["Thank you for sharing your details",
                            {"title":"We offer 3 packages ","packages":[{"cycle":"1 CYCLE PLAN","cost":"Approx. ₹1-1.65L","text":"One Embryo Transfer"},{"cycle":"2 CYCLE PLAN","cost":"Approx. ₹2-2.5L","text":"Two Embryo Transfer"},{"cycle":"3 CYCLE PLAN","cost":"Approx. ₹3.5-3.75L","text":"Three Embryo Transfer"}],"body":"The right plan will be recommended by your consulting doctor based on your reports and medical history"},
                            "Do you want a free consultation to get personalized plan and pricing details?"],
                "expected_input": "pincode",
                "valid_condition": r"^\d{6}$",
                "action": "fetch_centers_api",
                "other_text": [
                    "Sorry, the Pincode is invalid",
                    " Please enter a valid pincode to check clinic availability near you",
                ],
                "final_text": [
                    "We cannot proceed with the booking process without these details. Please share your pincode to continue",
                    "You can enter your city or area name instead",
                ],
                "next_step": None,
            },
        },
    }

    thread_obj_id = ObjectId(thread_id)
    thread = await Thread.find_one(Thread.id == thread_obj_id)
    step_count = thread.step_count
    print("step_count", step_count)

    if thread and thread.step_id:
        step_id = thread.step_id
    elif not step_id:
        user_message=await step_check(thread_id,packages_flow,5)
        print("printing user message after existing user ",user_message)
        new_thread=await Thread.find_one(Thread.id == thread_obj_id)
        if new_thread.step_id:
            step_id=new_thread.step_id
        else:
            step_id = "1"
            user_message = "How much does IVF cycle cost?"

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

    packages_flow = {
        "flow_id": "cost_and_package",
        "steps": {
            "1": {
                "step_id": "1",
                "message": ["To share the package details, I’ll need a few quick details from you","Please share your name"],
                "expected_input": "The user wants to know the cost of an IVF cycle or the packages available for an IVF cycle.",
                "valid_condition": "",
                "action": None,
                "other_text": "",
                "final_text": "",
                "next_step": "2",
            },
            "2": {
                "step_id": "2",
                "message": "Thanks. Please provide your mobile number",
                "expected_input": "name of the person",
                "valid_condition": r"^[A-Za-z\s]{2,50}$",
                "action": "send_otp_api",
                "other_text": "Sorry, I couldn’t recognize that as a name. Could you please re-enter your full name Let's try again",  # "Please share your name it is important for appointment booking step",
                "final_text": [
                    "We cannot continue with the booking without your name. Please enter your name to proceed",
                    "You can still explore information without giving your name. Would you like to know about topics below",
                ],
                "next_step": "3",
            },
            "3": {
                "step_id": "3",
                "message": "Please enter the OTP sent to your mobile number for verification",
                "expected_input": "only ten digit phone number",
                "valid_condition": r"^\d{10}$",
                "action": "verify_otp_api",
                "other_text": "Please enter a valid ten digit Phone Number it is important for booking an appointment",
                "final_text": [
                    "We cannot continue with the booking without your phone number. Please enter your number to proceed",
                    "You can still explore information without giving your number. Would you like to know about topics below",
                ],
                "next_step": "4",
            },
            "4": {
                "step_id": "4",
                "message": [
                    "Your mobile number is verified. Thank you for confirming!",
                    "Now please mention your preferred pin code",
                ],
                "expected_input": "6 digit otp",
                "valid_condition": r"^\d{6}$",
                "action": None,
                "other_text": "Oops! The OTP you entered doesn’t match. Please try again",
                "final_text": "You’ve reached the maximum OTP attempts. You can request a new OTP in 1 hour",
                "next_step": "5",
            },
            "5": {
                "step_id": "5",
                "message": ["Thank you for sharing your details",
                            {"title":"We offer 3 packages ","packages":[{"cycle":"1 CYCLE PLAN","cost":"Approx. ₹1-1.65L","text":"One Embryo Transfer"},{"cycle":"2 CYCLE PLAN","cost":"Approx. ₹2-2.5L","text":"Two Embryo Transfer"},{"cycle":"3 CYCLE PLAN","cost":"Approx. ₹3.5-3.75L","text":"Three Embryo Transfer"}],"body":"The right plan will be recommended by your consulting doctor based on your reports and medical history"},
                            "Do you want a free consultation to get personalized plan and pricing details?"],
                "expected_input": "pincode",
                "valid_condition": r"^\d{6}$",
                "action": "fetch_centers_api",
                "other_text": [
                    "Sorry, the Pincode is invalid",
                    " Please enter a valid pincode to check clinic availability near you",
                ],
                "final_text": [
                    "We cannot proceed with the booking process without these details. Please share your pincode to continue",
                    "You can enter your city or area name instead",
                ],
                "next_step": None,
            },
        },
    }

    step = packages_flow["steps"].get(step_id)
    if not step:
        return {"error": "Invalid step"}

    if not user_message or user_message.strip() == "":
        user_message = ""

    existing_user=await User_Info.find_one(User_Info.thread_id == thread_id)
    if (step["step_id"]=="3"):
        match = re.search(r"\b\d{10}\b", user_message)
        if match:
            phone_number = match.group(0)
              # the actual 10-digit number
            print(existing_user.name)
            if existing_user:
                otp_request = OtpRequest(contact_no=phone_number, name=existing_user.name)
            else:
                otp_request = OtpRequest(contact_no=phone_number, name="Guest")
            otp = await create_or_update_otp_entry(otp_request, thread_id)
            await send_indira_otp(contact_no=phone_number, otp_code=otp["otp_code"])
            otp.pop("otp_code", None)
            if language =="English" and thread:
                thread.flow_id = flow_id
                thread.step_id = step["next_step"]
                thread.step_count = 1
                await thread.save()
                user = await User_Info.find_one(User_Info.thread_id == thread_id)
                user.phone_number = phone_number
                await user.save()
                return step["message"], None
        # if not(match) and language=="English":
        #     return step["other_text"], None

    if (step["step_id"]=="4" ):
        match = re.search(r"\b\d{6}\b", user_message)
        if match:
            otp = match.group(0)
            otp_request = OtpVerify(otp_code=otp,contact_no=existing_user.phone_number, name=existing_user.name)
            result=await verify_otp_entry(otp_request, thread_id)
            print("result of otp verification", result)
            if result and language=="English" and thread:
                thread.flow_id = flow_id
                thread.step_id = step["next_step"]
                thread.step_count = 1
                await thread.save()
                return step["message"], None
            if result and language !="English":
                thread.flow_id = flow_id
                thread.step_id = step["next_step"]
                thread.step_count = 1
                await thread.save()
                prompt=f"Yo have to just return {step['message']} in translated langauage-{language} Output:as Json and in same structure like the message which i have given"
                llm_answer = await ask_openai_validation_assistant(prompt)
                try:
                    llm_json = json.loads(llm_answer)
                except:
                    llm_json=[llm_answer]
                return llm_json,None
            if not(result) and language=="English":
                if existing_user.name:
                    otp_request = OtpRequest(contact_no=existing_user.phone_number, name=existing_user.name)
                else:
                    otp_request = OtpRequest(contact_no=existing_user.phone_number, name="Guest")
                otp = await create_or_update_otp_entry(otp_request, thread_id)
                await send_indira_otp(contact_no=existing_user.phone_number, otp_code=otp["otp_code"])
                return step["other_text"], None
            if not(result) and language!="English":
                prompt=f"Yo have to just return {step['other_text']} in translated langauage-{language} Output:as Json and in same structure like the message which i have given"
                llm_answer = await ask_openai_validation_assistant(prompt)
                if existing_user.name:
                    otp_request = OtpRequest(contact_no=existing_user.phone_number, name=existing_user.name)
                else:
                    otp_request = OtpRequest(contact_no=existing_user.phone_number, name="Guest")
                otp = await create_or_update_otp_entry(otp_request, thread_id)
                await send_indira_otp(contact_no=existing_user.phone_number, otp_code=otp["otp_code"])
                try:
                    llm_json = json.loads(llm_answer)
                except:
                    llm_json=[llm_answer]
                return llm_json,None
            
        # if not(match) and language=="English":
        #     return step["other_text"], None
        # return step["message"], None
    if step["step_id"] == "5":
        match = re.search(r"\b\d{6}\b", user_message)
        if match:
            pincode = match.group(0)  # the actual 6-digit code
            response = find_nearest_by_postal(pincode)  # pass only the pincode
        else:
            response = None

        if response:
            user = await User_Info.find_one(User_Info.thread_id == thread_id)
            user.preffered_center = response
            user.pincode=pincode
            await user.save()
            next_step = step["next_step"]
            user = await User_Info.find_one(User_Info.thread_id == thread_id)
            result=await call_ivf_lead_creation_api(
            full_name=user.name,
            contact_no=user.phone_number,
            pincode=user.pincode
          ) 
            print(result)
            if thread:
                thread.flow_id = flow_id
                thread.step_id = next_step
                await thread.save()
                
            if language=="English":
                return step['message'], "cost_and_package"
        # else:
        # return ["Sorry, the Pincode is invalid"," Please enter a valid pincode to check clinic availability near you"], None

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

    # client = boto3.client("bedrock-runtime")
    # model_id = "anthropic.claude-3-haiku-20240307-v1:0"

    # response = client.converse(
    #     modelId=model_id,
    #     messages=[{"role": "user", "content": [{"text": prompt}]}],
    #     inferenceConfig={"maxTokens": 500, "temperature": 0},
    # )

    # llm_answer = response["output"]["message"]["content"][0]["text"].strip()

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
        if step["step_id"] == "2":
            user_info = User_Info(name=user_message, thread_id=thread_id)

            await user_info.insert()
        if step["step_id"] == "3":
            user = await User_Info.find_one(User_Info.thread_id == thread_id)
            user.phone_number = user_message
            await user.save()
        if step["step_id"] == "5":
            user = await User_Info.find_one(User_Info.thread_id == thread_id)
            user.pincode = user_message
            await user.save()

        # Save thread
        if thread:
            thread.flow_id = flow_id
            thread.step_id = next_step
            thread.step_count = 1
            await thread.save()

        if step["step_id"] == "5":
            return llm_json.get("bot_response"), "cost_and_package"
        else:
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
