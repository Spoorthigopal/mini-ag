from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime

class DocumentUploadRequest(BaseModel):
    """
    Pydantic schema representing the document upload metadata.
    Note: FastAPI handles UploadFile separately in multipart form requests.
    """
    category: str = Field(..., description="Document category")
    document_name: Optional[str] = Field(None, description="Optional custom document name")
    description: Optional[str] = Field(None, description="Optional document description")

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        allowed = ["certificates", "transcripts", "documents", "certificates_backup"]
        if v not in allowed:
            raise ValueError(f"Category must be one of: {', '.join(allowed)}")
        return v


class DocumentResponse(BaseModel):
    """
    Metadata information for a single secure document.
    """
    document_id: str
    document_name: str
    category: str
    file_size: int
    upload_date: datetime
    last_accessed: datetime
    encrypted: bool = True
    checksum: str

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """
    Paginated list of secure documents with storage metrics.
    """
    total_documents: int
    category_filter: Optional[str] = None
    documents: List[DocumentResponse]
    storage_used: int
    storage_limit: int = 500 * 1024 * 1024  # Default 500MB storage limit

    class Config:
        from_attributes = True


class DocumentDeleteRequest(BaseModel):
    """
    Delete confirmation payload.
    """
    document_id: str
