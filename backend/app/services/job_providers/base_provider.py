from abc import ABC, abstractmethod

class BaseJobProvider(ABC):
    """
    Abstract Base Class for external Job Search API Providers.
    Ensures provider layer is decoupled from internal matching engine.
    """

    @abstractmethod
    def search_jobs(self, search_params: dict) -> dict:
        """
        Search live jobs from external provider.
        
        Args:
            search_params: dict containing keyword, location, country, remote, page, limit, etc.
            
        Returns:
            dict with 'success', 'source', 'total', 'page', and list of raw/normalized 'jobs'.
        """
        pass

    @abstractmethod
    def verify_job_status(self, provider_job_id: str) -> str:
        """
        Check if a job is still LIVE, EXPIRED, or REMOVED on provider.
        """
        pass
