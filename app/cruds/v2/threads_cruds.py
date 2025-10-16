from fastapi import HTTPException
from app.models.v2.threads import Thread
from app.models.v2.message import Message
from bson import ObjectId


async def get_thread_by_name(thread_id: str):
    try:
        thread = await Thread.find_one(Thread.id == ObjectId(thread_id))
        if thread:
            print("thread_found")
            return thread.thread_name

        return None
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Internal error while fetching thread name"
        )


async def update_thread_name(thread_id: str, name: str) -> bool:
    try:
        thread = await Thread.find_one(Thread.id == ObjectId(thread_id))
        if thread:
            thread.thread_name = name
            await thread.save()
            return True
        return False
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Internal error while updating thread name"
        )


async def delete_thread(thread_id: str):
    try:
        thread = await Thread.find_one(Thread.id == ObjectId(thread_id))
        if thread:
            await Message.find(Message.thread_id == thread_id).delete()
            await thread.delete()
            return {"message": "Thread and its messages deleted successfully"}

        return {"message": "Thread not found"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Internal error while deleting thread"
        )


async def update_thread_name_later(manager, thread_id, messages):
    chat_name = await manager.get_thread_name(messages)
    await update_thread_name(thread_id, chat_name)
