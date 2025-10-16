from fastapi import APIRouter, Depends,Query
from app.cruds.v2.message_cruds import create_message, get_all_messages
from app.auth.auth import get_current_user
from app.schemas.v2.message_schemas import MessageCreate
from app.utils.response import create_response
from app.schemas.response import responsemodel
from app.models.v2.message import Feedack



# class MessageCreate(BaseModel):
#     content: Union[str, List[str]]
#     sender: str


router = APIRouter()


@router.get("/get_all_messages",response_model=responsemodel)
async def get_all_messages_route(current_user: dict = Depends(get_current_user)):
    try:
        thread_id = current_user["thread_id"]
        if thread_id:
            messages = await get_all_messages(thread_id)
            return create_response(
            success=True,
            result={"message": "Messages Fetched Successfully","messages":messages},
            status_code=201
            )
        else:
            return create_response(
                success=False,
                error_message="You have not selected any thread",
                status_code=403
                )

    except Exception as e:
        return create_response(
            success=False,
            error_message="Internal Server error during LLM model creation",
            error_detail=str(e),
            status_code=500
            )


@router.post("/messages",response_model=responsemodel)
async def post_message(msg: MessageCreate,feedback:Feedack=Query(None),current_user: dict = Depends(get_current_user)):
    try:
        thread_id = current_user["thread_id"]
        if thread_id:
            message = await create_message(msg,thread_id,feedback)
            return create_response(
            success=True,
            result={"message": "Message created successfully","message":message},
            status_code=201
            )
        return create_response(
                success=False,
                error_message="You have not selected any thread",
                status_code=403
                )
    except Exception as e:
        return create_response(
            success=False,
            error_message="Internal Server error during Message creation",
            error_detail=str(e),
            status_code=500
            )
    