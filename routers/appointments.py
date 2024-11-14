from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

import schemas
import models
from database import get_db
from routers.auth import get_current_user

router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"]
)

# Create appointment (for patients)
@router.post("/", response_model=schemas.AppointmentResponse)
async def create_appointment(
    appointment: schemas.AppointmentCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patients can create appointments"
        )
    
    # Get patient profile
    patient = db.query(models.Patient).filter(models.Patient.user_id == current_user.user_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found"
        )
    
    # Verify doctor exists
    doctor = db.query(models.Doctor).filter(models.Doctor.doctor_id == appointment.doctor_id).first()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )
    
    # Check if appointment time is available
    existing_appointment = db.query(models.Appointment).filter(
        models.Appointment.doctor_id == appointment.doctor_id,
        models.Appointment.appointment_date == appointment.appointment_date
    ).first()
    
    if existing_appointment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This time slot is already booked"
        )
    
    db_appointment = models.Appointment(
        patient_id=patient.patient_id,
        doctor_id=appointment.doctor_id,
        appointment_date=appointment.appointment_date
    )
    
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

# Get appointments for current user (works for both doctors and patients)
@router.get("/my-appointments", response_model=List[schemas.AppointmentResponse])
async def get_my_appointments(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role == "patient":
        patient = db.query(models.Patient).filter(models.Patient.user_id == current_user.user_id).first()
        appointments = db.query(models.Appointment).filter(
            models.Appointment.patient_id == patient.patient_id
        ).all()
    else:  # doctor
        doctor = db.query(models.Doctor).filter(models.Doctor.user_id == current_user.user_id).first()
        appointments = db.query(models.Appointment).filter(
            models.Appointment.doctor_id == doctor.doctor_id
        ).all()
    
    return appointments

# Update appointment (for doctors)
@router.patch("/{appointment_id}", response_model=schemas.AppointmentResponse)
async def update_appointment(
    appointment_id: int,
    appointment_update: schemas.AppointmentUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "doctor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can update appointments"
        )
    
    # Get doctor profile
    doctor = db.query(models.Doctor).filter(models.Doctor.user_id == current_user.user_id).first()
    
    # Get appointment
    db_appointment = db.query(models.Appointment).filter(
        models.Appointment.appointment_id == appointment_id,
        models.Appointment.doctor_id == doctor.doctor_id
    ).first()
    
    if not db_appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Update appointment fields
    for field, value in appointment_update.dict(exclude_unset=True).items():
        setattr(db_appointment, field, value)
    
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

# Get available time slots for a doctor
@router.get("/available-slots/{doctor_id}")
async def get_available_slots(
    doctor_id: int,
    date: datetime,
    db: Session = Depends(get_db)
):
    # Get all appointments for the doctor on the given date
    existing_appointments = db.query(models.Appointment).filter(
        models.Appointment.doctor_id == doctor_id,
        models.Appointment.appointment_date >= date.replace(hour=0, minute=0),
        models.Appointment.appointment_date < date.replace(hour=23, minute=59)
    ).all()
    
    # Create list of booked times
    booked_times = [apt.appointment_date.hour for apt in existing_appointments]
    
    # Assuming working hours are 9 AM to 5 PM
    available_slots = []
    for hour in range(9, 17):
        if hour not in booked_times:
            slot_time = date.replace(hour=hour, minute=0)
            available_slots.append(slot_time)
    
    return {"available_slots": available_slots}



# from fastapi import APIRouter, Depends, HTTPException, Path, Query
# from sqlalchemy.orm import Session
# from sqlalchemy import and_, or_
# from datetime import datetime
# from typing import List, Optional, Annotated
# from pydantic import BaseModel, Field, validator
# from enum import Enum
# from .auth import get_current_user

# router = APIRouter(prefix="/patient/appointments", tags=["patient appointments"])

# class AppointmentStatus(str, Enum):
#     SCHEDULED = "scheduled"
#     COMPLETED = "completed"
#     CANCELLED = "cancelled"

# # Pydantic Models
# class BookAppointmentRequest(BaseModel):
#     doctor_id: int = Field(..., gt=0)
#     appointment_date: str = Field(..., min_length=10, max_length=10)
#     description: Optional[str] = Field(None, max_length=500)

#     @validator('appointment_date')
#     def validate_date_format(cls, v):
#         try:
#             date = datetime.strptime(v, '%Y-%m-%d')
#             if date.date() < datetime.now().date():
#                 raise ValueError("Appointment date cannot be in the past")
#             return v
#         except ValueError as e:
#             raise ValueError("Invalid date format. Use YYYY-MM-DD")

# class AppointmentResponse(BaseModel):
#     apnt_id: int
#     doctor_id: int
#     appointment_date: str
#     description: Optional[str]
#     status: str
#     notes: Optional[str]
#     prescription: Optional[str]
#     doctor_name: Optional[str]

#     class Config:
#         orm_mode = True

# # Dependencies
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# db_dependency = Annotated[Session, Depends(get_db)]
# user_dependency = Annotated[dict, Depends(get_current_user)]

# # Helper Functions
# def check_doctor_availability(db: Session, doctor_id: int, appointment_date: str) -> bool:
#     # Convert string date to datetime
#     date = datetime.strptime(appointment_date, '%Y-%m-%d')
    
#     # Check if doctor exists and is available on that day
#     doctor_schedule = db.query(DoctorSchedule).filter(
#         and_(
#             DoctorSchedule.doctor_id == doctor_id,
#             DoctorSchedule.day_of_week == date.weekday(),
#             DoctorSchedule.is_available == True
#         )
#     ).first()
    
#     if not doctor_schedule:
#         return False
    
#     # Check for existing appointments
#     existing_appointment = db.query(Appointment).filter(
#         and_(
#             Appointment.doctor_id == doctor_id,
#             Appointment.appointment_date == appointment_date,
#             Appointment.status != AppointmentStatus.CANCELLED
#         )
#     ).first()
    
#     return not bool(existing_appointment)

# # Routes
# @router.get("/", response_model=List[AppointmentResponse])
# async def get_patient_appointments(
#     user: user_dependency,
#     db: db_dependency,
#     status: Optional[str] = Query(None, enum=["scheduled", "completed", "cancelled"]),
#     from_date: Optional[str] = Query(None, regex=r'^\d{4}-\d{2}-\d{2}$'),
#     to_date: Optional[str] = Query(None, regex=r'^\d{4}-\d{2}-\d{2}$')
# ):
#     """Get all appointments for the logged-in patient with optional filters"""
#     if not user:
#         raise HTTPException(status_code=401, detail='Authentication Failed')
    
#     query = db.query(Appointment).filter(Appointment.patient_id == user.get('id'))
    
#     if status:
#         query = query.filter(Appointment.status == status)
#     if from_date:
#         query = query.filter(Appointment.appointment_date >= from_date)
#     if to_date:
#         query = query.filter(Appointment.appointment_date <= to_date)
    
#     appointments = query.order_by(Appointment.appointment_date).all()
    
#     # Enhance appointments with doctor information
#     for appt in appointments:
#         doctor = db.query(Doctor).join(User).filter(Doctor.doctor_id == appt.doctor_id).first()
#         if doctor:
#             appt.doctor_name = f"Dr. {doctor.user.first_name} {doctor.user.last_name}"
    
#     return appointments

# @router.get("/available-doctors")
# async def get_available_doctors(
#     user: user_dependency,
#     db: db_dependency,
#     date: str = Query(..., regex=r'^\d{4}-\d{2}-\d{2}$')
# ):
#     """Get list of available doctors for a specific date"""
#     if not user:
#         raise HTTPException(status_code=401, detail='Authentication Failed')
    
#     # Get all doctors with their schedules
#     available_doctors = db.query(Doctor).join(User).join(DoctorSchedule).filter(
#         and_(
#             DoctorSchedule.day_of_week == datetime.strptime(date, '%Y-%m-%d').weekday(),
#             DoctorSchedule.is_available == True
#         )
#     ).all()
    
#     return [{"doctor_id": doc.doctor_id,
#              "name": f"Dr. {doc.user.first_name} {doc.user.last_name}",
#              "specialization": doc.specialization}
#             for doc in available_doctors]

# @router.post("/", status_code=201, response_model=AppointmentResponse)
# async def book_appointment(
#     user: user_dependency,
#     db: db_dependency,
#     appointment: BookAppointmentRequest
# ):
#     """Book a new appointment"""
#     if not user:
#         raise HTTPException(status_code=401, detail='Authentication Failed')
    
#     # Check if doctor exists
#     doctor = db.query(Doctor).filter(Doctor.doctor_id == appointment.doctor_id).first()
#     if not doctor:
#         raise HTTPException(status_code=404, detail="Doctor not found")
    
#     # Check doctor availability
#     if not check_doctor_availability(db, appointment.doctor_id, appointment.appointment_date):
#         raise HTTPException(status_code=400, detail="Selected time slot is not available")
    
#     # Create appointment
#     new_appointment = Appointment(
#         doctor_id=appointment.doctor_id,
#         patient_id=user.get('id'),
#         appointment_date=appointment.appointment_date,
#         description=appointment.description,
#         status=AppointmentStatus.SCHEDULED
#     )
    
#     db.add(new_appointment)
#     db.commit()
#     db.refresh(new_appointment)
#     return new_appointment

# @router.delete("/{appt_id}", status_code=204)
# async def cancel_appointment(
#     user: user_dependency,
#     db: db_dependency,
#     appt_id: int = Path(..., gt=0)
# ):
#     """Cancel an appointment"""
#     if not user:
#         raise HTTPException(status_code=401, detail='Authentication Failed')
    
#     appointment = db.query(Appointment).filter(
#         and_(
#             Appointment.apnt_id == appt_id,
#             Appointment.patient_id == user.get('id')
#         )
#     ).first()
    
#     if not appointment:
#         raise HTTPException(status_code=404, detail="Appointment not found")
    
#     if appointment.status == AppointmentStatus.COMPLETED:
#         raise HTTPException(status_code=400, detail="Cannot cancel a completed appointment")
    
#     # Instead of deleting, mark as cancelled
#     appointment.status = AppointmentStatus.CANCELLED
#     db.commit()