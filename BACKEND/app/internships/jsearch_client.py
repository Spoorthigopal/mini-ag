import httpx
from app.config import settings
from typing import List, Dict, Any
import logging
import re

logger = logging.getLogger(__name__)


class JSearchClient:
    """JSearch API Client via RapidAPI"""

    def __init__(self):
        self.api_key = settings.jsearch_api_key
        self.host = "jsearch.p.rapidapi.com"
        self.base_url = f"https://{self.host}"

    def query_jsearch(
        self,
        search_term: str,
        location: str = "India",
        job_type: str = "internship",
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Query JSearch API for internship jobs."""
        try:
            headers = {
                "x-rapidapi-key": self.api_key,
                "x-rapidapi-host": self.host
            }
            params = {
                "query": search_term,
                "location": location,
                "job_type": job_type,
                "num_pages": 1
            }
            with httpx.Client(timeout=30.0) as client:
                response = client.get(
                    f"{self.base_url}/search",
                    headers=headers,
                    params=params
                )
                response.raise_for_status()

            data = response.json()
            jobs = data.get("data", [])
            return jobs[:limit]

        except httpx.HTTPError as e:
            logger.error(f"JSearch API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error querying JSearch: {e}")
            raise

    def parse_job_listing(self, raw_job: Dict[str, Any]) -> Dict[str, Any]:
        """Parse raw JSearch listing to standardized format."""
        try:
            return {
                "job_title": raw_job.get("job_title", ""),
                "company_name": raw_job.get("employer_name", ""),
                "company_rating": self._parse_rating(raw_job.get("employer_company_type", "")),
                "location": raw_job.get("job_city", "") or raw_job.get("job_location", "India"),
                "job_description": raw_job.get("job_description", ""),
                "stipend": self._parse_salary(raw_job.get("job_min_salary", 0)),
                "duration_months": self._parse_duration(raw_job.get("job_employment_type", "")),
                "job_type": "internship",
                "required_skills": raw_job.get("job_required_skills") or [],
                "application_url": raw_job.get("job_apply_link", ""),
                "jsearch_job_id": raw_job.get("job_id", ""),
                "posted_date": raw_job.get("job_posted_at_datetime_utc", ""),
                "application_deadline": raw_job.get("job_offer_expiration_datetime_utc", ""),
                "job_status": "active",
                "embedding_text": (
                    f"{raw_job.get('job_title', '')} "
                    f"{raw_job.get('employer_name', '')} "
                    f"{raw_job.get('job_description', '')[:400]}"
                )
            }
        except Exception as e:
            logger.error(f"Parse error: {e}")
            raise

    def _parse_rating(self, rating_str: str) -> float:
        try:
            numbers = re.findall(r'[\d.]+', str(rating_str))
            return float(numbers[0]) if numbers else 0.0
        except Exception:
            return 0.0

    def _parse_salary(self, salary_val) -> float:
        try:
            if isinstance(salary_val, (int, float)):
                return float(salary_val)
            numbers = re.findall(r'\d+', str(salary_val))
            return float(numbers[0]) if numbers else 0.0
        except Exception:
            return 0.0

    def _parse_duration(self, employment_type: str) -> int:
        try:
            months_match = re.search(r'(\d+)\s*month', str(employment_type).lower())
            return int(months_match.group(1)) if months_match else 3
        except Exception:
            return 3


# Global instance
jsearch_client = JSearchClient()


def get_jsearch_client() -> JSearchClient:
    return jsearch_client
