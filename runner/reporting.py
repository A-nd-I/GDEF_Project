"""Reporting fallback (spec section 11): a plain-language summary_report.md
generated from the same outputs, so the demo never depends on the frontend.
"""

from __future__ import annotations

from collections import Counter
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
        f"- Temperature: {manifest.get('temperature')}",
        f"- Total interactions: {len(records)}",
        "",
        "## Interactions by experiment",
    ]
    for exp, n in sorted(by_exp.items()):
        lines.append(f"- {exp}: {n}")
    lines += ["", "## Interactions by country"]
    for c, n in sorted(by_country.items()):
        lines.append(f"- {c}: {n}")
    lines += [
        "",
        "## What was tested",
        "Governance drift across jurisdictions (A), long multi-turn pressure (B), "
        "and direct stress (C), using the GDEF framework. Raw outputs are in "
        "`raw_outputs.jsonl`; reviewer scoring goes in `findings_matrix.csv`.",
        "",
        "## Reproducibility",
        "Outputs were produced by the runner from the scenario dataset using a "
        "fixed system prompt and logged model/version, temperature, and seed. "
        "See the run manifest for exact parameters.",
        "",
        "_Scored findings (drift type, severity, evidence quotes) are added after "
        "annotation; this fallback report covers what ran and how to reproduce it._",
    ]
    Path(path).write_text("\n".join(lines), encoding="utf-8")
