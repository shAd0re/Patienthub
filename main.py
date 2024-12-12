from fastapi import FastAPI, Request
#Body is used for http requests except get
import models
from database import engine
from routers import auth, appointments, billing
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os


templates = Jinja2Templates(directory="templates")


app = FastAPI()


app.mount("/static", StaticFiles(directory="static"), name="static")


models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(appointments.router)
app.include_router(billing.router)


@app.get("/", response_class=HTMLResponse)
async def render_login(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "hide_navbar": True})

@app.get("/doctor-db", response_class=HTMLResponse)
async def render_docdb(request: Request):
    return templates.TemplateResponse("doctor_db.html", {"request": request})


@app.get("/doc", response_class=HTMLResponse)
async def doctor_db(request: Request):
    return templates.TemplateResponse("doctor_db.html", {"request": request})


# @app.get("/", response_class=HTMLResponse)
# async def render_login(request: Request):
#     return templates.TemplateResponse("register.html", {"request": request, "hide_navbar": True})

# @app.get("/", response_class=HTMLResponse)
# async def render_login(request: Request):
#     return templates.TemplateResponse("index&register.html", {"request": request, "hide_navbar": True})


