from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class AutomationJob(Base):
    __tablename__ = "automation_jobs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    schedule = Column(String, nullable=False)   # e.g. "every_5_minutes"
    job_type = Column(String, nullable=False)   # e.g. "http_ping", "script"
    target = Column(String)                     # URL or script path

    is_active = Column(Boolean, default=True)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_run_at = Column(DateTime(timezone=True))

    owner = relationship("User", back_populates="jobs")
    runs = relationship("JobRunLog", back_populates="job", cascade="all, delete-orphan")
