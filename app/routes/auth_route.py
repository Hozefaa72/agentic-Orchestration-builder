from fastapi import APIRouter, HTTPException, status
from app.cruds.user_cruds import (
    get_user_by_email,
    create_user,
    verify_user_password,
)
from app.auth.jwt_handler import sign_jwt
from app.schemas.user_schemas import UserLogin, UserSignup
from datetime import datetime, timezone
from pymongo.errors import PyMongoError

auth_router = APIRouter()


# class UserSignup(BaseModel):
#     name: str
#     email: EmailStr
#     password: str


# class UserLogin(BaseModel):
#     email: EmailStr
#     password: str


@auth_router.post("/signup")
async def signup(user_data: UserSignup):
    try:
        existing_user = await get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        user = await create_user(user_data)  # assume this already has checks
        if not user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User creation failed",
            )

        token = sign_jwt(str(user.id))
        return {"msg": "Signup successful", "user": user, "token": token}

    except HTTPException as http_exc:
        raise http_exc

    except PyMongoError as db_exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred during signup",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@auth_router.post("/login")
async def login(user_data: UserLogin):
    try:
        if not user_data.email or not user_data.password:
            raise HTTPException(
                status_code=422, detail="Email and password are required"
            )
        user = await get_user_by_email(user_data.email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if user and await verify_user_password(user, user_data.password):
            user.last_login = datetime.now(
                timezone.utc
            )  # Set last_login to current UTC time
            await user.save()
            token = sign_jwt(str(user.id))
            return {"msg": "Login succesful", "user": user, "token": token}
        raise HTTPException(status_code=401, detail="Invalid credentials")
    except HTTPException as http_exc:
        raise http_exc  # Let FastAPI handle known errors

    except PyMongoError as db_err:
        raise HTTPException(status_code=500, detail="Database error during login")

    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Internal server error during login"
        )

@auth_router.get("/guest_token")
async def guest_token():
    try:
        print("inside guest token")
        token = sign_jwt("guest")
        print("token generated",token)
        return {"msg": "Guest token generated", "token": token}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Internal server error during guest token generation"
        )