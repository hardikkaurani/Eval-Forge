from abc import ABC, abstractmethod

from pydantic import BaseModel


class ProviderResponse(BaseModel):
    """Unified response object returned by all LLM Providers."""
    text: str
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    latency_ms: int | None = None
    model_name: str

class BaseProvider(ABC):
    """Abstract Base Class that all evaluation LLM Providers must implement."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.0,
        max_tokens: int | None = None,
        timeout: float = 30.0,
        **kwargs
    ) -> ProviderResponse:
        """Generate response from the provider model."""
        pass
