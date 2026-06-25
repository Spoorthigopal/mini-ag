from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class WelfareSchemeResponse(BaseModel):
    id: str
    name: str
    description: str
    scheme_type: str
    amount: Optional[float] = None
    eligibility_criteria: Optional[Dict[str, Any]] = None
    provider: str
    application_deadline: Optional[str] = None
    application_url: Optional[str] = None
    contact_email: Optional[str] = None
    benefits: Optional[List[str]] = None
    documents_required: Optional[List[str]] = None
    processing_time: Optional[str] = None
    scheme_status: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "National Scholarship Scheme",
                "description": "Financial assistance for meritorious students",
                "scheme_type": "Scholarship",
                "amount": 50000,
                "eligibility_criteria": {"gpa": "7.0+", "income": "below_5lakh"},
                "provider": "Ministry of Education",
                "application_deadline": "2024-06-30",
                "application_url": "https://scheme.edu.in/apply",
                "contact_email": "help@scheme.edu.in",
                "benefits": ["Tuition fee waiver", "Monthly stipend"],
                "documents_required": ["Marksheet", "Income certificate"],
                "processing_time": "30 days",
                "scheme_status": "active"
            }
        }


class WelfareFilterParams(BaseModel):
    scheme_type: Optional[str] = None
    amount_min: Optional[float] = None
    amount_max: Optional[float] = None
    provider: Optional[str] = None
    status: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "scheme_type": "Scholarship",
                "amount_min": 10000,
                "amount_max": 100000,
                "provider": "Ministry of Education",
                "status": "active"
            }
        }


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    session_id: Optional[str] = None
    filters: Optional[WelfareFilterParams] = None

    class Config:
        json_schema_extra = {
            "example": {
                "query": "What scholarships are available for engineering students?",
                "session_id": "conv-123",
                "filters": {"scheme_type": "Scholarship"}
            }
        }


class ChatResponse(BaseModel):
    response: str
    schemes: List[WelfareSchemeResponse]
    session_id: str

    class Config:
        json_schema_extra = {
            "example": {
                "response": "Here are the top scholarships for engineering students...",
                "schemes": [],
                "session_id": "conv-123"
            }
        }
