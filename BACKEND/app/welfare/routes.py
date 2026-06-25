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
from typing import List
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/welfare", tags=["welfare"])


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
