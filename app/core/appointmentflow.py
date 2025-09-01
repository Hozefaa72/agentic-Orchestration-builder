# import boto3
# from app.models.threads import Thread

# async def appointment_flow(thread_id: str, flow_id: str, step_id: str, language: str, user_message: str):
#     if step_id is None:
#         step_id = "1"   # start at first step
#     print("printing step_id",step_id)
#     print("printing thread_id",thread_id)
#     print("printing flow_id",flow_id)
#     print("printing user_message", user_message)
#     print("printing language", language)

#     appointmentflow = {
#         "flow_id": "book_appointment",
#         "steps": {
#             "1": {"step_id": "1", "message": "Please tell me your name.", "expected_input": "name", "action": None, "next_step": "2"},
#             "2": {"step_id": "2", "message": "Thanks {name}! Could you please share your phone number?", "expected_input": "phone_number", "action": None, "next_step": "3"},
#             "3": {"step_id": "3", "message": "We’ve sent an OTP to {phone_number}. Please enter the OTP.", "expected_input": "otp", "action": "send_otp_api", "next_step": "4"},
#             "4": {"step_id": "4", "message": "OTP verified ✅. Please share the PIN code where you’re looking for a center.", "expected_input": "pincode", "action": "verify_otp_api", "next_step": "5"},
#             "5": {"step_id": "5", "message": "Here are 3 nearby centers for PIN {pincode}: {centers_list}. Please select one.", "expected_input": "center_selection", "action": "fetch_centers_api", "next_step": "6"},
#             "6": {"step_id": "6", "message": "You selected {center}. Full address: {center_address}. Now, please select a preferred date.", "expected_input": "date", "action": None, "next_step": "7"},
#             "7": {"step_id": "7", "message": "Available time slots on {date} are: {time_slots}. Please choose one.", "expected_input": "time_slot", "action": "fetch_time_slots_api", "next_step": "8"},
#             "8": {"step_id": "8", "message": "Great! Your appointment is booked at {center} on {date} at {time_slot}. A confirmation has been sent to {phone_number}.", "expected_input": None, "action": "save_appointment_api", "next_step": None},
#         }
#     }

#     step = appointmentflow["steps"].get(step_id)
#     if not step:
#         return {"error": "Invalid step"}

#     # 🟢 Case 1: First time on this step → just ask the step message
#     if not user_message or user_message.strip() == "":
#         user_message=""

#     # 🟢 Case 2: Validate with LLM
#     prompt = f"""
# You are a step validation bot.
# Conversation language = {language}.
# We are in flow: {flow_id}, step: {step_id}.

# Step Definition:
# - Expected input: {step['expected_input']}
# - Step message: {step['message']}

# User message: "{user_message}"

# Task:
# 1. Check if user message matches the expected input type.
#    - If YES: respond in {language} with the NEXT STEP message (filling placeholders if possible).
#    - If NO: politely re-ask the SAME step in {language}, saying what is missing.
# 2. Do NOT skip steps. Only move to next_step if input is valid.
# """

#     client = boto3.client("bedrock-runtime")
#     model_id = "anthropic.claude-3-haiku-20240307-v1:0"

#     response = client.converse(
#         modelId=model_id,
#         messages=[{"role": "user", "content": [{"text": prompt}]}],
#         inferenceConfig={"maxTokens": 200, "temperature": 0.2},
#     )

#     answer = response["output"]["message"]["content"][0]["text"].strip()

#     # Decide if move forward or not (simple rule: if answer contains re-ask → stay)
#     if "please" in answer.lower() and step["expected_input"] in answer.lower():
#         # invalid input, stay on current step
#         next_step = step_id
#     else:
#         # assume valid, move forward
#         next_step = step["next_step"] or step_id

#     # update thread in DB
#     thread = await Thread.find_one(Thread.id == thread_id)
#     if thread:
#         thread.flow_id = flow_id
#         thread.step_id = next_step
#         await thread.save()

#     return answer
import re
import boto3
from app.models.threads import Thread
from app.models.user_info import User_Info
from app.core.ivf_centers import find_nearest_by_postal
from bson import ObjectId
import json


async def appointment_flow(
    thread_id: str, flow_id: str, step_id: str, language: str, user_message: str
):
   
    thread_obj_id = ObjectId(thread_id)
    thread = await Thread.find_one(Thread.id == thread_obj_id)


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

    appointmentflow = {
        "flow_id": "book_appointment",
        "steps": {
            "1": {
                "step_id": "1",
                "message": "To book appointment, please share your name ",
                "expected_input": "name",
                "valid_condition": "",
                "action": None,
                "other_text":"",
                "final_text":"",
                "next_step": "2"
            },
            "2": {
                "step_id": "2",
                "message": "Thanks. Please provide your mobile number so we can proceed with booking your appointment",
                "expected_input": "name of the person",
                "valid_condition": r"^[A-Za-z\s]{2,50}$",
                "action": "send_otp_api",
                "other_text":"Please share your name it is important for appointment booking step",
                "final_text":"",
                "next_step": "3"
            },
            "3": {
                "step_id": "3",
                "message": "Please enter the OTP sent to your mobile number for verification",
                "expected_input": "phone number",
                "valid_condition": r"^\d{10}$",
                "action": "verify_otp_api",
                "other_text":"Please enter a valid ten digit Phone Number",
                "final_text":"",
                "next_step": "4"
            },
            "4": {
                "step_id": "4",
                "message": ["Your mobile number is verified. Thank you for confirming!","Now please mention your preferred pin code to continue with the booking "],
                "expected_input": "6 digit otp",
                "valid_condition": r"^\d{6}$",
                "action": None,
                "other_text":"Oops! The OTP you entered doesn’t match. Please try again",
                "final_text":"You’ve reached the maximum OTP attempts. You can request a new OTP in 1 hour",
                "next_step": "5"
            },
            "5": {
                "step_id": "5",
                "message": "",
                "expected_input": "pincode",
                "valid_condition": r"^\d{6}$",
                "action": "fetch_centers_api",
                "other_text":["Sorry, the Pincode is invalid"," Please enter a valid pincode to check clinic availability near you"],
                "final_text":"",
                "next_step": "6",
            },
            "6": {
                "step_id": "6",
                "message": ["","Please select your preferred date from the calendar."],
                "expected_input": "center_selection",
                "valid_condition": r".+",
                "action": None,
                "other_text":"",
                "final_text":"",
                "next_step": "7",
            },
            "7": {
                "step_id": "7",
                "message": "Please pick a time slot time to book your appointment",
                "expected_input": "date",
                "valid_condition": r"^\d{4}-\d{2}-\d{2}$",
                "action": "fetch_time_slots_api",
                "other_text":"",
                "final_text":"",
                "next_step": "8",
            },
            "8": {
                "step_id": "8",
                "message": " Great! Your appointment is booked at {center} on {date} at {time_slot}. A confirmation has been sent to {phone_number}.",
                "expected_input": "time-slot",
                "valid_condition": r"^\d{2}:\d{2}",
                "action": "save_appointment_api",
                "other_text":"",
                "final_text":"",
                "next_step": None,
            },
        },
    }

    step = appointmentflow["steps"].get(step_id)
    if not step:
        return {"error": "Invalid step"}

 
    if not user_message or user_message.strip() == "":
        user_message = ""
    # msg = step["message"]
    # user = await User_Info.find_one(User_Info.thread_id == thread_id)

    # # अगर message list में है तो उसे join कर लो
    # if isinstance(msg, list):
    #     msg = " ".join(msg)

    # # name placeholder replace
    # if "{name}" in msg:
    #     if step["step_id"] == "2":  
    #         # Step 2 पर user_message ही name है
    #         msg = msg.replace("{name}", user_message)
    #     elif user and user.name:
    #         msg = msg.replace("{name}", user.name)

    # # pincode replace
    # if "{pincode}" in msg and user and getattr(user, "pincode", None):
    #     msg = msg.replace("{pincode}", user.pincode)

    # # center replace
    # if "{center}" in msg and user and getattr(user, "center", None):
    #     msg = msg.replace("{center}", user.center)

    # # date replace
    # if "{date}" in msg and user and getattr(user, "date", None):
    #     msg = msg.replace("{date}", user.date)

    # # time_slot replace
    # if "{time_slot}" in msg and user and getattr(user, "time_slot", None):
    #     msg = msg.replace("{time_slot}", user.time_slot)
  
    # print(msg)
    if step["step_id"]=="5":
        response=find_nearest_by_postal(user_message)
        if response:
            user=await User_Info.find_one(User_Info.thread_id==thread_id)
            user.preffered_center=response
            await user.save()
            next_step = step["next_step"]
            if thread:
                thread.flow_id = flow_id
                thread.step_id = next_step
                await thread.save()
            return response,"centers"
        else:
            return "Postal code not found or invalid",None
        
    if step["step_id"]=="6":
        user=await User_Info.find_one(User_Info.thread_id==thread_id)
        for c in user.preffered_center:
            if c["City"].strip().lower() == user_message.strip().lower():
                user.address=c["Address"]
                await user.save()
                step["message"][0]=c["Address"]
        if step["message"][0]=="":
            return "Please enter a valid city",None

            







   
    prompt = f"""
You are a validation assistant.
Conversation language = {language}.
Step: {step_id}, Expecting: {step['expected_input']}
the expected input can also be in user selected language also 
User input: "{user_message}"
Valid condition (regex): {step['valid_condition']}

please return the response only this {step['message']}
and if the {step['message']} is list then return that list in user language- {language}
if the user enters invalid response then the expected input then use {step['other_text']} and if it enters invalid input three times then give him {step['final_text']} and in user language

 Important: Respond ONLY in valid JSON, nothing else.
Format:
{{
  "status": "VALID" or "INVALID",
  "bot_response": "string or list of string  (next message to show the user in {language})"
}}

Rules:
- If regex + meaning are correct → status = "VALID" and bot_response = next step message (filled with variables if available).
- If not valid → status = "INVALID" and bot_response = re-ask current step politely in {language}.
"""

    client = boto3.client("bedrock-runtime")
    model_id = "anthropic.claude-3-haiku-20240307-v1:0"

    response = client.converse(
        modelId=model_id,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"maxTokens": 200, "temperature": 0},
    )

    llm_answer = response["output"]["message"]["content"][0]["text"].strip()
    print("raw llm answer:", llm_answer)



    try:
        llm_json = json.loads(llm_answer)
    except Exception:
        # fallback if model doesn't output strict JSON
        llm_json = {"status": "INVALID", "bot_response": step["message"]}

    # Final decision
    if llm_json.get("status") == "VALID":
        next_step = step["next_step"]
        print(next_step)
        if step["step_id"]=="2":
            user_info = User_Info(
            name=user_message,
            thread_id=thread_id
        )

            await user_info.insert()
        if step["step_id"]=="3":
            user=await User_Info.find_one(User_Info.thread_id==thread_id)
            user.phone_number=user_message
            await user.save()
        if step["step_id"]=="5":
            user=await User_Info.find_one(User_Info.thread_id==thread_id)
            user.pincode=user_message
            await user.save()
        if step["step_id"]=="7":
            user=await User_Info.find_one(User_Info.thread_id==thread_id)
            user.checkup_date=user_message
            await user.save()
        if step["step_id"]=="8":
            user=await User_Info.find_one(User_Info.thread_id==thread_id)
            user.checkup_time_slot=user_message
            await user.save()




        # Save thread
        if thread:
            thread.flow_id = flow_id
            thread.step_id = next_step
            await thread.save()

        # return structured JSON (with bot response filled from flow)

        if step["step_id"]=="7":
            return llm_json.get("bot_response"),"time_slots"
        elif step["step_id"]=="6":
            return llm_json.get("bot_response"),"calendar"
        else:
            return llm_json.get("bot_response"),None
    else:
        # stay on same step
        if thread and step["step_id"] == "1":
            next_step = step["next_step"]
            thread.flow_id = flow_id
            thread.step_id = next_step
            await thread.save()
        return llm_json.get("bot_response"),None
