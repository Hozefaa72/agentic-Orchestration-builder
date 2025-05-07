from fastapi import APIRouter, HTTPException, Depends
from backend.app.database.curds import create_message, get_all_messages
from backend.app.modules.auth import get_current_user
from pydantic import BaseModel
from typing import Union, List


class MessageCreate(BaseModel):
    content: Union[str, List[str]]
    sender: str


router = APIRouter()


@router.get("/get_all_messages/")
async def get_all_messages_route(current_user: dict = Depends(get_current_user)):
    try:
        thread_id = current_user["thread_id"]

        messages = await get_all_messages(thread_id)
        return {"messages": messages}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/messages/")
async def post_message(
    msg: MessageCreate, current_user: dict = Depends(get_current_user)
):
    try:

        user_id = current_user["thread_id"]

        message = await create_message(
            content=msg.content, sender=msg.sender, thread_id=user_id
        )

        return {"message": "Message created successfully", "data": message}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
