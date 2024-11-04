from fastapi import APIRouter, Query, HTTPException, Depends, Path
#Body is used for http requests except get
from pydantic import BaseModel, Field
import starlette.status
from models import Appointment
from database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
import starlette


router = APIRouter()



class AppointmentRequest(BaseModel):
    apnt_id: int = None
    doctor_id: int
    patient_id: int
    appointment_date: str = Field(min_length=10, max_length=10)
    notes: str = Field(max_length= 120)
    prescrition: str
    





# static endpoints go first !
# endpts with dynamic parameters{} go last (space=%)!
# read/get will be an important api-request to use for database queries!
#request body uses exclusively "" for str



#dbms
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


class DBAppointmentRequest(BaseModel):
    doctor_id: int
    patient_id: int
    appointment_date: str = Field(min_length=10, max_length=10)
    notes: str = Field(max_length= 120)
    prescrition: str



@router.get("/", status_code= starlette.status.HTTP_200_OK)
async def dbget_appointments(db: db_dependency):
    return db.query(Appointment).all()


@router.get("/dbappointments/{appointment_id}", status_code= starlette.status.HTTP_200_OK)
async def dbget_appointments(db: db_dependency, appointment_id: int = Path(gt=0)):
    apnmt_model = db.query(Appointment).filter(Appointment.apnt_id == appointment_id).first()
    if apnmt_model is not None:
        return apnmt_model
    raise HTTPException(status_code=404, detail='Not found')


@router.post("/dbappointmet-post", status_code= starlette.status.HTTP_201_CREATED)
async def create_dbap(db: db_dependency, appointment_req: DBAppointmentRequest):
    app_model = Appointment(**appointment_req.dict())

    db.add(app_model)
    db.commit()


@router.put("/appointment/{appt_id}", status_code= starlette.status.HTTP_204_NO_CONTENT)
async def update_appt(db:db_dependency,  
                      appointment_req: DBAppointmentRequest,
                      appt_id: int = Path(gt=0)):
     app_model = db.query(Appointment).filter(Appointment.apnt_id == appt_id).first()
     if app_model is None:
         raise HTTPException(status_code=404, detail="Appointment not found")
     
    #  app_model.doctor_id = appointment_req.doctor_id
    #  app_model.patient_id = appointment_req.patient_id
     app_model.appointment_date = appointment_req.appointment_date
     app_model.prescrition = appointment_req.prescrition
     app_model.notes = appointment_req.notes
     

     db.add(app_model)
     db.commit()


@router.delete("/appointment/{appt_id}", status_code= starlette.status.HTTP_204_NO_CONTENT)
async def delete_appt(db:db_dependency, 
                      appt_id: int = Path(gt=0)):
     app_model = db.query(Appointment).filter(Appointment.apnt_id == appt_id).first()
     if app_model is None:
         raise HTTPException(status_code=404, detail="Appointment not found")
     db.query(Appointment).filter(Appointment.apnt_id == appt_id).delete()

     db.commit()

    


#Appointment for db
#dbms