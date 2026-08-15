from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain.memory import ConversationBufferMemory
from app.shared.llm import llm
import logging
import asyncio

logger = logging.getLogger(__name__)


# ─── CONSTANTS ────────────────────────────────────────────────────────────────

# System prompt template injected at the start of every interview conversation.
# Variables are filled in at runtime from the job context dict.
SYSTEM_MESSAGE_TEMPLATE = """You are an expert interview coach specializing in {job_title} roles at {company}.
Your role is to conduct a realistic mock interview and provide constructive feedback.

Job Context:
- Title: {job_title}
- Company: {company}
- Required Skills: {required_skills}
- Experience Level: {experience_level}
- Key Responsibilities: {key_responsibilities}

Interview Conduct Rules:
1. Ask one question at a time
2. Questions should progressively test: technical depth, problem-solving,
   communication, and cultural fit
3. Each question should relate to job responsibilities
4. After user answers, ask follow-up if answer is incomplete
5. Conduct interview for exactly 5-7 questions then summarize
6. After final answer, provide:
   - Technical assessment
   - Soft skills assessment
   - Fit with job assessment
   - Actionable improvement areas

Response Format:
- Always structure response as: QUESTION: [question text]
- For feedback: FEEDBACK: [structured feedback]
"""


# ─── RESPONSE PARSING ─────────────────────────────────────────────────────────

def parse_response(response: str) -> tuple:
    """
    Parse a raw LLM response string to extract the type and content.

    Expected formats:
      - "QUESTION: <question text>"
      - "FEEDBACK: <feedback text>"
      - Raw JSON starting with '{' and containing 'overall_rating'

    Returns:
        A tuple (response_type, text_content) where response_type is
        one of "QUESTION" or "FEEDBACK".
    Falls back to ("QUESTION", <full response>) if no prefix is found.
    """
    response_stripped = response.strip()

    # Check for clean prefix at the start of the response
    if response_stripped.startswith("QUESTION:"):
        return "QUESTION", response_stripped[len("QUESTION:"):].strip()
    elif response_stripped.startswith("FEEDBACK:"):
        return "FEEDBACK", response_stripped[len("FEEDBACK:"):].strip()

    # Search within the response body for the prefix
    if "QUESTION:" in response_stripped:
        parts = response_stripped.split("QUESTION:", 1)
        return "QUESTION", parts[1].strip()
    elif "FEEDBACK:" in response_stripped:
        parts = response_stripped.split("FEEDBACK:", 1)
        return "FEEDBACK", parts[1].strip()

    # Detect JSON-style feedback blob
    if response_stripped.startswith("{") and "overall_rating" in response_stripped:
        return "FEEDBACK", response_stripped

    # Default: treat the entire response as a question
    return "QUESTION", response_stripped


# ─── MAIN CHAIN FUNCTION ──────────────────────────────────────────────────────

async def run_interview_chain(
    job_context: dict,
    messages_history: list,
    user_input: str,
    temperature: float = 0.7
) -> tuple:
    """
    Build and invoke the Gemini interview chain for a single turn.

    Process:
      1. Load past messages (up to 40) into LangChain ConversationBufferMemory.
      2. Format the system prompt with job context variables.
      3. Invoke the LLM with [SystemMessage] + history + [HumanMessage].
      4. Parse the response; retry up to 2 times if the format is wrong.
      5. On repeated failures, return a safe fallback question.

    Args:
        job_context:      Dict with job_title, company, required_skills, etc.
        messages_history: List of past {'role': ..., 'content': ...} dicts.
        user_input:       The candidate's latest message.
        temperature:      Sampling temperature for the LLM (default 0.7).

    Returns:
        Tuple (response_type, parsed_content) — e.g. ("QUESTION", "Tell me about...").
    """
    # ── 1. Initialize memory and load conversation history ────────────────────
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    for msg in messages_history[-40:]:  # Limit to last 40 messages (~20 turns)
        role = msg.get("role")
        content = msg.get("content")
        if role == "user":
            memory.chat_memory.add_user_message(content)
        else:
            memory.chat_memory.add_ai_message(content)

    # ── 2. Build the system prompt from the job context ───────────────────────
    system_text = SYSTEM_MESSAGE_TEMPLATE.format(
        job_title=job_context.get("job_title", "Software Developer"),
        company=job_context.get("company", "the company"),
        required_skills=job_context.get("required_skills", "General engineering"),
        experience_level=job_context.get("experience_level", "Junior"),
        key_responsibilities=job_context.get("key_responsibilities", "Product development")
    )

    # ── 3. Assemble the full prompt message list ───────────────────────────────
    history = memory.load_memory_variables({})["chat_history"]
    prompt_messages = [SystemMessage(content=system_text)]
    prompt_messages.extend(history)
    prompt_messages.append(HumanMessage(content=user_input))

    retries = 2
    fallback_question = "Could you elaborate on your experience with building web services or APIs?"

    # ── 4. Invoke LLM with retry logic ────────────────────────────────────────
    for attempt in range(retries + 1):
        try:
            # Apply a 15-second timeout to prevent hanging requests
            response = await asyncio.wait_for(
                llm.ainvoke(prompt_messages),
                timeout=15.0
            )
            content = response.content

            # Parse and validate response format
            role, parsed = parse_response(content)

            if role in ["QUESTION", "FEEDBACK"] and parsed:
                return role, parsed

            logger.warning(
                f"Attempt {attempt}/{retries}: LLM output did not match format rules. "
                f"Output: {content[:100]}..."
            )
            # Instruct the model to correct its format on the next retry
            prompt_messages.append(AIMessage(content=content))
            prompt_messages.append(HumanMessage(
                content=(
                    "Please format your previous response correctly using either "
                    "'QUESTION:' or 'FEEDBACK:' prefix."
                )
            ))
        except asyncio.TimeoutError:
            logger.error("LLM call timed out.")
            if attempt == retries:
                return "QUESTION", "Can you explain a technical challenge you recently overcame?"
        except Exception as e:
            logger.error(f"Error during chain invocation: {e}")
            if attempt == retries:
                break
            await asyncio.sleep(1)  # Brief pause before retry

    # ── 5. Final fallback question ─────────────────────────────────────────────
    return "QUESTION", "Tell me about a project you are proud of and the technical decisions you made."
