from pinecone import Pinecone
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import settings
from app.shared.embeddings import embeddings_client
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

INTERNSHIP_PROMPT = """You are a helpful career advisor for university students in India.
Based on the student's resume and the available internship/job opportunities, provide personalized recommendations.

Resume Summary: {resume_summary}

Available Opportunities:
{jobs_context}

User Query: {query}

Provide 2-3 specific, actionable recommendations with clear reasons why each role suits the student.
Include tips on how to strengthen their application."""


class InternshipRAG:
    """RAG system for internship jobs using Pinecone + Gemini"""

    def __init__(self):
        self.index_name = "internship-jobs"
        self.embedding_dim = 384
        self._index = None

    def _get_index(self):
        """Lazy-load Pinecone index."""
        if self._index is None:
            pc = Pinecone(api_key=settings.pinecone_api_key)
            self._index = pc.Index(self.index_name)
        return self._index

    def query_vector_db(self, query_text: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Query Pinecone for relevant internship jobs."""
        try:
            query_embedding = embeddings_client.embed_text(query_text)
            index = self._get_index()
            results = index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            jobs = []
            for match in results.get("matches", []):
                jobs.append({
                    "id": match["id"],
                    "score": match["score"],
                    "metadata": match.get("metadata", {})
                })
            return jobs
        except Exception as e:
            logger.error(f"Pinecone query error: {e}")
            return []

    def rank_jobs_by_resume(
        self,
        jobs: List[Dict[str, Any]],
        resume_text: str,
        resume_skills: List[str]
    ) -> List[Dict[str, Any]]:
        """Rank jobs by skill match count against resume skills."""
        try:
            for job in jobs:
                job_description = job["metadata"].get("description", "").lower()
                match_count = sum(
                    1 for skill in resume_skills
                    if skill.lower() in job_description
                )
                total_skills = max(len(resume_skills), 1)
                job["match_score"] = round((match_count / total_skills) * 100, 1)

            jobs.sort(key=lambda x: x.get("match_score", 0), reverse=True)
            return jobs
        except Exception as e:
            logger.error(f"Ranking error: {e}")
            return jobs

    def generate_job_recommendation(
        self,
        query: str,
        resume_text: str,
        top_jobs: List[Dict[str, Any]]
    ) -> str:
        """Generate AI job recommendations using Gemini."""
        try:
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                google_api_key=settings.gemini_api_key,
                temperature=0.7
            )

            jobs_context = "\n".join([
                f"- {j['metadata'].get('job_title', 'N/A')} at "
                f"{j['metadata'].get('company_name', 'N/A')} "
                f"[Match: {j.get('match_score', 0):.0f}%]: "
                f"{j['metadata'].get('description', '')[:150]}..."
                for j in top_jobs[:5]
            ]) or "No specific jobs found in database yet."

            prompt = INTERNSHIP_PROMPT.format(
                resume_summary=resume_text[:400] if resume_text else "Not provided",
                jobs_context=jobs_context,
                query=query
            )

            response = llm.invoke([{"role": "user", "content": prompt}])
            return response.content

        except Exception as e:
            logger.error(f"Recommendation generation error: {e}")
            raise

    def upsert_job(self, job_id: str, embedding: List[float], metadata: dict):
        """Upsert a job into Pinecone index."""
        try:
            index = self._get_index()
            index.upsert(vectors=[{"id": job_id, "values": embedding, "metadata": metadata}])
        except Exception as e:
            logger.error(f"Pinecone upsert error: {e}")
            raise


# Global instance
internship_rag = InternshipRAG()


def get_internship_rag() -> InternshipRAG:
    return internship_rag
