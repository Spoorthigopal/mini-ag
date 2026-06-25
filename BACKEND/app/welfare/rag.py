from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from app.config import settings
from duckduckgo_search import DDGS
from typing import List, Dict, Any
import logging
import json
import os

logger = logging.getLogger(__name__)

welfare_chat_sessions = {}

class WelfareRAG:
    """RAG system for welfare schemes using local JSON + Gemini + Web Search Fallback"""

    def __init__(self):
        self.schemes_data = []
        self._load_json()

    def _load_json(self):
        try:
            json_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "schemes.json")
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.schemes_data = data.get("schemes", [])
            logger.info(f"Loaded {len(self.schemes_data)} schemes into memory.")
        except Exception as e:
            logger.error(f"Failed to load schemes.json: {e}")

    def query_vector_db(self, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Mock Pinecone query by performing basic substring match on JSON for UI display."""
        q = query_text.lower()
        results = []
        for s in self.schemes_data:
            if q in s.get("name", "").lower() or q in s.get("description", "").lower():
                # We need to return an object that looks like what the frontend expects
                results.append({
                    "id": s["id"], 
                    "score": 0.9, 
                    "metadata": s
                })
                if len(results) >= top_k:
                    break
        return results

    def generate_response(
        self,
        query: str,
        session_id: str
    ) -> str:
        """Generate response using Gemini with full JSON context or Web fallback."""
        try:
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                google_api_key=settings.gemini_api_key,
                temperature=0.3
            )

            if session_id not in welfare_chat_sessions:
                welfare_chat_sessions[session_id] = []
            history = welfare_chat_sessions[session_id]

            # 1. Check if the query is a general question requiring web search
            # We use a very fast classification prompt
            search_check = f"Is the following query asking about a specific government/university welfare scheme or scholarship? Query: '{query}'. Reply YES or NO."
            decision = llm.invoke([{"role": "user", "content": search_check}]).content.strip().upper()

            if "NO" in decision:
                # Fallback to DuckDuckGo Web Search
                try:
                    with DDGS() as ddgs:
                        results = list(ddgs.text(query, max_results=3))
                    
                    web_context = "\n".join([f"- {r['title']}: {r['body']} (Link: {r['href']})" for r in results])
                    system_prompt = f"You are a helpful assistant. You searched the web for the user's query. Provide a conversational, helpful response based on these search results. Always include the source links.\n\nWeb Results:\n{web_context}"
                    
                    history.append({"role": "user", "content": query})
                    messages = [{"role": "system", "content": system_prompt}]
                    # Keep last 6 messages
                    messages.extend(history[-6:])
                    
                    response = llm.invoke(messages).content
                    history.append({"role": "assistant", "content": response})
                    
                    return f"Searched on web...\n\n{response}"
                except Exception as e:
                    logger.error(f"Web search error: {e}")
                    return "I'm sorry, I couldn't find information in the database, and the web search failed."

            # 2. Scheme Database Query
            # Build ultra-dense context of all schemes
            context_lines = []
            for s in self.schemes_data:
                url = s.get("application_url") or s.get("metadata", {}).get("website") or "No URL available"
                context_lines.append(f"[{s['id']}] {s['name']} | URL: {url} | Eligibility: {s.get('eligibility', [])} | Deadline: {s.get('deadline', 'Ongoing')}")
            
            context_str = "\n".join(context_lines)

            system_prompt = f"""You are a helpful welfare scheme advisor for university students.
You must answer the user's query STRICTLY using the provided scheme database context.
If the answer is not contained in the schemes, say "I don't have information about that in the database."
CRUCIAL INSTRUCTION: If the user asks for links or URLs, you MUST provide the exact URL from the context.

Database Context:
{context_str}"""

            history.append({"role": "user", "content": query})
            
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(history[-6:])

            response = llm.invoke(messages).content
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
