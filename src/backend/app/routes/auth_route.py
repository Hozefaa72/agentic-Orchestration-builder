from fastapi import APIRouter, HTTPException
from backend.app.database.curds import (
    get_user_by_email,
    create_user,
    verify_user_password,
)
from backend.app.modules.jwt_handler import sign_jwt
from pydantic import BaseModel, EmailStr
from beanie.exceptions import DocumentNotFound
from datetime import datetime

auth_router = APIRouter()


class UserSignup(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


@auth_router.post("/signup")
async def signup(user_data: UserSignup):
    existing_user = await get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = await create_user(user_data)
    token = sign_jwt(str(user.id))
    return {"msg": "Signup succesful", "user": user, "token": token}


@auth_router.post("/login")
async def login(user_data: UserLogin):
    try:
        user = await get_user_by_email(user_data.email)
        if user and await verify_user_password(user, user_data.password):
            user.last_login = datetime.utcnow()  # Set last_login to current UTC time
            await user.save()
            token = sign_jwt(str(user.id))
            return {"msg": "Login succesful", "user": user, "token": token}
        raise HTTPException(status_code=401, detail="Invalid credentials")
    except DocumentNotFound:
        raise HTTPException(status_code=404, detail="User not Found")
