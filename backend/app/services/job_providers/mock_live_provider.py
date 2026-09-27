import logging
from app.services.job_providers.base_provider import BaseJobProvider

logger = logging.getLogger(__name__)

class MockLiveJobProvider(BaseJobProvider):
    """
    DEPRECATED / DISABLED: Synthetic mock data provider.
    Career Lens production pipeline strictly forbids synthetic/mock job fabrication.
    All live job recommendations are retrieved strictly from authorized external API endpoints.
    """

    def __init__(self):
        self.provider_name = "Disabled Synthetic Provider"

    def is_configured(self) -> bool:
        return False


    def search_jobs(self, search_params: dict) -> dict:
        logger.warning("MockLiveJobProvider invoked, but synthetic job fabrication is disabled in production.")
        return {
            "success": False,
            "error": "SYNTHETIC_DATA_DISABLED",
            "message": "Synthetic job generation is strictly disabled. Only genuine live API vacancies are served.",
            "source": self.provider_name,
            "total": 0,
            "page": 1,
            "limit": 0,
            "jobs": []
        }

    def verify_job_status(self, provider_job_id: str) -> str:
        return "EXPIRED"
