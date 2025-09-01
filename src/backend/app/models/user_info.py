from beanie import Document
from pydantic import EmailStr, Field
from datetime import datetime,timezone
from typing import Optional
from enum import Enum

class AppointmentStatus(str, Enum):
    BOOKED = "booked"
    NOT_BOOKED = "not_booked"
    IN_PROCESS = "in_process"

class User_Info(Document):

    name: Optional[str] = None
    phone_number: Optional[str] = None
    pincode:Optional[str] = None
    address: Optional[str] = None
    City: Optional[str] = None
    State: Optional[str] = None
    preffered_center:Optional[list]=[]
    checkup_date:Optional[str]=None
    checkup_time_slot:Optional[str]=None
    appointment_status:AppointmentStatus = AppointmentStatus.NOT_BOOKED
    thread_id:str

    class Settings:
        name = "user_information"
