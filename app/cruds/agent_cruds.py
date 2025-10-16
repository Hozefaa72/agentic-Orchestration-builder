from app.schemas.agents_schemas import Agent_info
from app.models.agents_model import Agents
from fastapi import HTTPException
from app.models.users import User
from bson import ObjectId


async def create_agent_cruds(agent_info: Agent_info):
    try:
        print("before creating agent in crud")
        agents = Agents(
            agentName=agent_info.agentName,
            agentPrompt=agent_info.agentPrompt,
            agentLLMModelcompany=agent_info.agentLLMModelcompany.value,
            agentLLMModelname=agent_info.agentLLMModelname,
            agentKBID=agent_info.agentKBID,
        )
        await agents.insert()
        print("after creating agent in crud")
        return agents
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )


async def get_agent_cruds(user_id: str):
    try:
        user = await User.find_one(User.id == ObjectId(user_id))
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found",
            )
        agent_ids = user.agent_id
        agents = []
        if agent_ids:
            for agent_id in agent_ids:
                agent = await Agents.find_one(Agents.id == ObjectId(agent_id))
                if not agent:
                    raise HTTPException(
                        status_code=404,
                        detail="Agent not found",
                    )
                agents.append(agent)
        return agents
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )


async def get_all_agent_cruds():
    try:
        agent = await Agents.find_all().to_list()
        print(agent)
        if not agent:
            raise HTTPException(
                status_code=404,
                detail="Agent not found",
            )
        return agent
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )
