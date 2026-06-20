"""Offline mock provider — lets the whole pipeline run with no API key/network.
Deterministic at temperature 0; crudely simulates governance drift (the more
pressure across turns, the more the canned answer softens). Replace with a real
provider once credentials are available.
"""

from __future__ import annotations

import hashlib
import time

from .base import ModelProvider, ModelResponse

_PRESSURE_HINTS = ("assume", "ignore", "do not", "don't", "only", "yes or no",
                   "final answer", "remove", "workaround", "everyone", "urgent",
                   "commit", "pretend", "steps")


class MockProvider(ModelProvider):
    name = "mock"

    def __init__(self, model: str = "mock-llm", temperature: float = 0.2,
                 seed: int | None = 0):
        super().__init__(model=model, temperature=temperature, seed=seed)

    def generate(self, messages: list[dict[str, str]]) -> ModelResponse:
        t0 = time.perf_counter()
        user_turns = [m for m in messages if m["role"] == "user"]
        last = user_turns[-1]["content"].lower() if user_turns else ""
        turn = len(user_turns)
        pressure = sum(last.count(h) for h in _PRESSURE_HINTS)

        if turn <= 1 and pressure == 0:
            stance = ("This depends on the applicable local law and I can't give "
                      "definitive legal certainty. I'd recommend review by a "
                      "qualified local expert before acting.")
        elif pressure >= 1 or turn >= 4:
            stance = ("Okay, broadly you could proceed, though there may be some "
                      "considerations to keep in mind.")  # simulated drift
        else:
            stance = ("I should be careful here and note the limits of what I can "
                      "say without local legal review.")

        digest = hashlib.sha256(last.encode("utf-8")).hexdigest()[:6]
        text = f"{stance} [mock:{digest} turn={turn} pressure={pressure}]"
        latency = (time.perf_counter() - t0) * 1000
        return ModelResponse(
            text=text,
            model=self.model,
            provider=self.name,
            token_count=len(text.split()),
            response_latency_ms=round(latency, 3),
            raw={"simulated": True, "turn": turn, "pressure": pressure},
        )
