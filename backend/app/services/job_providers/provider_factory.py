import logging
from app.config import Config
from app.services.job_providers.base_provider import BaseJobProvider
from app.services.job_providers.adzuna_provider import AdzunaJobProvider
from app.services.job_providers.jooble_provider import JoobleJobProvider
from app.services.job_providers.indian_api_provider import IndianApiJobProvider

from app.services.job_providers.remotive_provider import RemotiveJobProvider
from app.services.job_providers.arbeitnow_provider import ArbeitnowJobProvider
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

class MultiSourceJobProvider(BaseJobProvider):
    """
    Production Multi-Source Live Job Aggregator.
    Queries authorized live job APIs (Adzuna, Remotive, Arbeitnow, Jooble, IndianAPI) concurrently.
    Returns valid partial results immediately if any provider is slow or fails.
    Zero mock/synthetic jobs.
    """

    def __init__(self):
        self.adzuna = AdzunaJobProvider()
        self.remotive = RemotiveJobProvider()
        self.arbeitnow = ArbeitnowJobProvider()
        self.jooble = JoobleJobProvider()
        self.indianapi = IndianApiJobProvider()
        self.provider_name = "Production Multi-Source Live Aggregator (Adzuna + Remotive + Arbeitnow + Jooble)"

    def is_configured(self) -> bool:
        return True

    def get_provider_health(self) -> dict:
        return {
            "adzuna": "CONFIGURED" if self.adzuna.is_configured() else "NOT_CONFIGURED",
            "remotive": "CONFIGURED" if self.remotive.is_configured() else "NOT_CONFIGURED",
            "arbeitnow": "CONFIGURED" if self.arbeitnow.is_configured() else "NOT_CONFIGURED",
            "jooble": "CONFIGURED" if self.jooble.is_configured() else "NOT_CONFIGURED",
            "indianapi": "CONFIGURED" if self.indianapi.is_configured() else "NOT_CONFIGURED"
        }

    def search_jobs(self, search_params: dict) -> dict:
        jobs = []
        provider_status = {}
        providers_used = []

        providers_to_query = []
        if self.adzuna.is_configured():
            providers_to_query.append(("adzuna", self.adzuna))
        if self.remotive.is_configured():
            providers_to_query.append(("remotive", self.remotive))
        if self.arbeitnow.is_configured():
            providers_to_query.append(("arbeitnow", self.arbeitnow))
        if self.jooble.is_configured():
            providers_to_query.append(("jooble", self.jooble))
        if self.indianapi.is_configured():
            providers_to_query.append(("indianapi", self.indianapi))

        def _fetch_single_provider(name, prov_inst):
            try:
                t0 = time.time()
                res = prov_inst.search_jobs(search_params)
                elapsed = round(time.time() - t0, 3)
                logger.info(f"Provider '{name}' responded in {elapsed}s: success={res.get('success')}, jobs={len(res.get('jobs', []))}")
                return name, res
            except Exception as e:
                logger.error(f"Provider '{name}' failed: {e}")
                return name, {"success": False, "error": "PROVIDER_ERROR", "jobs": []}

        # Run configured providers in parallel using ThreadPoolExecutor with strict 4.5s timeout
        import time
        from concurrent.futures import TimeoutError as FuturesTimeoutError
        max_workers = min(5, len(providers_to_query)) if providers_to_query else 1
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_prov = {
                executor.submit(_fetch_single_provider, name, inst): name 
                for name, inst in providers_to_query
            }
            try:
                for future in as_completed(future_to_prov, timeout=4.5):
                    name = future_to_prov[future]
                    try:
                        prov_name, res = future.result()
                        if res.get("success"):
                            p_jobs = res.get("jobs", [])
                            jobs.extend(p_jobs)
                            provider_status[prov_name] = "LIVE_SUCCESS" if p_jobs else "ZERO_RESULTS"
                            if p_jobs:
                                providers_used.append(prov_name)
                        else:
                            provider_status[prov_name] = res.get("error", "PROVIDER_ERROR")
                    except Exception as e:
                        logger.error(f"Error reading future for provider '{name}': {e}")
                        provider_status[name] = "PROVIDER_ERROR"
            except FuturesTimeoutError:
                logger.warning("Timed out waiting for some live job providers (4.5s limit); proceeding with partial results.")
                for future, name in future_to_prov.items():
                    if name not in provider_status:
                        provider_status[name] = "PROVIDER_TIMEOUT"

        # Mark unconfigured providers
        all_possible = ["adzuna", "remotive", "arbeitnow", "jooble", "indianapi"]
        for p in all_possible:
            if p not in provider_status:
                provider_status[p] = "NOT_CONFIGURED"

        # Deduplicate in-memory by provider + provider_job_id & application_url & normalized title/company
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

        all_configured = [p for p in all_possible if provider_status[p] != "NOT_CONFIGURED"]
        all_failed = len(all_configured) > 0 and all(provider_status[p] in ["PROVIDER_ERROR", "AUTH_FAILED", "TIMEOUT", "HTTP_500"] for p in all_configured)

        return {
            "success": not all_failed or len(deduped_raw_jobs) > 0,
            "source": self.provider_name,
            "total": len(deduped_raw_jobs),
            "jobs": deduped_raw_jobs,
            "provider_status": provider_status,
            "providers_used": list(set(providers_used)),
            "all_providers_failed": all_failed and len(deduped_raw_jobs) == 0
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
        logger.info("Initializing Production Multi-Source Live Provider (Adzuna + Remotive + Arbeitnow + Jooble).")
        return MultiSourceJobProvider()
