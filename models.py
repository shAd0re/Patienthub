from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, DateTime, Float
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String)  # 'doctor' or 'patient'
    dob = Column(Date)
    
    # Relationships
    patient = relationship("Patient", back_populates="user", uselist=False)
    doctor = relationship("Doctor", back_populates="user", uselist=False)

class Patient(Base):
    __tablename__ = "patients"

    patient_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    first_name = Column(String)
    last_name = Column(String)
    gender = Column(String)
    phone = Column(String)
    
    # Relationships
    user = relationship("User", back_populates="patient")
    appointments = relationship("Appointment", back_populates="patient")

class Doctor(Base):
    __tablename__ = "doctors"

    doctor_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    first_name = Column(String)
    last_name = Column(String)
    phone = Column(String)
    specialization = Column(String)
    
    # Relationships
    user = relationship("User", back_populates="doctor")
    appointments = relationship("Appointment", back_populates="doctor")

class Appointment(Base):
    __tablename__ = "appointments"

    appointment_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.patient_id"))
    doctor_id = Column(Integer, ForeignKey("doctors.doctor_id"))
    appointment_date = Column(DateTime)
    treatment = Column(String, nullable=True)
    diagnosis = Column(String, nullable=True)
    prescription = Column(String, nullable=True)
    
    # Relationships
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
    billing = relationship("Billing", back_populates="appointment", uselist=False)

class Billing(Base):
    __tablename__ = "billings"

    billing_id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.appointment_id"))
    billing_date = Column(Date)
    amount = Column(Float)
    
    # Relationship
    appointment = relationship("Appointment", back_populates="billing")