import logging
import requests
from datetime import datetime, timezone
from app.services.job_providers.base_provider import BaseJobProvider
from app.config import Config

logger = logging.getLogger(__name__)

class JoobleJobProvider(BaseJobProvider):
    """
    Jooble REST API Provider Adapter.
    Queries official Jooble REST API endpoint with country/region specific API key.
    """

    def __init__(self):
        self.enabled = Config.JOOBLE_ENABLED
        self.api_key = Config.JOOBLE_API_KEY
        self.base_url = Config.JOOBLE_BASE_URL.rstrip('/')
        self.results_per_page = Config.JOOBLE_RESULTS_PER_PAGE
        self.timeout = Config.JOOBLE_TIMEOUT
        self.provider_name = "Jooble Jobs"

    def is_configured(self) -> bool:
        return bool(self.enabled and self.api_key and self.api_key.strip())

    def search_jobs(self, search_params: dict) -> dict:
        keyword = search_params.get('keyword', '').strip()
        location = search_params.get('location', '').strip()
        page = search_params.get('page', 1)
        limit = search_params.get('limit', self.results_per_page)

        if not self.is_configured():
            logger.info("Jooble API key not configured or provider disabled.")
            return {
                "success": False,
                "error": "NOT_CONFIGURED",
                "message": "Jooble API key not configured.",
                "jobs": [],
                "total": 0
            }

        endpoint = f"{self.base_url}/{self.api_key}" if self.api_key not in self.base_url else self.base_url

        payload = {
            "keywords": keyword,
            "location": location,
            "page": page,
            "ResultOnPage": min(limit, 50)
        }

        try:
            response = requests.post(
                endpoint,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=self.timeout
            )

            if response.status_code == 200:
                data = response.json()
                results = data.get('jobs', [])
                total = data.get('totalCount', len(results))

                normalized_jobs = []
                for item in results:
                    norm = self._normalize_jooble_job(item)
                    if norm.get("application_url"):
                        normalized_jobs.append(norm)

                return {
                    "success": True,
                    "source": self.provider_name,
                    "total": total,
                    "page": page,
                    "limit": limit,
                    "jobs": normalized_jobs
                }
            elif response.status_code in [401, 403]:
                logger.error(f"Jooble API authentication failed HTTP {response.status_code}")
                return {"success": False, "error": "AUTH_FAILED", "message": "Jooble API authentication failed."}
            else:
                logger.error(f"Jooble API HTTP {response.status_code}: {response.text}")
                return {"success": False, "error": f"HTTP_{response.status_code}", "message": "Jooble provider temporarily unavailable."}

        except requests.exceptions.Timeout:
            logger.error("Jooble API connection timed out.")
            return {"success": False, "error": "TIMEOUT", "message": "Jooble API connection timed out."}
        except Exception as e:
            logger.error(f"Jooble API exception: {e}")
            return {"success": False, "error": "PROVIDER_ERROR", "message": str(e)}

    def verify_job_status(self, provider_job_id: str) -> str:
        return "LIVE"

    def _normalize_jooble_job(self, item: dict) -> dict:
        now_iso = datetime.now(timezone.utc).isoformat()
        job_id = str(item.get('id') or item.get('link', ''))
        raw_loc = item.get('location', '').strip()
        app_url = item.get('link', '').strip()

        salary_raw = item.get('salary', '')
        salary_dict = None
        if salary_raw:
            salary_dict = {"raw": str(salary_raw), "currency": "INR"}

        workplace = "REMOTE" if ("remote" in raw_loc.lower() or "remote" in str(item.get('title', '')).lower()) else "ON_SITE"

        return {
            "provider": "jooble",
            "provider_job_id": job_id,
            "title": item.get('title', 'Software Vacancy'),
            "company": item.get('company', 'Enterprise'),
            "raw_description": item.get('snippet', '') or item.get('type', ''),
            "location": raw_loc or "India",
            "locations": [raw_loc] if raw_loc else [],
            "raw_location": raw_loc,
            "country": "IN",
            "city": raw_loc,
            "workplace_type": workplace,
            "employment_type": item.get('type', 'FULL_TIME'),
            "experience": "UNKNOWN",
            "education": "UNKNOWN",
            "skills": [],
            "salary": salary_dict,
            "salary_currency": "INR",
            "posted_at": item.get('updated', '') or now_iso,
            "updated_date": item.get('updated', ''),
            "last_verified_at": now_iso,
            "application_url": app_url,
            "source_url": app_url,
            "source": "Jooble Jobs",
            "source_name": "Jooble Jobs",
            "is_live": True
        }
