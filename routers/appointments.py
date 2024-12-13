from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session, joinedload
from typing import List
from datetime import datetime

import schemas
import models
from database import get_db
from routers.auth import get_current_user


from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles


templates = Jinja2Templates(directory="templates")


router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"]
)

#Get doctor availability
@router.get("/doctors/{doctor_id}/availability", response_model=schemas.AvailabilityResponse)
async def get_doctor_availability(
    doctor_id: int,
    date: str = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Get doctor from database
    doctor = db.query(models.Doctor).filter(models.Doctor.doctor_id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Get doctor's available days and times
    available_days = doctor.days_list
    available_times = doctor.times_list
    
    print(f"Processed available days for doctor {doctor_id}: {available_days}")
    print(f"Processed available times for doctor {doctor_id}: {available_times}")
    
    if date:
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            day_of_week = date_obj.strftime('%A')
            
            # Check if doctor works on this day
            if day_of_week not in available_days:
                return schemas.AvailabilityResponse(
                    available_days=available_days,
                    available_times=[]
                )
            
            # Get existing appointments for this date
            existing_appointments = db.query(models.Appointment).filter(
                models.Appointment.doctor_id == doctor_id,
                models.Appointment.appointment_date == date
            ).all()
            
            # Remove booked times from available times
            booked_times = set(apt.appointment_time for apt in existing_appointments)
            available_times = [t for t in available_times if t not in booked_times]
        
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format")
    
    return schemas.AvailabilityResponse(
        available_days=available_days,
        available_times=available_times
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
    
    # Validate date and time format
    try:
        date_obj = datetime.strptime(appointment.appointment_date, '%Y-%m-%d')
        time_obj = datetime.strptime(appointment.appointment_time, '%H:%M').time()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date or time format")
    
    # Check if date is in the future
    if date_obj.date() < datetime.now().date():
        raise HTTPException(status_code=400, detail="Cannot book appointments in the past")
    
    # Check if doctor works on this day
    day_of_week = date_obj.strftime('%A')
    if day_of_week not in doctor.available_days:
        raise HTTPException(status_code=400, detail="Doctor is not available on this day")
    

    # Check if appointment time is available
    existing_appointment = db.query(models.Appointment).filter(
        models.Appointment.doctor_id == appointment.doctor_id,
        models.Appointment.appointment_date == appointment.appointment_date,
        models.Appointment.appointment_time == appointment.appointment_time
    ).first()
    
    if existing_appointment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This time slot is already booked"
        )
    
    # Create new appointment
    db_appointment = models.Appointment(
        patient_id=patient.patient_id,
        doctor_id=appointment.doctor_id,
        appointment_date=appointment.appointment_date,

        appointment_time=appointment.appointment_time,
        description=appointment.description
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


@router.get("/all-appointments")
async def get_all_appointments(request: Request, 
                               db: Session = Depends(get_db)):
    doctors = db.query(models.Doctor).all()
    


    appointments = db.query(models.Appointment)\
        .options(joinedload(models.Appointment.patient))\
        .options(joinedload(models.Appointment.doctor))\
        .all()
    
    return templates.TemplateResponse("dashboard.html", {"request": request, "appointments": appointments, "doctors":doctors})

@router.get("/all-doctors")
async def get_all_doctors(request: Request, db: Session = Depends(get_db)):
    doctors = db.query(models.Doctor).all()
    print("Doctors found:", [(d.first_name, d.last_name) for d in doctors])  # Debug print
    patients = db.query(models.Patient).all()
    return templates.TemplateResponse("dashboard.html", {"request": request, "doctors": doctors, "patients":patients})


