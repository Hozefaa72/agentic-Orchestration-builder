from app.schemas.orchestration_schema import orchestration
from app.models.orchestration_model import Orchestration
from fastapi import HTTPException
from app.models.users import User
from bson import ObjectId
from app.cruds.step_cruds import step_execution
from app.models.orchestration_instace import StepsStatus
from app.models.orchestration_instace import OrchestrationInstance
import traceback


async def create_orchestration_cruds(orchestration_data: orchestration):
    try:
        print("before creating agent in crud")
        orch = Orchestration(
            orchestrationName=orchestration_data.orchestrationName,
            orchestrationDescription=orchestration_data.orchestrationDescription,
            adminids=orchestration_data.adminids,
        )
        await orch.insert()
        print("after creating agent in crud")
        return orch
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )


async def setfinal_step(orchestration_id, step_id):
    try:
        orch = await Orchestration.find_one(
            Orchestration.id == ObjectId(orchestration_id)
        )
        orch.finalstep = str(step_id)
        await orch.save()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )


async def setinitialstep(orchestration_id, step_id):
    try:
        orch = await Orchestration.find_one(
            Orchestration.id == ObjectId(orchestration_id)
        )
        orch.intialstep = str(step_id)
        await orch.save()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )


async def add_stepid_orchestration(orch_id: str, step_id: str):
    try:
        orch = await Orchestration.find_one(Orchestration.id == ObjectId(orch_id))
        print("the user is ", orch)
        if not orch:
            raise HTTPException(status_code=404, detail="User not found")
        print("the user before adding agent is ", orch)
        if orch.stepids is None:

            orch.stepids = []
        print("the agent id is ", orch_id)
        orch.stepids.append((str(step_id)))
        await orch.save()
        print("after saving the orchestration in")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )


async def add_agentid_orchestration(orch_id: str, agent_id: str):
    try:
        orch = await Orchestration.find_one(Orchestration.id == ObjectId(orch_id))
        print("the user is ", orch)
        if not orch:
            raise HTTPException(status_code=404, detail="User not found")
        print("the user before adding agent is ", orch)
        if orch.agentids is None:

            orch.agentids = []
        print("the agent id is ", orch_id)
        orch.agentids.append((str(agent_id)))
        await orch.save()
        print("after saving the orchestration in")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )


async def add_kbid_orchestration(orch_id: str, kb_id: str):
    try:
        orch = await Orchestration.find_one(Orchestration.id == ObjectId(orch_id))
        print("the user is ", orch)
        if not orch:
            raise HTTPException(status_code=404, detail="User not found")
        print("the user before adding agent is ", orch)
        if orch.kbids is None:

            orch.kbids = []
        print("the agent id is ", orch_id)
        orch.kbids.append((str(kb_id)))
        await orch.save()
        print("after saving the orchestration in")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )


async def get_orchestration_response_cruds(orchestration_insatnce_id, user_input=None):
    orch_ins = await OrchestrationInstance.find_one(
        OrchestrationInstance.id == orchestration_insatnce_id
    )
    cstep = ""
    if orch_ins.currentstep and orch_ins.status != StepsStatus.PENDING:
        cstep = orch_ins.currentstep
        user_input = orch_ins.stepoutput
        response, next_step = await step_execution(
            user_input, cstep, orchestration_insatnce_id
        )

    elif orch_ins.status != StepsStatus.PENDING:
        orch = await Orchestration.find_one(
            Orchestration.id == ObjectId(orch_ins.orchestration_id)
        )
        cstep = orch.intialstep
        response, next_step = await step_execution(
            user_input, cstep, orchestration_insatnce_id
        )
    else:
        return None

    if next_step:
        orch_ins.currentstep = next_step
        orch_ins.previousstep = cstep
        await orch_ins.save()
    return response


async def get_admin_orchestration_cruds(user_id):
    try:
        print("inside the crud operation")
        orh = await User.find(User.id == ObjectId(user_id)).to_list()
        print("the orch fecthed are", orh)
        return orh
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )


async def get_all_orchestration_cruds():
    try:
        print("inside the crud operation")
        orh = await Orchestration.find_all().to_list()
        print("the orch fecthed are", orh)
        return orh
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )
