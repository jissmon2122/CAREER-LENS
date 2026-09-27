import logging
import requests
from datetime import datetime, timezone
from app.services.job_providers.base_provider import BaseJobProvider
from app.config import Config

logger = logging.getLogger(__name__)

class AdzunaJobProvider(BaseJobProvider):
    """
    Adzuna Live Job Search API Provider Adapter.
    Communicates securely with Adzuna API without exposing credentials to frontend.
    """

    def __init__(self):
        self.app_id = Config.ADZUNA_APP_ID
        self.app_key = Config.ADZUNA_APP_KEY
        self.country = (Config.ADZUNA_COUNTRY or 'in').lower()
        self.base_url = Config.ADZUNA_BASE_URL or "https://api.adzuna.com/v1/api/jobs"
        self.results_per_page = Config.ADZUNA_RESULTS_PER_PAGE or 50
        self.timeout = Config.ADZUNA_TIMEOUT or 10
        self.provider_name = "Adzuna Jobs"

    def is_configured(self) -> bool:
        return bool(self.app_id and self.app_key)

    def search_jobs(self, search_params: dict) -> dict:
        keyword = search_params.get('keyword', '')
        location = search_params.get('location', '')
        page = search_params.get('page', 1)
        limit = search_params.get('limit', self.results_per_page)
        country = search_params.get('country', self.country).lower()

        if not self.is_configured():
            logger.info("Adzuna API credentials not configured.")
            return {
                "success": False,
                "error": "NOT_CONFIGURED",
                "message": "Adzuna API credentials not configured.",
                "jobs": [],
                "total": 0
            }

        url = f"{self.base_url.rstrip('/')}/{country}/search/{page}"
        params = {
            'app_id': self.app_id,
            'app_key': self.app_key,
            'results_per_page': min(limit, 50),
            'what': keyword,
            'where': location,
            'content-type': 'application/json'
        }

        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                total = data.get('count', len(results))

                normalized_jobs = []
                for item in results:
                    norm = self._normalize_adzuna_job(item, country)
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
            elif response.status_code == 429:
                logger.warning("Adzuna API rate limited (429).")
                return {"success": False, "error": "RATE_LIMITED", "message": "Live job search API rate limit reached. Showing cached vacancies."}
            else:
                logger.error(f"Adzuna API error HTTP {response.status_code}: {response.text}")
                return {"success": False, "error": f"HTTP_{response.status_code}", "message": "Live job provider temporarily unavailable."}
        except requests.exceptions.Timeout:
            logger.error("Adzuna API call timed out.")
            return {"success": False, "error": "TIMEOUT", "message": "Live job search connection timed out."}
        except Exception as e:
            logger.error(f"Adzuna API connection exception: {e}")
            return {"success": False, "error": "PROVIDER_ERROR", "message": str(e)}

    def verify_job_status(self, provider_job_id: str) -> str:
        return "LIVE"

    def _normalize_adzuna_job(self, item: dict, country: str) -> dict:
        location_obj = item.get('location', {})
        raw_display_name = location_obj.get('display_name', '')
        area_list = [a.strip() for a in raw_display_name.split(',') if a.strip()]
        city = area_list[0] if area_list else ''

        salary_min = item.get('salary_min')
        salary_max = item.get('salary_max')
        currency = "INR" if country == 'in' else "USD"

        salary_dict = None
        if salary_min or salary_max:
            salary_dict = {
                "min": float(salary_min) if salary_min else None,
                "max": float(salary_max) if salary_max else None,
                "currency": currency
            }

        app_url = item.get('redirect_url', '').strip()
        now_iso = datetime.now(timezone.utc).isoformat()

        title = item.get('title', 'Software Vacancy')
        company = item.get('company', {}).get('display_name', 'Tech Enterprise')

        contract_time = str(item.get('contract_time', '')).lower()
        employment_type = "FULL_TIME" if "full" in contract_time else ("PART_TIME" if "part" in contract_time else "FULL_TIME")

        return {
            "provider": "adzuna",
            "provider_job_id": str(item.get('id')),
            "title": title,
            "company": company,
            "raw_description": item.get('description', ''),
            "location": raw_display_name or 'India',
            "locations": area_list,
            "country": country.upper(),
            "city": city,
            "workplace_type": "ON_SITE",
            "employment_type": employment_type,
            "experience": "UNKNOWN",
            "salary": salary_dict,
            "salary_min": float(salary_min) if salary_min else None,
            "salary_max": float(salary_max) if salary_max else None,
            "salary_currency": currency,
            "posted_at": item.get('created', '') or now_iso,
            "last_verified_at": now_iso,
            "application_url": app_url,
            "source_url": app_url,
            "source": "Adzuna Jobs",
            "source_name": "Adzuna Jobs",
            "is_live": True
        }
