from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from typing import Any

LIST_SEP = ";"

INPUT_COLUMNS = [
    "scenario_id", "base_question_id", "country", "jurisdiction", "language",
    "domain", "user_role", "experiment_type", "turn_number", "prompt",
    "expected_governance_behaviors", "drift_risks", "pressure_type",
    "severity_if_failed", "notes",
]

OUTPUT_FIELDS = [
    "run_id", "scenario_id", "base_question_id", "country", "jurisdiction",
    "language", "domain", "user_role", "experiment_type", "turn_number",
    "pressure_type", "prompt", "response", "timestamp", "model", "provider",
    "temperature", "seed", "response_latency_ms", "token_count", "word_count", "conversation_id",
]
CSV_FIELDS = OUTPUT_FIELDS


@dataclass
class Scenario:
    scenario_id: str
    base_question_id: str
    country: str
    jurisdiction: str
    language: str
    domain: str
    user_role: str
    experiment_type: str
    turn_number: int
    prompt: str
    pressure_type: str = "NO_PRESSURE_BASELINE"
    expected_governance_behaviors: list[str] = field(default_factory=list)
    drift_risks: list[str] = field(default_factory=list)
    severity_if_failed: int | None = None
    notes: str = ""


@dataclass
class EvalRecord:
    run_id: str
    scenario_id: str
    base_question_id: str
    country: str
    jurisdiction: str
    language: str
    domain: str
    user_role: str
    experiment_type: str
    turn_number: int
    pressure_type: str
    prompt: str
    response: str
    timestamp: str
    model: str
    provider: str
    temperature: float
    seed: int | None = None
    response_latency_ms: float | None = None
    token_count: int | None = None
    word_count: int | None = None
    conversation_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_jsonl(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

    def to_csv_row(self) -> dict[str, Any]:
        d = self.to_dict()
        return {k: d.get(k, "") for k in CSV_FIELDS}
