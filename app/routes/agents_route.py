from fastapi import APIRouter,Depends
from app.auth.auth import get_current_user
from app.schemas.agents_schemas import Agent_info
from app.schemas.response import responsemodel
from app.utils.response import create_response
from app.cruds.agent_cruds import create_agent_cruds,get_agent_cruds,get_all_agent_cruds
from app.cruds.permission_cruds import get_permission_id_crud
from app.cruds.rolepermissionmapping_cruds import has_permission
from app.cruds.user_cruds import add_agent_to_user_cruds,get_user_role_id_cruds,same_agent_already_present
from app.core.agents import get_response_from_agent
from typing import Any
from app.cruds.orchestration_cruds import add_agentid_orchestration

router = APIRouter()


@router.post("/create_agent",response_model=responsemodel)
async def create_agent(agent_info:Agent_info,current_user: dict = Depends(get_current_user)):
    try:
        user_id=current_user.get("user_id")
        orchestration_id=current_user.get("orchestration_id")
        print("the user id is ",user_id)
        role_id=await get_user_role_id_cruds(user_id)
        permission_id=await get_permission_id_crud("Create Agent")
        print("the permission id is ",permission_id)
        if await has_permission(role_id,permission_id):
            if await same_agent_already_present(agent_info.agentName,user_id):
                return create_response(
                success=False,
                error_message="The same Agent name already present",
                status_code=401
                )
            print("you have permission to create agent")
            agent = await create_agent_cruds(agent_info)
            if orchestration_id:
                await add_agentid_orchestration(orchestration_id,agent.id)
            await add_agent_to_user_cruds(str(agent.id),user_id)
            return create_response(
                success=True,
                result={"message":"Agent created successfully","agent": agent},
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

@router.get("/get_agents",response_model=responsemodel)
async def fetch_agent(current_user: dict = Depends(get_current_user)):
    try:

        print("before creating agent")
        user_id=current_user.get("user_id")
        agent = await get_agent_cruds(user_id)

        return create_response(
            success=True,
            result={"message":"Agent fetched Successfully","agent": agent},
            status_code=200
            )
    except Exception as e:
        print(e)
        return create_response(
            success=False,
            error_message="Internal Server error during fetching agent",
            error_detail=str(e),
            status_code=500
            )
    
@router.get("/get_answer_from_agent",response_model=responsemodel)
async def get_answer_from_agent(agentid:str,user_question:Any,current_user:dict=Depends(get_current_user)):
    try:

        context=await get_response_from_agent(agentid,user_question)
            
        return create_response(
                    success=True,
                    result={"Answer": context},
                    status_code=201
                    )

    except Exception as e:
        print(e)
        return create_response(
            success=False,
            error_message="Internal Server error during getting knowledge base",
            error_detail=str(e),
            status_code=500
            )


@router.get("/get_all_agents",response_model=responsemodel)
async def fetch_all_agent(current_user: dict = Depends(get_current_user)):
    try:
        user_id=current_user.get("user_id")
        print("the user id is ",user_id)
        role_id=await get_user_role_id_cruds(user_id)
        print(role_id)
        permission_id=await get_permission_id_crud("Get All Agents")
        print("the permission id is ",permission_id)
        if await has_permission(role_id,permission_id):
            print("the user has permission")
            agent = await get_all_agent_cruds()

            return create_response(
                success=True,
                result={"message":"Agent fetched Successfully","agent": agent},
                status_code=200
                )
        else:
            return create_response(
                success=False,
                error_message="You do not have permission to fetch all agent",
                status_code=403
                )

    except Exception as e:
        print(e)
        return create_response(
            success=False,
            error_message="Internal Server error during fetching agent",
            error_detail=str(e),
            status_code=500
            )
