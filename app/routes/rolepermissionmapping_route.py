from fastapi import APIRouter,Depends
from app.auth.auth import get_current_user
from app.cruds.rolepermissionmapping_cruds import create_rolePermissionMapping_cruds
from app.schemas.role_permission_schema import rolepermissionmapping
from app.schemas.response import responsemodel
from app.utils.response import create_response


router = APIRouter()



@router.post("/create_rolepermissionmapping",response_model=responsemodel)
async def create_rolePermissionMapping(mapping:rolepermissionmapping,current_user: dict = Depends(get_current_user)):
    try:
        mapping=await create_rolePermissionMapping_cruds(mapping)

        return create_response(
            success=True,
            result={"message":"Role Permission Mapping created Successfully","rolepermissionmapping": mapping},
            status_code=201
            )
    except Exception as e:
        print(e)
        return create_response(
            success=False,
            error_message="Internal Server error during Role Permission Mapping creation",
            error_detail=str(e),
            status_code=500
            )

