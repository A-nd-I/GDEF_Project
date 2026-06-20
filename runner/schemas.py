"""Input (Scenario row) and output (EvalRecord) schemas — aligned to the GDEF
MVP Developer Specification (docs/GDEF_SPEC.md).

One CSV row = one (scenario, turn) unit. For Experiment B a scenario has 15
rows (turn_number 1..15); for A and C rows are single-turn.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from typing import Any

LIST_SEP = ";"  # separates multiple labels inside one CSV cell

# Exact input columns (spec section 4).
INPUT_COLUMNS = [
    "scenario_id", "base_question_id", "country", "jurisdiction", "language",
    "domain", "user_role", "experiment_type", "turn_number", "prompt",
    "expected_governance_behaviors", "drift_risks", "pressure_type",
    "severity_if_failed", "notes",
]

# Exact JSONL output fields (spec section 9.1) + raw preserved in metadata.
OUTPUT_FIELDS = [
    "run_id", "scenario_id", "base_question_id", "country", "jurisdiction",
    "language", "domain", "user_role", "experiment_type", "turn_number",
    "pressure_type", "prompt", "response", "timestamp", "model", "provider",
    "temperature", "response_latency_ms", "token_count", "conversation_id",
]
# raw_outputs.csv = OUTPUT_FIELDS (no nested metadata, which can hold newlines).
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
    experiment_type: str           # A_JURISDICTION_CONSISTENCY | B_... | C_...
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
    response_latency_ms: float | None = None
    token_count: int | None = None
    conversation_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)  # raw output preserved

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_jsonl(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

    def to_csv_row(self) -> dict[str, Any]:
        d = self.to_dict()
        return {k: d.get(k, "") for k in CSV_FIELDS}
