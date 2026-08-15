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


# ─── RATE LIMITING ────────────────────────────────────────────────────────────
# Simple in-memory store: maps user_id → list of request timestamps
rate_limit_store = {}


def check_rate_limit(user_id: str, limit: int = 5, period: int = 60) -> bool:
    """
    Enforce a per-user rate limit of `limit` requests per `period` seconds.

    Returns True if the request is allowed, False if the limit is exceeded.
    Uses a sliding-window approach backed by an in-memory dict.
    """
    now = time.time()
    if user_id not in rate_limit_store:
        rate_limit_store[user_id] = []

    # Discard timestamps outside the current window
    rate_limit_store[user_id] = [
        t for t in rate_limit_store[user_id] if now - t < period
    ]

    if len(rate_limit_store[user_id]) >= limit:
        return False

    rate_limit_store[user_id].append(now)
    return True


# ─── RESPONSE MODELS ──────────────────────────────────────────────────────────

class FeedbackSummaryWithDetails(BaseModel):
    """Combined response model: aggregated metrics + per-question feedback list."""
    summary: InterviewSummary
    feedback: List[FeedbackSchema]


# ─── MOCK INTERVIEW ENDPOINTS ─────────────────────────────────────────────────

# ENDPOINT 1 ── POST /api/interview/start
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
    Start a new mock interview session for a given job listing.

    - Validates the job exists in the database.
    - Creates a session record and generates the first question.
    - Returns the session_id and the opening question.
    """
    logger.info(
        f"User {current_user.id} requested to start interview for job {request.job_id}"
    )

    # Enforce rate limit before any heavy processing
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


# ENDPOINT 2 ── POST /api/interview/answer
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
    Submit the candidate's answer to the current interview question.

    - Verifies the session belongs to the authenticated user.
    - Evaluates the answer with Gemini and stores feedback.
    - Returns the next question or signals interview completion.
    """
    logger.info(
        f"User {current_user.id} submitted answer for session {request.session_id}"
    )

    # Enforce rate limit
    if not check_rate_limit(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Maximum 5 requests per minute allowed."
        )

    # Validate session exists and is owned by the current user
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
            message=(
                "Interview completed."
                if res["interview_complete"]
                else "Response processed successfully."
            )
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error processing answer for session {request.session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process interview response"
        )


# ENDPOINT 3 ── GET /api/interview/feedback
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
    Retrieve aggregated metrics and per-question feedback for an interview session.

    Returns:
      - summary: overall score, averages, top strengths/improvements, LLM recommendations
      - feedback: ordered list of per-question feedback records
    """
    logger.info(
        f"User {current_user.id} requested feedback summary for session {sessionId}"
    )

    # Validate session ownership before returning any data
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
        # Get aggregated metrics summary
        summary = await get_session_summary(session_id=sessionId, db=db)

        # Get all per-question feedback records in chronological order
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


# ENDPOINT 4 ── GET /api/interview/history
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
    Fetch paginated chat messages from a session's history (newest first).

    Supports skip/limit pagination. Returns InterviewMessage objects with
    role, content, and timestamp fields.
    """
    logger.info(
        f"User {current_user.id} requested chat history for session {sessionId}"
    )

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

    # Convert raw JSON messages to typed InterviewMessage objects
    messages_history = session.messages_json or []
    formatted_messages = []
    for msg in messages_history:
        formatted_messages.append(InterviewMessage(
            role=msg.get("role", "assistant"),
            content=msg.get("content", ""),
            timestamp=(
                msg.get("timestamp")
                or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            )
        ))

    # Reverse so newest messages come first, then paginate
    formatted_messages.reverse()
    return formatted_messages[skip:skip + limit]


# ─── STUDY COACH REQUEST MODELS ───────────────────────────────────────────────

class StudyPlanRequest(BaseModel):
    """Request body for creating a new study plan session."""
    job_id: str
    skill: str
    user_level: str  # "Beginner", "Intermediate", or "Expert"


class InteractionRequest(BaseModel):
    """Request body for interacting with the study coach."""
    session_id: str
    action: str    # "go_deeper", "move_next", or "jump_to_topic"
    message: str = ""


# ─── STUDY COACH ENDPOINTS ────────────────────────────────────────────────────

# ENDPOINT 5 ── POST /api/interview/study/plan
@router.post("/study/plan", status_code=200)
async def create_study_plan(
    request: StudyPlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a personalised study plan for a selected skill and experience level.
    Returns session_id, topics list, and current_topic_index.
    """
    return await generate_study_plan(
        user_id=current_user.id,
        job_id=request.job_id,
        skill=request.skill,
        user_level=request.user_level,
        db=db
    )


# ENDPOINT 6 ── POST /api/interview/study/teach
@router.post("/study/teach", status_code=200)
async def teach_current_topic(
    body: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get an AI-generated explanation for the current topic in the study plan.
    Expects JSON body: { "session_id": "..." }
    """
    session_id = body.get("session_id")
    if not session_id:
        raise HTTPException(status_code=422, detail="session_id is required")
    return await teach_topic(session_id, db)


# ENDPOINT 7 ── POST /api/interview/study/interact
@router.post("/study/interact", status_code=200)
async def interact_with_coach(
    request: InteractionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Handle a study coach interaction: go_deeper, move_next, or jump_to_topic.
    The 'message' field carries user follow-up text or topic index for jump_to_topic.
    """
    return await handle_interaction(
        session_id=request.session_id,
        action=request.action,
        user_message=request.message,
        db=db
    )


# ENDPOINT 8 ── GET /api/interview/study/resume/{session_id}
@router.get("/study/resume/{session_id}", status_code=200)
async def resume_study_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Resume a previous study session.
    Returns current progress including topics, current index, and full message history.
    """
    return await resume_session(session_id, db)


# ENDPOINT 9 ── GET /api/interview/study/user-sessions
@router.get("/study/user-sessions", status_code=200)
async def get_user_study_sessions(
    job_id: str = Query(None, description="Filter sessions by job UUID"),
    skill: str = Query(None, description="Filter sessions by skill name"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all active study sessions for the authenticated user.

    - With `skill` param: returns the most recent session for that skill.
    - Without `skill`: returns a dict of all sessions keyed by skill name.
    - Optionally filter by `job_id` (must be a valid UUID).
    """
    import uuid

    # Base query: active study sessions for this user (skill_focus must be set)
    query = db.query(InterviewSession).filter(
        InterviewSession.user_id == current_user.id,
        InterviewSession.skill_focus.isnot(None),
        InterviewSession.status == "active"
    )

    # Filter by job_id if a valid UUID is provided
    if job_id:
        try:
            uuid.UUID(str(job_id))
            query = query.filter(InterviewSession.job_id == job_id)
        except ValueError:
            pass  # Non-UUID job_id — skip filter

    # Return single session for a specific skill
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

    # Return all sessions grouped by skill (most recent per skill)
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
