from fastapi import FastAPI
#Body is used for http requests except get
from pydantic import BaseModel, Field

app = FastAPI()

class Appointment:
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
    



@app.get("/")
async def firstapi():
    return ("hey")

# static endpoints go first !
# endpts with dynamic parameters{} go last (space=%)!
# read/get will be an important api-request to use for database queries!
#request body uses exclusively "" for str

list_users = []


APPOINTMENTS = [
    Appointment(1, 0, 1, "29/10/2024", "Might need further tests", "none"),
    Appointment(2, 0, 2, "29/10/2024", "All ok", "none"),
    Appointment(3, 0, 3, "29/11/2024", "Mild headache", "advill"),
    Appointment(3, 0, 3, "29/11/2024", "Severe headache", "benadryll"),
    Appointment(3, 0, 3, "29/11/2024", "Mild headache", "nasal spray")
]


@app.get("/appointments")
async def get_appointments():
    return APPOINTMENTS


@app.post("/create-appointment")
async def create_appointment(appointment_request:AppointmentRequest):
    new_appointment = Appointment(**appointment_request.model_dump())
    APPOINTMENTS.append(find_appointmentid(new_appointment))


def find_appointmentid(appointment: Appointment):
    
    appointment.apnt_id = 1 if len(APPOINTMENTS) == 0 else APPOINTMENTS[-1].apnt_id +1
    
    return appointment


@app.get("/appointments/by-date/")
async def read_apnt_date(date: str):
    a_list = []
    for appointment in APPOINTMENTS:
        if appointment.appointment_date == date:
            a_list.append(appointment)
    return a_list

@app.get("/user-list")
async def get_users():
    return list_users





