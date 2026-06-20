"""Multi-turn conversation state.

The model has no memory between calls, so the full message list is resent each
turn. Sequential within a conversation (turn N+1 depends on turn N's reply).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field


@dataclass
class Conversation:
    system_prompt: str | None = None
    conversation_id: str | None = None
    messages: list[dict[str, str]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.conversation_id is None:
            self.conversation_id = f"conv_{uuid.uuid4().hex[:10]}"
        if self.system_prompt:
            self.messages.append({"role": "system", "content": self.system_prompt})

    @property
    def turn(self) -> int:
        return sum(1 for m in self.messages if m["role"] == "user")

    def add_user(self, content: str) -> None:
        self.messages.append({"role": "user", "content": content})

    def add_assistant(self, content: str) -> None:
        self.messages.append({"role": "assistant", "content": content})

    def payload(self) -> list[dict[str, str]]:
        return [dict(m) for m in self.messages]
