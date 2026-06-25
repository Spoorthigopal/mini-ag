from sqlalchemy import Column, String, Float, DateTime, Text, JSON, ARRAY
from sqlalchemy.sql import func
from app.database import Base
import uuid

class WelfareScheme(Base):
    __tablename__ = "welfare_schemes"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    scheme_type = Column(String(100), nullable=False, index=True)  # e.g., "Scholarship", "Grant"
    amount = Column(Float, nullable=True)
    eligibility_criteria = Column(JSON, nullable=True)  # e.g., {"age": "18-25", "income": "below_5lakh"}
    provider = Column(String(255), nullable=False, index=True)  # e.g., "Ministry of Education"
    application_deadline = Column(String(50), nullable=True)
    application_url = Column(String(500), nullable=True)
    contact_email = Column(String(255), nullable=True)
    benefits = Column(ARRAY(String), nullable=True)
    documents_required = Column(ARRAY(String), nullable=True)
    processing_time = Column(String(100), nullable=True)
    scheme_status = Column(String(50), default="active", nullable=False)  # active, upcoming, closed
    embedding_vector = Column(ARRAY(Float), nullable=True)  # For RAG - 384 dimensions (NVIDIA NIM)
    embedding_text = Column(Text, nullable=True)  # Original text for re-embedding
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<WelfareScheme(id={self.id}, name={self.name})>"
