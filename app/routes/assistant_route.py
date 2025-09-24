import asyncio
from fastapi import WebSocket, WebSocketDisconnect, APIRouter
import json
import logging

# from app.cruds.message_cruds import create_message,get_all_messages
from app.cruds.threads_cruds import update_thread_name, get_thread_by_name
from app.core.websocket_init import WebSocketManager
from app.core.appointmentflow import appointment_flow
from app.core.ivf_calculation_flow import ivf_success_calculation_flow
from app.core.end_flow import end_flow
from app.core.flow_classifier import flow_check
from fastapi import Query
from app.auth.jwt_handler import decode_jwt
import json
from app.core.lifestyleandpreparations import lifestyleAndPreparations
from bson import ObjectId
from app.models.threads import Thread
from app.core.loan_and_emi_options import loan_emi_option
from app.core.emergencyContact import EmergencyContact
from app.core.ivfSuccessRate import IVFSuccessRate
from app.core.consent_flow import ConsentFlow
from app.core.ivf_steps import ivfSteps
from app.core.ivf_packages import ivfPackages
from app.core.emotionalSupport import EmotionalSupport
from app.core.medicalTerms import MedicalTerms
from app.core.cancelReschedule import cancelRescheduleFlow
from app.core.greetings import greetingsFlow

router = APIRouter()
websocket_manager = WebSocketManager()
logger = logging.getLogger(__name__)


@router.websocket("/ws")
async def websocket_chat(websocket: WebSocket, token: str = Query(...)):
    logger.info(f"\U0001f7e1 Incoming WebSocket request with token: {token}")
    await websocket.accept()

    try:
        token = token.split(" ")[1]
        current_user = decode_jwt(token)
        logger.info(f"\u2705 Authenticated User: {current_user}")
    except Exception as e:
        logger.warning(f"\u274c JWT decode failed: {e}")
        await websocket.close(code=1008)
        return

    if not current_user:
        await websocket.close(code=1008)
        return

    user_id = current_user["user_id"]
    session_id = current_user["session_id"]

    await websocket_manager.connect(user_id, session_id, websocket)

    try:
        while True:
            raw_data = await websocket.receive_text()
            data = json.loads(raw_data)

            if data.get("type") == "message":
                content = data.get("message")
                # thread_id = active_connection["thread_id"]
                thread_id = data.get("thread_id")
                print("the thread id in websocket is", thread_id)
                thread_obj_id = ObjectId(thread_id)
                thread = await Thread.find_one(Thread.id == thread_obj_id)
                flow_id = thread.flow_id
                step_id = thread.step_id
                language = thread.language
                print("the sellected language is", language)
                print(thread)
                if data.get("isflow") == "confirm":
                    print("in confirm")
                    thread.flow_id = data.get("subtype")
                    await thread.save()
                    flow_id = data.get("subtype")
                    step_id = None
                else:
                    print("in flow check")
                    llm_flow_id = await flow_check(content)
                    if llm_flow_id != "None":
                        if llm_flow_id != flow_id:
                            thread.flow_id = llm_flow_id
                            thread.step_id = None
                            flow_id = llm_flow_id
                            step_id = None
                            await thread.save()
                    else:
                        response = await end_flow(thread_id, language,False)
                        for i in range(len(response)):
                            print(response[i])
                            await websocket.send_text(
                                json.dumps(
                                    {
                                        "type": "message",
                                        "text": response[i],
                                        "contentType": "out_of_context" if i == 1 else None,
                                    }
                                )
                            )


                if not thread_id:
                    await websocket.send_text(
                        json.dumps(
                            {
                                "type": "error",
                                "text": "Please initialize a thread before sending messages.",
                            }
                        )
                    )
                    continue

                if (
                    data.get("subtype") == "book_appointment"
                    or flow_id == "book_appointment"
                ):
                    print("in book appointment")
                    response, contentType = await appointment_flow(
                        thread_id, flow_id, step_id, language, content
                    )
                    if isinstance(response, list) and contentType == "calendar":
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "message",
                                    "text": response[0],
                                    "contentType": None,
                                }
                            )
                        )
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "message",
                                    "text": response[1],
                                    "contentType": contentType,
                                }
                            )
                        )
                    elif isinstance(response, list) and contentType == "booked":
                        for i, item in enumerate(response):
                            await websocket.send_text(
                                json.dumps(
                                    {
                                        "type": "message",
                                        "text": item,
                                        "contentType": contentType if i == 0 else None,
                                    }
                                )
                            )
                    elif isinstance(response, list) and contentType == "out_of_context":
                        for i, item in enumerate(response):
                            await websocket.send_text(
                                json.dumps(
                                    {
                                        "type": "message",
                                        "text": item,
                                        "contentType": "out_of_context" if i == 0 else None,
                                    }
                                )
                            )
                    elif isinstance(response, list) and contentType != "centers":
                        for message in response:
                            await websocket.send_text(
                                json.dumps(
                                    {
                                        "type": "message",
                                        "text": message,
                                        "contentType": contentType,
                                    }
                                )
                            )
                    else:
                        # handle single response or centers separately if needed
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "message",
                                    "text": response,
                                    "contentType": contentType,
                                }
                            )
                        )
                elif (
                    data.get("subtype") == "ivf_success_calculator"
                    or flow_id == "ivf_success_calculator"
                ):
                    response = await ivf_success_calculation_flow(language)
                    message = response
                    # # First message
                    print(response[0])
                    await websocket.send_text(
                        json.dumps({"type": "message", "text": message[0]})
                    )
                    # Small delay if you want them to appear one after the other
                    print(response[1])
                    # Second message
                    await websocket.send_text(
                        json.dumps(
                            {
                                "type": "message",
                                "text": message[1],
                                "contentType": "ivf_calculate",
                            }
                        )
                    )
                elif (data.get("subtype") == "Lifestyle_and_Preparations") or (
                    flow_id == "Lifestyle_and_Preparations"
                ):
                    response = await lifestyleAndPreparations(language)
                    await websocket.send_text(
                        json.dumps(
                            {
                                "type": "message",
                                "text": response[0],
                                "contentType": "Lifestyle_and_Preparations",
                            }
                        )
                    )
                    await websocket.send_text(
                        json.dumps(
                            {
                                "type": "message",
                                "text": response[1],
                                "contentType": None,
                            }
                        )
                    )
                    await websocket.send_text(
                        json.dumps(
                            {
                                "type": "message",
                                "text": response[2],
                                "contentType": "book_appointment",
                            }
                        )
                    )
                elif (data.get("subtype") == "loan_and_emi") or (
                    flow_id == "loan_and_emi"
                ):
                    response = await loan_emi_option(content, language)
                    for i in range(len(response)):
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "message",
                                    "text": response[i],
                                    "contentType": "loan_and_emi" if i == 2 else None,
                                }
                            )
                        )
                elif (data.get("subtype") == "emergency_contact") or (
                    flow_id == "emergency_contact"
                ):
                    response = await EmergencyContact(content, language)
                    for i in range(len(response)):
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "message",
                                    "text": response[i],
                                    "contentType": "emergency_contact",
                                }
                            )
                        )
                elif (data.get("subtype") == "success_rate") or (
                    flow_id == "success_rate"
                ):
                    response = await IVFSuccessRate(content, language)
                    if len(response) == 2:
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "message",
                                    "text": response[0],
                                    "contentType": "success_rate",
                                }
                            )
                        )
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "message",
                                    "text": response[1],
                                    "contentType": "ivf_calculate",
                                }
                            )
                        )
                    else:
                        for i in response:
                            await websocket.send_text(
                                json.dumps(
                                    {"type": "message", "text": i, "contentType": None}
                                )
                            )
                elif (data.get("subtype")=="ivf_steps" or flow_id=="ivf_steps"):
                    response,contentType = await ivfSteps(thread_id, flow_id, step_id, language, content)
                    if isinstance(response, list) and contentType=="ivf_steps":
                        print("i'm in if condition of ivf_steps")
                        for i in range(len(response)):
                            await websocket.send_text(
                            json.dumps(
                                {"type": "message", "text": response[i], "contentType": "ivf_steps" if i == 2 else None}
                            )
                            )
                    elif isinstance(response,list):
                        for i in response:
                            await websocket.send_text(
                            json.dumps(
                                {"type": "message", "text": i, "contentType": None}
                            )
                            )

                    else:
                        await websocket.send_text(
                            json.dumps(
                                {"type": "message", "text": response, "contentType": None}
                            )
                            )
                elif (data.get("subtype")=="cost_and_package" or flow_id=="cost_and_package"):
                    response,contentType = await ivfPackages(thread_id, flow_id, step_id, language, content)
                    if isinstance(response, list) and contentType=="cost_and_package":
                        print("i'm in if condition of ivf_costs")
                        for i in range(len(response)):
                            if i == 1:
                                content_type = "cost_and_package"
                            elif i == 2:
                                content_type = "book_appointment"
                            else:
                                content_type = None

                            await websocket.send_text(
                                json.dumps(
                                    {
                                        "type": "message",
                                        "text": response[i],
                                        "contentType": content_type
                                    }
                                )
                            )
                    elif isinstance(response,list):
                        for i in response:
                            await websocket.send_text(
                            json.dumps(
                                {"type": "message", "text": i, "contentType": None}
                            )
                            )

                    else:
                        await websocket.send_text(
                            json.dumps(
                                {"type": "message", "text": response, "contentType": None}
                            )
                            )
                elif (data.get("subtype") == "emotional_support") or (
                    flow_id == "emotional_support"
                ):
                    response = await EmotionalSupport(content, language)
                    for i in range(len(response)):
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "message",
                                    "text": response[i],
                                    "contentType": None,
                                }
                            )
                        )
                elif (data.get("subtype") == "out_of_context") or (
                    flow_id == "out_of_context"
                ):
                    response = await end_flow(thread_id, language)
                    for i in range(len(response)):
                        print(response[i])
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "message",
                                    "text": response[i],
                                    "contentType": "out_of_context" if i == 1 else None,
                                }
                            )
                        )
                elif (data.get("subtype") == "cancel_or_reschedule") or (
                    flow_id == "cancel_or_reschedule"
                ):
                    response,contentType = await cancelRescheduleFlow(thread_id, language,content)
                    if contentType=="out_of_context":
                        for i in range(len(response)):
                            print(response[i])
                            await websocket.send_text(
                                json.dumps(
                                    {
                                        "type": "message",
                                        "text": response[i],
                                        "contentType": "out_of_context" if i == 0 else None,
                                    }
                                )
                            )
                    else:
                        await websocket.send_text(
                                json.dumps(
                                    {
                                        "type": "message",
                                        "text": response,
                                        "contentType": contentType,
                                    }
                                )
                            )

                elif (
                    data.get("subtype") == "medical_terms"
                    or flow_id == "medical_terms"
                ):
                    response = await MedicalTerms(content,language)
                    if isinstance(response, list):
                        for i in response:
                            await websocket.send_text(
                                json.dumps(
                                    {"type": "message", "text": i, "contentType": None}
                                )
                            )
                    else:
                        await websocket.send_text(
                            json.dumps(
                                {"type": "message", "text": response, "contentType": None}
                            )
                        )
                elif (
                    data.get("subtype") == "greetings"
                    or flow_id == "greetings"
                ):
                    response = await greetingsFlow(content,language)
                    if isinstance(response, list):
                        for i in response:
                            await websocket.send_text(
                                json.dumps(
                                    {"type": "message", "text": i, "contentType": "greetings"}
                                )
                            )
                    else:
                        await websocket.send_text(
                            json.dumps(
                                {"type": "message", "text": response, "contentType": "greetings"}
                            )
                        )
                
                elif (data.get("subtype") == "legal_consent") or (
                    flow_id == "legal_consent"
                ):
                    response, contentType = await ConsentFlow(
                        thread_id, flow_id, step_id, language, content
                    )
                    if isinstance(response, list) and contentType == "out_of_context":
                        for i in range(len(response)):
                            print(response[i])
                            await websocket.send_text(
                                json.dumps(
                                    {
                                        "type": "message",
                                        "text": response[i],
                                        "contentType": (
                                            "out_of_context" if i == 0 else None
                                        ),
                                    }
                                )
                            )
                    elif isinstance(response, list):
                        for i in response:
                            await websocket.send_text(
                                json.dumps(
                                    {"type": "message", "text": i, "contentType": None}
                                )
                            )
                    else:
                        # handle single response or centers separately if needed
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "message",
                                    "text": response,
                                    "contentType": contentType,
                                }
                            )
                        )
                else:
                    continue

                thread_name = await get_thread_by_name(thread_id)
                if thread_name == "New Chat":
                    if data.get("subtype") == "appointment":
                        chat_name = "Booking an Appointment"
                    elif data.get("subtype") == "clinic":
                        chat_name = "Finding Near By Center"
                    else:
                        chat_name = "General Enquiry"
                    await update_thread_name(thread_id, chat_name)
                # await websocket.send_text(
                #         json.dumps({"type": "message", "text": response})
                #     )

            elif data.get("type") == "update-thread":
                await websocket_manager.broadcast_to_all_sessions(
                    user_id, "New thread created or updated!"
                )

            elif data.get("type") == "login_success":
                print("Login successful:", data.get("message"))

    except WebSocketDisconnect:
        websocket_manager.disconnect(user_id, session_id)
        print(f"User {user_id} disconnected.")
