from database import Base
from sqlalchemy import Column, Integer, String, ForeignKey

class Appointment(Base):
    __tablename__ = 'appointments'
    apnt_id =  Column(Integer, primary_key=True, index=True)
    doctor_id =  Column(Integer, ForeignKey("doctors.doctor_id"))
    patient_id =  Column(Integer, ForeignKey("patients.patient_id"))
    appointment_date = Column(String)
    notes = Column(String)
    prescrition = Column(String)
    

class Patient(Base):
    __tablename__ = 'patients'
    patient_id =  Column(Integer, primary_key=True, index=True)
    user_name = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    DOB = Column(String)
    gender = Column(String)
    phone = Column(String)
    hashed_password = Column(String)

class Doctor(Base):
    __tablename__ = 'doctors'
    doctor_id =  Column(Integer, primary_key=True, index=True)
    user_name = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    DOB = Column(String)
    specialization = Column(String)
    phone = Column(String)
    hashed_password = Column(String)


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String)
    user_name = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    DOB = Column(String)
    gender = Column(String)
    phone = Column(String)