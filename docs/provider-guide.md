# Provider Guide

EvalForge supports multiple LLM providers behind a shared interface.

## Built-in providers

- OpenAI
- Google Gemini
- Anthropic Claude
- Ollama
- OpenRouter
- DeepSeek

## Provider contract

Every provider implements the same async `generate()` interface and returns a normalized response containing:

- generated text
- prompt token count
- completion token count
- latency
- model name

## Configuration

Runtime defaults live in `backend/app/config/config.py` and can be overridden via environment variables.

## Notes

- Providers fall back to deterministic mock responses when credentials are missing in local testing.
- `Ollama` can be pointed at a custom base URL.
- `OpenRouter` and `DeepSeek` use OpenAI-compatible request shapes.
