from pydantic import BaseModel, EmailStr, condecimal
from datetime import date
from typing import Optional, Literal
from datetime import datetime
from decimal import Decimal

class UserBase(BaseModel):
    user_name: str
    role: Literal["doctor", "patient"]
    dob: date

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    user_id: int
    
    class Config:
        orm_mode = True

class PatientCreate(BaseModel):
    first_name: str
    last_name: str
    gender: Literal["male", "female", "other"]
    phone: str

class DoctorCreate(BaseModel):
    first_name: str
    last_name: str
    phone: str
    specialization: str

# Combined registration schemas
class PatientRegistration(BaseModel):
    user: UserCreate
    patient: PatientCreate

class DoctorRegistration(BaseModel):
    user: UserCreate
    doctor: DoctorCreate

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_name: str | None = None
    role: str | None = None

class UserLogin(BaseModel):
    user_name: str
    password: str

class AppointmentBase(BaseModel):
    doctor_id: int
    appointment_date: datetime

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentUpdate(BaseModel):
    treatment: Optional[str] = None
    diagnosis: Optional[str] = None
    prescription: Optional[str] = None



class BillingBase(BaseModel):
    amount: condecimal(max_digits=10, decimal_places=2)
    
class BillingCreate(BillingBase):
    appointment_id: int

class BillingResponse(BillingBase):
    billing_id: int
    appointment_id: int
    billing_date: date
    
    class Config:
        orm_mode = True

class AppointmentResponse(AppointmentBase):
    appointment_id: int
    patient_id: int
    treatment: Optional[str] = None
    diagnosis: Optional[str] = None
    prescription: Optional[str] = None
    billing: Optional[BillingResponse] = None
    
    class Config:
        orm_mode = True