from fastapi import APIRouter,Depends
from app.auth.auth import get_current_user
from app.cruds.permission_cruds import create_permission_cruds,get_permission_ids_cruds
from app.schemas.permission_schemas import permission
from app.schemas.response import responsemodel
from app.utils.response import create_response


router = APIRouter()



@router.post("/create_permission",response_model=responsemodel)
async def create_permission(permission_info:permission,current_user: dict = Depends(get_current_user)):
    try:
        permissions=await create_permission_cruds(permission_info)

        return create_response(
            success=True,
            result={"message": "Permissions created Successfully","permission_details":permissions},
            status_code=201
            )
    except Exception as e:
        print(e)
        return create_response(
            success=False,
            error_message="Internal Server error during permission creation",
            error_detail=str(e),
            status_code=500
            )

@router.get("get_permission_id",response_model=responsemodel)
async def get_role_id(current_user:dict=Depends(get_current_user)):
    try:
        permission_ids=await get_permission_ids_cruds()
        return create_response(
          success=True,
            result={"message": "Permission IDs Fetched Successfully","role":permission_ids},
            status_code=201
            )
    except Exception as e:
        return create_response(
            success=False,
            error_message="Internal Server error during role fetching",
            error_detail=str(e),
            status_code=500
            )
    
    