from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True, slots=True)
class ModelPrice:
    """Price per 1,000,000 tokens in USD."""

    input_price_per_1m: float
    output_price_per_1m: float


# Model Pricing Table (prices per 1,000,000 tokens)
MODEL_PRICING_TABLE: Dict[Tuple[str, str], ModelPrice] = {
    # OpenAI
    ("openai", "gpt-4o-mini"): ModelPrice(
        input_price_per_1m=0.15, output_price_per_1m=0.60
    ),
    ("openai", "gpt-4o"): ModelPrice(
        input_price_per_1m=2.50, output_price_per_1m=10.00
    ),
    ("openai", "gpt-3.5-turbo"): ModelPrice(
        input_price_per_1m=0.50, output_price_per_1m=1.50
    ),
    # Anthropic Claude
    ("claude", "claude-3-5-sonnet-latest"): ModelPrice(
        input_price_per_1m=3.00, output_price_per_1m=15.00
    ),
    ("claude", "claude-3-5-haiku-latest"): ModelPrice(
        input_price_per_1m=0.80, output_price_per_1m=4.00
    ),
    ("claude", "claude-3-opus-latest"): ModelPrice(
        input_price_per_1m=15.00, output_price_per_1m=75.00
    ),
    # Google Gemini
    ("gemini", "gemini-1.5-flash"): ModelPrice(
        input_price_per_1m=0.075, output_price_per_1m=0.30
    ),
    ("gemini", "gemini-1.5-pro"): ModelPrice(
        input_price_per_1m=1.25, output_price_per_1m=5.00
    ),
    # DeepSeek
    ("deepseek", "deepseek-chat"): ModelPrice(
        input_price_per_1m=0.14, output_price_per_1m=0.28
    ),
    ("deepseek", "deepseek-reasoner"): ModelPrice(
        input_price_per_1m=0.55, output_price_per_1m=2.19
    ),
    # NVIDIA NIM
    ("nvidia", "meta/llama-3.1-8b-instruct"): ModelPrice(
        input_price_per_1m=0.10, output_price_per_1m=0.10
    ),
    ("nvidia", "meta/llama-3.1-70b-instruct"): ModelPrice(
        input_price_per_1m=0.70, output_price_per_1m=0.70
    ),
    # OpenRouter
    ("openrouter", "meta-llama/llama-3-8b-instruct:free"): ModelPrice(
        input_price_per_1m=0.0, output_price_per_1m=0.0
    ),
    # Mock / Test Double
    ("mock", "mock-model"): ModelPrice(
        input_price_per_1m=1.00, output_price_per_1m=2.00
    ),
}


class CostCalculator:
    """Calculates monetary LLM execution costs in USD based on provider and model token counts."""

    @staticmethod
    def get_price(provider: str, model: str) -> ModelPrice | None:
        """Looks up model pricing. Returns None if unknown."""
        key = (provider.lower(), model.lower())
        if key in MODEL_PRICING_TABLE:
            return MODEL_PRICING_TABLE[key]

        # Partial match fallback (e.g. prefix match for versioned models)
        for (p, m), price in MODEL_PRICING_TABLE.items():
            if p == provider.lower() and (m in model.lower() or model.lower() in m):
                return price

        return None

    @staticmethod
    def calculate_cost(
        provider: str,
        model: str,
        prompt_tokens: int | None,
        completion_tokens: int | None,
    ) -> float | None:
        """Calculates total cost in USD. Returns None if model pricing is unknown."""
        price = CostCalculator.get_price(provider, model)
        if price is None:
            return None

        in_tokens = prompt_tokens or 0
        out_tokens = completion_tokens or 0

        cost = (in_tokens / 1_000_000.0) * price.input_price_per_1m + (
            out_tokens / 1_000_000.0
        ) * price.output_price_per_1m
        return round(cost, 8)
