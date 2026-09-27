"""
Job Provider Abstraction Layer for Career Lens Platform
"""
from app.services.job_providers.base_provider import BaseJobProvider
from app.services.job_providers.provider_factory import ProviderFactory

__all__ = ['BaseJobProvider', 'ProviderFactory']
