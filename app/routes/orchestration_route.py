from fastapi import APIRouter,Depends,Query
from app.auth.auth import get_current_user
from app.schemas.orchestration_schema import orchestration
from app.schemas.response import responsemodel
from app.utils.response import create_response
from app.cruds.permission_cruds import get_permission_id_crud
from app.cruds.rolepermissionmapping_cruds import has_permission
from app.cruds.user_cruds import add_orchestration_to_user_cruds,get_user_role_id_cruds,same_orchestration_already_present
from app.auth.jwt_handler import update_jwt
from app.cruds.orchestration_cruds import create_orchestration_cruds,get_orchestration_response_cruds,get_admin_orchestration_cruds,get_all_orchestration_cruds
from typing import Any,Optional
from app.models.orchestration_instace import OrchestrationInstance
from app.models.orchestration_model import Orchestration
from bson import ObjectId

router = APIRouter()


@router.post("/create_orchestration",response_model=responsemodel)
async def create_orchestration(orchestration_data:orchestration,current_user: dict = Depends(get_current_user)):
    try:
        print("inside route")
        user_id=current_user.get("user_id")
        session_id=current_user.get("session_id")
        role_id=await get_user_role_id_cruds(user_id)
        permission_id=await get_permission_id_crud("Create Orchestration")
        if await has_permission(role_id,permission_id):
            print("user has permission")
            if await same_orchestration_already_present(orchestration_data.orchestrationName,user_id):
                return create_response(
                success=False,
                error_message="The same Orchestration name already present",
                status_code=401
                )
            orchestration_model = await create_orchestration_cruds(orchestration_data)
            await add_orchestration_to_user_cruds(str(orchestration_model.id),user_id)
            token=await update_jwt(user_id,str(orchestration_model.id),session_id)
            return create_response(
                success=True,
                result={"message":"Agent created successfully","agent": orchestration_model,"Toeken Generated":token},
                status_code=201
                )
        else:
            return create_response(
                success=False,
                error_message="You do not have permission to create agent",
                status_code=403
                )
    except Exception as e:
        print(e)
        return create_response(
            success=False,
            error_message="Internal Server error during agent creation",
            error_detail=str(e),
            status_code=500
            )
@router.get("/get_orchestration_response",response_model=responsemodel)
async def get_orchestration_response(user_input:Optional[Any]=Query(None),current_user:dict=Depends(get_current_user)):
    try:
        orchestration_id=current_user.get("orchestration_id")
        user_id=current_user.get("user_id")
        role_id=await get_user_role_id_cruds(user_id)
        permission_id=await get_permission_id_crud("Use Orchestration")
        if await has_permission(role_id,permission_id):
            orch_ins=await OrchestrationInstance.find_one(OrchestrationInstance.orchestration_id==orchestration_id,OrchestrationInstance.user_id==user_id)
            print("the orch instance is preent",orch_ins)
            if not(orch_ins):
                print("orchestration not preseent")
                orch_ins=OrchestrationInstance(
                    orchestration_id=orchestration_id,
                    user_id=user_id
                )
                await orch_ins.insert()
            response=await  get_orchestration_response_cruds(orch_ins.id,user_input)
            if response:
                return create_response(
                    success=True,
                    result={"message":"Response created successfully","reponse": response},
                    status_code=201
                    )
            else:
                return create_response(
                    success=True,
                    result={"message":"Response  is in pending state"},
                    status_code=201
                    )
        else:
            return create_response(
                success=False,
                error_message="You do not have permission to create agent",
                status_code=403
                )


    except Exception as e:
        return create_response(
            success=False,
            error_message="Internal Server error during agent creation",
            error_detail=str(e),
            status_code=500
            )
@router.get("/get_admin_orchestration",response_model=responsemodel)
async def get_admin_orchestration(current_user:dict=Depends(get_current_user)):
    try:
        user_id=current_user.get("user_id")
        role_id=await get_user_role_id_cruds(user_id)
        permission_id=await get_permission_id_crud("Get Admin's all Orchestration")
        if await has_permission(role_id,permission_id):
            orch=await get_admin_orchestration_cruds(user_id)
            return create_response(
                    success=True,
                    result={"message":"Admin's Orchestration Fetched successfully","reponse": orch},
                    status_code=201
                    )
        else:
            return create_response(
                success=False,
                error_message="You do not have permission to create agent",
                status_code=403
                )
    except Exception as e:
        return create_response(
            success=False,
            error_message="Internal Server error during agent creation",
            error_detail=str(e),
            status_code=500
            )
    
@router.get("/get_all_orchestration",response_model=responsemodel)
async def get_all_orchestration(current_user:dict=Depends(get_current_user)):
    try:
        user_id=current_user.get("user_id")
        role_id=await get_user_role_id_cruds(user_id)
        permission_id=await get_permission_id_crud("Get  all Orchestration")
        if await has_permission(role_id,permission_id):
            orch=await get_all_orchestration_cruds()
            return create_response(
                    success=True,
                    result={"message":"Admin's Orchestration Fetched successfully","reponse": orch},
                    status_code=201
                    )
        else:
            return create_response(
                success=False,
                error_message="You do not have permission to create agent",
                status_code=403
                )
    except Exception as e:
        return create_response(
            success=False,
            error_message="Internal Server error during agent creation",
            error_detail=str(e),
            status_code=500
            )
    
@router.get("/select_orchestration",response_model=responsemodel)
async def select_orchestration(orchestration_id:str,current_user:dict=Depends(get_current_user)):
    try:
        user_id=current_user.get("user_id")
        session_id=current_user.get("session_id")
        orchestration_model=await Orchestration.find_one(Orchestration.id==ObjectId(orchestration_id))
        token=await update_jwt(user_id,orchestration_id,session_id)
        return create_response(
                success=True,
                result={"message":"Agent created successfully","Orchestration": orchestration_model,"Toeken Generated":token},
                status_code=201
                )

    except Exception as e:
        return create_response(
            success=False,
            error_message="Internal Server error during agent creation",
            error_detail=str(e),
            status_code=500
            )
