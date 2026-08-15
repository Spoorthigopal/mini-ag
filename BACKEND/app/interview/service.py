import asyncio
from sqlalchemy.orm import Session
from app.interview.models import InterviewSession, InterviewFeedback
from app.internships.models import InternshipJob
from app.auth.models import User
from app.interview.chains import run_interview_chain
from app.shared.llm import call_gemini
from datetime import datetime, timedelta
import uuid
import logging
import json
from collections import Counter
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


# ─── MOCK INTERVIEW FUNCTIONS ─────────────────────────────────────────────────

async def start_interview(user_id: str, job_id: str, db: Session) -> dict:
    """
    Start a new mock interview session.

    - Validates that both the user and job exist in the database.
    - Creates an InterviewSession record with status='active'.
    - Generates the first interview question via the LangChain chain.
    - Stores the first assistant message and returns the session details.
    """
    try:
        # Validate user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )

        # Validate job exists
        job = db.query(InternshipJob).filter(InternshipJob.id == job_id).first()
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job with ID {job_id} not found"
            )

        # Create active interview session record
        session_uuid = str(uuid.uuid4())
        session = InterviewSession(
            user_id=user_id,
            job_id=job_id,
            session_id=session_uuid,
            started_at=datetime.utcnow(),
            status="active",
            messages_json=[]
        )
        db.add(session)
        db.commit()
        db.refresh(session)

        # Build job context dict for the interview chain prompt
        job_context = {
            "job_title": job.job_title,
            "company": job.company_name,
            "required_skills": (
                ", ".join(job.required_skills)
                if job.required_skills
                else "General technical skills"
            ),
            "experience_level": (
                "Junior/Intern"
                if not job.duration_months
                else f"{job.duration_months} months dur"
            ),
            "key_responsibilities": (
                job.job_description[:500]
                if job.job_description
                else "General development duties"
            )
        }

        # Generate the first interview question (empty history, greeting input)
        _, first_question = await run_interview_chain(
            job_context=job_context,
            messages_history=[],
            user_input="Hello! I am ready to start my mock interview."
        )

        # Persist first assistant message to session history
        first_msg = {
            "role": "assistant",
            "content": f"QUESTION: {first_question}",
            "timestamp": datetime.utcnow().isoformat()
        }
        session.messages_json = [first_msg]
        db.commit()

        return {
            "session_id": session.session_id,
            "question": first_question,
            "interview_started": True
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        logger.error(f"Database error starting interview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database or system error occurred while starting mock interview"
        )


async def evaluate_single_answer(
    question: str,
    user_answer: str,
    job_title: str
) -> dict:
    """
    Evaluate a single candidate answer using Gemini.

    Returns a dict with:
      - technical_accuracy (float 0-10)
      - communication_clarity (float 0-10)
      - relevance_to_job (float 0-10)
      - strengths (list[str])
      - improvement_areas (list[str])
      - sample_better_answer (str)
    Falls back to default scores (6.0) on any parsing error.
    """
    prompt = f"""You are an expert interview coach evaluating a candidate's answer for a {job_title} role.
Question: {question}
Candidate's Answer: {user_answer}

Provide feedback strictly as a JSON object with this structure:
{{
  "technical_accuracy": 7.5,
  "communication_clarity": 8.0,
  "relevance_to_job": 7.0,
  "strengths": ["Clear explanation of concept X", "Good logical structure"],
  "improvement_areas": ["Could specify libraries used", "Elaborate on scaling"],
  "sample_better_answer": "A stronger answer would be: ..."
}}
Do not write anything else besides the raw JSON object.
"""
    try:
        response = await call_gemini(
            prompt,
            system_context="You are a strict, helpful AI interviewer."
        )
        # Extract JSON block from response
        start = response.find("{")
        end = response.rfind("}") + 1
        if start != -1 and end > start:
            data = json.loads(response[start:end])
            return {
                "technical_accuracy": float(data.get("technical_accuracy", 7.0)),
                "communication_clarity": float(data.get("communication_clarity", 7.0)),
                "relevance_to_job": float(data.get("relevance_to_job", 7.0)),
                "strengths": list(data.get("strengths", [])),
                "improvement_areas": list(data.get("improvement_areas", [])),
                "sample_better_answer": str(data.get("sample_better_answer", ""))
            }
    except Exception as e:
        logger.error(f"Error evaluating single answer: {e}")

    # Default fallback scores if evaluation fails
    return {
        "technical_accuracy": 6.0,
        "communication_clarity": 6.0,
        "relevance_to_job": 6.0,
        "strengths": ["Answered the question"],
        "improvement_areas": ["Provide more detailed structure"],
        "sample_better_answer": "Try to detail your design choices or experience more."
    }


async def process_answer(session_id: str, user_answer: str, db: Session) -> dict:
    """
    Process a candidate's answer to the current interview question.

    Flow:
      1. Validate the session is active and not expired (>1 hour).
      2. Identify the last question asked.
      3. Append the candidate's answer to session history.
      4. Evaluate the answer with Gemini and store an InterviewFeedback record.
      5. If 7 questions have been answered, mark the session 'completed'.
      6. Otherwise, generate the next question and append it to history.
    """
    try:
        # Fetch and validate the active session
        session = db.query(InterviewSession).filter(
            InterviewSession.session_id == session_id
        ).first()

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Interview session {session_id} not found"
            )

        if session.status != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Interview session is not active"
            )

        # Expire sessions that have exceeded the 1-hour time limit
        if datetime.utcnow() - session.started_at > timedelta(hours=1):
            session.status = "expired"
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Interview session has expired (max 1 hour limit exceeded)"
            )

        # Identify the last question posed by the assistant
        last_question = "Tell me about yourself."
        messages = list(session.messages_json or [])
        for msg in reversed(messages):
            if msg.get("role") == "assistant":
                content = msg.get("content", "")
                last_question = (
                    content[len("QUESTION:"):].strip()
                    if content.startswith("QUESTION:")
                    else content.strip()
                )
                break

        # Append candidate response to session history
        messages.append({
            "role": "user",
            "content": user_answer,
            "timestamp": datetime.utcnow().isoformat()
        })
        session.messages_json = messages
        db.commit()

        # Fetch job info to provide role-specific context during evaluation
        job = db.query(InternshipJob).filter(InternshipJob.id == session.job_id).first()
        job_title = job.job_title if job else "Software Developer"

        # Evaluate the answer and store feedback record
        feedback_eval = await evaluate_single_answer(last_question, user_answer, job_title)

        feedback = InterviewFeedback(
            session_id=session_id,
            question=last_question,
            user_answer=user_answer,
            technical_accuracy=feedback_eval["technical_accuracy"],
            communication_clarity=feedback_eval["communication_clarity"],
            relevance_to_job=feedback_eval["relevance_to_job"],
            strengths=feedback_eval["strengths"],
            improvement_areas=feedback_eval["improvement_areas"],
            sample_answer=feedback_eval["sample_better_answer"]
        )
        db.add(feedback)
        db.commit()
        db.refresh(feedback)

        # Count answered questions to check against the 7-question limit
        total_questions = db.query(InterviewFeedback).filter(
            InterviewFeedback.session_id == session_id
        ).count()

        # Mark session complete after 7 questions
        if total_questions >= 7:
            session.status = "completed"
            session.ended_at = datetime.utcnow()
            db.commit()

            return {
                "session_id": session_id,
                "next_question": None,
                "feedback": feedback,
                "interview_complete": True
            }

        # Build job context for next question generation
        job_context = {
            "job_title": job.job_title if job else "Software Developer",
            "company": job.company_name if job else "the company",
            "required_skills": (
                ", ".join(job.required_skills)
                if (job and job.required_skills)
                else "General technical skills"
            ),
            "experience_level": (
                "Junior/Intern"
                if not (job and job.duration_months)
                else f"{job.duration_months} months dur"
            ),
            "key_responsibilities": (
                job.job_description[:500]
                if (job and job.job_description)
                else "General development duties"
            )
        }

        # Generate the next interview question via the LangChain chain
        _, next_question_text = await run_interview_chain(
            job_context=job_context,
            messages_history=messages,
            user_input=user_answer
        )

        # Append next question to session history
        messages.append({
            "role": "assistant",
            "content": f"QUESTION: {next_question_text}",
            "timestamp": datetime.utcnow().isoformat()
        })
        session.messages_json = messages
        db.commit()

        return {
            "session_id": session_id,
            "next_question": next_question_text,
            "feedback": feedback,
            "interview_complete": False
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        logger.error(f"Error processing interview answer: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error occurred while processing mock interview response"
        )


async def get_session_summary(session_id: str, db: Session) -> dict:
    """
    Aggregate all feedback entries for a session into a summary report.

    Calculates:
      - Averages for technical accuracy, communication clarity, relevance
      - Overall score on a 0-100 scale
      - Top-3 recurring strengths and improvement areas
      - LLM-generated recommendations and job-fit assessment
    """
    # Verify the session exists
    session = db.query(InterviewSession).filter(
        InterviewSession.session_id == session_id
    ).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview session {session_id} not found"
        )

    # Fetch all feedback records for the session
    feedback_entries = db.query(InterviewFeedback).filter(
        InterviewFeedback.session_id == session_id
    ).all()

    if not feedback_entries:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "No feedback records found for this session. "
                "Complete at least one question first."
            )
        )

    # Calculate per-metric averages
    total_q = len(feedback_entries)
    tech_avg = sum(f.technical_accuracy for f in feedback_entries) / total_q
    comm_avg = sum(f.communication_clarity for f in feedback_entries) / total_q
    rel_avg = sum(f.relevance_to_job for f in feedback_entries) / total_q

    # Overall score mapped to a 0-100 scale
    overall_score = ((tech_avg + comm_avg + rel_avg) / 3.0) * 10.0

    # Aggregate and rank recurring strengths and improvement areas
    strengths_pool = []
    improvements_pool = []
    for f in feedback_entries:
        if isinstance(f.strengths, list):
            strengths_pool.extend(f.strengths)
        if isinstance(f.improvement_areas, list):
            improvements_pool.extend(f.improvement_areas)

    top_strengths = [item for item, _ in Counter(strengths_pool).most_common(3)]
    top_improvements = [item for item, _ in Counter(improvements_pool).most_common(3)]

    # Fallback text in case the Gemini summary call fails
    recommendations = (
        "Focus on structuring responses using the STAR method "
        "(Situation, Task, Action, Result)."
    )
    job_fit_assessment = (
        "Shows appropriate fundamental skill set but needs minor refinement "
        "in communicating technical depth."
    )

    # Ask Gemini for cohesive qualitative recommendations
    summary_prompt = f"""You are an expert interview coach summarizing a mock interview.
Performance Metrics:
- Total Questions: {total_q}
- Tech Accuracy Average: {tech_avg:.2f}/10
- Communication Clarity Average: {comm_avg:.2f}/10
- Relevance Average: {rel_avg:.2f}/10
- Overall Rating: {overall_score:.2f}/100

Key Strengths: {top_strengths}
Key Improvement Areas: {top_improvements}

Provide:
1. Overall recommendation (1-2 sentences on what they should focus on next).
2. Job fit assessment (1-2 sentences rating their readiness for this specific role).

Format your response strictly as JSON:
{{
  "recommendations": "...",
  "job_fit_assessment": "..."
}}
"""
    try:
        response = await call_gemini(
            summary_prompt,
            system_context="You are a professional HR evaluator."
        )
        start = response.find("{")
        end = response.rfind("}") + 1
        if start != -1 and end > start:
            data = json.loads(response[start:end])
            recommendations = data.get("recommendations", recommendations)
            job_fit_assessment = data.get("job_fit_assessment", job_fit_assessment)
    except Exception as e:
        logger.error(f"Error compiling recommendations in summary: {e}")

    return {
        "session_id": session_id,
        "total_questions": total_q,
        "overall_score": round(overall_score, 2),
        "technical_average": round(tech_avg, 2),
        "communication_average": round(comm_avg, 2),
        "relevance_average": round(rel_avg, 2),
        "strengths": top_strengths,
        "improvements": top_improvements,
        "recommendations": recommendations,
        "job_fit_assessment": job_fit_assessment
    }


# ─── STUDY COACH FUNCTIONS ────────────────────────────────────────────────────

# Static study plans used as fallback when Gemini is unavailable or rate-limited
STATIC_PLANS = {
    "React": {
        "Beginner": [
            "What is React and how browsers render UI",
            "JSX syntax and writing your first component",
            "Props: passing data between components",
            "State with useState hook",
            "Handling events and user input",
            "useEffect and side effects",
            "Fetching data from an API"
        ],
        "Intermediate": [
            "React component lifecycle deep-dive",
            "useContext and avoiding prop drilling",
            "useReducer for complex state",
            "Custom hooks and reusability",
            "React Router and navigation",
            "Performance with useMemo and useCallback",
            "React Query for server state"
        ],
        "Expert": [
            "Concurrent rendering and Suspense",
            "Server Components (React 18+)",
            "Code splitting and lazy loading",
            "Advanced patterns: compound components",
            "Testing with React Testing Library",
            "Micro-frontend architecture",
            "Performance profiling and optimization"
        ],
    },
    "TypeScript": {
        "Beginner": [
            "Types vs interfaces and when to use each",
            "Basic generics",
            "Union and intersection types",
            "Type narrowing and guards",
            "Working with arrays and tuples"
        ],
        "Intermediate": [
            "Utility types (Partial, Pick, Omit)",
            "Conditional types",
            "Template literal types",
            "Module augmentation",
            "Decorators and metadata"
        ],
        "Expert": [
            "Infer keyword and type inference tricks",
            "Higher-kinded types patterns",
            "Complex generic constraints",
            "Declaration files (.d.ts)",
            "TypeScript compiler API"
        ],
    },
    "Python": {
        "Beginner": [
            "Python data types and variables",
            "Control flow: if/else, loops",
            "Functions and scope",
            "Lists, dicts, sets and tuples",
            "File I/O and exceptions"
        ],
        "Intermediate": [
            "Object-oriented programming in Python",
            "List comprehensions and generators",
            "Decorators and closures",
            "Modules, packages and pip",
            "Working with APIs using requests"
        ],
        "Expert": [
            "Async/await with asyncio",
            "Metaclasses and descriptors",
            "Performance: profiling and optimisation",
            "C extensions and Cython basics",
            "Writing library-quality code"
        ],
    },
    "SQL": {
        "Beginner": [
            "SELECT, WHERE, ORDER BY basics",
            "JOINs: INNER, LEFT, RIGHT",
            "Aggregate functions: COUNT, SUM, AVG",
            "GROUP BY and HAVING",
            "INSERT, UPDATE, DELETE"
        ],
        "Intermediate": [
            "Subqueries and CTEs",
            "Window functions: ROW_NUMBER, RANK",
            "Indexes and query plans",
            "Transactions and ACID",
            "Stored procedures and triggers"
        ],
        "Expert": [
            "Query optimisation and execution plans",
            "Partitioning and sharding strategies",
            "Replication and high availability",
            "Full-text search",
            "Database normalisation to BCNF/4NF"
        ],
    },
}


def _get_static_plan(skill: str, level: str) -> list:
    """
    Return a static study plan for the given skill and level.
    Used as a fallback when Gemini quota is exhausted.
    If skill/level combo is not found, returns a generic 5-topic plan.
    """
    plan = STATIC_PLANS.get(skill, {}).get(level, None)
    if plan:
        return plan
    return [
        f"Fundamentals of {skill}",
        f"Core concepts in {skill}",
        f"Practical {skill} examples",
        f"Advanced {skill} patterns",
        f"Best practices for {skill} in production",
    ]


async def generate_study_plan(
    user_id: str,
    job_id: str,
    skill: str,
    user_level: str,
    db: Session
) -> dict:
    """
    Create a personalised study plan session for the selected skill and level.

    - Calls Gemini to generate a 5-7 topic ordered plan.
    - Falls back to STATIC_PLANS if Gemini is unavailable.
    - Persists the plan as an InterviewSession with skill_focus set.
    """
    # Validate user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Optionally resolve the job by UUID
    job = None
    if job_id:
        try:
            uuid.UUID(str(job_id))
            job = db.query(InternshipJob).filter(InternshipJob.id == job_id).first()
        except ValueError:
            pass  # Non-UUID job_id — skip job lookup

    job_title = job.job_title if job else "Software Developer"
    valid_job_id = job.id if job else None

    # Try Gemini for a dynamic plan; fall back to static if quota exceeded
    topics = []
    try:
        prompt = f"""You are an expert educator and study plan designer.
A student wants to learn "{skill}" for a "{job_title}" role. Their self-rated level is: {user_level}.

Create a structured study plan with 5-7 topics ordered from foundational to advanced.
Return ONLY a JSON array like this: ["Topic 1", "Topic 2", "Topic 3", "Topic 4", "Topic 5"]
"""
        try:
            raw = await call_gemini(
                prompt,
                system_context=(
                    "You are a curriculum designer. "
                    "Respond with valid JSON only, no markdown blocks."
                ),
                temperature=0.5,
                max_retries=2,
                custom_api_key="AIzaSyCLTCE_qh9EXFmZfozuiGEMdUetSSGb3dA"
            )
        except Exception as e:
            logger.error(f"LLM Error generating plan: {e}")
            raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

        # Strip possible markdown fences from response
        if raw.startswith("```json"):
            raw = raw[7:]
        if raw.startswith("```"):
            raw = raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]
        raw = raw.strip()

        # Extract the JSON array
        start = raw.find("[")
        end = raw.rfind("]") + 1
        if start != -1 and end > start:
            topics = json.loads(raw[start:end])
    except Exception as e:
        logger.warning(f"Gemini unavailable for study plan, using static fallback: {e}")

    if not topics:
        topics = _get_static_plan(skill, user_level)

    # Persist the study session to the database
    session_uuid = str(uuid.uuid4())
    session = InterviewSession(
        user_id=user_id,
        job_id=valid_job_id,
        session_id=session_uuid,
        started_at=datetime.utcnow(),
        status="active",
        messages_json=[],
        skill_focus=skill,
        user_level=user_level,
        study_plan=topics,
        current_topic_index=0
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return {
        "session_id": session_uuid,
        "skill": skill,
        "level": user_level,
        "topics": topics,
        "current_topic_index": 0
    }


async def teach_topic(session_id: str, db: Session) -> dict:
    """
    Generate a rich, structured explanation for the current topic in the study plan.

    Returns the topic explanation along with interview Q&A hints and a check-in question.
    If all topics are complete, returns a congratulations message.
    """
    # Fetch the study session
    session = db.query(InterviewSession).filter(
        InterviewSession.session_id == session_id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    topics = session.study_plan or []
    idx = session.current_topic_index or 0

    # All topics completed — return celebration response
    if idx >= len(topics):
        return {
            "session_id": session_id,
            "topic": "All topics completed!",
            "explanation": (
                "🎉 **Congratulations!** You've completed the entire study plan. "
                "You should now have a solid understanding of the skill. "
                "Keep practising, and you'll do great in your interviews!"
            ),
            "current_index": idx,
            "total_topics": len(topics),
            "is_complete": True
        }

    topic = topics[idx]
    skill = session.skill_focus or "the subject"
    level = session.user_level or "Beginner"
    job = db.query(InternshipJob).filter(InternshipJob.id == session.job_id).first()
    job_title = job.job_title if job else "Software Developer"

    # Build the teaching prompt with structured sections
    prompt = f"""You are a friendly tutor teaching "{topic}" to a {level} learning "{skill}" for a {job_title} role.

**The Hook** (2 sentences): Start with a fun, relatable real-world analogy.

**Easy Explanation** (3-4 sentences): Explain the core idea in plain English anyone can understand.

**Technical Deep-Dive** (4-6 sentences + a short code snippet if relevant): How does it actually work under the hood at a {level} level?

**Interview Questions**: List 2-3 common interview questions on this topic with brief answer hints.

**Check-in**: End with one question to test their understanding.

Be concise, warm, and human. Total response: ~350 words."""

    try:
        explanation = await call_gemini(
            prompt,
            system_context=(
                "You are a friendly, expert programming tutor. "
                "Be concise but thorough. Use a conversational, human tone."
            ),
            temperature=0.7,
            max_tokens=700,
            max_retries=2,
            custom_api_key="AIzaSyCLTCE_qh9EXFmZfozuiGEMdUetSSGb3dA"
        )
    except Exception as e:
        logger.error(f"LLM Error in teach_topic: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"AI service error while teaching topic: {str(e)}"
        )

    # Append explanation to session message history
    messages = list(session.messages_json or [])
    messages.append({
        "role": "assistant",
        "content": explanation,
        "timestamp": datetime.utcnow().isoformat(),
        "topic_index": idx
    })
    session.messages_json = messages
    db.commit()

    return {
        "session_id": session_id,
        "topic": topic,
        "explanation": explanation,
        "current_index": idx,
        "total_topics": len(topics),
        "is_complete": False
    }


async def handle_interaction(
    session_id: str,
    action: str,
    user_message: str,
    db: Session
) -> dict:
    """
    Handle a user interaction with the study coach.

    Supported actions:
      - 'move_next'     — Advance to the next topic and teach it.
      - 'go_deeper'     — Answer a follow-up question on the current topic.
      - 'jump_to_topic' — Jump directly to a topic by index (index in user_message).

    Raises HTTP 400 for invalid actions or out-of-range topic indices.
    """
    session = db.query(InterviewSession).filter(
        InterviewSession.session_id == session_id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    topics = session.study_plan or []
    idx = session.current_topic_index or 0
    topic = topics[idx] if idx < len(topics) else "All topics"
    skill = session.skill_focus or "the subject"

    messages = list(session.messages_json or [])

    # ── move_next: advance to the next topic ──────────────────────────────────
    if action == "move_next":
        new_idx = idx + 1
        session.current_topic_index = new_idx
        messages.append({
            "role": "user",
            "content": "➡️ Let's move to the next topic",
            "timestamp": datetime.utcnow().isoformat()
        })
        session.messages_json = messages
        db.commit()
        return await teach_topic(session_id, db)

    # ── go_deeper: answer a follow-up question on the current topic ───────────
    elif action == "go_deeper":
        messages.append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.utcnow().isoformat()
        })

        # Build recent conversation context (last 3 turns)
        recent_history = "\n".join([
            f"{m['role'].capitalize()}: {m['content'][:300]}"
            for m in messages[-6:]
        ])

        prompt = f"""Student is learning "{topic}" (in "{skill}") and asked: "{user_message}"

**Easy Answer** (2-3 sentences): Explain in plain English with a real-world analogy.
**Technical Answer** (3-5 sentences + code snippet if helpful): Detailed technical explanation.
**Interview Tip**: One related interview question with a brief answer hint.

End with a short follow-up question. Be warm and concise (~250 words)."""

        try:
            response = await call_gemini(
                prompt,
                system_context=(
                    "You are a friendly, expert tutor. "
                    "Be concise, clear, and use a conversational tone."
                ),
                temperature=0.6,
                max_tokens=600,
                max_retries=2,
                custom_api_key="AIzaSyCLTCE_qh9EXFmZfozuiGEMdUetSSGb3dA"
            )
        except Exception as e:
            logger.error(f"LLM Error in go_deeper: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"AI service error: {str(e)}"
            )

        messages.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.utcnow().isoformat()
        })
        session.messages_json = messages
        db.commit()

        return {
            "session_id": session_id,
            "topic": topic,
            "explanation": response,
            "current_index": idx,
            "total_topics": len(topics),
            "is_complete": False,
            "action": "go_deeper"
        }

    # ── jump_to_topic: jump directly to a specific topic index ───────────────
    elif action == "jump_to_topic":
        try:
            target_index = int(user_message)  # user_message holds the target index
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Invalid topic index")
        if target_index < 0 or target_index >= len(topics):
            raise HTTPException(status_code=400, detail="Topic index out of range")
        session.current_topic_index = target_index
        db.commit()
        return await teach_topic(session_id, db)

    raise HTTPException(
        status_code=400,
        detail="Invalid action. Use 'go_deeper', 'move_next', or 'jump_to_topic'."
    )


async def resume_session(session_id: str, db: Session) -> dict:
    """
    Resume an existing study session.
    Returns session metadata including skill, level, topics, progress, and full history.
    """
    session = db.query(InterviewSession).filter(
        InterviewSession.session_id == session_id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": session_id,
        "skill": session.skill_focus,
        "level": session.user_level,
        "topics": session.study_plan or [],
        "current_topic_index": session.current_topic_index or 0,
        "messages": session.messages_json or [],
        "status": session.status
    }
