"""
Seed welfare schemes into the database and Pinecone.
Run: python scripts/seed_welfare_schemes.py
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
from app.welfare.service import load_welfare_schemes_to_db

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

WELFARE_SCHEMES = [
    {
        "name": "National Scholarship Portal (NSP)",
        "description": "Central government scholarship portal providing financial assistance to meritorious students from economically weaker sections for pursuing higher education.",
        "scheme_type": "Scholarship",
        "amount": 50000.0,
        "eligibility_criteria": {"income": "below_6lakh", "marks": "60%+", "category": "SC/ST/OBC/Minority/General"},
        "provider": "Ministry of Education",
        "application_deadline": "October 31",
        "application_url": "https://scholarships.gov.in",
        "contact_email": "helpdesk@nsp.gov.in",
        "benefits": ["Tuition fee reimbursement", "Maintenance allowance", "Book grant"],
        "documents_required": ["Aadhar Card", "Income Certificate", "Marksheet", "Bank Passbook", "Caste Certificate"],
        "processing_time": "45-60 days",
        "scheme_status": "active"
    },
    {
        "name": "Prime Minister's Research Fellowship (PMRF)",
        "description": "Fellowship for meritorious students to pursue PhD in IITs, IISc and IISERs with enhanced fellowship amount.",
        "scheme_type": "Fellowship",
        "amount": 70000.0,
        "eligibility_criteria": {"degree": "B.Tech/M.Tech/M.Sc", "cgpa": "8.0+", "institution": "Top-tier institutions"},
        "provider": "Ministry of Education",
        "application_deadline": "February 28",
        "application_url": "https://www.pmrf.in",
        "contact_email": "pmrf@iitd.ac.in",
        "benefits": ["Monthly fellowship of Rs 70,000", "Research grant of Rs 2 lakh/year", "International travel grant"],
        "documents_required": ["Degree Certificate", "CGPA Transcript", "Research Proposal", "NOC from institution"],
        "processing_time": "3-4 months",
        "scheme_status": "active"
    },
    {
        "name": "Central Sector Scheme of Scholarships (CSS)",
        "description": "Scholarship for college and university students securing above 80th percentile in Class XII board exams.",
        "scheme_type": "Scholarship",
        "amount": 20000.0,
        "eligibility_criteria": {"marks": "80th percentile in Class XII", "income": "below_8lakh", "age": "18-25"},
        "provider": "Ministry of Education",
        "application_deadline": "November 30",
        "application_url": "https://scholarships.gov.in",
        "contact_email": "css@education.gov.in",
        "benefits": ["Rs 10,000 per year for 1st-3rd year UG", "Rs 20,000 per year for PG"],
        "documents_required": ["Class XII Marksheet", "Income Certificate", "Aadhar Card", "Bank Details"],
        "processing_time": "30 days",
        "scheme_status": "active"
    },
    {
        "name": "AICTE Pragati Scholarship for Girls",
        "description": "Scholarship for girl students pursuing technical education (Diploma and Degree) to promote women in technical fields.",
        "scheme_type": "Scholarship",
        "amount": 50000.0,
        "eligibility_criteria": {"gender": "Female", "course": "Technical Diploma/Degree", "income": "below_8lakh"},
        "provider": "AICTE",
        "application_deadline": "September 30",
        "application_url": "https://www.aicte-pragati-saksham-gov.in",
        "contact_email": "pragati@aicte.gov.in",
        "benefits": ["Rs 50,000 per year", "Tuition fee reimbursement up to Rs 30,000"],
        "documents_required": ["Admission Letter", "Income Certificate", "Aadhar Card", "Bank Passbook"],
        "processing_time": "60 days",
        "scheme_status": "active"
    },
    {
        "name": "AICTE Saksham Scholarship for Differently Abled",
        "description": "Scholarship for differently abled students pursuing technical education to support inclusive education.",
        "scheme_type": "Scholarship",
        "amount": 50000.0,
        "eligibility_criteria": {"disability": "40%+ disability", "course": "Technical Diploma/Degree", "income": "below_8lakh"},
        "provider": "AICTE",
        "application_deadline": "September 30",
        "application_url": "https://www.aicte-pragati-saksham-gov.in",
        "contact_email": "saksham@aicte.gov.in",
        "benefits": ["Rs 50,000 per year", "Special equipment allowance"],
        "documents_required": ["Disability Certificate", "Admission Letter", "Income Certificate"],
        "processing_time": "60 days",
        "scheme_status": "active"
    },
    {
        "name": "Ishan Uday - Special Scholarship for North East",
        "description": "Scholarship for students from North Eastern region for general degree courses.",
        "scheme_type": "Scholarship",
        "amount": 54000.0,
        "eligibility_criteria": {"region": "North East India", "income": "below_4.5lakh", "course": "General Degree"},
        "provider": "UGC",
        "application_deadline": "October 31",
        "application_url": "https://scholarships.gov.in",
        "contact_email": "ishan@ugc.ac.in",
        "benefits": ["Rs 5,400 per month for day scholars", "Rs 7,800 per month for hostellers"],
        "documents_required": ["Domicile Certificate", "Income Certificate", "Marksheet"],
        "processing_time": "45 days",
        "scheme_status": "active"
    },
    {
        "name": "Kishore Vaigyanik Protsahan Yojana (KVPY)",
        "description": "Fellowship program to identify and encourage talented students to pursue research careers in basic sciences.",
        "scheme_type": "Fellowship",
        "amount": 80000.0,
        "eligibility_criteria": {"stream": "Science", "marks": "75% in Class X/XII", "aptitude": "KVPY exam"},
        "provider": "Department of Science and Technology",
        "application_deadline": "September 15",
        "application_url": "https://kvpy.iisc.ac.in",
        "contact_email": "kvpy@iisc.ac.in",
        "benefits": ["Monthly fellowship SA/SX/SB: Rs 5,000-7,000", "Annual contingency grant", "Summer program access"],
        "documents_required": ["Class X/XII Marksheet", "Enrollment Certificate"],
        "processing_time": "6 months (after exam)",
        "scheme_status": "active"
    },
    {
        "name": "Post-Matric Scholarship for SC Students",
        "description": "Scholarship for Scheduled Caste students studying at post-matriculation or post-secondary stage.",
        "scheme_type": "Scholarship",
        "amount": 30000.0,
        "eligibility_criteria": {"category": "Scheduled Caste", "income": "below_2.5lakh", "stage": "Post-matric"},
        "provider": "Ministry of Social Justice and Empowerment",
        "application_deadline": "November 30",
        "application_url": "https://scholarships.gov.in",
        "contact_email": "pms-sc@socialjustice.gov.in",
        "benefits": ["Maintenance allowance", "Study tour charges", "Thesis typing/printing charges"],
        "documents_required": ["Caste Certificate", "Income Certificate", "Previous year marksheet"],
        "processing_time": "60 days",
        "scheme_status": "active"
    },
    {
        "name": "Maulana Azad National Fellowship (MANF)",
        "description": "Fellowship for minority community students pursuing M.Phil and PhD at universities/institutions recognized by UGC.",
        "scheme_type": "Fellowship",
        "amount": 31000.0,
        "eligibility_criteria": {"religion": "Muslim/Christian/Buddhist/Sikh/Jain/Parsi", "qualification": "Post-graduation", "income": "below_6lakh"},
        "provider": "Ministry of Minority Affairs",
        "application_deadline": "March 31",
        "application_url": "https://maef.nic.in",
        "contact_email": "manf@maef.nic.in",
        "benefits": ["JRF: Rs 31,000/month", "SRF: Rs 35,000/month", "Contingency & HRA allowances"],
        "documents_required": ["Community Certificate", "Post-graduation certificate", "Admission letter"],
        "processing_time": "3-4 months",
        "scheme_status": "active"
    },
    {
        "name": "National Means cum Merit Scholarship (NMMS)",
        "description": "Scholarship to arrest dropout rate of meritorious students at class VIII level and encourage them for higher studies.",
        "scheme_type": "Scholarship",
        "amount": 12000.0,
        "eligibility_criteria": {"class": "Class IX onwards", "income": "below_1.5lakh", "marks": "55%+ in Class VIII"},
        "provider": "Ministry of Education",
        "application_deadline": "October 31",
        "application_url": "https://scholarships.gov.in",
        "contact_email": "nmms@education.gov.in",
        "benefits": ["Rs 1,000 per month (Rs 12,000/year)"],
        "documents_required": ["Class VIII Marksheet", "Income Certificate", "State selection exam result"],
        "processing_time": "30 days",
        "scheme_status": "active"
    }
]


def main():
    logger.info("Seeding welfare schemes...")
    init_db()
    db = SessionLocal()
    try:
        load_welfare_schemes_to_db(db, WELFARE_SCHEMES)
        count = db.query(WelfareScheme).count()
        logger.info(f"✅ Welfare schemes seeded successfully! Total in DB: {count}")
    except Exception as e:
        logger.error(f"❌ Seeding failed: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
