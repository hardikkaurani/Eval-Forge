from app.evaluation.providers.base import BaseProvider, ProviderResponse
from app.evaluation.registry.registry import provider_registry


@provider_registry.register("mock")
class MockProvider(BaseProvider):
    """Explicit Mock Provider registered solely for testing purposes."""

    display_name = "Mock Provider"

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "mock-model",
        custom_response: str | None = None,
    ):
        self.model = model
        self.custom_response = custom_response

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.0,
        max_tokens: int | None = None,
        timeout: float = 30.0,
        **kwargs,
    ) -> ProviderResponse:
        text = (
            self.custom_response
            or '{"score": 4.5, "confidence": 0.9, "reasoning": "Mocked provider evaluation response."}'
        )
        return ProviderResponse(
            text=text,
            prompt_tokens=10,
            completion_tokens=15,
            latency_ms=50,
            model_name=self.model,
        )
