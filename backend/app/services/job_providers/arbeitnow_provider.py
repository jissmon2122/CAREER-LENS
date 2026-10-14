import logging
import requests
from app.services.job_providers.base_provider import BaseJobProvider
from app.config import Config

logger = logging.getLogger(__name__)

class ArbeitnowJobProvider(BaseJobProvider):
    """
    Arbeitnow Live Job Board API Provider.
    Fetches real-time active vacancies directly without requiring API keys.
    """

    def __init__(self):
        self.base_url = "https://www.arbeitnow.com/api/job-board-api"
        self.timeout = (2.5, 4.0)
        self.provider_name = "Arbeitnow Live Board"
        self.session = requests.Session()
        self._cache = {}

    def is_configured(self) -> bool:
        return True

    def search_jobs(self, search_params: dict) -> dict:
        import time, copy
        keyword = search_params.get('keyword', '').strip().lower()
        location = search_params.get('location', '').strip().lower()
        page = search_params.get('page', 1)
        limit = search_params.get('limit', getattr(Config, 'JOB_API_DEFAULT_RESULTS', 50))

        cache_key = (keyword, location, page, limit)
        now_ts = time.time()
        if cache_key in self._cache:
            entry = self._cache[cache_key]
            if now_ts - entry["timestamp"] < 1800:
                return copy.deepcopy(entry["data"])

        try:
            url = f"{self.base_url}?page={page}"
            response = self.session.get(url, timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                raw_jobs = data.get('data', [])

                keyword_tokens = [t for t in keyword.split() if len(t) > 2]

                filtered_jobs = []
                for item in raw_jobs:
                    job_title = str(item.get('title', '')).lower()
                    company_name = str(item.get('company_name', '')).lower()
                    job_loc = str(item.get('location', '')).lower()
                    job_desc = str(item.get('description', '')).lower()
                    tags_str = " ".join([str(t).lower() for t in item.get('tags', [])])

                    # Require title match for relevance
                    if keyword_tokens:
                        title_match = any(token in job_title for token in keyword_tokens)
                        if not title_match:
                            continue

                    if location:
                        is_location_match = (
                            location in job_loc or
                            location in job_title or
                            'remote' in job_loc
                        )
                        if not is_location_match:
                            continue

                    filtered_jobs.append(item)

                total = len(filtered_jobs)
                paginated_raw = filtered_jobs[:limit]

                normalized_jobs = [self._normalize_arbeitnow_job(j) for j in paginated_raw]

                result_payload = {
                    "success": True,
                    "source": self.provider_name,
                    "total": total,
                    "page": page,
                    "limit": limit,
                    "jobs": normalized_jobs
                }
                self._cache[cache_key] = {"timestamp": now_ts, "data": result_payload}
                return result_payload
            else:
                logger.error(f"Arbeitnow API HTTP {response.status_code}: {response.text}")
                return {"success": False, "error": f"HTTP_{response.status_code}", "message": "Live job provider temporarily unavailable."}

        except Exception as e:
            logger.error(f"Arbeitnow API exception: {e}")
            return {"success": False, "error": "PROVIDER_ERROR", "message": str(e)}

    def verify_job_status(self, provider_job_id: str) -> str:
        return "LIVE"

    def _normalize_arbeitnow_job(self, item: dict) -> dict:
        tags = item.get('tags', [])
        required_skills = [t.strip() for t in tags if isinstance(t, str)] if tags else []

        return {
            "provider": "arbeitnow",
            "provider_job_id": str(item.get('slug')),
            "title": item.get('title', 'Software Vacancy'),
            "company": item.get('company_name', 'Tech Enterprise'),
            "raw_description": item.get('description', ''),
            "location": item.get('location', 'Europe / Remote'),
            "candidate_required_location": item.get('location', ''),
            "country": "EU",
            "city": item.get('location', ''),
            "salary_min": None,
            "salary_max": None,
            "salary_currency": "EUR",
            "posted_at": str(item.get('created_at', '')),
            "application_url": item.get('url', ''),
            "source_url": item.get('url', ''),
            "source_name": "Arbeitnow Live Board",
            "required_skills": required_skills[:8],
            "is_live": True
        }
