import dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, BaseMessage
import logging
from app.config import settings
from app.shared.exceptions import AIServiceError
import asyncio
from typing import Optional, List
import os

dotenv.load_dotenv()

logger = logging.getLogger(__name__)


# ─── CLIENT INITIALIZATION ────────────────────────────────────────────────────
# Global cached Gemini client (avoids re-initialising on every request)
_gemini_client = None

try:
    # Default global LLM instance used by the interview chains module
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY_INTERVIEW"),
        temperature=0.7,
        max_output_tokens=2048,
        top_p=0.95,
        top_k=40,
        convert_system_message_to_human=True,
        max_retries=0  # Disable LangChain internal retries; our code handles fallback
    )
except Exception:
    llm = None


def get_gemini_client() -> ChatGoogleGenerativeAI:
    """
    Lazy-load and cache a Gemini client using the configured API key.
    Raises AIServiceError if the key is missing or initialisation fails.
    """
    global _gemini_client
    if _gemini_client is not None:
        return _gemini_client

    try:
        api_key = (
            os.getenv("GOOGLE_API_KEY_INTERVIEW")
            or settings.GOOGLE_API_KEY
            or settings.gemini_api_key
        )
        if not api_key:
            raise ValueError("Google API key is not configured")

        _gemini_client = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=api_key,
            temperature=0.7,
            max_output_tokens=2048,
            top_p=0.95,
            top_k=40,
            convert_system_message_to_human=True,
            max_retries=0  # Disable LangChain internal retries
        )
        return _gemini_client
    except Exception as e:
        logger.error(f"Failed to initialize ChatGoogleGenerativeAI: {e}", exc_info=True)
        raise AIServiceError(f"Failed to initialize AI client: {str(e)}")


# ─── GEMINI API CALL ──────────────────────────────────────────────────────────

async def call_gemini(
    prompt: str,
    system_context: str = "",
    temperature: float = 0.7,
    max_tokens: int = 2048,
    max_retries: int = 3,
    custom_api_key: str = None
) -> str:
    """
    Call the Gemini API with retry logic, exponential back-off, and
    rate-limit handling.

    Args:
        prompt:          The user-facing prompt text.
        system_context:  Optional system instruction for the LLM.
        temperature:     Sampling temperature (0.0 – 1.0).
        max_tokens:      Maximum output tokens.
        max_retries:     How many times to retry on transient errors.
        custom_api_key:  Use a specific API key instead of the default.

    Returns:
        The raw string content from the Gemini response.

    Raises:
        AIServiceError: On rate-limit exhaustion or unrecoverable errors.
    """
    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty")

    # Obtain the standard cached client
    client = get_gemini_client()

    # Re-instantiate with custom settings if non-defaults are requested
    if custom_api_key or temperature != 0.7 or max_tokens != 2048:
        api_key = (
            custom_api_key
            or os.getenv("GOOGLE_API_KEY_INTERVIEW")
            or settings.GOOGLE_API_KEY
            or settings.gemini_api_key
        )
        client = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=api_key,
            temperature=temperature,
            max_output_tokens=max_tokens,
            top_p=0.95,
            top_k=40,
            convert_system_message_to_human=True,
            max_retries=0,
            request_timeout=30
        )

    # Build message list (system + user)
    messages: List[BaseMessage] = []
    if system_context:
        messages.append(SystemMessage(content=system_context))
    messages.append(HumanMessage(content=prompt))

    attempt = 1

    while attempt <= max_retries:
        try:
            logger.info(
                f"Calling Gemini API (Attempt {attempt}/{max_retries}). "
                f"Prompt (truncated): {prompt[:100]}..."
            )
            # Async invocation
            response = await client.ainvoke(messages)
            content = response.content

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

            # ── Rate Limit Handling (HTTP 429 / ResourceExhausted) ────────────
            is_rate_limit = (
                "429" in error_msg
                or "ResourceExhausted" in error_msg
                or "rate limit" in error_msg.lower()
                or "ResourceExhausted" in error_class
            )

            if is_rate_limit and attempt < max_retries:
                sleep_time = (2 ** attempt) + 3  # 5s → 7s → 11s back-off
                logger.info(f"Rate limit hit. Sleeping for {sleep_time}s and retrying...")
                await asyncio.sleep(sleep_time)
                attempt += 1
                continue
            elif is_rate_limit:
                raise AIServiceError(
                    f"Gemini rate limit exceeded after {max_retries} retries: {error_msg}"
                )

            # ── Connection / Timeout Handling ─────────────────────────────────
            is_timeout_or_conn = (
                "timeout" in error_msg.lower()
                or "connection" in error_msg.lower()
                or "api connection" in error_msg.lower()
                or "deadline" in error_msg.lower()
            )

            if is_timeout_or_conn and attempt < max_retries:
                sleep_time = 2 ** attempt
                logger.info(f"Connection/timeout error. Backing off for {sleep_time}s...")
                await asyncio.sleep(sleep_time)
                attempt += 1
                continue
            else:
                logger.error(
                    f"Final failure or unhandled exception during Gemini call: "
                    f"{error_class} - {error_msg}"
                )
                raise AIServiceError(f"Gemini LLM call failed: {error_msg}")

    raise AIServiceError("Gemini call failed after maximum retries")
