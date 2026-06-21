from __future__ import annotations

import statistics
from collections import Counter, defaultdict
from pathlib import Path

from .schemas import EvalRecord


def write_summary_report(path: str | Path, *, records: list[EvalRecord],
                         manifest: dict) -> None:
    by_exp = Counter(r.experiment_type for r in records)
    by_model = Counter(r.model for r in records)
    by_country = Counter(r.country for r in records)

    lines = [
        "# GDEF Run Summary",
        "",
        f"- Run ID: `{manifest.get('run_id')}`",
        f"- Timestamp: {manifest.get('timestamp')}",
        f"- Models: {', '.join(sorted(by_model)) or '(none)'}",
        f"- Temperature: {manifest.get('temperature')} | Seed: {manifest.get('seed')}",
        f"- Repetitions: {manifest.get('repetitions', 1)}",
        f"- Total interactions: {len(records)}",
        "",
        "## Interactions by experiment",
    ]
    for exp, n in sorted(by_exp.items()):
        lines.append(f"- {exp}: {n}")
    lines += ["", "## Interactions by country"]
    for c, n in sorted(by_country.items()):
        lines.append(f"- {c}: {n}")

    reps = manifest.get("repetitions", 1)
    if reps > 1 and records:
        lines += ["", "## Variability across repetitions"]
        by_scenario: dict[str, list[EvalRecord]] = defaultdict(list)
        for r in records:
            by_scenario[f"{r.scenario_id}_t{r.turn_number}"].append(r)

        lines.append("| scenario | turn | latency_mean_ms | latency_std_ms | tokens_mean | tokens_std |")
        lines.append("|----------|------|-----------------|----------------|-------------|------------|")
        for key, recs in sorted(by_scenario.items()):
            latencies = [r.response_latency_ms for r in recs if r.response_latency_ms is not None]
            tokens = [r.token_count for r in recs if r.token_count is not None]
            lat_mean = f"{statistics.mean(latencies):.0f}" if latencies else "-"
            lat_std = f"{statistics.stdev(latencies):.0f}" if len(latencies) > 1 else "-"
            tok_mean = f"{statistics.mean(tokens):.0f}" if tokens else "-"
            tok_std = f"{statistics.stdev(tokens):.0f}" if len(tokens) > 1 else "-"
            sid = recs[0].scenario_id
            turn = recs[0].turn_number
            lines.append(f"| {sid} | {turn} | {lat_mean} | {lat_std} | {tok_mean} | {tok_std} |")

    lines += [
        "",
        "## Reproducibility",
        f"Git commit: `{manifest.get('git_commit') or 'unknown'}`",
        "Raw outputs: `raw_outputs.jsonl` — reviewer scoring: `findings_matrix.csv`.",
        "",
        "_Scored findings are added after annotation._",
    ]
    Path(path).write_text("\n".join(lines), encoding="utf-8")
