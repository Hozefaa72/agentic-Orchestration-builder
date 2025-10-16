from fastapi import APIRouter, Depends
from app.models.v2.threads import Thread
from datetime import datetime, timezone
from app.auth.auth import get_current_user
from app.auth.jwt_handler import update_jwt
from app.cruds.v2.threads_cruds import delete_thread, update_thread_name
from app.schemas.v2.thread_schemas import ThreadEditRequest, ChangeLangRequest
from bson import ObjectId
from app.schemas.response import responsemodel
from app.utils.response import create_response

router = APIRouter()


@router.delete("/delete_thread",response_model=responsemodel)
async def delete_threadd(thread_id: str, current_user: dict = Depends(get_current_user)):
    try:
        if thread_id:
            respone = await delete_thread(thread_id)
            return create_response(
            success=True,
            result={"message": "Thread Deleted Successully","response":respone},
            status_code=201
            )
        else:
            return create_response(
                success=False,
                error_message="You do not have Thread.",
                status_code=403
                )
    except Exception as e:
        return create_response(
            success=False,
            error_message="Internal Server error during LLM model creation",
            error_detail=str(e),
            status_code=500
            )


@router.post("/edit_name",response_model=responsemodel)
async def edit_name(request: ThreadEditRequest, current_user: dict = Depends(get_current_user)):
    try:
        thread_id=current_user.get("thread_id")
        if thread_id:
            response = await update_thread_name(thread_id, request.name)
            if response:
                return create_response(
                        success=True,
                        result={"message": "Thread Name Updated Successfully","response":response},
                        status_code=201
                        )
            else:
                return create_response(
                success=False,
                error_message="Thread Name not Updated",
                status_code=403
                )
        else:
            return create_response(
                success=False,
                error_message="Thread Not Found",
                status_code=403
                )

    except Exception as e:
        return create_response(
            success=False,
            error_message="Internal Server error during LLM model creation",
            error_detail=str(e),
            status_code=500
            )


@router.get("/get_threads",response_model=responsemodel)
async def get_user_threads(current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user.get("user_id")
        print("meri user id hai ",user_id)
        if user_id:
            threads = await Thread.find(Thread.user_id == user_id).sort(-Thread.timestamp).to_list()
            return create_response(
            success=True,
            result={"message": "Thread fetched Successfully","response":threads},
            status_code=201
            )
        else:
            return create_response(
                success=False,
                error_message="User Not found",
                status_code=403
                )
    except Exception as e:
        return create_response(
            success=False,
            error_message="Internal Server error during LLM model creation",
            error_detail=str(e),
            status_code=500
            )


@router.get("/create_threads",response_model=responsemodel)
async def create_thread(lang:str,current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user.get("user_id")
        session_id = current_user.get("session_id")
        if user_id:
            print("before creating thread")
            new_thread = Thread(
                user_id=user_id,
                thread_name="New Chat",
                language=lang,
                timestamp=datetime.now(timezone.utc),
            )
            print("after creating thread")
            token = update_jwt(user_id, str(new_thread.id), session_id)
            await new_thread.save()
            print("the id of the thread created is ",new_thread.id)
            return create_response(
                    success=True,
                    result={"message": "Thread created successfully","Thread":new_thread,"token":token},
                    status_code=201
                    )
        else:
            return create_response(
                success=False,
                error_message="User Not Found",
                status_code=403
                )
    except Exception as e:
        return create_response(
            success=False,
            error_message="Internal Server error during LLM model creation",
            error_detail=str(e),
            status_code=500
            )


@router.get("/select_threads",response_model=responsemodel)
async def select_thread(thread_id: str, current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user.get("user_id")
        session_id = current_user.get("session_id")
        if user_id:
            thread = await Thread.find_one(Thread.id == ObjectId(thread_id))
            token = update_jwt(user_id, thread_id, session_id)
            return create_response(
                    success=True,
                    result={"message": "thread Selected successfully","Thread":thread,"token":token},
                    status_code=201
                    )
        else:
            return create_response(
                    success=False,
                    error_message="User Not Found",
                    status_code=403
                    )
    except Exception as e:
        return create_response(
            success=False,
            error_message="Internal Server error during LLM model creation",
            error_detail=str(e),
            status_code=500
            )

@router.post("/change_language",response_model=responsemodel)
async def change_language(request: ChangeLangRequest,current_user: dict = Depends(get_current_user)):
    try:
        print("thread_id printing in language change router",request.thread_id)
        thread_id=current_user.et("thread_id")
        if thread_id:
            thread = await Thread.find_one(Thread.id == ObjectId(thread_id))
            thread.language = request.language
            await thread.save()
            new_thread = await Thread.find_one(Thread.id == ObjectId(thread_id))
            print("new thread after language change",new_thread.language)
            print("new thread after language change",new_thread.id)
            return create_response(
                    success=True,
                    result={"message": "Language Changed successfully"},
                    status_code=201
                    )
        else:
            return create_response(
                success=False,
                error_message="thread Not Found",
                status_code=403
                )

    except Exception as e:
        return create_response(
            success=False,
            error_message="Internal Server error during LLM model creation",
            error_detail=str(e),
            status_code=500
            )