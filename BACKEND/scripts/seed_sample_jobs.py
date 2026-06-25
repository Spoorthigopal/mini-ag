"""
Seed sample internship/job listings into the database.
Run: python scripts/seed_sample_jobs.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app.database import SessionLocal, init_db
from app.auth.models import User  # noqa: F401
from app.welfare.models import WelfareScheme  # noqa: F401
from app.internships.models import InternshipJob  # noqa: F401
from app.interview.models import InterviewSession  # noqa: F401
from app.digilocker.models import Document  # noqa: F401
from app.shared.models import Conversation  # noqa: F401
from app.shared.embeddings import embeddings_client

import logging
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SAMPLE_JOBS = [
    {
        "job_title": "Software Development Intern",
        "company_name": "Infosys",
        "company_rating": 4.0,
        "location": "Bengaluru, India",
        "job_description": "Work on real-world software projects using Java, Python and cloud technologies. Collaborate with senior developers on enterprise applications.",
        "stipend": 15000.0,
        "duration_months": 6,
        "job_type": "internship",
        "required_skills": ["Java", "Python", "SQL", "Git"],
        "preferred_qualifications": ["B.Tech Computer Science", "Knowledge of cloud platforms"],
        "application_url": "https://career.infosys.com",
        "posted_date": "2024-01-15",
        "application_deadline": "2024-03-31",
        "job_status": "active"
    },
    {
        "job_title": "Data Science Intern",
        "company_name": "TCS",
        "company_rating": 3.9,
        "location": "Mumbai, India",
        "job_description": "Assist data science team in building ML models, data pipelines and analytics dashboards using Python, pandas, and scikit-learn.",
        "stipend": 20000.0,
        "duration_months": 3,
        "job_type": "internship",
        "required_skills": ["Python", "Machine Learning", "Pandas", "SQL"],
        "preferred_qualifications": ["Statistics background", "Experience with Jupyter notebooks"],
        "application_url": "https://careers.tcs.com",
        "posted_date": "2024-01-20",
        "application_deadline": "2024-04-15",
        "job_status": "active"
    },
    {
        "job_title": "Frontend Developer Intern",
        "company_name": "Flipkart",
        "company_rating": 4.2,
        "location": "Bengaluru, India",
        "job_description": "Build responsive user interfaces for India's largest e-commerce platform using React.js and TypeScript.",
        "stipend": 25000.0,
        "duration_months": 6,
        "job_type": "internship",
        "required_skills": ["React.js", "TypeScript", "HTML", "CSS", "JavaScript"],
        "preferred_qualifications": ["Experience with Redux", "Understanding of REST APIs"],
        "application_url": "https://jobs.flipkart.com",
        "posted_date": "2024-01-25",
        "application_deadline": "2024-04-30",
        "job_status": "active"
    },
    {
        "job_title": "Machine Learning Engineer",
        "company_name": "Google",
        "company_rating": 4.5,
        "location": "Hyderabad, India",
        "job_description": "Develop and deploy machine learning models at scale using TensorFlow and Google Cloud Platform.",
        "stipend": 80000.0,
        "duration_months": None,
        "job_type": "full-time",
        "required_skills": ["Python", "TensorFlow", "PyTorch", "GCP", "MLOps"],
        "preferred_qualifications": ["M.Tech/PhD in ML", "Publications in top conferences"],
        "application_url": "https://careers.google.com",
        "posted_date": "2024-01-10",
        "application_deadline": "2024-05-31",
        "job_status": "active"
    },
    {
        "job_title": "Backend Developer Intern",
        "company_name": "Swiggy",
        "company_rating": 4.1,
        "location": "Bengaluru, India",
        "job_description": "Work on backend microservices for India's leading food delivery platform using Go, Python and Kubernetes.",
        "stipend": 30000.0,
        "duration_months": 6,
        "job_type": "internship",
        "required_skills": ["Go", "Python", "Docker", "Kubernetes", "PostgreSQL"],
        "preferred_qualifications": ["System design knowledge", "Experience with distributed systems"],
        "application_url": "https://careers.swiggy.com",
        "posted_date": "2024-02-01",
        "application_deadline": "2024-04-20",
        "job_status": "active"
    },
    {
        "job_title": "Cloud Engineering Intern",
        "company_name": "Microsoft",
        "company_rating": 4.4,
        "location": "Hyderabad, India",
        "job_description": "Assist in building and maintaining Azure cloud infrastructure. Work on automation, monitoring and DevOps pipelines.",
        "stipend": 45000.0,
        "duration_months": 6,
        "job_type": "internship",
        "required_skills": ["Azure", "Python", "Terraform", "CI/CD", "Linux"],
        "preferred_qualifications": ["Azure certifications", "Experience with ARM templates"],
        "application_url": "https://careers.microsoft.com",
        "posted_date": "2024-02-05",
        "application_deadline": "2024-05-01",
        "job_status": "active"
    },
    {
        "job_title": "Android Developer Intern",
        "company_name": "Paytm",
        "company_rating": 3.8,
        "location": "Noida, India",
        "job_description": "Develop features for Paytm's Android application serving 300M+ users. Work with Kotlin, Jetpack Compose and payment APIs.",
        "stipend": 20000.0,
        "duration_months": 3,
        "job_type": "internship",
        "required_skills": ["Android", "Kotlin", "Java", "REST APIs", "Git"],
        "preferred_qualifications": ["Published app on Play Store", "Knowledge of MVVM architecture"],
        "application_url": "https://jobs.paytm.com",
        "posted_date": "2024-02-10",
        "application_deadline": "2024-04-10",
        "job_status": "active"
    },
    {
        "job_title": "Full Stack Developer",
        "company_name": "Razorpay",
        "company_rating": 4.3,
        "location": "Bengaluru, India",
        "job_description": "Build full-stack features for payment infrastructure used by 8M+ businesses. React frontend + Node.js backend.",
        "stipend": 60000.0,
        "duration_months": None,
        "job_type": "full-time",
        "required_skills": ["React.js", "Node.js", "TypeScript", "PostgreSQL", "Redis"],
        "preferred_qualifications": ["Fintech experience", "High-performance system knowledge"],
        "application_url": "https://razorpay.com/jobs",
        "posted_date": "2024-02-12",
        "application_deadline": "2024-05-15",
        "job_status": "active"
    },
    {
        "job_title": "DevOps Engineer Intern",
        "company_name": "Zomato",
        "company_rating": 4.0,
        "location": "Gurugram, India",
        "job_description": "Help build and maintain CI/CD pipelines, monitoring systems and cloud infrastructure for Zomato's platform.",
        "stipend": 25000.0,
        "duration_months": 6,
        "job_type": "internship",
        "required_skills": ["Docker", "Kubernetes", "Jenkins", "AWS", "Bash scripting"],
        "preferred_qualifications": ["AWS certification", "Experience with Grafana/Prometheus"],
        "application_url": "https://www.zomato.com/careers",
        "posted_date": "2024-02-15",
        "application_deadline": "2024-04-30",
        "job_status": "active"
    },
    {
        "job_title": "AI/ML Research Intern",
        "company_name": "Samsung Research India",
        "company_rating": 4.2,
        "location": "Bengaluru, India",
        "job_description": "Research and develop AI models for Samsung's next-gen products. Focus on NLP, computer vision and edge AI.",
        "stipend": 35000.0,
        "duration_months": 6,
        "job_type": "internship",
        "required_skills": ["Python", "PyTorch", "Deep Learning", "NLP", "Computer Vision"],
        "preferred_qualifications": ["Research publications", "Experience with model optimization"],
        "application_url": "https://research.samsung.com/careers",
        "posted_date": "2024-02-18",
        "application_deadline": "2024-05-20",
        "job_status": "active"
    }
]


def main():
    logger.info("Seeding sample jobs...")
    init_db()
    db = SessionLocal()
    try:
        added = 0
        for job_data in SAMPLE_JOBS:
            existing = db.query(InternshipJob).filter(
                InternshipJob.job_title == job_data["job_title"],
                InternshipJob.company_name == job_data["company_name"]
            ).first()
            if existing:
                logger.info(f"  Skipping existing: {job_data['job_title']} at {job_data['company_name']}")
                continue

            embedding_text = f"{job_data['job_title']} {job_data['company_name']} {job_data['job_description'][:200]}"
            try:
                embedding = embeddings_client.embed_text(embedding_text)
            except Exception as e:
                logger.warning(f"  Could not embed job: {e}")
                embedding = None

            job_id = str(uuid.uuid4())
            job = InternshipJob(
                id=job_id,
                **job_data,
                embedding_text=embedding_text,
                embedding_vector=embedding
            )
            db.add(job)

            # Upsert into Pinecone
            if embedding:
                try:
                    from app.internships.rag import internship_rag
                    internship_rag.upsert_job(
                        job_id=job_id,
                        embedding=embedding,
                        metadata={
                            "job_title": job_data.get("job_title", ""),
                            "company_name": job_data.get("company_name", ""),
                            "location": job_data.get("location", ""),
                            "description": job_data.get("job_description", "")[:400],
                            "stipend": float(job_data.get("stipend") or 0.0),
                            "job_type": job_data.get("job_type", "internship")
                        }
                    )
                except Exception as e:
                    logger.warning(f"  Pinecone upsert failed for job: {e}")

            added += 1

        db.commit()
        total = db.query(InternshipJob).count()
        logger.info(f"✅ Jobs seeded! Added {added} new jobs. Total in DB: {total}")
    except Exception as e:
        logger.error(f"❌ Job seeding failed: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
