from __future__ import annotations

from .base import ModelProvider, ModelResponse
from .mock import MockProvider
from .ollama import OllamaProvider
from .openrouter import OpenRouterProvider

MODEL_PROVIDER = {
    "mock-llm": "mock",
    "gpt-5-mini": "openrouter",
    "qwen-3": "openrouter",
    "ollama": "ollama",
}


def get_provider(model: str, *, temperature: float = 0.2, seed: int | None = 0,
                 max_tokens: int | None = None, reasoning: bool = True) -> ModelProvider:
    model = model.strip()
    provider = MODEL_PROVIDER.get(model, model)
    if provider in ("mock", "mock-llm"):
        return MockProvider(model="mock-llm", temperature=temperature, seed=seed)
    if provider == "ollama":
        return OllamaProvider(model=model, temperature=temperature, seed=seed, max_tokens=max_tokens)
    if provider == "openrouter":
        return OpenRouterProvider(model=model, temperature=temperature, seed=seed,
                                  max_tokens=max_tokens, reasoning=reasoning)
    if provider in ("openai", "anthropic"):
        raise NotImplementedError(f"Provider '{provider}' not implemented. Use openrouter or mock-llm.")
    if "/" in model:
        return OpenRouterProvider(model=model, temperature=temperature, seed=seed,
                                  max_tokens=max_tokens, reasoning=reasoning)
    raise ValueError(
        f"Unknown model '{model}'. "
        "For OpenRouter use 'org/model' (e.g. 'qwen/qwen3.5-flash-02-23'). "
        "For Ollama use '--model ollama' and set the model name, or prefix with 'ollama:'. "
        "For offline testing use '--model mock-llm'."
    )


__all__ = ["ModelProvider", "ModelResponse", "MockProvider", "get_provider",
           "MODEL_PROVIDER"]
