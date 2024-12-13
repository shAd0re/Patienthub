from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date

import models
import schemas
from database import get_db
from routers.auth import get_current_user

router = APIRouter(
    prefix="/billing",
    tags=["Billing"]
)

@router.post("/", response_model=schemas.BillingResponse)
async def create_bill(
    billing: schemas.BillingCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify user is a doctor
    if current_user.role != "doctor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can create bills"
        )
    
    # Get doctor profile
    doctor = db.query(models.Doctor).filter(models.Doctor.user_id == current_user.user_id).first()
    
    # Verify appointment exists and belongs to the doctor
    appointment = db.query(models.Appointment).filter(
        models.Appointment.appointment_id == billing.appointment_id,
        models.Appointment.doctor_id == doctor.doctor_id
    ).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Check if bill already exists
    existing_bill = db.query(models.Billing).filter(
        models.Billing.appointment_id == billing.appointment_id
    ).first()
    
    if existing_bill:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bill already exists for this appointment"
        )
    
    # Create bill
    db_billing = models.Billing(
        appointment_id=billing.appointment_id,
        amount=billing.amount,
        billing_date=date.today()
    )
    
    db.add(db_billing)
    db.commit()
    db.refresh(db_billing)
    return db_billing

@router.get("/my-bills", response_model=List[schemas.BillingResponse])
async def get_my_bills(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role == "patient":
        patient = db.query(models.Patient).filter(models.Patient.user_id == current_user.user_id).first()
        bills = db.query(models.Billing).join(models.Appointment).filter(
            models.Appointment.patient_id == patient.patient_id
        ).all()
    else:  # doctor
        doctor = db.query(models.Doctor).filter(models.Doctor.user_id == current_user.user_id).first()
        bills = db.query(models.Billing).join(models.Appointment).filter(
            models.Appointment.doctor_id == doctor.doctor_id
        ).all()
    
    return bills

@router.get("/{billing_id}", response_model=schemas.BillingResponse)
async def get_bill(
    billing_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    bill = db.query(models.Billing).filter(models.Billing.billing_id == billing_id).first()
    if not bill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bill not found"
        )
    
    # Get associated appointment
    appointment = db.query(models.Appointment).filter(
        models.Appointment.appointment_id == bill.appointment_id
    ).first()
    
    # Verify user has access to this bill
    if current_user.role == "patient":
        patient = db.query(models.Patient).filter(models.Patient.user_id == current_user.user_id).first()
        if appointment.patient_id != patient.patient_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this bill"
            )
    else:  # doctor
        doctor = db.query(models.Doctor).filter(models.Doctor.user_id == current_user.user_id).first()
        if appointment.doctor_id != doctor.doctor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this bill"
            )
    
    return bill