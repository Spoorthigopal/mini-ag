from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.prompts import PromptTemplate
from app.config import settings
from duckduckgo_search import DDGS
from pinecone import Pinecone
from typing import List, Dict, Any
import logging
import json
import os
import time

logger = logging.getLogger(__name__)

welfare_chat_sessions = {}

class WelfareRAG:
    """RAG system for welfare schemes using Pinecone + Gemini + Web Search Fallback"""

    def __init__(self):
        self.schemes_data = []
        self._load_json()
        
        # Initialize Embeddings
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=settings.gemini_api_key
        )
        
        # Initialize Pinecone
        try:
            self.pc = Pinecone(api_key=settings.pinecone_api_key)
            self.index = self.pc.Index(settings.PINECONE_INDEX_NAME)
            logger.info("Connected to Pinecone successfully.")
            self._init_vector_db()
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {e}")

    def _load_json(self):
        try:
            json_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "schemes.json")
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.schemes_data = data.get("schemes", [])
            logger.info(f"Loaded {len(self.schemes_data)} schemes into memory.")
        except Exception as e:
            logger.error(f"Failed to load schemes.json: {e}")

    def _init_vector_db(self):
        """Initialize Pinecone index with vectors if it's empty."""
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
                        
                        # Ensure values are simple types for Pinecone
                        for k, v in metadata.items():
                            if isinstance(v, (list, dict)):
                                metadata[k] = json.dumps(v)
                        
                        vectors_to_upsert.append({
                            "id": s.get("id"),
                            "values": embedding,
                            "metadata": metadata
                        })
                        
                    self.index.upsert(vectors=vectors_to_upsert)
                    logger.info(f"Upserted batch {i//batch_size + 1}")
                    time.sleep(1) # Simple rate limiting
                    
                logger.info("Data ingestion complete.")
            else:
                logger.info(f"Pinecone index has {stats.get('total_vector_count', 0)} vectors. Skipping ingestion.")
        except Exception as e:
            logger.error(f"Error during vector DB initialization: {e}")

    def query_vector_db(self, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Query Pinecone for top-k matching schemes."""
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

    def generate_response(
        self,
        query: str,
        session_id: str,
        top_schemes: List[Dict[str, Any]]
    ) -> str:
        """Generate response using NVIDIA NIM with Pinecone context or Web fallback."""
        try:
            import requests

            if session_id not in welfare_chat_sessions:
                welfare_chat_sessions[session_id] = []
            history = welfare_chat_sessions[session_id]

            context_lines = []
            for m in top_schemes:
                s = m.get("metadata", {})
                url = s.get("website") or "No URL available"
                scheme_id = s.get("id") or m.get("id", "Unknown")
                context_lines.append(f"[{scheme_id}] {s.get('scheme_name', 'Unknown Scheme')} | URL: {url}\nDetails: {s.get('text', '')}")
            
            context_str = "\n\n".join(context_lines)

            system_prompt = f"""You are a helpful welfare scheme advisor for university students.
You must answer the user's query STRICTLY using the provided scheme database context.
If the answer is not contained in the schemes, say EXACTLY "I don't have information about that in the database."
CRUCIAL INSTRUCTION: If the user asks for links or URLs, you MUST provide the exact URL from the context.

Database Context:
{context_str}"""

            history.append({"role": "user", "content": query})
            
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(history[-6:])

            headers = {
                "Authorization": f"Bearer {settings.nvidia_nim_api_key}",
                "Content-Type": "application/json"
            }
            
            def _call_nvidia(msg_list):
                payload = {
                    "model": "meta/llama-3.1-70b-instruct",
                    "messages": msg_list,
                    "temperature": 0.3,
                    "max_tokens": 1024
                }
                resp = requests.post("https://integrate.api.nvidia.com/v1/chat/completions", json=payload, headers=headers)
                resp.raise_for_status()
                return resp.json()["choices"][0]["message"]["content"]

            response = _call_nvidia(messages)
            
            # Check for fallback
            if "I don't have information about that in the database." in response:
                try:
                    with DDGS() as ddgs:
                        results = list(ddgs.text(query, max_results=3))
                    
                    if results:
                        web_context = "\n".join([f"- {r['title']}: {r['body']} (Link: {r['href']})" for r in results])
                        web_prompt = f"You are a helpful assistant. You searched the web for the user's query. Provide a conversational, helpful response based on these search results. Always include the source links.\n\nWeb Results:\n{web_context}"
                        web_messages = [{"role": "system", "content": web_prompt}]
                        web_messages.extend(history[-6:])
                        
                        response = _call_nvidia(web_messages)
                        response = f"Searched on web...\n\n{response}"
                except Exception as e:
                    logger.error(f"Web search error: {e}")

            history.append({"role": "assistant", "content": response})
            return response

        except Exception as e:
            logger.error(f"Response generation error: {e}")
            raise

    def upsert_scheme(self, scheme_id: str, embedding: List[float], metadata: dict):
        pass

# Global instance
welfare_rag = WelfareRAG()

def get_welfare_rag() -> WelfareRAG:
    return welfare_rag
