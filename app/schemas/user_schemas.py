from pydantic import BaseModel,EmailStr
from app.schemas.role_schema import roles

class UserSignup(BaseModel):
    name: str
    email: EmailStr
    password: str
    role_name: roles

class UserLogin(BaseModel):
    email: EmailStr
    password: str