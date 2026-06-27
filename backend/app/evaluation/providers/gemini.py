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


@provider_registry.register("gemini")
class GeminiProvider(BaseProvider):
    """Google Gemini API client provider."""

    def __init__(self, api_key: str | None = None, model: str = "gemini-1.5-flash"):
        self.api_key = api_key or (settings.GEMINI_API_KEY.get_secret_value() if settings.GEMINI_API_KEY else None)
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
                text='{"score": 4.2, "reasoning": "Mocked Gemini response."}',
                prompt_tokens=8,
                completion_tokens=12,
                latency_ms=150,
                model_name=self.model
            )

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}

        contents = []
        if system_prompt:
            contents.append({
                "role": "user",
                "parts": [{"text": f"System Instruction: {system_prompt}"}]
            })
        contents.append({
            "role": "user",
            "parts": [{"text": prompt}]
        })

        data = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                **kwargs
            }
        }
        if max_tokens:
            data["generationConfig"]["maxOutputTokens"] = max_tokens

        start_time = time.perf_counter()
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=data, headers=headers, timeout=timeout)

                if response.status_code == 429:
                    raise RateLimitException("gemini", response.text)
                elif response.status_code >= 500:
                    raise ProviderUnavailableException("gemini", response.text)
                elif response.status_code != 200:
                    raise ProviderUnavailableException("gemini", f"HTTP Status {response.status_code}: {response.text}")

                result = response.json()
                latency = int((time.perf_counter() - start_time) * 1000)

                text = result["candidates"][0]["content"]["parts"][0]["text"]
                usage = result.get("usageMetadata", {})

                return ProviderResponse(
                    text=text,
                    prompt_tokens=usage.get("promptTokenCount"),
                    completion_tokens=usage.get("candidatesTokenCount"),
                    latency_ms=latency,
                    model_name=self.model
                )
        except httpx.TimeoutException as e:
            raise TimeoutException("gemini", timeout) from e
        except Exception as e:
            if isinstance(e, (RateLimitException, ProviderUnavailableException, TimeoutException)):
                raise e
            raise ProviderUnavailableException("gemini", str(e)) from e
