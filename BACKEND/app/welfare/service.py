from sqlalchemy.orm import Session
from app.welfare.models import WelfareScheme
from app.welfare.rag import welfare_rag
from app.welfare.schemas import WelfareFilterParams
from app.shared.embeddings import embeddings_client
from typing import List, Tuple
import logging
import uuid

logger = logging.getLogger(__name__)


def load_welfare_schemes_to_db(db: Session, schemes_data: List[dict]):
    """Load welfare schemes into PostgreSQL and Pinecone with embeddings."""
    try:
        added = 0
        for scheme_data in schemes_data:
            existing = db.query(WelfareScheme).filter(
                WelfareScheme.name == scheme_data["name"]
            ).first()
            if existing:
                continue

            embedding_text = (
                f"{scheme_data['name']} {scheme_data['description']} "
                f"{scheme_data['scheme_type']} {scheme_data['provider']}"
            )

            try:
                embedding_vector = embeddings_client.embed_text(embedding_text)
            except Exception as e:
                logger.warning(f"Could not embed scheme '{scheme_data['name']}': {e}")
                embedding_vector = None

            scheme_id = str(uuid.uuid4())
            scheme = WelfareScheme(
                id=scheme_id,
                **{k: v for k, v in scheme_data.items() if k != "id"},
                embedding_text=embedding_text,
                embedding_vector=embedding_vector
            )
            db.add(scheme)

            # Upsert into Pinecone
            if embedding_vector:
                try:
                    welfare_rag.upsert_scheme(
                        scheme_id=scheme_id,
                        embedding=embedding_vector,
                        metadata={
                            "name": scheme_data["name"],
                            "description": scheme_data["description"][:500],
                            "scheme_type": scheme_data["scheme_type"],
                            "provider": scheme_data["provider"],
                            "scheme_status": scheme_data.get("scheme_status", "active")
                        }
                    )
                except Exception as e:
                    logger.warning(f"Pinecone upsert failed for '{scheme_data['name']}': {e}")

            added += 1

        db.commit()
        logger.info(f"Loaded {added} new welfare schemes")

    except Exception as e:
        logger.error(f"Error loading schemes: {e}")
        db.rollback()
        raise


def get_filtered_schemes(db: Session, filters: WelfareFilterParams = None) -> List[WelfareScheme]:
    """Get welfare schemes with optional filtering."""
    try:
        query = db.query(WelfareScheme)
        if filters:
            if filters.scheme_type:
                query = query.filter(WelfareScheme.scheme_type == filters.scheme_type)
            if filters.amount_min is not None:
                query = query.filter(WelfareScheme.amount >= filters.amount_min)
            if filters.amount_max is not None:
                query = query.filter(WelfareScheme.amount <= filters.amount_max)
            if filters.provider:
                query = query.filter(WelfareScheme.provider.ilike(f"%{filters.provider}%"))
            if filters.status:
                query = query.filter(WelfareScheme.scheme_status == filters.status)
        return query.all()
    except Exception as e:
        logger.error(f"Error filtering schemes: {e}")
        raise


def chat_with_welfare_bot(
    user_query: str,
    filters: WelfareFilterParams = None,
    session_id: str = None
) -> Tuple[str, List[dict], str]:
    """Process welfare bot chat query using Pinecone RAG + Gemini."""
    try:
        retrieved_schemes = welfare_rag.query_vector_db(user_query, top_k=5)
        response = welfare_rag.generate_response(user_query, retrieved_schemes)
        return response, retrieved_schemes, session_id or str(uuid.uuid4())
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise
