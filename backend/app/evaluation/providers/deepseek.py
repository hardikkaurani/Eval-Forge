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


@provider_registry.register("deepseek")
class DeepSeekProvider(BaseProvider):
    """DeepSeek API client provider (OpenAI compatible)."""

    def __init__(self, api_key: str | None = None, model: str = "deepseek-chat"):
        self.api_key = api_key or (settings.DEEPSEEK_API_KEY.get_secret_value() if settings.DEEPSEEK_API_KEY else None)
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
                text='{"score": 4.6, "reasoning": "Mocked DeepSeek response."}',
                prompt_tokens=11,
                completion_tokens=17,
                latency_ms=110,
                model_name=self.model
            )

        url = "https://api.deepseek.com/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        data = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            **kwargs
        }
        if max_tokens:
            data["max_tokens"] = max_tokens

        start_time = time.perf_counter()
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=data, headers=headers, timeout=timeout)

                if response.status_code == 429:
                    raise RateLimitException("deepseek", response.text)
                elif response.status_code >= 500:
                    raise ProviderUnavailableException("deepseek", response.text)
                elif response.status_code != 200:
                    raise ProviderUnavailableException("deepseek", f"HTTP Status {response.status_code}: {response.text}")

                result = response.json()
                latency = int((time.perf_counter() - start_time) * 1000)

                text = result["choices"][0]["message"]["content"]
                usage = result.get("usage", {})

                return ProviderResponse(
                    text=text,
                    prompt_tokens=usage.get("prompt_tokens"),
                    completion_tokens=usage.get("completion_tokens"),
                    latency_ms=latency,
                    model_name=self.model
                )
        except httpx.TimeoutException as e:
            raise TimeoutException("deepseek", timeout) from e
        except Exception as e:
            if isinstance(e, (RateLimitException, ProviderUnavailableException, TimeoutException)):
                raise e
            raise ProviderUnavailableException("deepseek", str(e)) from e
