from sqlalchemy import Column, String, DateTime, Text, JSON, ForeignKey, Float, Integer
from sqlalchemy.sql import func
from app.database import Base
import uuid


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    job_id = Column(String(36), ForeignKey("internship_jobs.id"), nullable=True)
    session_id = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), index=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(50), default="active", nullable=False)
    messages_json = Column(JSON, nullable=True, default=list)
    skill_focus = Column(String(255), nullable=True)
    user_level = Column(String(50), nullable=True)
    study_plan = Column(JSON, nullable=True, default=list)
    current_topic_index = Column(Integer, default=0, nullable=False)

    def __repr__(self):
        return f"<InterviewSession id={self.id} user_id={self.user_id} status={self.status}>"


class InterviewFeedback(Base):
    __tablename__ = "interview_feedbacks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("interview_sessions.session_id"), nullable=False, index=True)
    question = Column(Text, nullable=False)
    user_answer = Column(Text, nullable=False)
    technical_accuracy = Column(Float, nullable=False)
    communication_clarity = Column(Float, nullable=False)
    relevance_to_job = Column(Float, nullable=False)
    strengths = Column(JSON, nullable=False, default=list)  # list of strings
    improvement_areas = Column(JSON, nullable=False, default=list)  # list of strings
    sample_answer = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<InterviewFeedback id={self.id} session_id={self.session_id}>"
