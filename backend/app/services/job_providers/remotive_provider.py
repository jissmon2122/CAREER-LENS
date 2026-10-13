import logging
import requests
from app.services.job_providers.base_provider import BaseJobProvider
from app.config import Config

logger = logging.getLogger(__name__)

class RemotiveJobProvider(BaseJobProvider):
    """
    Remotive Live Job Search API Provider.
    Retrieves real-time active developer, tech, and remote vacancies directly without requiring API keys.
    """

    def __init__(self):
        self.base_url = "https://remotive.com/api/remote-jobs"
        self.timeout = min(getattr(Config, 'JOB_API_TIMEOUT', 6), 6)
        self.provider_name = "Remotive Live Feed"
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

        params = {}
        if keyword:
            first_token = keyword.split()[0]
            if len(first_token) > 2:
                params['search'] = first_token

        try:
            response = self.session.get(self.base_url, params=params, timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                raw_jobs = data.get('jobs', [])

                keyword_tokens = [t for t in keyword.split() if len(t) > 2]

                filtered_jobs = []
                for item in raw_jobs:
                    req_loc = str(item.get('candidate_required_location', '')).lower()
                    job_title = str(item.get('title', '')).lower()
                    company_name = str(item.get('company_name', '')).lower()
                    job_desc = str(item.get('description', '')).lower()
                    tags_str = " ".join([str(t).lower() for t in item.get('tags', [])])

                    # Title must contain at least one significant keyword token
                    if keyword_tokens:
                        title_match = any(token in job_title for token in keyword_tokens)
                        if not title_match:
                            continue

                    # Location filter check (allow Remote/Worldwide if user searches specific city)
                    if location:
                        is_location_match = (
                            location in req_loc or
                            location in job_title or
                            'remote' in req_loc or
                            'worldwide' in req_loc or
                            'anywhere' in req_loc or
                            'apac' in req_loc or
                            'global' in req_loc
                        )
                        if not is_location_match:
                            continue

                    filtered_jobs.append(item)

                total = len(filtered_jobs)
                start_idx = (page - 1) * limit
                end_idx = start_idx + limit
                paginated_raw = filtered_jobs[start_idx:end_idx]

                normalized_jobs = [self._normalize_remotive_job(j) for j in paginated_raw]

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
                logger.error(f"Remotive API HTTP {response.status_code}: {response.text}")
                return {"success": False, "error": f"HTTP_{response.status_code}", "message": "Live job provider temporarily unavailable."}

        except Exception as e:
            logger.error(f"Remotive API exception: {e}")
            return {"success": False, "error": "PROVIDER_ERROR", "message": str(e)}

    def verify_job_status(self, provider_job_id: str) -> str:
        return "LIVE"

    def _normalize_remotive_job(self, item: dict) -> dict:
        tags = item.get('tags', [])
        required_skills = [t.strip() for t in tags if isinstance(t, str)] if tags else []
        app_url = item.get('url', '').strip()
        from datetime import datetime, timezone
        now_iso = datetime.now(timezone.utc).isoformat()
        raw_loc = item.get('candidate_required_location', 'Remote Worldwide')

        return {
            "provider": "remotive",
            "provider_job_id": str(item.get('id')),
            "title": item.get('title', 'Software Developer'),
            "company": item.get('company_name', 'Tech Company'),
            "raw_description": item.get('description', ''),
            "location": raw_loc,
            "locations": [raw_loc] if raw_loc else [],
            "candidate_required_location": raw_loc,
            "country": "GLOBAL",
            "city": "Remote",
            "workplace_type": "REMOTE",
            "employment_type": "FULL_TIME",
            "experience": "UNKNOWN",
            "salary": None,
            "salary_min": None,
            "salary_max": None,
            "salary_currency": "USD",
            "posted_at": item.get('publication_date', '') or now_iso,
            "last_verified_at": now_iso,
            "application_url": app_url,
            "source_url": app_url,
            "source": "Remotive Live Feed",
            "source_name": "Remotive Live Feed",
            "required_skills": required_skills[:8],
            "is_live": True
        }
