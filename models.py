from database import Base
from sqlalchemy import Column, Integer, String

class Appointment(Base):
    __tablename__ = 'appointments'
    apnt_id: int =  Column(Integer, primary_key=True, index=True)
    doctor_id: int =  Column(Integer)
    patient_id: int =  Column(Integer)
    appointment_date: str = Column(String)
    notes: str = Column(String)
    prescrition: str = Column(String)
    

class Patient(Base):
    __tablename__ = 'patients'
    patient_id: int =  Column(Integer, primary_key=True, index=True)
    user_id: str = Column(String)
    user_name: str = Column(String)
    first_name: str = Column(String)
    last_name: str = Column(String)
    DOB: str = Column(String)
    gender: str = Column(String)
    phone: str = Column(String)

class Doctor(Base):
    __tablename__ = 'doctors'
    doctor_id: int =  Column(Integer, primary_key=True, index=True)
    user_id: str = Column(String)
    user_name: str = Column(String)
    first_name: str = Column(String)
    last_name: str = Column(String)
    DOB: str = Column(String)
    specialization: str = Column(String)
    phone: str = Column(String)

