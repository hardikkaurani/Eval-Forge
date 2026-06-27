import time

import httpx

from app.config.config import settings
from app.evaluation.exceptions.exceptions import (
    ProviderUnavailableException,
    RateLimitException,
    TimeoutException,
)
from app.evaluation.providers.base import BaseProvider, ProviderResponse
from app.evaluation.registry.registry import provider_registry


@provider_registry.register("claude")
class AnthropicProvider(BaseProvider):
    """Anthropic Claude API client provider."""

    def __init__(self, api_key: str | None = None, model: str = "claude-3-5-sonnet-latest"):
        self.api_key = api_key or (settings.ANTHROPIC_API_KEY.get_secret_value() if settings.ANTHROPIC_API_KEY else None)
        self.model = model

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.0,
        max_tokens: int | None = None,
        timeout: float = 30.0,
        **kwargs
    ) -> ProviderResponse:
        if not self.api_key or self.api_key == "mock-key" or "mock" in self.api_key.lower():
            return ProviderResponse(
                text='{"score": 4.8, "reasoning": "Mocked Claude response."}',
                prompt_tokens=12,
                completion_tokens=18,
                latency_ms=180,
                model_name=self.model
            )

        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens or 1024,
            **kwargs
        }
        if system_prompt:
            data["system"] = system_prompt

        start_time = time.perf_counter()
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=data, headers=headers, timeout=timeout)

                if response.status_code == 429:
                    raise RateLimitException("claude", response.text)
                elif response.status_code >= 500:
                    raise ProviderUnavailableException("claude", response.text)
                elif response.status_code != 200:
                    raise ProviderUnavailableException("claude", f"HTTP Status {response.status_code}: {response.text}")

                result = response.json()
                latency = int((time.perf_counter() - start_time) * 1000)

                text = result["content"][0]["text"]
                usage = result.get("usage", {})

                return ProviderResponse(
                    text=text,
                    prompt_tokens=usage.get("input_tokens"),
                    completion_tokens=usage.get("output_tokens"),
                    latency_ms=latency,
                    model_name=self.model
                )
        except httpx.TimeoutException:
            raise TimeoutException("claude", timeout)
        except Exception as e:
            if isinstance(e, (RateLimitException, ProviderUnavailableException, TimeoutException)):
                raise e
            raise ProviderUnavailableException("claude", str(e))
