from fastapi import HTTPException
from app.models.v2.message import Message
from app.models.v2.message import Feedack
from app.schemas.v2.message_schemas import MessageCreate


async def create_message(msg:MessageCreate,thread_id:str,feedback:Feedack=None):
    try:
        message = Message(
            content=msg.content,
            sender=msg.sender,
            thread_id=thread_id,
            feedback=feedback.value,
        )

        await message.insert()
        return message
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Internal server error while creating message"
        )


async def get_all_messages(thread_id: str):
    try:
        if not thread_id or not isinstance(thread_id, str):
            raise HTTPException(status_code=422, detail="Invalid thread ID")
        message_objs = (
            await Message.find(Message.thread_id == thread_id)
            .sort(Message.timestamp)
            .to_list()
        )
        formatted_messages = [
            {"sender": msg.sender, "content": msg.content} for msg in message_objs
        ]
        return formatted_messages
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Internal server error while fetching messages"
        )


async def get_user_last_message(thread_id):
    message = (
        await Message.find(Message.thread_id == thread_id, Message.sender == "user")
        .sort("-timestamp")
        .first_or_none()
    )
    if message is None:
        return "No message yet"
    return message.content
