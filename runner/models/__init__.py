"""Provider registry / factory.

`get_provider("mock")` works offline today. The two MVP models (spec section 8)
are stubbed and ready to wire up once API access is confirmed:
  - gpt-5-mini  -> OpenAI (proprietary, low-cost reference)
  - qwen-3      -> OpenRouter (open-weight comparison)
  - ollama
Each stub just needs its SDK call filled in plus the matching key in .env.
"""

from __future__ import annotations

from .base import ModelProvider, ModelResponse
from .mock import MockProvider
from .ollama import OllamaProvider

MODEL_PROVIDER = {
    "mock-llm": "mock",
    "gpt-5-mini": "openai",
    "qwen-3": "openrouter",
    "ollama" : "ollama"
}


def get_provider(model: str, *, temperature: float = 0.2, seed: int | None = 0,
                 ) -> ModelProvider:
    model = model.strip()
    provider = MODEL_PROVIDER.get(model, model)  # allow passing provider name too
    if provider in ("mock", "mock-llm"):
        return MockProvider(model="mock-llm", temperature=temperature, seed=seed)
    if provider == "ollama":
        return OllamaProvider(model=model, temperature=temperature, seed=seed)
    if provider in ("openai", "openrouter", "anthropic"):
        raise NotImplementedError(
            f"Provider '{provider}' (model '{model}') is stubbed. Implement its "
            f"generate() in runner/models/{provider}.py (OpenAI-compatible client "
            f"works for both openai and openrouter), add the API key to .env, and "
            f"register it here. Until then use --model mock-llm.\n"
            f"OpenRouter is recommended: one key, many models (incl. qwen-3)."
        )
    # fallback to ollama for any unknown model name (local testing)
    return OllamaProvider(model=model, temperature=temperature, seed=seed)


__all__ = ["ModelProvider", "ModelResponse", "MockProvider", "get_provider",
           "MODEL_PROVIDER"]
