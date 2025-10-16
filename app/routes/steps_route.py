from fastapi import APIRouter,Depends
from app.auth.auth import get_current_user
from app.schemas.response import responsemodel
from app.utils.response import create_response
from app.cruds.step_cruds import create_step_cruds,set_step_connection,step_execution
from app.cruds.permission_cruds import get_permission_id_crud
from app.cruds.rolepermissionmapping_cruds import has_permission
from app.cruds.user_cruds import add_step_to_user_cruds,get_user_role_id_cruds,same_step_already_present
from app.schemas.step_schema import Step
from app.cruds.orchestration_cruds import setfinal_step,setinitialstep,add_stepid_orchestration

router = APIRouter()


@router.post("/create_step",response_model=responsemodel)
async def create_step(step_info:Step,current_user: dict = Depends(get_current_user)):
    try:
        user_id=current_user.get("user_id")
        orchestration_id=current_user.get("orchestration_id")
        print("the user id is ",user_id)
        role_id=await get_user_role_id_cruds(user_id)
        permission_id=await get_permission_id_crud("Create Step")
        print("the permission id is ",permission_id)
        if await has_permission(role_id,permission_id):
            if await same_step_already_present(step_info.StepName,user_id):
                return create_response(
                success=False,
                error_message="The same Step name already present",
                status_code=401
                )
            print("you have permission to create agent")
            step = await create_step_cruds(step_info)
            if orchestration_id:
                if step_info.isfinalstep:
                    await setfinal_step(orchestration_id,step.id)
                if step_info.isinitialstep:
                    await setinitialstep(orchestration_id,step.id)
                await add_stepid_orchestration(orchestration_id,step.id)
            if not(step.isinitialstep):
                await set_step_connection(step.PreviousStep,step.id)

            await add_step_to_user_cruds(str(step.id),user_id)
            return create_response(
                success=True,
                result={"message":"Agent created successfully","agent": step},
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
# @router.get("/get_step_response")
# async def get_step_response(user_input:str,step_id:str,orchestration_id="68ef69414b09525604e77885",current_user: dict = Depends(get_current_user)):
#     user_id=current_user.get("user_id")
#     orchestration_id=current_user.get("orchestration_id")
#     response,step_id=await step_execution(user_input,step_id,user_id,orchestration_id)
#     print(response)