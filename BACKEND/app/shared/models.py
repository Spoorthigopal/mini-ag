from sqlalchemy import Column, String, DateTime, Text, JSON, ForeignKey
from sqlalchemy.sql import func
from app.database import Base
import uuid


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    module_type = Column(String(50), nullable=False, index=True)  # welfare, internships, interview, digilocker
    messages_json = Column(JSON, nullable=True, default=list)
    conversation_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<Conversation id={self.id} user_id={self.user_id} module={self.module_type}>"


class RateLimitLog(Base):
    __tablename__ = "rate_limit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ip_address = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    def __repr__(self):
        return f"<RateLimitLog ip={self.ip_address} time={self.timestamp}>"
