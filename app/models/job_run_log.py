from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class JobRunLog(Base):
    __tablename__ = "job_run_logs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("automation_jobs.id"), nullable=False)

    status = Column(String, nullable=False)  # e.g. "success" or "failed"
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True))
    message = Column(String)
    output = Column(Text)

    job = relationship("AutomationJob", back_populates="runs")
