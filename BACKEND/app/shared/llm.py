from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
import logging
from app.config import settings
from app.shared.exceptions import AIServiceError
import time
import json
import asyncio
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

# Global client cache
_gemini_client = None

try:
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=settings.GOOGLE_API_KEY or settings.gemini_api_key or "placeholder",
        temperature=0.7,
        max_output_tokens=2048,
        top_p=0.95,
        top_k=40
    )
except Exception:
    llm = None

def get_gemini_client() -> ChatGoogleGenerativeAI:
    """Lazy load and cache Gemini client."""
    global _gemini_client
    if _gemini_client is not None:
        return _gemini_client
    
    try:
        api_key = settings.GOOGLE_API_KEY or settings.gemini_api_key
        if not api_key:
            raise ValueError("Google API key is not configured")
            
        _gemini_client = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=api_key,
            temperature=0.7,
            max_output_tokens=2048,
            top_p=0.95,
            top_k=40
        )
        return _gemini_client
    except Exception as e:
        logger.error(f"Failed to initialize ChatGoogleGenerativeAI: {e}", exc_info=True)
        raise AIServiceError(f"Failed to initialize AI client: {str(e)}")

async def call_gemini(
    prompt: str,
    system_context: str = "",
    temperature: float = 0.7,
    max_tokens: int = 2048,
    max_retries: int = 3
) -> str:
    """
    Call Gemini with retry logic, exponential backoff, and rate limit handling.
    """
    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty")

    # Get standard client
    client = get_gemini_client()
    
    # If custom temperature/tokens are requested, instantiate a configured client
    if temperature != 0.7 or max_tokens != 2048:
        api_key = settings.GOOGLE_API_KEY or settings.gemini_api_key
        client = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=api_key,
            temperature=temperature,
            max_output_tokens=max_tokens,
            top_p=0.95,
            top_k=40
        )

    messages = []
    if system_context:
        messages.append(SystemMessage(content=system_context))
    messages.append(HumanMessage(content=prompt))

    attempt = 1
    rate_limited_retried = False
    
    while attempt <= max_retries:
        try:
            logger.info(
                f"Calling Gemini API (Attempt {attempt}/{max_retries}). "
                f"Prompt (truncated): {prompt[:100]}..."
            )
            # Use standard ainvoke (async invoke)
            response = await client.ainvoke(messages)
            content = response.content
            
            # Log call (truncated for privacy)
            logger.info(
                f"Gemini call success. Model: {client.model}. "
                f"Response (truncated): {content[:100]}..."
            )
            return content
            
        except Exception as e:
            error_msg = str(e)
            error_class = e.__class__.__name__
            logger.warning(
                f"Gemini call failed (attempt {attempt}/{max_retries}). "
                f"Error: {error_class} - {error_msg}"
            )
            
            # Check for Rate Limits (ResourceExhausted / HTTP 429)
            is_rate_limit = (
                "429" in error_msg or 
                "ResourceExhausted" in error_msg or 
                "rate limit" in error_msg.lower() or
                "ResourceExhausted" in error_class
            )
            
            if is_rate_limit:
                if not rate_limited_retried:
                    logger.warning("Rate limit hit. Waiting 60 seconds before retrying once...")
                    await asyncio.sleep(60)
                    rate_limited_retried = True
                    # Keep same attempt count for rate limit retry
                    continue
                else:
                    logger.error("Rate limit hit again after wait period. Raising AIServiceError.")
                    raise AIServiceError(f"Gemini rate limit exceeded: {error_msg}")
            
            # Check for Connection or Timeout Errors
            is_timeout_or_conn = (
                "timeout" in error_msg.lower() or 
                "connection" in error_msg.lower() or
                "api connection" in error_msg.lower() or
                "deadline" in error_msg.lower()
            )
            
            if is_timeout_or_conn and attempt < max_retries:
                sleep_time = 2 ** attempt
                logger.info(f"Connection/timeout error. Backing off for {sleep_time}s...")
                await asyncio.sleep(sleep_time)
                attempt += 1
                continue
            else:
                logger.error(f"Final failure or unhandled exception during Gemini call: {error_class} - {error_msg}")
                raise AIServiceError(f"Gemini LLM call failed: {error_msg}")
                
    raise AIServiceError("Gemini call failed after maximum retries")

async def call_gemini_json(
    prompt: str,
    system_context: str = "",
    temperature: float = 0.7
) -> dict:
    """
    Call Gemini expecting a JSON response.
    """
    json_system_context = system_context
    json_instruction = "Respond with valid JSON only, no preamble."
    if json_instruction not in json_system_context:
        if json_system_context:
            json_system_context += f"\n{json_instruction}"
        else:
            json_system_context = json_instruction

    response_text = await call_gemini(
        prompt=prompt,
        system_context=json_system_context,
        temperature=temperature
    )
    
    # Strip markdown code block notation if present
    cleaned_text = response_text.strip()
    if cleaned_text.startswith("```json"):
        cleaned_text = cleaned_text[7:]
    elif cleaned_text.startswith("```"):
        cleaned_text = cleaned_text[3:]
        
    if cleaned_text.endswith("```"):
        cleaned_text = cleaned_text[:-3]
        
    cleaned_text = cleaned_text.strip()
    
    try:
        return json.loads(cleaned_text)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from AI response: {response_text}. Error: {e}")
        raise AIServiceError(f"Invalid JSON response: {str(e)}")

def create_prompt_template(system_template: str, input_variables: List[str]) -> ChatPromptTemplate:
    """Create reusable prompt template."""
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
    
    # Use "{question}" or fallback based on input variables
    human_var = "question"
    if "question" in input_variables:
        human_var = "question"
    elif "query" in input_variables:
        human_var = "query"
    elif len(input_variables) > 0:
        human_var = input_variables[-1]
        
    human_message_prompt = HumanMessagePromptTemplate.from_template(f"{{{human_var}}}")
    return ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
