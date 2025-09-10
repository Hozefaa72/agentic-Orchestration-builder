from fastapi import APIRouter,Depends
from app.models.user_info import User_Info
from app.schemas.user_information import UserInformation
from fastapi import HTTPException
from app.auth.auth import get_current_user

router = APIRouter()

@router.post("/insert_user_info")
async def insert_user_info(user_info:UserInformation,thread_id:str,current_user:dict=Depends(get_current_user)):
    try:
        if thread_id:
            print(thread_id)
            user= await User_Info.find_one(User_Info.thread_id == thread_id)
            print(user)
            if user:
                print("inside if")
                user.name=user_info.firstName
                user.phone_number=user_info.mobile
                user.email_id=user_info.email
                user.pincode=user_info.pincode
                user.employment_type=user_info.employmentType
                user.user_address=user_info.address
                user.preffered_center_address=user_info.treatmentLocation
                user.State=user_info.state
                user.pan_number=user_info.pan
                user.aadhar_number=user_info.aadhar

                await user.save()
            else:
                print("inside else")
                new_user=User_Info(
                    name=user_info.firstName,
                    phone_number=user_info.mobile,
                    email_id=user_info.email,
                    pincode=user_info.pincode,
                    employment_type=user_info.employmentType,
                    user_address=user_info.address,
                    preffered_center_address=user_info.treatmentLocation,
                    State=user_info.state,
                    pan_number=user_info.pan,
                    aadhar_number=user_info.aadhar,
                    thread_id=thread_id
                )
                await new_user.insert()
            return {"status_code":200,"message": "User information inserted successfully"}
        else:
            raise HTTPException(status_code=400, detail="thread_id is required")

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error") 