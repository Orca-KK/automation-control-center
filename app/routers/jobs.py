from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.automation_job import AutomationJob
from app.models.job_run_log import JobRunLog
from app.services.scheduler import run_job

# ✅ ONE router only (do not redefine this again later)
router = APIRouter(prefix="/jobs", tags=["jobs"])

templates = Jinja2Templates(directory="app/templates")


# -----------------------------
# UI Routes
# -----------------------------
@router.get("/ui", response_class=HTMLResponse)
def jobs_ui(request: Request):
    return templates.TemplateResponse(
        "jobs.html",
        {"request": request, "title": "Automation Jobs"},
    )


@router.get("/logs/ui", response_class=HTMLResponse)
def logs_ui(request: Request):
    return templates.TemplateResponse(
        "logs.html",
        {"request": request, "title": "Job Logs"},
    )


# -----------------------------
# Pydantic Schemas
# -----------------------------
class JobBase(BaseModel):
    name: str
    description: str | None = None
    schedule: str
    job_type: str
    target: str | None = None
    is_active: bool = True


class JobCreate(JobBase):
    owner_id: int | None = None


class JobRead(JobBase):
    id: int

    class Config:
        from_attributes = True


class LogRead(BaseModel):
    id: int
    job_id: int
    status: str
    started_at: str | None = None
    output: str | None = None

    class Config:
        from_attributes = True


# -----------------------------
# API Routes
# -----------------------------
@router.get("/", response_model=List[JobRead])
def list_jobs(db: Session = Depends(get_db)):
    return db.query(AutomationJob).order_by(AutomationJob.id.asc()).all()


@router.post("/", response_model=JobRead)
def create_job(job: JobCreate, db: Session = Depends(get_db)):
    data = job.dict()

    # ✅ Default owner_id if your app has no login/auth yet
    if data.get("owner_id") is None:
        data["owner_id"] = 1

    db_job = AutomationJob(**data)
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job



@router.delete("/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(AutomationJob).filter(AutomationJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(job)
    db.commit()
    return {"ok": True}


# ✅ Manual run endpoint (this is what your Run button calls)
@router.post("/{job_id}/run")
def run_job_now(job_id: int, db: Session = Depends(get_db)):
    job = db.query(AutomationJob).filter(AutomationJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if not job.is_active:
        raise HTTPException(status_code=400, detail="Job is inactive")

    run_job(job, db)
    return {"ok": True, "message": f"Job {job_id} executed"}


@router.get("/logs")
def get_logs(limit: int = 50, db: Session = Depends(get_db)):
    logs = (
        db.query(JobRunLog)
        .order_by(JobRunLog.id.desc())
        .limit(limit)
        .all()
    )
    return logs
