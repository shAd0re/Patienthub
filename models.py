from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, DateTime, Float, JSON
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
    available_days = Column(String)
    available_times = Column(String)

    # Relationships
    user = relationship("User", back_populates="doctor")
    appointments = relationship("Appointment", back_populates="doctor")

    @property
    def days_list(self):
        """Convert JSON string to list for available_days"""
        try:
            if not self.available_days:
                return []
            
            # Remove any extra quotes and spaces
            cleaned_string = self.available_days.strip('"\'').replace('\\', '')
            # If the string is already in list format, evaluate it
            if cleaned_string.startswith('[') and cleaned_string.endswith(']'):
                import ast
                return ast.literal_eval(cleaned_string)
            # If it's a comma-separated string, split it
            return [day.strip() for day in cleaned_string.split(',')]
        except Exception as e:
            print(f"Error parsing days for doctor {self.doctor_id}: {e}")
            print(f"Raw string was: {self.available_days}")
            return []

    @property
    def times_list(self):
        """Convert JSON string to list for available_times"""
        try:
            if not self.available_times:
                return []
            
            # Remove any extra quotes and spaces
            cleaned_string = self.available_times.strip('"\'').replace('\\', '')
            # If the string is already in list format, evaluate it
            if cleaned_string.startswith('[') and cleaned_string.endswith(']'):
                import ast
                return ast.literal_eval(cleaned_string)
            # If it's a comma-separated string, split it
            return [time.strip() for time in cleaned_string.split(',')]
        except Exception as e:
            print(f"Error parsing times for doctor {self.doctor_id}: {e}")
            print(f"Raw string was: {self.available_times}")
            return []
        
class Appointment(Base):
    __tablename__ = "appointments"

    appointment_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.patient_id"))
    doctor_id = Column(Integer, ForeignKey("doctors.doctor_id"))
    appointment_date = Column(String)  # YYYY-MM-DD
    appointment_time = Column(String)  # HH:MM
    description = Column(String, nullable=True)
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