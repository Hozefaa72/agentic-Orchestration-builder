from fastapi import APIRouter, HTTPException, Depends
from backend.app.models.threads import Thread
from datetime import datetime
from pydantic import BaseModel
from backend.app.modules.auth import get_current_user
from backend.app.modules.jwt_handler import update_jwt
from backend.app.database.curds import delete_thread, update_thread_name

chat_router = APIRouter()


class ThreadEditRequest(BaseModel):
    name: str
    thread_id: str


@chat_router.delete("/delete_thread")
async def delete_threadd(
    thread_id: str, current_user: dict = Depends(get_current_user)
):
    print("thread_id", thread_id)
    respone = await delete_thread(thread_id)
    return {"response": respone}


@chat_router.post("/edit_name")
async def edit_name(
    request: ThreadEditRequest, current_user: dict = Depends(get_current_user)
):
    if not request.thread_id:
        raise HTTPException(status_code=400, detail="Thread ID is missing or invalid")
    print("going for response", request.name)
    response = await update_thread_name(request.thread_id, request.name)
    if response:
        return {"response": "Name edited Successfully"}
    raise HTTPException(status_code=400, detail="Name not edited")


@chat_router.get("/get_threads")
async def get_user_threads(current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("user_id")
    print("get user", current_user)
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID is missing or invalid")

    threads = (
        await Thread.find(Thread.user_id == user_id).sort(-Thread.timestamp).to_list()
    )
    return {"threads": threads}


@chat_router.get("/create_threads")
async def create_thread(current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("user_id")
    session_id = current_user.get("session_id")
    print(current_user)
    print(user_id)
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID is missing or invalid")

    new_thread = Thread(
        user_id=user_id, thread_name="New Chat", timestamp=datetime.utcnow()
    )
    token = update_jwt(user_id, str(new_thread.id), session_id)

    await new_thread.save()

    return {"thread": new_thread, "token": token}


@chat_router.get("/select_threads")
async def select_thread(thread_id: str, current_user: dict = Depends(get_current_user)):

    user_id = current_user.get("user_id")
    session_id = current_user.get("session_id")
    print(current_user)
    print(user_id)
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID is missing or invalid")

    token = update_jwt(user_id, thread_id, session_id)

    return {"msg": token}
