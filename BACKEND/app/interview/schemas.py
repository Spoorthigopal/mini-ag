from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# ─── REQUEST SCHEMAS ──────────────────────────────────────────────────────────

class InterviewStartRequest(BaseModel):
    """Request body to initiate a new mock interview session for a specific job."""
    job_id: str = Field(..., description="ID of the internship/job to interview for")

    class Config:
        json_schema_extra = {
            "example": {"job_id": "550e8400-e29b-41d4-a716-446655440000"}
        }


class InterviewAnswerRequest(BaseModel):
    """Request body to submit the candidate's answer to the current question."""
    session_id: str = Field(..., description="Active interview session ID")
    answer: str = Field(
        ..., min_length=1, max_length=5000,
        description="User's answer to the current question"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "abc-123",
                "answer": "I used Python with FastAPI to build a RESTful API..."
            }
        }


# ─── SHARED MODELS ────────────────────────────────────────────────────────────

class InterviewMessage(BaseModel):
    """
    Represents a single turn in the interview conversation.
    role: 'assistant' for interviewer questions, 'user' for candidate answers.
    """
    role: str = Field(..., description="Role: 'assistant' (coach) or 'user' (candidate)")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "role": "assistant",
                "content": "QUESTION: Tell me about a challenging project you worked on.",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


# ─── FEEDBACK SCHEMAS ─────────────────────────────────────────────────────────

class InterviewFeedback(BaseModel):
    """
    Per-question feedback returned after evaluating a candidate's answer.
    All score fields are on a 0.0 – 10.0 scale.
    """
    question: str
    user_answer: str
    technical_accuracy: float = Field(
        ..., ge=0.0, le=10.0, description="Technical correctness score (0-10)"
    )
    communication_clarity: float = Field(
        ..., ge=0.0, le=10.0, description="Clarity of communication score (0-10)"
    )
    relevance_to_job: float = Field(
        ..., ge=0.0, le=10.0, description="Relevance to job role score (0-10)"
    )
    strengths: List[str] = Field(default_factory=list)
    improvement_areas: List[str] = Field(default_factory=list)
    sample_better_answer: str = Field(
        default="", description="Example of a stronger answer"
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "question": "Explain REST API design principles.",
                "user_answer": "REST uses HTTP methods like GET and POST...",
                "technical_accuracy": 7.5,
                "communication_clarity": 8.0,
                "relevance_to_job": 9.0,
                "strengths": ["Good understanding of HTTP methods", "Concise explanation"],
                "improvement_areas": ["Mention statelessness", "Discuss HATEOAS"],
                "sample_better_answer": "REST is an architectural style based on stateless communication...",
                "timestamp": "2024-01-15T10:35:00Z"
            }
        }


# ─── RESPONSE SCHEMAS ─────────────────────────────────────────────────────────

class InterviewSessionResponse(BaseModel):
    """API response returned when a new interview session is successfully created."""
    session_id: str
    message: str
    question: str   # The first question generated for the candidate

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "abc-123",
                "message": "Interview started! Answer each question thoughtfully.",
                "question": "QUESTION: Tell me about yourself and why you're interested in this role."
            }
        }


class InterviewAnswerResponse(BaseModel):
    """
    API response returned after the candidate submits an answer.
    interview_complete=True signals the final question has been answered.
    """
    session_id: str
    next_question: Optional[str] = None       # None when interview is complete
    feedback: Optional[InterviewFeedback] = None
    interview_complete: bool = False
    message: str = ""


class InterviewSummary(BaseModel):
    """
    Aggregated performance summary for a completed interview session.
    Scores are on a 0-100 scale for overall_score; 0-10 for averages.
    """
    session_id: str
    total_questions: int
    overall_score: float          # 0-100 composite score
    technical_average: float      # 0-10
    communication_average: float  # 0-10
    relevance_average: float      # 0-10
    strengths: List[str]          # Top recurring strengths across all questions
    improvements: List[str]       # Top recurring improvement areas
    recommendations: str          # LLM-generated next-steps advice
    job_fit_assessment: str       # LLM-generated role readiness assessment
