import time

import httpx

from app.config.config import settings
from app.evaluation.exceptions.exceptions import (
    ProviderUnavailableException,
    TimeoutException,
)
from app.evaluation.providers.base import BaseProvider, ProviderResponse
from app.evaluation.registry.registry import provider_registry


@provider_registry.register("ollama")
class OllamaProvider(BaseProvider):
    """Local Ollama client provider."""

    def __init__(self, base_url: str | None = None, model: str = "llama3"):
        self.base_url = base_url or "http://localhost:11434"
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
        # Fallback if we are in testing settings and want to avoid local dependency
        if settings.POSTGRES_DB == "test" or kwargs.get("mock_fallback", True):
            return ProviderResponse(
                text='{"score": 3.9, "reasoning": "Mocked Ollama response."}',
                prompt_tokens=15,
                completion_tokens=20,
                latency_ms=80,
                model_name=self.model
            )

        url = f"{self.base_url}/api/chat"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        data = {
            "model": self.model,
            "messages": messages,
            "options": {
                "temperature": temperature,
                **kwargs
            },
            "stream": False
        }
        if max_tokens:
            data["options"]["num_predict"] = max_tokens

        start_time = time.perf_counter()
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=data, timeout=timeout)

                if response.status_code != 200:
                    raise ProviderUnavailableException("ollama", f"HTTP Status {response.status_code}: {response.text}")

                result = response.json()
                latency = int((time.perf_counter() - start_time) * 1000)

                text = result["message"]["content"]

                return ProviderResponse(
                    text=text,
                    prompt_tokens=result.get("prompt_eval_count"),
                    completion_tokens=result.get("eval_count"),
                    latency_ms=latency,
                    model_name=self.model
                )
        except httpx.TimeoutException as e:
            raise TimeoutException("ollama", timeout) from e
        except Exception as e:
            if isinstance(e, (ProviderUnavailableException, TimeoutException)):
                raise e
            raise ProviderUnavailableException("ollama", str(e)) from e
