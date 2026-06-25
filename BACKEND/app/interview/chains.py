from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain.memory import ConversationBufferMemory
from app.shared.llm import llm
import logging
import asyncio

logger = logging.getLogger(__name__)

# System Prompt Template matching detailed requirements
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


def parse_response(response: str) -> tuple:
    """
    Parse LLM response to extract QUESTION or FEEDBACK content.
    Returns (response_type, text_content).
    """
    response_stripped = response.strip()
    
    # Try direct starts
    if response_stripped.startswith("QUESTION:"):
        return "QUESTION", response_stripped[len("QUESTION:"):].strip()
    elif response_stripped.startswith("FEEDBACK:"):
        return "FEEDBACK", response_stripped[len("FEEDBACK:"):].strip()
    
    # Search within text if not clean prefix
    if "QUESTION:" in response_stripped:
        parts = response_stripped.split("QUESTION:", 1)
        return "QUESTION", parts[1].strip()
    elif "FEEDBACK:" in response_stripped:
        parts = response_stripped.split("FEEDBACK:", 1)
        return "FEEDBACK", parts[1].strip()
        
    # Check if there is JSON-like structure inside for feedback
    if response_stripped.startswith("{") and "overall_rating" in response_stripped:
        return "FEEDBACK", response_stripped
        
    # Default fallback
    return "QUESTION", response_stripped


async def run_interview_chain(
    job_context: dict,
    messages_history: list,
    user_input: str,
    temperature: float = 0.7
) -> tuple:
    """
    Construct prompt, load memory, and call Gemini.
    Validates the response format and retries if malformed (max 2 retries).
    """
    # 1. Initialize ConversationBufferMemory (k=20 turns -> max 40 messages)
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    
    # Load past turns into memory
    for msg in messages_history[-40:]:
        role = msg.get("role")
        content = msg.get("content")
        if role == "user":
            memory.chat_memory.add_user_message(content)
        else:
            memory.chat_memory.add_ai_message(content)

    # 2. Build system message with formatted variables
    system_text = SYSTEM_MESSAGE_TEMPLATE.format(
        job_title=job_context.get("job_title", "Software Developer"),
        company=job_context.get("company", "the company"),
        required_skills=job_context.get("required_skills", "General engineering"),
        experience_level=job_context.get("experience_level", "Junior"),
        key_responsibilities=job_context.get("key_responsibilities", "Product development")
    )
    
    # 3. Retrieve conversation history
    history = memory.load_memory_variables({})["chat_history"]

    # 4. Form prompt messages list
    prompt_messages = [SystemMessage(content=system_text)]
    prompt_messages.extend(history)
    prompt_messages.append(HumanMessage(content=user_input))

    retries = 2
    fallback_question = "QUESTION: Could you elaborate on your experience with building web services or APIs?"
    
    for attempt in range(retries + 1):
        try:
            # Handle timeout using asyncio.wait_for (e.g., 15 seconds)
            response = await asyncio.wait_for(llm.ainvoke(prompt_messages), timeout=15.0)
            content = response.content
            
            # Parse response
            role, parsed = parse_response(content)
            
            # Validation check
            if role in ["QUESTION", "FEEDBACK"] and parsed:
                return role, parsed
                
            logger.warning(
                f"Attempt {attempt}/{retries}: LLM output did not match format rules. Output: {content[:100]}..."
            )
            # Add instruction for correction on next retry
            prompt_messages.append(AIMessage(content=content))
            prompt_messages.append(HumanMessage(content="Please format your previous response correctly using either 'QUESTION:' or 'FEEDBACK:' prefix."))
        except asyncio.TimeoutError:
            logger.error("LLM call timed out.")
            if attempt == retries:
                return "QUESTION", "Can you explain a technical challenge you recently overcame?"
        except Exception as e:
            logger.error(f"Error during chain invocation: {e}")
            if attempt == retries:
                break
            await asyncio.sleep(1)

    return "QUESTION", "Tell me about a project you are proud of and the technical decisions you made."
