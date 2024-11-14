from fastapi import FastAPI, Request
#Body is used for http requests except get
import models
from database import engine
from routers import auth, appointments, billing
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(directory="templates")


app = FastAPI()


models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(appointments.router)
app.include_router(billing.router)


@app.get("/", response_class=HTMLResponse)
async def render_login(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})



