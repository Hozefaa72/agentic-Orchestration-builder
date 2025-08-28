from fastapi import APIRouter, HTTPException, Depends, status
from backend.app.models.threads import Thread
from datetime import datetime, timezone
from pymongo.errors import PyMongoError
from backend.app.auth.auth import get_current_user
from backend.app.auth.jwt_handler import update_jwt
from backend.app.cruds.threads_cruds import delete_thread, update_thread_name
from backend.app.schemas.thread_schemas import ThreadEditRequest
from bson import ObjectId

chat_router = APIRouter()


# class ThreadEditRequest(BaseModel):
#     name: str
#     thread_id: str


@chat_router.delete("/delete_thread")
async def delete_threadd(
    thread_id: str, current_user: dict = Depends(get_current_user)
):
    try:
        if not thread_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Thread ID is required",
            )

        respone = await delete_thread(thread_id)
        return {"response": respone}

    except HTTPException as http_exc:
        raise http_exc

    except PyMongoError as db_err:
        raise HTTPException(
            status_code=500, detail="Database error while deleting thread"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Internal server error while deleting thread"
        )


@chat_router.post("/edit_name")
async def edit_name(
    request: ThreadEditRequest, current_user: dict = Depends(get_current_user)
):
    try:
        if not request.thread_id:
            raise HTTPException(
                status_code=400, detail="Thread ID is missing or invalid"
            )

        response = await update_thread_name(request.thread_id, request.name)
        if response:
            return {"response": "Name edited Successfully"}
        raise HTTPException(status_code=400, detail="Name not edited")
    except PyMongoError as db_err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while updating thread name",
        )

    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal error while editing thread name",
        )


@chat_router.get("/get_threads")
async def get_user_threads(current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID is missing or invalid")

        threads = (
            await Thread.find(Thread.user_id == user_id)
            .sort(-Thread.timestamp)
            .to_list()
        )
        return {"threads": threads}
    except PyMongoError as db_err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching threads",
        )

    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while fetching threads",
        )


@chat_router.get("/create_threads")
async def create_thread(lang:str,current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user.get("user_id")
        session_id = current_user.get("session_id")
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID is missing or invalid")

        new_thread = Thread(
            user_id=user_id,
            thread_name="New Chat",
            language=lang,
            timestamp=datetime.now(timezone.utc),
        )
        token = update_jwt(user_id, str(new_thread.id), session_id)

        await new_thread.save()

        return {
            "message": "Thread created successfully",
            "thread": new_thread,
            "token": token,
        }
    except HTTPException as http_exc:
        raise http_exc

    except PyMongoError as db_err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while creating thread",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while creating thread",
        )


@chat_router.get("/select_threads")
async def select_thread(thread_id: str, current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user.get("user_id")
        session_id = current_user.get("session_id")
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID is missing or invalid")
        try:
            thread_obj_id = ObjectId(thread_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid thread ID format"
            )

        thread = await Thread.find_one(Thread.id == thread_obj_id)
        if not thread or thread.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this thread"
            )

        token = update_jwt(user_id, thread_id, session_id)

        return {"msg": token}
    except HTTPException as http_exc:
        raise http_exc

    except PyMongoError as db_err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while selecting thread"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while selecting thread"
        )
