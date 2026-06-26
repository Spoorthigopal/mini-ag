from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.shared.dependencies import get_current_user
from app.auth.models import User
from app.interview.models import InterviewSession, InterviewFeedback
from app.interview.schemas import (
    InterviewStartRequest,
    InterviewAnswerRequest,
    InterviewMessage,
    InterviewFeedback as FeedbackSchema,
    InterviewSessionResponse,
    InterviewAnswerResponse,
    InterviewSummary
)
from app.interview.service import (
    start_interview, process_answer, get_session_summary,
    generate_study_plan, teach_topic, handle_interaction, resume_session
)
from typing import List, Optional
from pydantic import BaseModel
import time
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/interview", tags=["interview"])

# Rate Limit Storage
# Key: user_id, Value: list of timestamps of requests within the last minute
rate_limit_store = {}


def check_rate_limit(user_id: str, limit: int = 5, period: int = 60) -> bool:
    """
    Checks if a user has exceeded rate limits (5 requests/minute).
    """
    now = time.time()
    if user_id not in rate_limit_store:
        rate_limit_store[user_id] = []
    
    # Filter out timestamps older than the period
    rate_limit_store[user_id] = [t for t in rate_limit_store[user_id] if now - t < period]
    
    if len(rate_limit_store[user_id]) >= limit:
        return False
        
    rate_limit_store[user_id].append(now)
    return True


class FeedbackSummaryWithDetails(BaseModel):
    summary: InterviewSummary
    feedback: List[FeedbackSchema]


# ENDPOINT 1: POST /api/interview/start
@router.post(
    "/start",
    response_model=InterviewSessionResponse,
    status_code=status.HTTP_200_OK
)
async def start_session(
    request: InterviewStartRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Start a new interview session.
    """
    logger.info(f"User {current_user.id} requested to start interview for job {request.job_id}")
    
    # Rate Limit Validation
    if not check_rate_limit(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Maximum 5 requests per minute allowed."
        )

    try:
        result = await start_interview(
            user_id=current_user.id,
            job_id=request.job_id,
            db=db
        )
        return InterviewSessionResponse(
            session_id=result["session_id"],
            message="Interview session started successfully.",
            question=result["question"]
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error starting interview session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate mock interview session"
        )


# ENDPOINT 2: POST /api/interview/answer
@router.post(
    "/answer",
    response_model=InterviewAnswerResponse,
    status_code=status.HTTP_200_OK
)
async def submit_answer(
    request: InterviewAnswerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit candidate answer to current interview question.
    """
    logger.info(f"User {current_user.id} submitted answer for session {request.session_id}")
    
    # Rate Limit Validation
    if not check_rate_limit(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Maximum 5 requests per minute allowed."
        )

    # Validate session exists and belongs to user
    session = db.query(InterviewSession).filter(
        InterviewSession.session_id == request.session_id
    ).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview session not found"
        )
    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: Session belongs to a different candidate."
        )

    try:
        res = await process_answer(
            session_id=request.session_id,
            user_answer=request.answer,
            db=db
        )
        
        return InterviewAnswerResponse(
            session_id=res["session_id"],
            next_question=res["next_question"],
            feedback=res["feedback"],
            interview_complete=res["interview_complete"],
            message="Interview completed." if res["interview_complete"] else "Response processed successfully."
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error processing answer for session {request.session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process interview response"
        )


# ENDPOINT 3: GET /api/interview/feedback
@router.get(
    "/feedback",
    response_model=FeedbackSummaryWithDetails,
    status_code=status.HTTP_200_OK
)
async def get_feedback(
    sessionId: str = Query(..., alias="sessionId", description="Interview Session ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve aggregated metrics and single feedback records for a completed/active interview.
    """
    logger.info(f"User {current_user.id} requested feedback summary for session {sessionId}")

    # Validate session ownership
    session = db.query(InterviewSession).filter(
        InterviewSession.session_id == sessionId
    ).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview session not found"
        )
    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: Session belongs to a different candidate."
        )

    try:
        # Get metrics summary
        summary = await get_session_summary(session_id=sessionId, db=db)
        
        # Get detailed feedback list
        feedback_list = db.query(InterviewFeedback).filter(
            InterviewFeedback.session_id == sessionId
        ).order_by(InterviewFeedback.created_at.asc()).all()

        return FeedbackSummaryWithDetails(
            summary=InterviewSummary(**summary),
            feedback=feedback_list
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error compiling session feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate feedback summary"
        )


# ENDPOINT 4: GET /api/interview/history
@router.get(
    "/history",
    response_model=List[InterviewMessage],
    status_code=status.HTTP_200_OK
)
async def get_history(
    sessionId: str = Query(..., alias="sessionId", description="Interview Session ID"),
    skip: int = Query(0, ge=0, description="Pagination skip offset"),
    limit: int = Query(10, ge=1, le=100, description="Pagination page size limit"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Fetch paginated chat messages from session history (newest first).
    """
    logger.info(f"User {current_user.id} requested chat history for session {sessionId}")

    # Validate session ownership
    session = db.query(InterviewSession).filter(
        InterviewSession.session_id == sessionId
    ).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview session not found"
        )
    if session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: Session belongs to a different candidate."
        )

    # Fetch messages, reverse to list newest first, and apply pagination
    messages_history = session.messages_json or []
    # Convert list elements to InterviewMessage objects
    formatted_messages = []
    for msg in messages_history:
        formatted_messages.append(InterviewMessage(
            role=msg.get("role", "assistant"),
            content=msg.get("content", ""),
            timestamp=msg.get("timestamp") or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        ))

    # Reverse to return newest first
    formatted_messages.reverse()
    
    # Paginate
    paginated_messages = formatted_messages[skip:skip + limit]
    return paginated_messages


# ─── STUDY COACH ENDPOINTS ────────────────────────────────────────────────────

class StudyPlanRequest(BaseModel):
    job_id: str
    skill: str
    user_level: str  # "Beginner", "Intermediate", "Expert"


class InteractionRequest(BaseModel):
    session_id: str
    action: str  # "go_deeper" or "move_next"
    message: str = ""


@router.post("/study/plan", status_code=200)
async def create_study_plan(
    request: StudyPlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a personalised study plan for a selected skill and level."""
    return await generate_study_plan(
        user_id=current_user.id,
        job_id=request.job_id,
        skill=request.skill,
        user_level=request.user_level,
        db=db
    )


@router.post("/study/teach", status_code=200)
async def teach_current_topic(
    body: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get explanation for the current topic in the study plan."""
    session_id = body.get("session_id")
    if not session_id:
        raise HTTPException(status_code=422, detail="session_id is required")
    return await teach_topic(session_id, db)


@router.post("/study/interact", status_code=200)
async def interact_with_coach(
    request: InteractionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Handle user interaction: go_deeper or move_next."""
    return await handle_interaction(
        session_id=request.session_id,
        action=request.action,
        user_message=request.message,
        db=db
    )


@router.get("/study/resume/{session_id}", status_code=200)
async def resume_study_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Resume a previous study session."""
    return await resume_session(session_id, db)


@router.get("/study/user-sessions", status_code=200)
async def get_user_study_sessions(
    job_id: str = Query(None),
    skill: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all active study sessions for the user.
    - With skill param: returns single session for that skill.
    - Without skill: returns dict of all sessions keyed by skill.
    """
    import uuid
    query = db.query(InterviewSession).filter(
        InterviewSession.user_id == current_user.id,
        InterviewSession.skill_focus.isnot(None),
        InterviewSession.status == "active"
    )
    # Filter by job_id if valid UUID
    if job_id:
        try:
            uuid.UUID(str(job_id))
            query = query.filter(InterviewSession.job_id == job_id)
        except ValueError:
            pass  # non-UUID job_id — skip filter

    # Filter by skill if provided
    if skill:
        session = query.filter(
            InterviewSession.skill_focus == skill
        ).order_by(InterviewSession.started_at.desc()).first()
        if not session:
            return {}
        return {
            "session_id": session.session_id,
            "skill": session.skill_focus,
            "level": session.user_level,
            "topics": session.study_plan or [],
            "current_topic_index": session.current_topic_index or 0,
            "status": session.status
        }

    # Return all sessions keyed by skill (most recent per skill)
    sessions = query.order_by(InterviewSession.started_at.desc()).all()
    result = {}
    for s in sessions:
        if s.skill_focus and s.skill_focus not in result:
            result[s.skill_focus] = {
                "session_id": s.session_id,
                "skill": s.skill_focus,
                "level": s.user_level,
                "topics": s.study_plan or [],
                "current_topic_index": s.current_topic_index or 0,
                "status": s.status
            }
    return result
