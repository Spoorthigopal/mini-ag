from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class InterviewStartRequest(BaseModel):
    """Request to initiate an interview session for a specific job."""
    job_id: str = Field(..., description="ID of the internship/job to interview for")

    class Config:
        json_schema_extra = {
            "example": {"job_id": "550e8400-e29b-41d4-a716-446655440000"}
        }


class InterviewAnswerRequest(BaseModel):
    """Capture user's answer to an interview question."""
    session_id: str = Field(..., description="Active interview session ID")
    answer: str = Field(..., min_length=1, max_length=5000, description="User's answer to the current question")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "abc-123",
                "answer": "I used Python with FastAPI to build a RESTful API..."
            }
        }


class InterviewMessage(BaseModel):
    """Store a single conversation turn in the interview."""
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


class InterviewFeedback(BaseModel):
    """Detailed feedback on each interview answer."""
    question: str
    user_answer: str
    technical_accuracy: float = Field(..., ge=0.0, le=10.0, description="Technical correctness score (0-10)")
    communication_clarity: float = Field(..., ge=0.0, le=10.0, description="Clarity of communication score (0-10)")
    relevance_to_job: float = Field(..., ge=0.0, le=10.0, description="Relevance to job role score (0-10)")
    strengths: List[str] = Field(default_factory=list)
    improvement_areas: List[str] = Field(default_factory=list)
    sample_better_answer: str = Field(default="", description="Example of a stronger answer")
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


class InterviewSessionResponse(BaseModel):
    """API response for interview interactions."""
    session_id: str
    message: str
    question: str

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "abc-123",
                "message": "Interview started! Answer each question thoughtfully.",
                "question": "QUESTION: Tell me about yourself and why you're interested in this role."
            }
        }


class InterviewAnswerResponse(BaseModel):
    """Response after submitting an answer."""
    session_id: str
    next_question: Optional[str] = None
    feedback: Optional[InterviewFeedback] = None
    interview_complete: bool = False
    message: str = ""


class InterviewSummary(BaseModel):
    """Aggregated summary of a completed interview session."""
    session_id: str
    total_questions: int
    overall_score: float
    technical_average: float
    communication_average: float
    relevance_average: float
    strengths: List[str]
    improvements: List[str]
    recommendations: str
    job_fit_assessment: str
