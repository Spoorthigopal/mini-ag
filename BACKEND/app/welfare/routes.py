from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.shared.dependencies import get_current_user
from app.auth.models import User
from app.welfare.schemas import (
    WelfareSchemeResponse, ChatRequest, ChatResponse, WelfareFilterParams
)
from app.welfare.service import get_filtered_schemes, chat_with_welfare_bot
from app.welfare.models import WelfareScheme
from typing import List, Any
import logging
import json
import os
import re

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/welfare", tags=["welfare"])

JSON_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "schemes.json")


@router.get("/all", response_model=List[Any])
async def get_all_schemes_from_json():
    """Return all welfare schemes directly from the JSON knowledge base."""
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        schemes_raw = data.get("schemes", [])
        result = []
        for s in schemes_raw:
            meta = s.get("metadata", {})
            text = s.get("text", "")
            
            amount_match = re.search(r'₹([\d,]+)', text)
            amount = f"₹{amount_match.group(1)}" if amount_match else "₹10,000"
            
            eligibility = []
            lower_text = text.lower()
            if "sc" in lower_text or "st" in lower_text or "scheduled" in lower_text: eligibility.append("SC/ST")
            if "obc" in lower_text: eligibility.append("OBC")
            if "minority" in lower_text: eligibility.append("Minority")
            if "general" in lower_text: eligibility.append("General")
            if "degree" in lower_text or "undergraduate" in lower_text or "college" in lower_text: eligibility.append("Undergraduate")
            if "postgraduate" in lower_text or "pg" in lower_text or "phd" in lower_text: eligibility.append("Postgraduate")
            if not eligibility: eligibility.append("General")
            
            result.append({
                "id": meta.get("scheme_id", s.get("id", "")),
                "name": meta.get("scheme_name", ""),
                "description": text,
                "scheme_type": meta.get("scheme_type", "Government Scheme"),
                "provider": meta.get("provider", "Government of India"),
                "states": meta.get("states", "All India"),
                "category": meta.get("category", ""),
                "tags": meta.get("tags", ""),
                "application_url": meta.get("website", ""),
                "scheme_status": "active",
                "amount": amount,
                "deadline": "2026-12-31",
                "eligibility": eligibility
            })
        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="schemes.json not found. Please add data/schemes.json to the backend.")
    except Exception as e:
        logger.error(f"Error reading schemes.json: {e}")
        raise HTTPException(status_code=500, detail="Failed to load schemes")


@router.get("/schemes", response_model=List[WelfareSchemeResponse])
async def get_schemes(
    scheme_type: str = None,
    amount_min: float = None,
    amount_max: float = None,
    provider: str = None,
    status: str = "active",
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get welfare schemes with optional filters.

    Query parameters:
    - scheme_type: Scholarship, Grant, etc.
    - amount_min/amount_max: Financial range filter
    - provider: Ministry or organization name
    - status: active, upcoming, closed
    """
    try:
        filters = WelfareFilterParams(
            scheme_type=scheme_type,
            amount_min=amount_min,
            amount_max=amount_max,
            provider=provider,
            status=status
        )
        schemes = get_filtered_schemes(db, filters)
        return schemes[skip: skip + limit]
    except Exception as e:
        logger.error(f"Get schemes error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch schemes")


@router.get("/search", response_model=List[WelfareSchemeResponse])
async def search_schemes(
    query: str,
    top_k: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Semantic search for welfare schemes."""
    try:
        from app.welfare.rag import welfare_rag
        retrieved = welfare_rag.query_vector_db(query, top_k=top_k)
        scheme_ids = [s["id"] for s in retrieved]
        if not scheme_ids:
            return []
        
        db_schemes = db.query(WelfareScheme).filter(WelfareScheme.id.in_(scheme_ids)).all()
        db_schemes_dict = {s.id: s for s in db_schemes}
        sorted_schemes = [db_schemes_dict[sid] for sid in scheme_ids if sid in db_schemes_dict]
        
        return sorted_schemes
    except Exception as e:
        logger.error(f"Search schemes error: {e}")
        raise HTTPException(status_code=500, detail="Failed to search schemes")


@router.post("/chat", response_model=ChatResponse)
async def welfare_chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Chat with welfare scheme advisor (Gemini + Pinecone RAG).

    Request body:
    - query: Question about welfare schemes
    - session_id: Optional conversation session ID
    - filters: Optional scheme filters
    """
    try:
        response, retrieved, session_id = chat_with_welfare_bot(
            user_query=request.query,
            filters=request.filters,
            session_id=request.session_id
        )

        # Fetch DB objects for schemes found in Pinecone results
        scheme_ids = [s["id"] for s in retrieved]
        db_schemes = db.query(WelfareScheme).filter(WelfareScheme.id.in_(scheme_ids)).all()

        return ChatResponse(
            response=response,
            schemes=[WelfareSchemeResponse.model_validate(s) for s in db_schemes],
            session_id=session_id
        )
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Chat failed")


@router.get("/schemes/{scheme_id}", response_model=WelfareSchemeResponse)
async def get_scheme_by_id(
    scheme_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific welfare scheme by ID."""
    scheme = db.query(WelfareScheme).filter(WelfareScheme.id == scheme_id).first()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    return scheme
