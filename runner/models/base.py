"""Provider abstraction. The runner talks to models only through this interface,
so swapping backends never touches experiment logic. Real providers implement
`generate` on top of their SDK; see mock.py for the offline stub.
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ModelResponse:
    text: str
    model: str
    provider: str
    token_count: int | None = None
    response_latency_ms: float | None = None
    raw: dict[str, Any] = field(default_factory=dict) 


class ModelProvider(abc.ABC):
    name: str = "abstract" 

    def __init__(self, model: str, temperature: float = 0.2,
                 seed: int | None = 0):
        self.model = model
        self.temperature = temperature
        self.seed = seed

    @abc.abstractmethod
    def generate(self, messages: list[dict[str, str]]) -> ModelResponse:
        """Send the full message history (incl. system) and return the reply."""
        raise NotImplementedError
