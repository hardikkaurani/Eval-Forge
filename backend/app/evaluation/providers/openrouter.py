import time
import httpx
from app.evaluation.providers.base import BaseProvider, ProviderResponse
from app.evaluation.registry.registry import provider_registry
from app.evaluation.exceptions.exceptions import ProviderUnavailableException, RateLimitException, TimeoutException
from app.config.config import settings

@provider_registry.register("openrouter")
class OpenRouterProvider(BaseProvider):
    """OpenRouter API client provider (OpenAI compatible)."""
    
    def __init__(self, api_key: str | None = None, model: str = "meta-llama/llama-3-8b-instruct:free"):
        self.api_key = api_key or (settings.OPENROUTER_API_KEY.get_secret_value() if settings.OPENROUTER_API_KEY else None)
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
                text='{"score": 4.0, "reasoning": "Mocked OpenRouter response."}',
                prompt_tokens=14,
                completion_tokens=22,
                latency_ms=130,
                model_name=self.model
            )

        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://evalforge.com",
            "X-Title": "EvalForge",
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
                    raise RateLimitException("openrouter", response.text)
                elif response.status_code >= 500:
                    raise ProviderUnavailableException("openrouter", response.text)
                elif response.status_code != 200:
                    raise ProviderUnavailableException("openrouter", f"HTTP Status {response.status_code}: {response.text}")
                
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
        except httpx.TimeoutException:
            raise TimeoutException("openrouter", timeout)
        except Exception as e:
            if isinstance(e, (RateLimitException, ProviderUnavailableException, TimeoutException)):
                raise e
            raise ProviderUnavailableException("openrouter", str(e))
