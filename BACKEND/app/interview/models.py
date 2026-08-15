from sqlalchemy import Column, String, DateTime, Text, JSON, ForeignKey, Float, Integer
from sqlalchemy.sql import func
from app.database import Base
import uuid


# ─── INTERVIEW SESSION MODEL ──────────────────────────────────────────────────

class InterviewSession(Base):
    """
    Represents a single mock interview or study coach session.

    Used for both:
      - Mock interviews: job_id is set, skill_focus is NULL
      - Study sessions:  skill_focus is set, study_plan and current_topic_index track progress

    Status lifecycle: active → completed | expired
    """
    __tablename__ = "interview_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    job_id = Column(String(36), ForeignKey("internship_jobs.id"), nullable=True)

    # Unique public identifier returned to clients (distinct from internal PK)
    session_id = Column(
        String(36), unique=True, default=lambda: str(uuid.uuid4()), index=True
    )

    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(50), default="active", nullable=False)  # active | completed | expired

    # Ordered list of {"role": "user"|"assistant", "content": "...", "timestamp": "..."} dicts
    messages_json = Column(JSON, nullable=True, default=list)

    # Study coach fields (NULL for mock interview sessions)
    skill_focus = Column(String(255), nullable=True)         # e.g. "React", "Python"
    user_level = Column(String(50), nullable=True)           # "Beginner" | "Intermediate" | "Expert"
    study_plan = Column(JSON, nullable=True, default=list)   # Ordered list of topic strings
    current_topic_index = Column(Integer, default=0, nullable=False)

    def __repr__(self):
        return f"<InterviewSession id={self.id} user_id={self.user_id} status={self.status}>"


# ─── INTERVIEW FEEDBACK MODEL ─────────────────────────────────────────────────

class InterviewFeedback(Base):
    """
    Stores per-question feedback for a mock interview session.

    One record is created for each answer submitted during a session.
    Scores are on a 0-10 scale; strengths/improvement_areas are JSON arrays.
    """
    __tablename__ = "interview_feedbacks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(
        String(36), ForeignKey("interview_sessions.session_id"),
        nullable=False, index=True
    )

    question = Column(Text, nullable=False)      # The question that was asked
    user_answer = Column(Text, nullable=False)   # The candidate's raw answer

    # Gemini-evaluated scores (0.0 – 10.0)
    technical_accuracy = Column(Float, nullable=False)
    communication_clarity = Column(Float, nullable=False)
    relevance_to_job = Column(Float, nullable=False)

    strengths = Column(JSON, nullable=False, default=list)          # list[str]
    improvement_areas = Column(JSON, nullable=False, default=list)  # list[str]
    sample_answer = Column(Text, nullable=True)  # Example of a stronger answer

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<InterviewFeedback id={self.id} session_id={self.session_id}>"
