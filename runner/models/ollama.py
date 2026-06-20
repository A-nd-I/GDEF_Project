"""Ollama provider — uses Ollama's OpenAI-compatible endpoint (local, no key)."""

from __future__ import annotations

import time

from openai import OpenAI

from .base import ModelProvider, ModelResponse

_CLIENT: OpenAI | None = None


def _client() -> OpenAI:
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
    return _CLIENT


class OllamaProvider(ModelProvider):
    name = "ollama"

    def generate(self, messages: list[dict[str, str]]) -> ModelResponse:
        t0 = time.perf_counter()
        resp = _client().chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            seed=self.seed,
            max_tokens=self.max_tokens,
        )
        latency = (time.perf_counter() - t0) * 1000
        choice = resp.choices[0].message
        # ponytail: qwen3 thinking models put response in content; reasoning is the CoT scratchpad.
        # if content is empty the token budget was exhausted by thinking — raise so the user notices.
        text = choice.content or ""
        if not text:
            reasoning = getattr(choice, "reasoning", None) or ""
            raise RuntimeError(
                f"Empty response from {self.model} — token budget exhausted by thinking. "
                f"Run without --max-tokens or set it to 1500+. "
                f"Thinking preview: {reasoning[:200]!r}"
            )
        return ModelResponse(
            text=text,
            model=resp.model,
            provider=self.name,
            token_count=resp.usage.total_tokens if resp.usage else None,
            response_latency_ms=round(latency, 3),
            raw=resp.model_dump(),
        )
