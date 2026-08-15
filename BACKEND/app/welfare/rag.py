from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.config import settings
from pinecone import Pinecone
from typing import List, Dict, Any
import logging
import json
import os
import time
import requests

logger = logging.getLogger(__name__)

# ─── SESSION STORAGE ─────────────────────────────────────────────────────────
# In-memory store for per-session chat history (keyed by session_id)
welfare_chat_sessions = {}


# ─── WELFARE RAG CLASS ────────────────────────────────────────────────────────

class WelfareRAG:
    """
    RAG system for welfare schemes.
    Uses Pinecone for vector search and NVIDIA NIM (LLaMA) for response generation.
    Falls back to a 'not found' message if the scheme is not in the database.
    """

    def __init__(self):
        self.schemes_data = []
        self._load_json()

        # ── Google Gemini Embeddings ──────────────────────────────────────────
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=settings.gemini_api_key
        )

        # ── Pinecone Vector Index ─────────────────────────────────────────────
        try:
            self.pc = Pinecone(api_key=settings.pinecone_api_key)
            self.index = self.pc.Index(settings.PINECONE_INDEX_NAME)
            logger.info("Connected to Pinecone successfully.")
            self._init_vector_db()
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {e}")

    # ── Data Loading ──────────────────────────────────────────────────────────

    def _load_json(self):
        """Load welfare scheme data from schemes.json into memory."""
        try:
            json_path = os.path.join(
                os.path.dirname(__file__), "..", "..", "data", "schemes.json"
            )
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.schemes_data = data.get("schemes", [])
            logger.info(f"Loaded {len(self.schemes_data)} schemes into memory.")
        except Exception as e:
            logger.error(f"Failed to load schemes.json: {e}")

    # ── Vector DB Initialization ──────────────────────────────────────────────

    def _init_vector_db(self):
        """
        Populate Pinecone index with scheme embeddings on first startup.
        Skips ingestion if the index is already populated.
        """
        try:
            stats = self.index.describe_index_stats()
            if stats.get("total_vector_count", 0) == 0 and self.schemes_data:
                logger.info("Pinecone index is empty. Ingesting scheme data...")
                batch_size = 20
                for i in range(0, len(self.schemes_data), batch_size):
                    batch = self.schemes_data[i:i + batch_size]
                    vectors_to_upsert = []

                    for s in batch:
                        text_to_embed = s.get("text")
                        if not text_to_embed:
                            continue

                        embedding = self.embeddings.embed_query(text_to_embed)

                        metadata = s.get("metadata", {}).copy()
                        metadata["id"] = s.get("id", "")
                        metadata["text"] = text_to_embed

                        # Pinecone requires scalar metadata values
                        for k, v in metadata.items():
                            if isinstance(v, (list, dict)):
                                metadata[k] = json.dumps(v)

                        vectors_to_upsert.append({
                            "id": s.get("id"),
                            "values": embedding,
                            "metadata": metadata
                        })

                    self.index.upsert(vectors=vectors_to_upsert)
                    logger.info(f"Upserted batch {i // batch_size + 1}")
                    time.sleep(1)  # Respect Pinecone rate limits

                logger.info("Data ingestion complete.")
            else:
                logger.info(
                    f"Pinecone index has {stats.get('total_vector_count', 0)} vectors. "
                    "Skipping ingestion."
                )
        except Exception as e:
            logger.error(f"Error during vector DB initialization: {e}")

    # ── Vector Search ─────────────────────────────────────────────────────────

    def query_vector_db(self, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Query Pinecone for top-k welfare schemes matching the query.
        Returns a list of dicts with 'id', 'score', and 'metadata'.
        """
        try:
            query_embedding = self.embeddings.embed_query(query_text)
            response = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )

            results = []
            for match in response.get("matches", []):
                results.append({
                    "id": match["id"],
                    "score": match["score"],
                    "metadata": match["metadata"]
                })
            return results
        except Exception as e:
            logger.error(f"Error querying Pinecone: {e}")
            return []

    # ── Response Generation ───────────────────────────────────────────────────

    def generate_response(
        self,
        query: str,
        session_id: str,
        top_schemes: List[Dict[str, Any]]
    ) -> str:
        """
        Generate a response using NVIDIA NIM (LLaMA) with Pinecone scheme context.
        Maintains per-session chat history for multi-turn conversations.
        If the LLM cannot find relevant info in the database, it returns a
        clear 'not found' message — no external web search fallback.
        """
        # Initialise session history if not present
        if session_id not in welfare_chat_sessions:
            welfare_chat_sessions[session_id] = []
        history = welfare_chat_sessions[session_id]

        # Build scheme context string from Pinecone results
        context_lines = []
        for m in top_schemes:
            s = m.get("metadata", {})
            url = s.get("website") or "No URL available"
            scheme_id = s.get("id") or m.get("id", "Unknown")
            context_lines.append(
                f"[{scheme_id}] {s.get('scheme_name', 'Unknown Scheme')} | URL: {url}\n"
                f"Details: {s.get('text', '')}"
            )

        context_str = "\n\n".join(context_lines)

        # System prompt instructs the LLM to stay within the database context
        system_prompt = (
            "You are a helpful welfare scheme advisor for university students.\n"
            "You must answer the user's query STRICTLY using the provided scheme database context.\n"
            "If the answer is not contained in the schemes, say EXACTLY "
            "\"I don't have information about that in the database.\"\n"
            "CRUCIAL INSTRUCTION: If the user asks for links or URLs, "
            "you MUST provide the exact URL from the context.\n\n"
            f"Database Context:\n{context_str}"
        )

        history.append({"role": "user", "content": query})

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history[-6:])  # Keep last 3 turns for context

        headers = {
            "Authorization": f"Bearer {settings.nvidia_nim_api_key}",
            "Content-Type": "application/json"
        }

        def _call_nvidia(msg_list: list) -> str:
            """Internal helper to call the NVIDIA NIM chat completion API."""
            payload = {
                "model": "meta/llama-3.1-70b-instruct",
                "messages": msg_list,
                "temperature": 0.3,
                "max_tokens": 1024
            }
            resp = requests.post(
                "https://integrate.api.nvidia.com/v1/chat/completions",
                json=payload,
                headers=headers
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]

        try:
            response = _call_nvidia(messages)
        except Exception as e:
            logger.error(f"Response generation error: {e}")
            raise

        history.append({"role": "assistant", "content": response})
        return response

    # ── Upsert (placeholder) ──────────────────────────────────────────────────

    def upsert_scheme(self, scheme_id: str, embedding: List[float], metadata: dict):
        """Upsert a single scheme into Pinecone (reserved for future admin use)."""
        pass


# ─── GLOBAL INSTANCE ─────────────────────────────────────────────────────────

welfare_rag = WelfareRAG()


def get_welfare_rag() -> WelfareRAG:
    """FastAPI dependency: returns the global WelfareRAG instance."""
    return welfare_rag
