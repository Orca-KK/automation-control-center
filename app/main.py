from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

from app.routers import jobs
from app.services.scheduler import start_scheduler


app = FastAPI(title="Automation Control Center")

# start background scheduler
start_scheduler()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

app.mount(
    "/static",
    StaticFiles(directory=os.path.join(BASE_DIR, "static")),
    name="static",
)

app.include_router(jobs.router)



@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(
        "base.html",
        {
            "request": request,
            "title": "Automation Control Center",
            "page_title": "Dashboard (Coming Soon)",
            "message": "Your FastAPI app is running correctly.",
        },
    )
