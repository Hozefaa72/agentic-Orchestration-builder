import asyncio
from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from backend.app.core.assistant import manager
import json
import logging
from backend.app.cruds.message_cruds import create_message,get_all_messages
from backend.app.cruds.threads_cruds import update_thread_name,get_thread_by_name
from backend.app.core.websocket_init import WebSocketManager
from backend.app.core.appointmentflow import appointment_flow
from backend.app.core.end_flow import end_flow
from backend.app.core.flow_classifier import flow_check
from fastapi import Query
from backend.app.auth.jwt_handler import decode_jwt
import json
import time
from bson import ObjectId
from backend.app.models.threads import Thread

# os.environ["OPENAI_API_KEY"] = Settings().OPENAI_API_KEY
# faq= Settings().FAQ_FILE_ID
# clinic= Settings().CENTER_FILE_ID
# need = Settings().NEED_FILE_ID
# client = OpenAI(
#     api_key=Settings().OPENAI_API_KEY,
#     default_headers={"OpenAI-Beta": "assistants=v2"}
# )
# manager = IVFChatbot(client,faq,clinic,need)
assistant_router = APIRouter()
websocket_manager = WebSocketManager()
logger = logging.getLogger(__name__)

#####maincode####
# @assistant_router.websocket("/ws")
# async def websocket_chat(websocket: WebSocket, token: str = Query(...)):
#     print(f"🟡 Incoming WebSocket request with token: {token}")
#     await websocket.accept()

#     try:
#         current_user = decode_jwt(token)
#         print("✅ Authenticated User:", current_user)
#     except Exception as e:
#         print("❌ JWT decode failed:", str(e))
#         await websocket.close(code=1008)
#         return

#     if not current_user:
#         await websocket.close(code=1008)
#         return

#     user_id = current_user["user_id"]
#     session_id = current_user["session_id"]
#     active_connection = {
#         "user_id": user_id,
#         "session_id": session_id,
#         "thread_id": None,
#     }

#     try:
#         while True:
#             raw_data = await websocket.receive_text()
#             data = json.loads(raw_data)
#             print("📩 Received data:", data)

#             if data.get("type") == "init":
#                 new_thread_id = data.get("thread_id")
#                 if active_connection["thread_id"] != new_thread_id:
#                     active_connection["thread_id"] = new_thread_id
#                     # No need to call `connect` again since the WebSocket is already accepted.
#                     print(f"🔁 Switched to thread_id: {new_thread_id}")
#                 if data.get("welcome") == "faq":
#                     welcome_text = "Hi there! 👋 I’m Indira BOT, your personal assistant. I'm here to guide you through the most commonly asked questions and help you find quick, clear answers. If you need more help, I’m always just a message away!"
#                 elif data.get("welcome") == "nearby":
#                     welcome_text = "Hi there! 👋 I’m Indira BOT, your personal assistant. The Nearby Centers feature helps you quickly find the nearest service or support centers based on your location. Whether you're looking for assistance, appointments, or information — I’ve got you covered!"
#                     await websocket.send_text(
#                         json.dumps(
#                             {
#                                 "type": "init",
#                                 "text": welcome_text,
#                                 "isLocationPrompt": True,
#                             }
#                         )
#                     )
#                     continue
#                 elif data.get("welcome") == "need":
#                     print("need")
#                     welcome_text = "Hi there! 👋 I’m Indira BOT, your personal assistant. The Need Generation feature helps identify and understand your specific requirements — whether it's a service, support, or information you’re looking for. Just tell me what you need, and I’ll guide you to the right solution!"
#                     await websocket.send_text(
#                         json.dumps({"type": "init", "text": welcome_text})
#                     )
#                     continue
#                 else:
#                     welcome_text = "👋 Hi there! I’m Indira BOT — your personal assistant. How can I help you today?"
#                 # Save to DB (optional)
#                 # await create_message(content=welcome_text, sender="assistant", thread_id=thread_id)

#                 # Send welcome message to client
#                 await websocket.send_text(
#                     json.dumps({"type": "message", "text": welcome_text})
#                 )
#                 continue

#             elif data.get("type") == "message":
#                 print("in message")
#                 content = data.get("message")
#                 thread_id = active_connection["thread_id"]

#                 if not thread_id:
#                     await websocket.send_text(
#                         json.dumps(
#                             {
#                                 "type": "error",
#                                 "text": "❗ Please select or create a thread before sending messages.",
#                             }
#                         )
#                     )
#                     continue

#                 # Ensure assistant is initialized
#                 if not manager.assistant:
#                     await manager.initialize_assistant()  # Call async method here

#                 # Save user message
#                 await create_message(
#                     content=content, sender="user", thread_id=thread_id
#                 )

#                 # Fetch all messages in the thread
#                 messages = await get_all_messages(thread_id)

#                 # Get assistant response directly
#                 response = await manager.get_response(content, messages)
#                 print("Printing Response in router", response)

#                 print("Printing Response")
#                 await create_message(
#                     content=response, sender="assistant", thread_id=thread_id
#                 )
#                 print(thread_id)
#                 thread_name = await get_thread_by_name(thread_id)
#                 print(thread_name)
#                 if thread_name == "New Chat":
#                     chat_name = await manager.get_thread_name(messages)
#                     await update_thread_name(thread_id, chat_name)
#                     print(chat_name)
#                 response = {"type": "message", "text": response}
#                 # Send assistant's response via WebSocket
#                 await websocket.send_text(json.dumps(response))

#             elif data.get("type") == "update-thread":
#                 await websocket_manager.broadcast_to_all_sessions(
#                     user_id, "🆕 New thread created or updated!"
#                 )
#                 continue

#             elif data.get("type") == "login_success":
#                 print("🔐 Login successful:", data.get("message"))


#     except WebSocketDisconnect:
#         if active_connection["thread_id"]:
#             websocket_manager.disconnect(session_id)
#         print(f"🔌 User {user_id} disconnected.")
@assistant_router.websocket("/ws")
async def websocket_chat(websocket: WebSocket, token: str = Query(...)):
    logger.info(f"\U0001F7E1 Incoming WebSocket request with token: {token}")
    await websocket.accept()

    try:
        current_user = decode_jwt(token)
        logger.info(f"\u2705 Authenticated User: {current_user}")
    except Exception as e:
        logger.warning(f"\u274C JWT decode failed: {e}")
        await websocket.close(code=1008)
        return

    if not current_user:
        await websocket.close(code=1008)
        return

    user_id = current_user["user_id"]
    session_id = current_user["session_id"]
    active_connection = {
        "user_id": user_id,
        "session_id": session_id,
        "thread_id": None,
    }

    await websocket_manager.connect(user_id, session_id, websocket)

    try:
        while True:
            raw_data = await websocket.receive_text()
            data = json.loads(raw_data)

            if data.get("type") == "init":
                new_thread_id = data.get("thread_id")
                if active_connection["thread_id"] == new_thread_id:
                    continue
                if active_connection["thread_id"] != new_thread_id:
                    active_connection["thread_id"] = new_thread_id
                    websocket_manager.set_thread(user_id, session_id, new_thread_id)

                # Send appropriate welcome message based on context
                welcome_type = data.get("welcome")
                if welcome_type == "faq":
                    welcome_text = "Hi there! 👋 I’m Indira BOT, your personal assistant. I'm here to guide you through the most commonly asked questions and help you find quick, clear answers. If you need more help, I’m always just a message away!"
                elif welcome_type == "nearby":
                    welcome_text = "Hi there! 👋 I’m Indira BOT. The Nearby Centers feature helps you quickly find the nearest service or support centers based on your location."
                    await websocket.send_text(
                        json.dumps(
                            {
                                "type": "init",
                                "text": welcome_text,
                                "isLocationPrompt": True,
                            }
                        )
                    )
                    continue
                elif welcome_type == "appointment":
                    welcome_text = "Hello! 👋 Welcome! To book your appointment, please select your location first."
                    await websocket.send_text(
                        json.dumps(
                            {
                                "type": "init",
                                "text": welcome_text,
                                "isLocationPrompt": True,
                            }
                        )
                    )
                    continue
                elif welcome_type == "need":
                    welcome_text = "Hi there! 👋 I’m Indira BOT. The Need Generation feature helps identify and understand your specific requirements — just tell me what you need!"
                else:
                    welcome_text = "👋 Hi there! I’m Indira BOT — your personal assistant. How can I help you today?"

                await websocket.send_text(
                    json.dumps({"type": "message", "text": welcome_text})
                )
                continue

            elif data.get("type") == "message":
                content = data.get("message")
                # thread_id = active_connection["thread_id"]
                thread_id=data.get("thread_id")
                thread_obj_id = ObjectId(thread_id)
                thread = await Thread.find_one(Thread.id == thread_obj_id)
                flow_id=thread.flow_id
                step_id=thread.step_id
                language=thread.language
                print(thread)
                if data.get("isflow") =="confirm":
                    print("in confirm")
                    thread.flow_id=data.get("subtype")
                    await thread.save()
                    flow_id=data.get("subtype")
                    step_id=None
                elif data.get("isflow")=="end_flow" and data.get("subtype") =="end_flow":
                    response=await end_flow(thread_id,language)
                    flow_id=None
                    await websocket.send_text(
                        json.dumps({"type": "message", "text": response,"contentType":"end_flow"})
                    )
                else:
                    print("in flow check")
                    llm_flow_id=await flow_check(content)
                    if llm_flow_id != "None":
                        if llm_flow_id != flow_id:
                            thread.flow_id=llm_flow_id
                            thread.step_id=None
                            flow_id=llm_flow_id
                            step_id=None
                            await thread.save()


                            
                # if data.get("subtype") == "appointment":
                #     print("in appointment")
                #     response="To book appointment, please share your name "
                #     await websocket.send_text(
                #     json.dumps({"type": "message", "text": response})
                # )
                # print(thread_id)
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

                # Ensure assistant is ready
                if not manager.assistant:
                    await manager.initialize_assistant()
                # user = get_user_by_id(user_id)

                if data.get("subtype") == "book_appointment" or flow_id=="book_appointment":
                    print("in book appointment")
                    response,contentType=await appointment_flow(thread_id,flow_id,step_id,language,content)
                    if isinstance(response, list) and contentType == "calendar":
                        await websocket.send_text(
                            json.dumps({
                                "type": "message",
                                "text": response[0],
                                "contentType": None
                            })
                        )
                        await asyncio.sleep(1)
                        await websocket.send_text(
                            json.dumps({
                                "type": "message",
                                "text": response[1],
                                "contentType": contentType
                            })
                        )

                    elif isinstance(response, list) and contentType != "centers":
                        for message in response:
                            await websocket.send_text(
                                json.dumps({
                                    "type": "message",
                                    "text": message,
                                    "contentType": contentType
                                })
                            )
                            await asyncio.sleep(1)
                    else:
                        # handle single response or centers separately if needed
                        await websocket.send_text(
                            json.dumps({
                                "type": "message",
                                "text": response,
                                "contentType": contentType
                            })
                        )
                if data.get("subtype") == "ivf_success_calculator" or flow_id =="ivf_success_calculator":
                    msg1 = "Yes, Sure. We have devised an IVF Success Calculator which gives success rate based on historical data of Indira IVF."
                    msg2 = """This is how our IVF Success Calculator works.\n
                              1 Share details and reports\n
                              2 We analyze key fertility factors\n
                              3 Know success rate for each cycle"""

                    # First message
                    await websocket.send_text(
                        json.dumps({"type": "message", "text": msg1})
                    )

                    # Small delay if you want them to appear one after the other
                    await asyncio.sleep(1)

                    # Second message
                    await websocket.send_text(
                        json.dumps({"type": "message", "text": msg2,"contentType": "ivf_calculate"})
                    )

                    # For appointment: get only address without polluting main thread
                    # response_task = asyncio.create_task(
                    #     manager.get_nearby_center_address_only(content)
                    # )
                    # response = await response_task

                    # Only create a mini-message for user reference
                    # await create_message(
                    #     content=content, sender="user", thread_id=thread_id
                    # )
                    # await create_message(
                    #     content=response, sender="assistant", thread_id=thread_id
                    # )
                    # messages = await get_all_messages(thread_id)

                # else:

                #     # Normal user flow
                #     await create_message(
                #         content=content, sender="user", thread_id=thread_id
                #     )
                #     messages = await get_all_messages(thread_id)
                #     print("printing the subtypes ",data.get("subtype"))
                #     response_task = asyncio.create_task(
                #         manager.get_response(content, messages,data.get("subtype"))
                #     )
                #     response = await response_task

                #     await create_message(
                #         content=response, sender="assistant", thread_id=thread_id
                #     )

                # Auto-rename thread if it's "New Chat"
                thread_name = await get_thread_by_name(thread_id)
                if thread_name == "New Chat":
                    if data.get("subtype")=="appointment":
                        chat_name="Booking an Appointment"
                    elif data.get("subtype")=="clinic":
                        chat_name="Finding Near By Center"
                    else:
                        chat_name="General Enquiry"
                    # chat_name = asyncio.create_task(manager.get_thread_name(messages))
                    # chat_name = await chat_name
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
        websocket_manager.disconnect(
            user_id, session_id
        )
        print(f"User {user_id} disconnected.")
