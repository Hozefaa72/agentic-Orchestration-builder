from fastapi import APIRouter,Query
from app.models.steps_model import Steps
from bson import ObjectId
from app.models.orchestration_instace import OrchestrationInstance,StepsStatus
from typing import Optional
from app.auth.jwt_handler import decode_email_approval_jwt
from app.schemas.response import responsemodel
from app.utils.response import create_response

router = APIRouter()

@router.get("/response_approval",response_model=responsemodel)
async def handle_approval_action(token: Optional[str] = Query(None),isvalid: Optional[str] = Query(None)):
    try:
        data=await decode_email_approval_jwt(token)
        valid = str(isvalid).lower() == "true"
        orchestration_id = data["orchestration_id"]
        step_id = data["step_id"]
        user_id = data["admin_id"]
        step= await Steps.find_one(Steps.id==ObjectId(step_id))
        orch_ins=await OrchestrationInstance.find_one(OrchestrationInstance.orchestration_id==orchestration_id,OrchestrationInstance.user_id==user_id)

        if valid:
            orch_ins.currentstep=step.conditionmap.next_step
            orch_ins.previousstep=step_id
            orch_ins.status=StepsStatus.COMPLETED
            await orch_ins.save()
        else:
            if step.conditionmap.rollback_step!=step_id:
                orch_ins.currentstep=step.conditionmap.rollback_step
                orch_ins.previousstep=step_id
                orch_ins.status=StepsStatus.FAILED
                await orch_ins.save()
            else:
                orch_ins.status=StepsStatus.FAILED
                await orch_ins.save()
        return  create_response(
            success=True,
            result={"message": "status Updated SuccessFully"},
            status_code=201
            )
    except Exception as e:
        return create_response(
            success=False,
            error_message="Internal Server error during LLM model creation",
            error_detail=str(e),
            status_code=500
            )

