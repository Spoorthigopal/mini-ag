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


async def start_interview(user_id: str, job_id: str, db: Session) -> dict:
    """
    Start a new mock interview session.
    Validates user and job, creates the session, generates the first question, and stores it.
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

        # Create active Interview Session
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

        # Build initial job context for first question
        job_context = {
            "job_title": job.job_title,
            "company": job.company_name,
            "required_skills": ", ".join(job.required_skills) if job.required_skills else "General technical skills",
            "experience_level": "Junior/Intern" if not job.duration_months else f"{job.duration_months} months dur",
            "key_responsibilities": job.job_description[:500] if job.job_description else "General development duties"
        }

        # Generate first question (starting the conversation helper)
        # We pass empty history and prompt for the first question
        _, first_question = await run_interview_chain(
            job_context=job_context,
            messages_history=[],
            user_input="Hello! I am ready to start my mock interview."
        )

        # Store first assistant message in session
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
    """Evaluate a single user answer using Gemini."""
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
        response = await call_gemini(prompt, system_context="You are a strict, helpful AI interviewer.")
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
    Process candidate response: evaluates answer, saves feedback, check limits, generates next question.
    """
    try:
        # Fetch active session
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

        # Check session expiry (> 1 hour since started)
        if datetime.utcnow() - session.started_at > timedelta(hours=1):
            session.status = "expired"
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Interview session has expired (max 1 hour limit exceeded)"
            )

        # Identify last question asked to candidate
        last_question = "Tell me about yourself."
        messages = list(session.messages_json or [])
        for msg in reversed(messages):
            if msg.get("role") == "assistant":
                content = msg.get("content", "")
                if content.startswith("QUESTION:"):
                    last_question = content[len("QUESTION:"):].strip()
                else:
                    last_question = content.strip()
                break

        # Append candidate response to session's messages
        messages.append({
            "role": "user",
            "content": user_answer,
            "timestamp": datetime.utcnow().isoformat()
        })
        session.messages_json = messages
        db.commit()

        # Fetch job information for context
        job = db.query(InternshipJob).filter(InternshipJob.id == session.job_id).first()
        job_title = job.job_title if job else "Software Developer"

        # Evaluate response in real time
        feedback_eval = await evaluate_single_answer(last_question, user_answer, job_title)

        # Store feedback record in database
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

        # Count total answered questions to determine termination (5-7 questions)
        total_questions = db.query(InterviewFeedback).filter(
            InterviewFeedback.session_id == session_id
        ).count()

        # Complete interview if question threshold (7) is met
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

        # Otherwise, run chain to get next question
        job_context = {
            "job_title": job.job_title if job else "Software Developer",
            "company": job.company_name if job else "the company",
            "required_skills": ", ".join(job.required_skills) if (job and job.required_skills) else "General technical skills",
            "experience_level": "Junior/Intern" if not (job and job.duration_months) else f"{job.duration_months} months dur",
            "key_responsibilities": job.job_description[:500] if (job and job.job_description) else "General development duties"
        }

        # Query LangChain components
        _, next_question_text = await run_interview_chain(
            job_context=job_context,
            messages_history=messages,
            user_input=user_answer
        )

        # Append assistant next question to session's messages
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
    Fetch all feedback entries, calculate metrics, and output aggregated mock interview statistics.
    """
    # Verify session exists
    session = db.query(InterviewSession).filter(
        InterviewSession.session_id == session_id
    ).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview session {session_id} not found"
        )

    # Fetch all feedback entries
    feedback_entries = db.query(InterviewFeedback).filter(
        InterviewFeedback.session_id == session_id
    ).all()

    if not feedback_entries:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No feedback records found for this session. Complete at least one question first."
        )

    total_q = len(feedback_entries)
    tech_avg = sum(f.technical_accuracy for f in feedback_entries) / total_q
    comm_avg = sum(f.communication_clarity for f in feedback_entries) / total_q
    rel_avg = sum(f.relevance_to_job for f in feedback_entries) / total_q

    # Calculate overall rating on a 0-100 scale
    overall_score = ((tech_avg + comm_avg + rel_avg) / 3.0) * 10.0

    # Aggregate strengths and improvements
    strengths_pool = []
    improvements_pool = []
    for f in feedback_entries:
        if isinstance(f.strengths, list):
            strengths_pool.extend(f.strengths)
        if isinstance(f.improvement_areas, list):
            improvements_pool.extend(f.improvement_areas)

    # Get top 3 strengths and improvements
    top_strengths = [item for item, count in Counter(strengths_pool).most_common(3)]
    top_improvements = [item for item, count in Counter(improvements_pool).most_common(3)]

    # Make fallback values in case LLM summary call fails
    recommendations = "Focus on structuring responses using the STAR method (Situation, Task, Action, Result)."
    job_fit_assessment = "Shows appropriate fundamental skill set but needs minor refinement in communicating technical depth."

    # Call Gemini to compile cohesive summary evaluations
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
        response = await call_gemini(summary_prompt, system_context="You are a professional HR evaluator.")
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


def cleanup_expired_sessions(db: Session) -> int:
    """
    Finds all active sessions older than 24 hours and marks them as expired.
    Returns the count of modified sessions.
    """
    try:
        cutoff = datetime.utcnow() - timedelta(hours=24)
        expired_sessions = db.query(InterviewSession).filter(
            InterviewSession.status == "active",
            InterviewSession.started_at < cutoff
        ).all()

        count = len(expired_sessions)
        for s in expired_sessions:
            s.status = "expired"

        db.commit()
        return count
    except Exception as e:
        db.rollback()
        logger.error(f"Error executing expired sessions cleanup: {e}")
        return 0


# ─── STUDY COACH FUNCTIONS ────────────────────────────────────────────────────

async def generate_study_plan(
    user_id: str,
    job_id: str,
    skill: str,
    user_level: str,
    db: Session
) -> dict:
    """Create a personalized study plan session for the selected skill and level."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    job = db.query(InternshipJob).filter(InternshipJob.id == job_id).first()
    job_title = job.job_title if job else "Software Developer"

    prompt = f"""You are an expert educator and study plan designer.
A student wants to learn "{skill}" for a "{job_title}" role. Their self-rated level is: {user_level}.

Create a structured study plan with 5-7 topics ordered from foundational to advanced.
Each topic should be a clear, specific concept (not vague like "Introduction").

Return ONLY a JSON array like this:
["Topic 1 Name", "Topic 2 Name", "Topic 3 Name", "Topic 4 Name", "Topic 5 Name"]

Make topics specific and actionable. Example for React Beginner: 
["What is React and how browsers render components", "JSX syntax and writing your first component", "Props: passing data between components", "State with useState hook", "Handling events and user input", "useEffect and lifecycle basics", "Fetching data from an API"]
"""
    raw = await call_gemini(prompt, system_context="You are a curriculum designer. Respond with JSON only.")
    
    # Parse the topics list
    start = raw.find("[")
    end = raw.rfind("]") + 1
    topics = []
    if start != -1 and end > start:
        try:
            topics = json.loads(raw[start:end])
        except Exception:
            topics = [f"Introduction to {skill}", f"Core Concepts of {skill}", f"Practical {skill} Applications",
                      f"Advanced {skill} Patterns", f"Best Practices for {skill}"]
    
    if not topics:
        topics = [f"Introduction to {skill}", f"Core Concepts of {skill}", f"Practical {skill} Applications",
                  f"Advanced {skill} Patterns", f"Best Practices for {skill}"]

    # Create a session
    session_uuid = str(uuid.uuid4())
    session = InterviewSession(
        user_id=user_id,
        job_id=job_id,
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
    """Generate a rich explanation for the current topic in the session."""
    session = db.query(InterviewSession).filter(
        InterviewSession.session_id == session_id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    topics = session.study_plan or []
    idx = session.current_topic_index or 0

    if idx >= len(topics):
        return {
            "session_id": session_id,
            "topic": "All topics completed!",
            "explanation": "🎉 Congratulations! You've completed the entire study plan. You should now have a solid understanding of the skill. Keep practising!",
            "current_index": idx,
            "total_topics": len(topics),
            "is_complete": True
        }

    topic = topics[idx]
    skill = session.skill_focus or "the subject"
    level = session.user_level or "Beginner"
    job = db.query(InternshipJob).filter(InternshipJob.id == session.job_id).first()
    job_title = job.job_title if job else "Software Developer"

    prompt = f"""You are a warm, engaging tutor teaching "{topic}" (part of learning "{skill}" for a {job_title} role).
The student is a "{level}".

Structure your explanation like this:
1. **Hook** - Start with a relatable real-world analogy or story (2-3 sentences). Make it conversational, NOT textbook-style.
2. **The Core Idea** - Explain the concept in plain English first. Then give a short, concrete real-world example (e.g., how Instagram, Spotify, or Uber uses this).
3. **Let's Get Technical** - Now explain the technical details, with a short code snippet if applicable (keep it under 12 lines).
4. **Key Takeaway** - One sentence summary of the most important thing to remember.

Keep the TOTAL response under 500 words. Be encouraging and human. Do not use bullet points for the overall structure - use flowing paragraphs with bold headings."""

    explanation = await call_gemini(prompt, system_context="You are an encouraging, world-class programming tutor.", temperature=0.4, max_tokens=800)

    # Store in messages
    messages = list(session.messages_json or [])
    messages.append({
        "role": "assistant",
        "content": f"**Topic {idx + 1}: {topic}**\n\n{explanation}",
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
    """Handle 'go_deeper' or 'move_next' actions from the user."""
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

    if action == "move_next":
        new_idx = idx + 1
        session.current_topic_index = new_idx
        messages.append({
            "role": "user",
            "content": "Move to next topic →",
            "timestamp": datetime.utcnow().isoformat()
        })
        session.messages_json = messages
        db.commit()
        return await teach_topic(session_id, db)

    elif action == "go_deeper":
        # User asked a follow-up question on the current topic
        messages.append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Build conversation context
        recent_history = "\n".join([
            f"{m['role'].capitalize()}: {m['content'][:300]}"
            for m in messages[-6:]
        ])

        prompt = f"""You are teaching "{topic}" (in the context of "{skill}") and the student asked:
"{user_message}"

Conversation so far:
{recent_history}

Answer their question in a helpful, human way. Give a real-world example if possible. Be concise (under 300 words). If they ask to go even deeper on a sub-concept, do so enthusiastically."""

        response = await call_gemini(prompt, system_context="You are an expert, encouraging tutor.", temperature=0.5, max_tokens=600)

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

    raise HTTPException(status_code=400, detail="Invalid action. Use 'go_deeper' or 'move_next'.")


async def resume_session(session_id: str, db: Session) -> dict:
    """Resume an existing study session."""
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
