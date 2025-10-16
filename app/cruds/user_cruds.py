from fastapi import HTTPException
from app.models.users import User
from passlib.context import CryptContext
from bson import ObjectId
import logging
import hashlib
from app.schemas.user_schemas import UserSignup
from app.cruds.role_cruds import get_role_id
from app.models.orchestration_model import Orchestration
from app.models.agents_model import Agents
from app.models.steps_model import Steps

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
logger = logging.getLogger(__name__)


async def hash_password(password: str):
    try:
        print("before passwword hashing")
        prehashed = hashlib.sha256(password.encode("utf-8")).hexdigest()
        return pwd_context.hash(prehashed)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to securely hash password")


async def verify_password(plain_password: str, hashed_password: str):
    try:
        prehashed = hashlib.sha256(plain_password.encode("utf-8")).hexdigest()
        print("the hashed password is ", hashed_password)
        print("The prehsahed password is ", prehashed)
        print("Loaded password schemes:", pwd_context.schemes())

        result = pwd_context.verify(prehashed, hashed_password)
        print(result)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Internal error during password check"
        )


async def create_user(user_data: UserSignup):
    try:
        password_hash = await hash_password(user_data.password)
        print("the hashed password id", password_hash)
        role_id = await get_role_id(user_data.role_name.value)
        user = User(
            name=user_data.name,
            email=user_data.email,
            password_hash=password_hash,
            role_id=role_id,
        )
        await user.insert()
        return user

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")


async def get_user_by_email(email: str):
    try:
        print(email)
        print("before finding user")
        user = await User.find_one(User.email == email)
        print("after finding user")
        print(user)
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")


async def get_user_by_id(user_id: str):
    try:
        user_obj_id = ObjectId(user_id)
        user = await User.find_one(User.id == user_obj_id)
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")


async def verify_user_password(user: User, password: str):
    try:
        return await verify_password(password, user.password_hash)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Internal error during password verification"
        )


async def add_agent_to_user_cruds(agent_id: str, user_id: str):
    try:
        user = await User.find_one(User.id == ObjectId(user_id))
        print("the user is ", user)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        print("the user before adding agent is ", user)
        if user.agent_id is None:

            user.agent_id = []
        print("the agent id is ", agent_id)
        user.agent_id.append(agent_id)
        await user.save()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )


async def add_orchestration_to_user_cruds(orch_id: str, user_id: str):
    try:
        user = await User.find_one(User.id == ObjectId(user_id))
        print("the user is ", user)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        print("the user before adding agent is ", user)
        if user.orchestration_id is None:

            user.orchestration_id = []
        print("the agent id is ", orch_id)
        user.orchestration_id.append(orch_id)
        await user.save()
        print("after saving the orchestration in")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )


async def add_step_to_user_cruds(step_id: str, user_id: str):
    try:
        user = await User.find_one(User.id == ObjectId(user_id))
        print("the user is ", user)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        print("the user before adding agent is ", user)
        if user.step_id is None:

            user.step_id = []
        print("the agent id is ", step_id)
        user.step_id.append(step_id)
        await user.save()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )


async def add_knowledgebase_to_user_cruds(kb_id: str, user_id: str):
    try:
        user = await User.find_one(User.id == ObjectId(user_id))
        print("the user is ", user)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        print("the user before adding agent is ", user)
        if user.knowledgebase_id is None:

            user.knowledgebase_id = []
        print("the agent id is ", kb_id)
        user.knowledgebase_id.append(kb_id)
        await user.save()
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )


async def get_user_role_id_cruds(user_id: str):
    try:
        user = await User.find_one(User.id == ObjectId(user_id))
        print(user)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user.role_id
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )


async def same_orchestration_already_present(orch_name, user_id):
    try:
        user = await User.find_one(User.id == ObjectId(user_id))
        for orch in user.orchestration_id:
            orch_model = await Orchestration.find_one(
                Orchestration.id == ObjectId(orch)
            )
            if orch_model and orch_model.orchestrationName == orch_name:
                return True

        return False
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )


async def same_agent_already_present(agent_name, user_id):
    try:
        user = await User.find_one(User.id == ObjectId(user_id))
        for agent in user.agent_id:
            agent_model = await Agents.find_one(Agents.id == ObjectId(agent))
            if agent_model.agentName == agent_name:
                return True
        return False
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )


async def same_step_already_present(step_name, user_id):
    try:
        user = await User.find_one(User.id == ObjectId(user_id))
        for step in user.step_id:
            step_model = await Steps.find_one(Steps.id == ObjectId(step))
            if step_model.StepName == step_name:
                return True
        return False
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )
