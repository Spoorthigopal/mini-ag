from sqlalchemy import Column, String, Float, DateTime, Text, JSON, ARRAY, Integer
from sqlalchemy.sql import func
from app.database import Base
import uuid


class InternshipJob(Base):
    __tablename__ = "internship_jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_title = Column(String(255), nullable=False, index=True)
    company_name = Column(String(255), nullable=False, index=True)
    company_rating = Column(Float, nullable=True)
    location = Column(String(255), nullable=False, index=True)
    job_description = Column(Text, nullable=False)
    stipend = Column(Float, nullable=True)
    duration_months = Column(Integer, nullable=True)
    job_type = Column(String(50), nullable=False)
    required_skills = Column(ARRAY(String), nullable=True)
    preferred_qualifications = Column(ARRAY(String), nullable=True)
    application_url = Column(String(500), nullable=True)
    jsearch_job_id = Column(String(255), unique=True, nullable=True, index=True)
    posted_date = Column(String(50), nullable=True)
    application_deadline = Column(String(50), nullable=True)
    job_status = Column(String(50), default="active", nullable=False)
    embedding_vector = Column(ARRAY(Float), nullable=True)
    embedding_text = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<InternshipJob id={self.id} title={self.job_title} company={self.company_name}>"
