from fastapi import APIRouter
from pydantic import BaseModel
from models import Patient
router = APIRouter()


class CreatePatient(BaseModel):
    user_name: str
    first_name: str
    last_name: str
    DOB: str
    gender: str
    phone: str
    password: str


class CreateDoctor(BaseModel):
    user_name: str
    first_name: str
    last_name: str
    DOB: str
    specialization: str
    phone: str
    password: str

@router.post("/auth/")
async def create_patient(cr_patient: CreatePatient):
    patient_model = Patient(
        user_name = cr_patient.user_name,
        first_name = cr_patient.first_name,
        last_name = cr_patient.last_name,
        DOB = cr_patient.DOB,
        gender = cr_patient.gender,
        phone = cr_patient.phone,
        hashed_password = cr_patient.password
    )

    return patient_model