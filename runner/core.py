"""Core engine: turns scenario rows into execution units and runs them.

Single-turn units (A, C) are independent calls. Multi-turn units (B) are one
conversation replayed turn by turn. Everything is sequential within a unit;
units are independent and could be parallelised later (asyncio / thread pool +
rate limiting). Outputs follow the spec (section 11).
"""

from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path

from .conversation import Conversation
from .io_utils import ResultWriter, group_units, write_run_manifest
from .models.base import ModelProvider
from .reporting import write_summary_report
from .schemas import EvalRecord, Scenario
from .templates import SYSTEM_PROMPT


def _git_commit() -> str | None:
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                             text=True, timeout=5)
        return out.stdout.strip() or None
    except Exception:
        return None


def estimate_interactions(scenarios: list[Scenario], repetitions: int) -> dict:
    units = group_units(scenarios)
    by_exp: dict[str, int] = {}
    for unit in units:
        exp = unit[0].experiment_type
        by_exp[exp] = by_exp.get(exp, 0) + len(unit) * repetitions
    by_exp["TOTAL"] = sum(by_exp.values())
    return by_exp


def _run_unit(unit: list[Scenario], provider: ModelProvider, *, run_id: str,
              system_prompt: str | None):
    multi_turn = len(unit) > 1
    conv = Conversation(system_prompt=system_prompt)
    conv_id = conv.conversation_id if multi_turn else None
    for row in unit:
        conv.add_user(row.prompt)
        resp = provider.generate(conv.payload())
        conv.add_assistant(resp.text)
        yield EvalRecord(
            run_id=run_id,
            scenario_id=row.scenario_id,
            base_question_id=row.base_question_id,
            country=row.country,
            jurisdiction=row.jurisdiction,
            language=row.language,
            domain=row.domain,
            user_role=row.user_role,
            experiment_type=row.experiment_type,
            turn_number=row.turn_number,
            pressure_type=row.pressure_type,
            prompt=row.prompt,
            response=resp.text,
            timestamp=datetime.now(timezone.utc).isoformat(),
            model=resp.model,
            provider=resp.provider,
            temperature=provider.temperature,
            response_latency_ms=resp.response_latency_ms,
            token_count=resp.token_count,
            conversation_id=conv_id,
            metadata={"raw": resp.raw},  # raw output preservation
        )


def run_evaluation(*, scenarios: list[Scenario], provider: ModelProvider,
                   output_dir: str | Path, repetitions: int, run_id: str,
                   logger, system_prompt: str | None = SYSTEM_PROMPT) -> dict:
    units = group_units(scenarios)
    n = 0
    with ResultWriter(output_dir) as writer:
        for unit in units:
            for _ in range(repetitions):
                for record in _run_unit(unit, provider, run_id=run_id,
                                        system_prompt=system_prompt):
                    writer.write(record)
                    n += 1
            head = unit[0]
            logger.info("[%s] %s (%d turn(s)) done — %d records total",
                        head.experiment_type, head.scenario_id, len(unit), n)
        writer.export_all()
        records = writer.records

    manifest = {
        "run_id": run_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": provider.model,
        "provider": provider.name,
        "temperature": provider.temperature,
        "seed": provider.seed,
        "repetitions": repetitions,
        "system_prompt": system_prompt,
        "total_interactions": n,
        "git_commit": _git_commit(),
    }
    out = Path(output_dir)
    write_run_manifest(out / f"run_{run_id}_manifest.json", manifest)
    (out / "reports").mkdir(exist_ok=True)
    write_summary_report(out / "reports" / "summary_report.md",
                         records=records, manifest=manifest)
    return manifest
