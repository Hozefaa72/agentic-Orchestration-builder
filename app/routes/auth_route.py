from fastapi import APIRouter
from app.cruds.user_cruds import get_user_by_email,create_user,verify_user_password
from app.auth.jwt_handler import sign_jwt
from app.schemas.user_schemas import UserLogin, UserSignup
from app.utils.response import create_response
from app.schemas.response import responsemodel

router = APIRouter()

@router.post("/signup",response_model=responsemodel)
async def signup(user_data: UserSignup):
    try:
        existing_user = await get_user_by_email(user_data.email)

        if existing_user:
            return{
                "msg": "email already Registered", "user": existing_user
            }

        user = await create_user(user_data)  

        token = sign_jwt(str(user.id))
        return create_response(
            success=True,
            result={"message":"Sign up Successfull","user": user, "token": token},
            status_code=201
            )


    except Exception as e:
        return create_response(
            success=False,
            error_message="Internal Server error during signup",
            error_detail=str(e),
            status_code=500
        )


@router.post("/login",response_model=responsemodel)
async def login(user_data: UserLogin):
    try:
        user = await get_user_by_email(user_data.email)
        print("the user is",user)
        if user and await verify_user_password(user, user_data.password):
            token = sign_jwt(str(user.id))
            print("before returning the response")
            return create_response(
                success=True,
                result={"message":"Login Successfull","user": user, "token": token},
                status_code=200
            )
            
        else:
            return create_response(
                success=False,
                error_message="Invalid email or password",
                status_code=401
            )

    except Exception as e:
        return create_response(
            success=False,
            error_message="Internal Server error during login",
            error_detail=str(e),
            status_code=500
        )

@router.get("/guest_token",response_model=responsemodel)
async def guest_token():
    try:
        print("inside guest token")
        token = sign_jwt("guest")
        print("token generated",token)
        return create_response(
            success=True,
            result={"message":"Guest token generated Successfully","token": token},
            status_code=200
        )
    except Exception as e:
        return create_response(
            success=False,
            error_message="Internal Server error during guest token generation",
            error_detail=str(e),
            status_code=500
        )