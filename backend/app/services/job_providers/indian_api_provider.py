import logging
import requests
from datetime import datetime, timezone
from app.services.job_providers.base_provider import BaseJobProvider
from app.config import Config

logger = logging.getLogger(__name__)

class IndianApiJobProvider(BaseJobProvider):
    """
    IndianAPI Jobs REST Provider Adapter.
    Queries official IndianAPI jobs endpoint securely with server-side API key.
    """

    def __init__(self):
        self.enabled = Config.INDIANAPI_ENABLED
        self.api_key = Config.INDIANAPI_API_KEY
        self.base_url = Config.INDIANAPI_BASE_URL.rstrip('/')
        self.limit = Config.INDIANAPI_RESULTS_LIMIT
        self.timeout = (2.5, 4.0)
        self.provider_name = "IndianAPI Jobs"

    def is_configured(self) -> bool:
        return bool(self.enabled and self.api_key and self.api_key.strip())

    def search_jobs(self, search_params: dict) -> dict:
        keyword = search_params.get('keyword', '').strip()
        location = search_params.get('location', '').strip()
        page = search_params.get('page', 1)
        limit = search_params.get('limit', self.limit)

        if not self.is_configured():
            logger.info("IndianAPI API key not configured or provider disabled.")
            return {
                "success": False,
                "error": "NOT_CONFIGURED",
                "message": "IndianAPI API key not configured.",
                "jobs": [],
                "total": 0
            }

        url = f"{self.base_url}/jobs" if not self.base_url.endswith("/jobs") else self.base_url

        headers = {
            "x-api-key": self.api_key,
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json"
        }

        params = {
            "title": keyword,
            "keyword": keyword,
            "location": location,
            "page": page,
            "limit": min(limit, 50)
        }

        try:
            response = requests.get(url, headers=headers, params=params, timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                results = data.get('jobs', data.get('data', []))
                if isinstance(results, dict):
                    results = results.get('jobs', [])

                total = data.get('total', len(results))

                normalized_jobs = []
                for item in results:
                    norm = self._normalize_indianapi_job(item)
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
                logger.error(f"IndianAPI authentication failed HTTP {response.status_code}")
                return {"success": False, "error": "AUTH_FAILED", "message": "IndianAPI authentication failed."}
            else:
                logger.error(f"IndianAPI HTTP {response.status_code}: {response.text}")
                return {"success": False, "error": f"HTTP_{response.status_code}", "message": "IndianAPI provider temporarily unavailable."}

        except requests.exceptions.Timeout:
            logger.error("IndianAPI connection timed out.")
            return {"success": False, "error": "TIMEOUT", "message": "IndianAPI connection timed out."}
        except Exception as e:
            logger.error(f"IndianAPI exception: {e}")
            return {"success": False, "error": "PROVIDER_ERROR", "message": str(e)}

    def verify_job_status(self, provider_job_id: str) -> str:
        return "LIVE"

    def _normalize_indianapi_job(self, item: dict) -> dict:
        now_iso = datetime.now(timezone.utc).isoformat()
        job_id = str(item.get('id') or item.get('job_id') or item.get('apply_link', ''))
        raw_loc = item.get('location', '').strip()
        app_url = (item.get('apply_link') or item.get('application_url') or item.get('url') or '').strip()

        salary_dict = item.get('salary')
        if not isinstance(salary_dict, dict) and salary_dict:
            salary_dict = {"raw": str(salary_dict), "currency": "INR"}
        elif not salary_dict:
            salary_dict = None

        workplace = str(item.get('workplace_type') or item.get('job_type') or '').upper()
        if "REMOTE" not in workplace and ("remote" in raw_loc.lower() or "remote" in str(item.get('title', '')).lower()):
            workplace = "REMOTE"
        elif "ON_SITE" not in workplace and "HYBRID" not in workplace:
            workplace = "ON_SITE"

        return {
            "provider": "indianapi",
            "provider_job_id": job_id,
            "title": item.get('title', 'Software Vacancy'),
            "company": item.get('company') or item.get('company_name') or 'Tech Enterprise',
            "raw_description": item.get('description', '') or item.get('raw_description', ''),
            "location": raw_loc or "India",
            "locations": [raw_loc] if raw_loc else [],
            "raw_location": raw_loc,
            "country": "IN",
            "city": raw_loc,
            "workplace_type": workplace,
            "employment_type": item.get('job_type', 'FULL_TIME'),
            "experience": item.get('experience', 'UNKNOWN'),
            "education": item.get('education', 'UNKNOWN'),
            "skills": item.get('skills', []),
            "salary": salary_dict,
            "salary_currency": "INR",
            "posted_at": item.get('posted_date') or item.get('created_at') or now_iso,
            "updated_date": item.get('updated_date', ''),
            "last_verified_at": now_iso,
            "application_url": app_url,
            "source_url": app_url,
            "source": "IndianAPI Jobs",
            "source_name": "IndianAPI Jobs",
            "is_live": True
        }
