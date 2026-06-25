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
from app.interview.service import start_interview, process_answer, get_session_summary
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
