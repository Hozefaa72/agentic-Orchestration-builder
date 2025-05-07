from backend.app.models.users import User
from beanie.exceptions import DocumentNotFound
from beanie import PydanticObjectId
from passlib.context import CryptContext
from typing import Optional, Union, List
from backend.app.models.message import Message
from datetime import datetime
from backend.app.models.threads import Thread
from bson import ObjectId

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def hash_password(password: str) -> str:
    return pwd_context.hash(password)


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def create_user(user_data) -> User:

    password_hash = await hash_password(user_data.password)

    user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=password_hash,
        signup_platform="web",
    )

    await user.insert()
    return user


async def get_user_by_email(email: str) -> Optional[User]:
    try:
        user = await User.find_one(User.email == email)
        return user
    except DocumentNotFound:
        return None


async def get_user_by_id(user_id: str) -> Optional[User]:
    try:
        user_obj_id = ObjectId(user_id)
        user = await User.find_one(User.email == user_obj_id)
        return user
    except DocumentNotFound:
        return None


async def verify_user_password(user: User, password: str) -> bool:
    return await verify_password(password, user.password_hash)


async def create_message(
    content: Union[str, List[str]],
    sender: str,
    thread_id: str,
) -> Message:
    message = Message(
        content=content,
        role=sender,
        sender=sender,
        thread_id=thread_id,
        timestamp=datetime.utcnow(),
        feedback=-1,
    )

    await message.insert()
    return message


async def get_all_messages(thread_id: str) -> List:
    message_objs = (
        await Message.find(Message.thread_id == thread_id)
        .sort(Message.timestamp)
        .to_list()
    )

    formatted_messages = [
        {"role": msg.sender, "content": msg.content} for msg in message_objs
    ]

    return formatted_messages


async def get_thread_by_name(thread_id: str):
    try:
        thread_obj_id = ObjectId(thread_id)
    except Exception as e:
        print(f"Invalid ObjectId: {e}")
        return None

    thread = await Thread.find_one(Thread.id == thread_obj_id)

    if thread:
        print("thread_found")
        return thread.thread_name

    return None


async def update_thread_name(thread_id: str, name: str) -> bool:
    try:
        thread_obj_id = ObjectId(thread_id)
        thread = await Thread.find_one(Thread.id == thread_obj_id)

        if thread:
            thread.thread_name = name
            await thread.save()
            return True

        return False
    except Exception as e:
        print(f"Error updating thread name: {e}")
        return False


async def get_user_last_message(thread_id):
    message = (
        await Message.find(Message.thread_id == thread_id, Message.sender == "user")
        .sort("-timestamp")
        .first_or_none()
    )

    if message is None:
        return "No message yet"

    return message.content


async def delete_thread(thread_id):
    thread = await Thread.get(PydanticObjectId(thread_id))
    if thread:
        await thread.delete()
        return {"message": "Thread deleted successfully"}
    return {"message": "Thread not found"}


async def update_thread_name_later(manager, thread_id, messages):
    chat_name = await manager.get_thread_name(messages)
    await update_thread_name(thread_id, chat_name)
