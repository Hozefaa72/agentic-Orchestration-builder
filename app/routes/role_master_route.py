from fastapi import APIRouter,Depends
from app.auth.auth import get_current_user
from app.cruds.role_cruds import create_role,get_role_ids_cruds
from app.schemas.role_schema import role
from app.schemas.response import responsemodel
from app.utils.response import create_response


router = APIRouter()



@router.post("/create_role",response_model=responsemodel)
async def create_role_route(role_info:role,current_user: dict = Depends(get_current_user)):
    try:
        roles=await create_role(role_info)

        return create_response(
            success=True,
            result={"message": "Role created Successfully","role":roles},
            status_code=201
            )
    except Exception as e:
        print(e)
        return create_response(
            success=False,
            error_message="Internal Server error during role creation",
            error_detail=str(e),
            status_code=500
            )


@router.get("get_role_id",response_model=responsemodel)
async def get_role_id(current_user:dict=Depends(get_current_user)):
    try:
        role_ids=await get_role_ids_cruds()
        return create_response(
          success=True,
            result={"message": "Role Fetched Successfully","role":role_ids},
            status_code=201
            )
    except Exception as e:
        return create_response(
            success=False,
            error_message="Internal Server error during role fetching",
            error_detail=str(e),
            status_code=500
            )
