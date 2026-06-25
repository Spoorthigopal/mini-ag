from sqlalchemy.orm import Session
from app.internships.models import InternshipJob
from app.internships.jsearch_client import jsearch_client
from app.internships.resume_parser import resume_parser
from app.internships.rag import internship_rag
from app.internships.schemas import InternshipFilterParams
from app.shared.embeddings import embeddings_client
from typing import List, Tuple, Optional
import logging
import uuid

logger = logging.getLogger(__name__)

DEFAULT_SEARCH_TERMS = [
    "Python intern", "React intern", "Data Science intern",
    "DevOps intern", "Java intern", "ML engineer intern",
    "Android developer intern", "Full stack intern"
]


def sync_jobs_from_jsearch(db: Session, search_terms: List[str] = None):
    """Sync internship jobs from JSearch API into DB and Pinecone."""
    if not search_terms:
        search_terms = DEFAULT_SEARCH_TERMS

    total_added = 0
    try:
        for search_term in search_terms:
            try:
                raw_jobs = jsearch_client.query_jsearch(search_term, limit=20)
            except Exception as e:
                logger.warning(f"JSearch failed for '{search_term}': {e}")
                continue

            for raw_job in raw_jobs:
                parsed = jsearch_client.parse_job_listing(raw_job)

                if not parsed.get("jsearch_job_id"):
                    continue

                existing = db.query(InternshipJob).filter(
                    InternshipJob.jsearch_job_id == parsed["jsearch_job_id"]
                ).first()
                if existing:
                    continue

                try:
                    embedding = embeddings_client.embed_text(parsed.get("embedding_text", ""))
                except Exception as e:
                    logger.warning(f"Embedding failed: {e}")
                    embedding = None

                job_id = str(uuid.uuid4())
                job_data = {k: v for k, v in parsed.items() if k != "embedding_text"}
                job = InternshipJob(
                    id=job_id,
                    **job_data,
                    embedding_text=parsed.get("embedding_text", ""),
                    embedding_vector=embedding
                )
                db.add(job)

                # Sync to Pinecone
                if embedding:
                    try:
                        internship_rag.upsert_job(
                            job_id=job_id,
                            embedding=embedding,
                            metadata={
                                "job_title": parsed.get("job_title", ""),
                                "company_name": parsed.get("company_name", ""),
                                "location": parsed.get("location", ""),
                                "description": parsed.get("job_description", "")[:400],
                                "stipend": parsed.get("stipend", 0),
                                "job_type": parsed.get("job_type", "internship")
                            }
                        )
                    except Exception as e:
                        logger.warning(f"Pinecone upsert failed: {e}")

                total_added += 1

        db.commit()
        logger.info(f"JSearch sync complete. Added {total_added} new jobs.")
    except Exception as e:
        logger.error(f"Sync error: {e}")
        db.rollback()
        raise


def get_filtered_jobs(db: Session, filters: InternshipFilterParams = None) -> List[InternshipJob]:
    """Get internship jobs from DB with optional filters."""
    try:
        query = db.query(InternshipJob).filter(InternshipJob.job_status == "active")
        if filters:
            if filters.company_name:
                query = query.filter(InternshipJob.company_name.ilike(f"%{filters.company_name}%"))
            if filters.location:
                query = query.filter(InternshipJob.location.ilike(f"%{filters.location}%"))
            if filters.stipend_min is not None:
                query = query.filter(InternshipJob.stipend >= filters.stipend_min)
            if filters.stipend_max is not None:
                query = query.filter(InternshipJob.stipend <= filters.stipend_max)
            if filters.duration_months is not None:
                query = query.filter(InternshipJob.duration_months <= filters.duration_months)
        return query.order_by(InternshipJob.created_at.desc()).all()
    except Exception as e:
        logger.error(f"Filter error: {e}")
        raise


def chat_with_internship_bot(
    user_query: str,
    resume_text: Optional[str] = None,
    filters: Optional[InternshipFilterParams] = None
) -> Tuple[str, List[dict], Optional[str]]:
    """Process internship bot chat using Pinecone RAG + Gemini."""
    try:
        retrieved_jobs = internship_rag.query_vector_db(user_query, top_k=10)

        resume_skills = []
        if resume_text:
            resume_skills = resume_parser.extract_skills(resume_text)
            retrieved_jobs = internship_rag.rank_jobs_by_resume(
                retrieved_jobs, resume_text, resume_skills
            )

        response = internship_rag.generate_job_recommendation(
            query=user_query,
            resume_text=resume_text or "",
            top_jobs=retrieved_jobs
        )

        return response, retrieved_jobs, None
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise
