from sqlalchemy import Column, String, DateTime, Text, Integer, LargeBinary, ForeignKey, Index
from sqlalchemy.sql import func
from app.database import Base
import uuid


class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    document_id = Column(String(36), unique=True, nullable=False, index=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False, index=True)  # certificates, transcripts, documents, certificates_backup
    file_size = Column(Integer, nullable=False)
    encrypted_data = Column(LargeBinary, nullable=False)  # Ciphertext
    salt = Column(LargeBinary(16), nullable=False)        # 16 bytes derivation salt
    nonce = Column(LargeBinary(12), nullable=False)       # 12 bytes IV nonce
    tag = Column(LargeBinary(16), nullable=False)         # 16 bytes authentication tag
    checksum = Column(String(64), nullable=False)         # SHA-256 hex checksum
    upload_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_accessed = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Indexes for optimization
    __table_args__ = (
        Index("idx_user_document", "user_id", "document_id"),
        Index("idx_user_category", "user_id", "category"),
        Index("idx_upload_date", "upload_date"),
    )

    def __repr__(self):
        return f"<Document id={self.id} filename={self.filename} category={self.category}>"
