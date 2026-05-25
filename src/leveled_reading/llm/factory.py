from __future__ import annotations

from ..config import Settings
from .base import LLMClient
from .mock import MockLLMClient
from .api_client import APILLMClient


def build_llm_client(settings: Settings, provider_override: str | None = None) -> LLMClient:
    provider = (provider_override or settings.provider).lower()
    if provider == "mock":
        return MockLLMClient()
    if provider == "api":
        return APILLMClient(settings)
    raise ValueError(f"Unsupported provider: {provider}. Use 'mock' or 'api'.")
