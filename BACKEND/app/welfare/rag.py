from pinecone import Pinecone
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from app.config import settings
from app.shared.embeddings import embeddings_client
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

WELFARE_PROMPT_TEMPLATE = """You are a helpful welfare scheme advisor for university students in India.
You must answer the user's query STRICTLY AND EXCLUSIVELY using the provided scheme information.
Do not use any outside knowledge or make up information. If the answer is not contained in the provided schemes, state exactly: "I'm sorry, but I can only answer based on the provided scholarship database, and I do not have information about that."

Relevant Schemes:
{context}

User Query: {question}

Provide a helpful, accurate response focusing on:
1. Relevant schemes matching the query
2. Key eligibility criteria
3. How to apply
4. Important deadlines"""


class WelfareRAG:
    """RAG system for welfare schemes using Pinecone + Gemini"""

    def __init__(self):
        self.index_name = "welfare-schemes"
        self.embedding_dim = 384
        self._index = None

    def _get_index(self):
        """Lazy-load Pinecone index."""
        if self._index is None:
            pc = Pinecone(api_key=settings.pinecone_api_key)
            self._index = pc.Index(self.index_name)
        return self._index

    def query_vector_db(self, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Query Pinecone for relevant welfare schemes."""
        try:
            query_embedding = embeddings_client.embed_text(query_text)
            index = self._get_index()
            results = index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            schemes = []
            for match in results.get("matches", []):
                schemes.append({
                    "id": match["id"],
                    "score": match["score"],
                    "metadata": match.get("metadata", {})
                })
            return schemes
        except Exception as e:
            logger.error(f"Pinecone query error: {e}")
            return []

    def generate_response(
        self,
        query: str,
        retrieved_schemes: List[Dict[str, Any]]
    ) -> str:
        """Generate response using Gemini with retrieved schemes as context."""
        try:
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                google_api_key=settings.gemini_api_key,
                temperature=0.7
            )

            context = "\n".join([
                f"- {s['metadata'].get('name', 'Unknown')}: {s['metadata'].get('description', 'N/A')}"
                for s in retrieved_schemes
            ]) if retrieved_schemes else "No specific schemes found in database."

            prompt = PromptTemplate(
                template=WELFARE_PROMPT_TEMPLATE,
                input_variables=["context", "question"]
            )

            full_prompt = prompt.format(context=context, question=query)
            response = llm.invoke([{"role": "user", "content": full_prompt}])
            return response.content

        except Exception as e:
            logger.error(f"Response generation error: {e}")
            raise

    def upsert_scheme(self, scheme_id: str, embedding: List[float], metadata: dict):
        """Upsert a welfare scheme into Pinecone."""
        try:
            index = self._get_index()
            index.upsert(vectors=[{"id": scheme_id, "values": embedding, "metadata": metadata}])
        except Exception as e:
            logger.error(f"Pinecone upsert error: {e}")
            raise


# Global instance
welfare_rag = WelfareRAG()


def get_welfare_rag() -> WelfareRAG:
    return welfare_rag
