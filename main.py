from fastapi import FastAPI
#Body is used for http requests except get
import models
from database import engine
from routers import auth, appointments

app = FastAPI()


models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(appointments.router)

