from app.models.threads import Thread
from bson import ObjectId
from app.core.boto3client import bot_generate
import json
from app.models.user_info import User_Info, AppointmentStatus


async def cancelRescheduleFlow(
    thread_id: str, language: str,user_message:str
):
   
    thread_obj_id = ObjectId(thread_id)
    thread = await Thread.find_one(Thread.id == thread_obj_id)
    booked_user = await User_Info.find_one(User_Info.thread_id == thread_id)
    if booked_user and (booked_user.appointment_status != AppointmentStatus.BOOKED or booked_user.appointment_status != AppointmentStatus.CANCELLED or booked_user.appointment_status!=AppointmentStatus.RESCHEDULED):
        print("appointment not booked yet")
        booked_message = "Your appointment is not booked yet",
        return booked_message,"book_appointment"

    if not booked_user:
        return "Hope this helps! You can come back anytime to explore  or get more info",None
    cancel_messages = [{"first_text":"To cancel your appointment, please contact our call center between 9 AM and 6 PM.","second_text":"CUSTOMER CARE NUMBER","phone_number":"1800 3092429"},
        "Hope this helps! You can come back anytime to explore  or get more info"
    ]
    resechdule_messages = [{"first_text":"To reschedule your appointment, please contact our call center between 9 AM and 6 PM.","second_text":"CUSTOMER CARE NUMBER","phone_number":"1800 3092429"},
        "Hope this helps! You can come back anytime to explore  or get more info"
    ]

    prompt=f"""You are a helpful assistant. 

Your task is:
1. Determine if the user wants to cancel or reschedule an appointment based on their message.
2. Respond **only** with messages corresponding to that intent, translated into the user's language ({language}).
3. Include the first and second texts in the dictionary as translated as well.
4. Return the intent type as either "cancel" or "reschedule".

Guidelines:
- Do NOT return messages for the other intent.
--same structure as message
- Return strictly as a JSON object with two fields:
    {{
        "type": "<cancel or reschedule>",
        "messages": [dict,<translated_message>]
    }}

User message: "{user_message}"
Cancel messages dictionary: {cancel_messages}
Reschedule messages dictionary: {resechdule_messages} """
    response= await bot_generate(prompt,500)
    # thread.flow_id=None
    # thread.step_id=None
    # await thread.save()
    try:
        answer = json.loads(response)  # will give list
    except:
        answer = [response] 

    if answer['type'] == 'cancel':
        thread.flow_id = "book_appointment"
        thread.step_id = None
        await thread.save()
        user = await User_Info.find_one(User_Info.thread_id == thread_id)
        user.appointment_status = AppointmentStatus.CANCELLED
        await user.save()
    else:
        thread.flow_id = 'book_appointment'
        thread.step_id = None
        await thread.save()
        user = await User_Info.find_one(User_Info.thread_id == thread_id)
        user.appointment_status = AppointmentStatus.RESCHEDULED
        await user.save()
    print("cancel or reschrdule answer ",answer)
    return answer['messages'],"out_of_context"



