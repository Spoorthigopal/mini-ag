import pdfplumber
import re
import io
from typing import List
import logging

logger = logging.getLogger(__name__)


class ResumeParser:
    """Parse resume PDF files and extract structured information."""

    COMMON_SKILLS = [
        "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go", "Rust",
        "React", "Angular", "Vue.js", "Next.js", "Node.js", "Express",
        "Django", "FastAPI", "Flask", "Spring Boot",
        "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch",
        "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform",
        "Git", "GitHub", "CI/CD", "Jenkins", "GitHub Actions",
        "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Scikit-learn",
        "Data Science", "Pandas", "NumPy", "Matplotlib", "Tableau", "Power BI",
        "Excel", "SAP", "Salesforce", "Jira", "Linux", "Bash",
        "REST API", "GraphQL", "Microservices", "System Design", "Agile", "Scrum"
    ]

    @staticmethod
    def parse_pdf_resume(file_bytes: bytes) -> str:
        """Extract text from PDF resume bytes."""
        try:
            text = ""
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"PDF parsing error: {e}")
            raise

    @staticmethod
    def extract_skills(resume_text: str) -> List[str]:
        """Extract skills from resume text by matching known skill list."""
        try:
            skills = []
            resume_lower = resume_text.lower()
            for skill in ResumeParser.COMMON_SKILLS:
                # Use word boundary matching for accuracy
                pattern = r'\b' + re.escape(skill.lower()) + r'\b'
                if re.search(pattern, resume_lower):
                    skills.append(skill)
            return list(set(skills))
        except Exception as e:
            logger.error(f"Skill extraction error: {e}")
            return []

    @staticmethod
    def extract_experience_years(resume_text: str) -> int:
        """Extract years of experience from resume text."""
        try:
            patterns = [
                r'(\d+)\s*\+?\s*years?\s+of\s+experience',
                r'experience[:\s]+(\d+)\s*\+?\s*years?',
                r'(\d+)\s+years?\s+experience'
            ]
            for pattern in patterns:
                match = re.search(pattern, resume_text.lower())
                if match:
                    return int(match.group(1))
            return 0
        except Exception:
            return 0

    @staticmethod
    def extract_education(resume_text: str) -> str:
        """Extract highest education level from resume."""
        text_lower = resume_text.lower()
        if "phd" in text_lower or "doctorate" in text_lower:
            return "PhD"
        elif "m.tech" in text_lower or "m.e." in text_lower or "m.sc" in text_lower or "master" in text_lower:
            return "Masters"
        elif "b.tech" in text_lower or "b.e." in text_lower or "b.sc" in text_lower or "bachelor" in text_lower:
            return "Bachelors"
        elif "diploma" in text_lower:
            return "Diploma"
        return "Not specified"


# Global instance
resume_parser = ResumeParser()


def get_resume_parser() -> ResumeParser:
    return resume_parser
