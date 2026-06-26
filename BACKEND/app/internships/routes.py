from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.shared.dependencies import get_current_user
from app.auth.models import User
from app.internships.schemas import (
    InternshipJobResponse, InternshipChatRequest, InternshipChatResponse,
    InternshipFilterParams, ResumeUploadResponse
)
from app.internships.service import get_filtered_jobs, chat_with_internship_bot, sync_jobs_from_jsearch
from app.internships.resume_parser import resume_parser
from app.internships.models import InternshipJob
from typing import List, Optional
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/internships", tags=["internships"])


@router.get("/jobs", response_model=List[InternshipJobResponse])
async def get_jobs(
    company_name: Optional[str] = None,
    location: Optional[str] = None,
    stipend_min: Optional[float] = None,
    stipend_max: Optional[float] = None,
    duration_months: Optional[int] = None,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get internship jobs with optional filters.

    Query parameters:
    - company_name: Filter by company
    - location: Filter by city/location
    - stipend_min/stipend_max: Stipend range
    - duration_months: Maximum duration
    """
    try:
        filters = InternshipFilterParams(
            company_name=company_name,
            location=location,
            stipend_min=stipend_min,
            stipend_max=stipend_max,
            duration_months=duration_months
        )
        jobs = get_filtered_jobs(db, filters)
        return jobs[skip: skip + limit]
    except Exception as e:
        logger.error(f"Get jobs error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch jobs")


@router.get("/jobs/{job_id}", response_model=InternshipJobResponse)
async def get_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific internship job by ID."""
    job = db.query(InternshipJob).filter(InternshipJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("/search_live")
async def search_live_jsearch(
    query: str,
    limit: int = 10,
    current_user: User = Depends(get_current_user)
):
    """Live search using JSearch API."""
    from app.internships.jsearch_client import jsearch_client
    try:
        raw_jobs = jsearch_client.query_jsearch(query, limit=limit)
        results = []
        for raw in raw_jobs:
            parsed = jsearch_client.parse_job_listing(raw)
            # Ensure id exists for frontend mapping
            parsed["id"] = parsed.get("jsearch_job_id") or str(uuid.uuid4())
            results.append(parsed)
        return results
    except Exception as e:
        logger.error(f"Live search error: {e}")
        raise HTTPException(status_code=500, detail="Search failed")


@router.post("/upload-resume", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload and parse a resume PDF.
    Returns extracted skills, experience and education.
    """
    try:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are accepted")

        contents = await file.read()
        resume_text = resume_parser.parse_pdf_resume(contents)
        skills = resume_parser.extract_skills(resume_text)
        experience_years = resume_parser.extract_experience_years(resume_text)
        education = resume_parser.extract_education(resume_text)

        return ResumeUploadResponse(
            message="Resume parsed successfully",
            skills_extracted=skills,
            experience_years=experience_years,
            education=education,
            file_name=file.filename
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Resume upload error: {e}")
        raise HTTPException(status_code=500, detail="Resume parsing failed")


@router.post("/chat", response_model=InternshipChatResponse)
async def internship_chat(
    request: InternshipChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Chat with internship career advisor (Gemini + Pinecone RAG).

    Request body:
    - query: Question about internships or career advice
    - session_id: Optional conversation session ID
    - filters: Optional job filters
    """
    try:
        response, retrieved_jobs, session_id = chat_with_internship_bot(
            user_query=request.query,
            filters=request.filters
        )

        # Build job responses from Pinecone metadata + DB lookup
        job_ids = [j["id"] for j in retrieved_jobs]
        db_jobs = db.query(InternshipJob).filter(InternshipJob.id.in_(job_ids)).all()

        # Add match scores
        score_map = {j["id"]: j.get("match_score", 0) for j in retrieved_jobs}
        job_responses = []
        for job in db_jobs:
            job_resp = InternshipJobResponse.model_validate(job)
            job_resp.match_score = score_map.get(job.id)
            job_responses.append(job_resp)

        return InternshipChatResponse(
            response=response,
            jobs=job_responses[:5],
            session_id=request.session_id or str(uuid.uuid4())
        )
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Chat failed")


@router.post("/sync")
async def sync_jobs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Trigger manual sync of jobs from JSearch API."""
    try:
        sync_jobs_from_jsearch(db)
        total = db.query(InternshipJob).count()
        return {"message": "Jobs synced successfully", "total_jobs": total}
    except Exception as e:
        logger.error(f"Sync error: {e}")
        raise HTTPException(status_code=500, detail="Sync failed")
