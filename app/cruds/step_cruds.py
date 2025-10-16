from app.schemas.step_schema import Step
from fastapi import HTTPException
from app.models.steps_model import Steps
import traceback
from bson import ObjectId
from typing import Any
from app.core.agents import get_response_from_agent
from app.core.email_send import send_approval_email
from app.models.users import User
from datetime import datetime, timezone
from app.auth.jwt_handler import generate_approval_token
from app.core.agents import generate_agent_approval
from app.models.orchestration_instace import StepsStatus
from app.models.orchestration_instace import OrchestrationInstance
from app.utils.config import ENV_PROJECT


async def set_step_connection(previuos_step_id, next_step_id):
    try:
        print("inside the set step connection cruds")
        step = await Steps.find_one(Steps.id == ObjectId(previuos_step_id))
        if step:
            step.NextStep = str(next_step_id)
            await step.save()
    except:
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )


async def create_step_cruds(step: Step):
    try:
        print("before creating agent in crud")
        print(step)
        step_data = Steps(
            StepName=step.StepName,
            StepDescription=step.StepDescription,
            PreviousStep=step.PreviousStep,
            NextStep=step.NextStep,
            AgentID=step.AgentID,
            canhumanintrupt=step.canhumanintrupt,
            expectedinput=step.expectedinput,
            expectedoutput=step.expectedoutput,
            ispriorstep=step.ispriorstep,
            validconditions=step.validconditions,
            isactivestep=step.isactivestep,
            adminid=step.adminid,
            isinitialstep=step.isinitialstep,
            isfinalstep=step.isfinalstep,
            canrollback=step.canrollback_agent,
            rollbackstep=step.rollbackstep_agent,
            userapprovalrequired=step.userapprovalrequired,
            adminapprovalrequired=step.adminapprovalrequired,
            conditionmap=step.conditionmap,
            status=step.status.value,
        )
        await step_data.insert()
        print("after creating agent in crud")
        if not (step_data.isinitialstep):
            await set_step_connection(step_data.PreviousStep, step_data.id)
        return step_data
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )


async def step_execution(user_input: Any, step_id: str, orchestration_insatce_id):
    try:
        step = await Steps.find_one(Steps.id == ObjectId(step_id))
        orch_ins = await OrchestrationInstance.find_one(
            OrchestrationInstance.id == orchestration_insatce_id
        )
        if step:
            orch_ins.stepinput = user_input
            orch_ins.isactivestep = True
            orch_ins.status = StepsStatus.INPROGRESS
            await orch_ins.save()
            response = await get_response_from_agent(
                step.AgentID, user_input, step.expectedinput, step.expectedoutput
            )
            orch_ins.stepoutput = response
            await orch_ins.save()
            if step.canhumanintrupt:
                if step.userapprovalrequired:
                    user = await User.find_one(User.id == ObjectId(orch_ins.user_id))
                    admin = await User.find_one(User.id == ObjectId(step.adminid))
                    orch_ins.status = StepsStatus.PENDING
                    orch_ins.approvalsentat = datetime.now(timezone.utc)
                    await orch_ins.save()
                    if step.user_ids is None:
                        step.user_ids = []
                    step.user_ids.append(orch_ins.user_id)
                    await step.save()
                    token = await generate_approval_token(
                        orch_ins.orchestration_id,
                        step_id,
                        orch_ins.user_id,
                        step.approvaltimeoutdays,
                        ENV_PROJECT.EMAIL_SECRET_KEY,
                    )
                    await send_approval_email(
                        user.email, token, response, step.expectedoutput
                    )
                else:
                    admin = await User.find_one(User.id == ObjectId(step.adminid))
                    orch_ins.status = StepsStatus.PENDING
                    orch_ins.approvalsentat = datetime.now(timezone.utc)
                    await orch_ins.save()
                    token = await generate_approval_token(
                        orch_ins.orchestration_id,
                        step_id,
                        step.adminid,
                        step.approvaltimeoutdays,
                        ENV_PROJECT.EMAIL_SECRET_KEY,
                    )
                    await send_approval_email(
                        admin.email, token, response, step.expectedoutput
                    )
                return response, None
            else:
                isvalid = generate_agent_approval(
                    response, step.expectedoutput, step.validconditions
                )
                if isvalid:
                    orch_ins.status = StepsStatus.COMPLETED
                    orch_ins.isactivestep = False
                    await orch_ins.save()
                    if step.isfinalstep:
                        return response, None
                    elif step.NextStep:
                        return response, step.NextStep
                    else:
                        return response, None

                elif not (isvalid) and step.canrollback_agent:
                    orch_ins.status = StepsStatus.FAILED
                    orch_ins.isactivestep = False
                    await orch_ins.save()
                    return response, step.rollbackstep_agent
                else:
                    orch_ins.status = StepsStatus.FAILED
                    orch_ins.isactivestep = False
                    await orch_ins.save()
                    if step.isinitialstep:
                        return response, step_id
                    else:
                        return response, step.PreviousStep
        else:
            raise HTTPException(status_code=404, detail="Step not found")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )
