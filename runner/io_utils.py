from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

from .schemas import CSV_FIELDS, LIST_SEP, EvalRecord, Scenario

FINDINGS_COLUMNS = [
    "run_id", "scenario_id", "base_question_id", "country", "jurisdiction",
    "language", "domain", "user_role", "experiment_type", "turn_number",
    "pressure_type", "model", "provider", "prompt", "response",
    "transparency_score", "jurisdiction_awareness_score", "human_oversight_score",
    "reliability_score", "context_awareness_score", "pressure_resistance_score",
    "consistency_score", "unsupported_certainty_score", "overall_governance_score",
    "overall_governance_classification", "drift_observed", "drift_type",
    "severity_score", "pass_fail", "evidence_quote", "reviewer_notes", "reviewer",
]


def _split(cell: str) -> list[str]:
    return [p.strip() for p in (cell or "").split(LIST_SEP) if p.strip()]


def _int_or_none(v: str):
    v = (v or "").strip()
    return int(v) if v.isdigit() else None


def load_scenarios(path: str | Path) -> list[Scenario]:
    path = Path(path)
    rows: list[Scenario] = []
    with path.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append(Scenario(
                scenario_id=(r.get("scenario_id") or "").strip(),
                base_question_id=(r.get("base_question_id") or "").strip(),
                country=(r.get("country") or "").strip(),
                jurisdiction=(r.get("jurisdiction") or "").strip(),
                language=(r.get("language") or "").strip(),
                domain=(r.get("domain") or "").strip(),
                user_role=(r.get("user_role") or "").strip(),
                experiment_type=(r.get("experiment_type") or "").strip(),
                turn_number=_int_or_none(r.get("turn_number")) or 1,
                prompt=(r.get("prompt") or "").strip(),
                pressure_type=(r.get("pressure_type") or "NO_PRESSURE_BASELINE").strip(),
                expected_governance_behaviors=_split(r.get("expected_governance_behaviors")),
                drift_risks=_split(r.get("drift_risks")),
                severity_if_failed=_int_or_none(r.get("severity_if_failed")),
                notes=(r.get("notes") or "").strip(),
            ))
    return rows


def group_units(scenarios: list[Scenario]) -> list[list[Scenario]]:
    units: list[list[Scenario]] = []
    b_groups: dict[str, list[Scenario]] = {}
    for s in scenarios:
        if s.experiment_type == "B_BEHAVIORAL_DRIFT":
            b_groups.setdefault(s.scenario_id, []).append(s)
        else:
            units.append([s])
    for sid, rows in b_groups.items():
        rows.sort(key=lambda r: r.turn_number)
        units.append(rows)
    return units


class ResultWriter:
    def __init__(self, output_dir: str | Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.jsonl_path = self.output_dir / "raw_outputs.jsonl"
        self._fh = self.jsonl_path.open("w", encoding="utf-8")
        self._rows: list[EvalRecord] = []

    def write(self, record: EvalRecord) -> None:
        self._fh.write(record.to_jsonl() + "\n")
        self._fh.flush()
        self._rows.append(record)

    def export_all(self) -> dict:
        self._export_csv("raw_outputs.csv", CSV_FIELDS,
                         [r.to_csv_row() for r in self._rows])
        fm_rows = [{c: r.to_dict().get(c, "") for c in FINDINGS_COLUMNS} for r in self._rows]
        self._export_csv("findings_matrix.csv", FINDINGS_COLUMNS, fm_rows)
        self._export_model_comparison()
        self._export_csv("top_findings.csv", FINDINGS_COLUMNS, [])
        return {"records": len(self._rows)}

    def _export_csv(self, name: str, fields: list[str], rows: list[dict]) -> None:
        with (self.output_dir / name).open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            for row in rows:
                w.writerow(row)

    def _export_model_comparison(self) -> None:
        counts = Counter((r.model, r.experiment_type, r.country) for r in self._rows)
        fields = ["model", "experiment_type", "country", "interactions"]
        rows = [{"model": m, "experiment_type": e, "country": c, "interactions": n}
                for (m, e, c), n in sorted(counts.items())]
        self._export_csv("model_comparison.csv", fields, rows)

    @property
    def records(self) -> list[EvalRecord]:
        return self._rows

    def close(self) -> None:
        self._fh.close()

    def __enter__(self) -> "ResultWriter":
        return self

    def __exit__(self, *exc) -> None:
        self.close()


def write_run_manifest(path: str | Path, manifest: dict) -> None:
    Path(path).write_text(json.dumps(manifest, indent=2, ensure_ascii=False),
                          encoding="utf-8")
