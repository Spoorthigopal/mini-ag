from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class InternshipJobResponse(BaseModel):
    id: str
    job_title: str
    company_name: str
    company_rating: Optional[float] = None
    location: str
    job_description: str
    stipend: Optional[float] = None
    duration_months: Optional[int] = None
    job_type: str
    required_skills: Optional[List[str]] = None
    application_url: Optional[str] = None
    posted_date: Optional[str] = None
    application_deadline: Optional[str] = None
    job_status: str
    match_score: Optional[float] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "job_title": "Python Backend Intern",
                "company_name": "TechCorp",
                "company_rating": 4.5,
                "location": "Bangalore",
                "job_description": "Build scalable APIs using FastAPI",
                "stipend": 30000,
                "duration_months": 3,
                "job_type": "internship",
                "required_skills": ["Python", "FastAPI", "PostgreSQL"],
                "application_url": "https://apply.techcorp.com",
                "job_status": "active",
                "match_score": 85.0
            }
        }


class InternshipFilterParams(BaseModel):
    company_name: Optional[str] = None
    location: Optional[str] = None
    stipend_min: Optional[float] = None
    stipend_max: Optional[float] = None
    duration_months: Optional[int] = None
    skills: Optional[List[str]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "company_name": "Google",
                "location": "Bangalore",
                "stipend_min": 20000,
                "stipend_max": 100000,
                "duration_months": 3,
                "skills": ["Python", "React"]
            }
        }


class ResumeUploadResponse(BaseModel):
    message: str
    skills_extracted: List[str]
    experience_years: int
    education: str
    file_name: str


class InternshipChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    session_id: Optional[str] = None
    filters: Optional[InternshipFilterParams] = None

    class Config:
        json_schema_extra = {
            "example": {
                "query": "What internships are available for Python developers?",
                "session_id": "conv-456",
                "filters": {"location": "Bangalore"}
            }
        }


class InternshipChatResponse(BaseModel):
    response: str
    jobs: List[InternshipJobResponse]
    session_id: str

    class Config:
        json_schema_extra = {
            "example": {
                "response": "Here are the best internships for Python developers...",
                "jobs": [],
                "session_id": "conv-456"
            }
        }
