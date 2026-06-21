"""OpenRouter provider — OpenAI-compatible API, many models with one key."""

from __future__ import annotations

import os
import time

from dotenv import load_dotenv
from openai import OpenAI

from .base import ModelProvider, ModelResponse

load_dotenv()

_CLIENT: OpenAI | None = None


def _client() -> OpenAI:
    global _CLIENT
    if _CLIENT is None:
        api_key = os.getenv("OPEN_ROUTER_API_KEY")
        if not api_key:
            raise RuntimeError("OPEN_ROUTER_API_KEY not set in .env")
        _CLIENT = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
    return _CLIENT


class OpenRouterProvider(ModelProvider):
    name = "openrouter"

    def generate(self, messages: list[dict[str, str]]) -> ModelResponse:
        t0 = time.perf_counter()
        extra: dict | None = None if self.reasoning else {"reasoning": {"enabled": False}}
        resp = _client().chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            seed=self.seed,
            max_tokens=self.max_tokens,
            extra_body=extra,
        )
        latency = (time.perf_counter() - t0) * 1000
        choice = resp.choices[0].message
        text = choice.content or getattr(choice, "reasoning_content", None) or ""
        return ModelResponse(
            text=text,
            model=resp.model,
            provider=self.name,
            token_count=resp.usage.total_tokens if resp.usage else None,
            response_latency_ms=round(latency, 3),
            raw=resp.model_dump(),
        )
