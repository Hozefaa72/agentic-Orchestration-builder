from fastapi import WebSocket, WebSocketDisconnect, APIRouter
import json
from app.cruds.v2.threads_cruds import get_thread_by_name
from app.core.v2.websocket_init import WebSocketManager
from fastapi import Query
from app.auth.jwt_handler import decode_jwt
import json
from bson import ObjectId
from app.models.v2.threads import Thread


router = APIRouter()
websocket_manager = WebSocketManager()

@router.websocket("/ws")
async def websocket_chat(websocket: WebSocket, token: str = Query(...)):
    await websocket.accept()
    try:
        token = token.split(" ")[1]
        current_user = decode_jwt(token)
    except Exception as e:
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
                thread_id = data.get("thread_id")
                print("the thread id in websocket is", thread_id)
                thread_obj_id = ObjectId(thread_id)
                thread = await Thread.find_one(Thread.id == thread_obj_id)
                language = thread.language
                print("the sellected language is", language)
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

                thread_name = await get_thread_by_name(thread_id)

            elif data.get("type") == "update-thread":
                await websocket_manager.broadcast_to_all_sessions(
                    user_id, "New thread created or updated!"
                )

            elif data.get("type") == "login_success":
                print("Login successful:", data.get("message"))

    except WebSocketDisconnect:
        websocket_manager.disconnect(user_id, session_id)
        print(f"User {user_id} disconnected.")
