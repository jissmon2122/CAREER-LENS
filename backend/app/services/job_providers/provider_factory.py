import logging
from app.config import Config
from app.services.job_providers.base_provider import BaseJobProvider
from app.services.job_providers.adzuna_provider import AdzunaJobProvider
from app.services.job_providers.jooble_provider import JoobleJobProvider
from app.services.job_providers.indian_api_provider import IndianApiJobProvider

logger = logging.getLogger(__name__)

class MultiSourceJobProvider(BaseJobProvider):
    """
    Production Multi-Source Live Job Aggregator.
    Queries authorized live job APIs (Adzuna, Jooble, IndianAPI) independently.
    Zero mock/synthetic jobs.
    """

    def __init__(self):
        self.adzuna = AdzunaJobProvider()
        self.jooble = JoobleJobProvider()
        self.indianapi = IndianApiJobProvider()
        self.provider_name = "Production Multi-Source Live Aggregator (Adzuna + Jooble + IndianAPI)"

    def is_configured(self) -> bool:
        return True

    def get_provider_health(self) -> dict:
        return {
            "adzuna": "CONFIGURED" if self.adzuna.is_configured() else "NOT_CONFIGURED",
            "jooble": "CONFIGURED" if self.jooble.is_configured() else "NOT_CONFIGURED",
            "indianapi": "CONFIGURED" if self.indianapi.is_configured() else "NOT_CONFIGURED"
        }

    def search_jobs(self, search_params: dict) -> dict:
        jobs = []
        provider_status = {}
        providers_used = []

        # 1. Query Adzuna
        if self.adzuna.is_configured():
            try:
                res = self.adzuna.search_jobs(search_params)
                if res.get("success"):
                    adz_jobs = res.get("jobs", [])
                    jobs.extend(adz_jobs)
                    provider_status["adzuna"] = "LIVE_SUCCESS" if adz_jobs else "ZERO_RESULTS"
                    if adz_jobs:
                        providers_used.append("adzuna")
                else:
                    provider_status["adzuna"] = res.get("error", "PROVIDER_ERROR")
            except Exception as e:
                logger.error(f"Adzuna query error: {e}")
                provider_status["adzuna"] = "PROVIDER_ERROR"
        else:
            provider_status["adzuna"] = "NOT_CONFIGURED"

        # 2. Query Jooble
        if self.jooble.is_configured():
            try:
                res = self.jooble.search_jobs(search_params)
                if res.get("success"):
                    joo_jobs = res.get("jobs", [])
                    jobs.extend(joo_jobs)
                    provider_status["jooble"] = "LIVE_SUCCESS" if joo_jobs else "ZERO_RESULTS"
                    if joo_jobs:
                        providers_used.append("jooble")
                else:
                    provider_status["jooble"] = res.get("error", "PROVIDER_ERROR")
            except Exception as e:
                logger.error(f"Jooble query error: {e}")
                provider_status["jooble"] = "PROVIDER_ERROR"
        else:
            provider_status["jooble"] = "NOT_CONFIGURED"

        # 3. Query IndianAPI
        if self.indianapi.is_configured():
            try:
                res = self.indianapi.search_jobs(search_params)
                if res.get("success"):
                    ind_jobs = res.get("jobs", [])
                    jobs.extend(ind_jobs)
                    provider_status["indianapi"] = "LIVE_SUCCESS" if ind_jobs else "ZERO_RESULTS"
                    if ind_jobs:
                        providers_used.append("indianapi")
                else:
                    provider_status["indianapi"] = res.get("error", "PROVIDER_ERROR")
            except Exception as e:
                logger.error(f"IndianAPI query error: {e}")
                provider_status["indianapi"] = "PROVIDER_ERROR"
        else:
            provider_status["indianapi"] = "NOT_CONFIGURED"

        # Deduplicate in-memory by provider + provider_job_id & application_url
        seen_keys = set()
        deduped_raw_jobs = []
        for j in jobs:
            pid = str(j.get("provider_job_id", ""))
            prov = str(j.get("provider", ""))
            app_url = str(j.get("application_url", "")).strip()
            key1 = (prov, pid) if pid else None
            key2 = app_url if app_url else None
            key3 = (j.get("company", "").lower().strip(), j.get("title", "").lower().strip(), j.get("location", "").lower().strip())

            if (key1 and key1 in seen_keys) or (key2 and key2 in seen_keys) or (key3 in seen_keys):
                continue

            if key1:
                seen_keys.add(key1)
            if key2:
                seen_keys.add(key2)
            seen_keys.add(key3)
            deduped_raw_jobs.append(j)

        all_configured = [p for p, s in provider_status.items() if s != "NOT_CONFIGURED"]
        all_failed = len(all_configured) > 0 and all(provider_status[p] in ["PROVIDER_ERROR", "AUTH_FAILED", "TIMEOUT", "HTTP_500"] for p in all_configured)

        return {
            "success": not all_failed,
            "source": self.provider_name,
            "total": len(deduped_raw_jobs),
            "jobs": deduped_raw_jobs,
            "provider_status": provider_status,
            "providers_used": list(set(providers_used)),
            "all_providers_failed": all_failed
        }

    def verify_job_status(self, provider_job_id: str) -> str:
        return "LIVE"

class ProviderFactory:
    """
    Factory class to instantiate the MultiSourceJobProvider.
    Decouples application code from external API dependencies.
    """

    @classmethod
    def get_provider(cls, provider_name: str = None) -> BaseJobProvider:
        logger.info("Initializing Production Multi-Source Live Provider (Adzuna + Jooble + IndianAPI).")
        return MultiSourceJobProvider()
