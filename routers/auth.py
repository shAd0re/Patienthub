from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models
import schemas
from security import (
    verify_password,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    SECRET_KEY,
    ALGORITHM
)
from database import get_db
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str):
    return pwd_context.hash(password)

@router.post("/register/patient", response_model=schemas.UserResponse)
def register_patient(
    registration_data: schemas.PatientRegistration,
    db: Session = Depends(get_db)
):
    # Check if username already exists
    db_user = db.query(models.User).filter(
        models.User.user_name == registration_data.user.user_name
    ).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Create user
    db_user = models.User(
        user_name=registration_data.user.user_name,
        password=get_password_hash(registration_data.user.password),
        role="patient",
        dob=registration_data.user.dob
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create patient profile
    db_patient = models.Patient(
        user_id=db_user.user_id,
        first_name=registration_data.patient.first_name,
        last_name=registration_data.patient.last_name,
        gender=registration_data.patient.gender,
        phone=registration_data.patient.phone
    )
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    
    return db_user

@router.post("/register/doctor", response_model=schemas.UserResponse)
def register_doctor(
    registration_data: schemas.DoctorRegistration,
    db: Session = Depends(get_db)
):
    # Check if username already exists
    db_user = db.query(models.User).filter(
        models.User.user_name == registration_data.user.user_name
    ).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Create user
    db_user = models.User(
        user_name=registration_data.user.user_name,
        password=get_password_hash(registration_data.user.password),
        role="doctor",
        dob=registration_data.user.dob
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create doctor profile
    db_doctor = models.Doctor(
        user_id=db_user.user_id,
        first_name=registration_data.doctor.first_name,
        last_name=registration_data.doctor.last_name,
        phone=registration_data.doctor.phone,
        specialization=registration_data.doctor.specialization
    )
    db.add(db_doctor)
    db.commit()
    db.refresh(db_doctor)
    
    return db_user

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_name: str = payload.get("sub")
        if user_name is None:
            raise credentials_exception
        token_data = schemas.TokenData(user_name=user_name)
    except JWTError:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.user_name == token_data.user_name).first()
    if user is None:
        raise credentials_exception
    return user


@router.post("/login", response_model=schemas.Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Find user by username
    user = db.query(models.User).filter(models.User.user_name == form_data.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.user_name, "role": user.role},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Example of protected route
@router.get("/me", response_model=schemas.UserResponse)
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user