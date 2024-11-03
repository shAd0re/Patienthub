from fastapi import FastAPI, Query, HTTPException, Depends, Path
#Body is used for http requests except get
from pydantic import BaseModel, Field
import starlette.status
import models
from models import Appointment
from database import engine, SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
import starlette

app = FastAPI()


models.Base.metadata.create_all(bind=engine)

class Appointments:
    apnt_id: int
    doctor_id: int
    patient_id: int
    appointment_date: str
    notes: str
    prescrition: str
    
    

    def __init__(self, apnt_id, doctor_id, patient_id, appointment_date, notes, prescrition ):
        self.apnt_id = apnt_id
        self.doctor_id = doctor_id
        self.patient_id = patient_id
        self.appointment_date = appointment_date
        self.notes = notes
        self.prescrition = prescrition


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

list_users = []


APPOINTMENTS = [
    Appointments(1, 0, 1, "29/10/2024", "Might need further tests", "none"),
    Appointments(2, 0, 2, "29/10/2024", "All ok", "none"),
    Appointments(3, 0, 3, "29/11/2024", "Mild headache", "advill"),
    Appointments(3, 0, 3, "29/11/2024", "Severe headache", "benadryll"),
    Appointments(3, 0, 3, "29/11/2024", "Mild headache", "nasal spray")
]


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



@app.get("/", status_code= starlette.status.HTTP_200_OK)
async def dbget_appointments(db: db_dependency):
    return db.query(Appointment).all()


@app.get("/dbappointments/{appointment_id}", status_code= starlette.status.HTTP_200_OK)
async def dbget_appointments(db: db_dependency, appointment_id: int = Path(gt=0)):
    apnmt_model = db.query(Appointment).filter(Appointment.apnt_id == appointment_id).first()
    if apnmt_model is not None:
        return apnmt_model
    raise HTTPException(status_code=404, detail='Not found')


@app.post("/dbappointmet-post", status_code= starlette.status.HTTP_201_CREATED)
async def create_dbap(db: db_dependency, appointment_req: DBAppointmentRequest):
    app_model = Appointment(**appointment_req.dict())

    db.add(app_model)
    db.commit()


@app.put("/appointment/{appt_id}", status_code= starlette.status.HTTP_204_NO_CONTENT)
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


@app.delete("/appointment/{appt_id}", status_code= starlette.status.HTTP_204_NO_CONTENT)
async def delete_appt(db:db_dependency, 
                      appt_id: int = Path(gt=0)):
     app_model = db.query(Appointment).filter(Appointment.apnt_id == appt_id).first()
     if app_model is None:
         raise HTTPException(status_code=404, detail="Appointment not found")
     db.query(Appointment).filter(Appointment.apnt_id == appt_id).delete()

     db.commit()

    


#Appointment for db
#dbms



@app.get("/appointments")
async def get_appointments():
    return APPOINTMENTS


@app.post("/create-appointment")
async def create_appointment(appointment_request:AppointmentRequest):
    new_appointment = Appointments(**appointment_request.model_dump())
    APPOINTMENTS.append(find_appointmentid(new_appointment))


def find_appointmentid(appointment: Appointments):
    
    appointment.apnt_id = 1 if len(APPOINTMENTS) == 0 else APPOINTMENTS[-1].apnt_id +1
    
    return appointment


@app.get("/appointments/by-date/")
async def read_apnt_date(date: str = Query(min_length=10, max_length=10)):
    a_list = []
    for appointment in APPOINTMENTS:
        if appointment.appointment_date == date:
            a_list.append(appointment)
    return a_list

@app.get("/user-list")
async def get_users():
    return list_users





