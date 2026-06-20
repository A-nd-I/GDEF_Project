# GDEF — Governance Drift Evaluation Runner

Probes frontier LLMs for **governance-aware behavior** across jurisdictions (A),
long multi-turn pressure (B), and direct stress (C). Implements the GDEF MVP
developer spec — see `docs/GDEF_SPEC.md` (the contract) and the full PDF.

## Quick start (offline, no API key)

```bash
python run.py --scenarios data/scenarios_sample.csv --validate   # check controlled lists
python run.py --scenarios data/scenarios_sample.csv --dry-run     # count interactions
python run.py --model mock-llm --scenarios data/scenarios_sample.csv  # run end-to-end
```

Outputs land in `outputs/`: `raw_outputs.jsonl` (lossless source of truth),
`raw_outputs.csv`, `findings_matrix.csv` (annotation template), `model_comparison.csv`,
`top_findings.csv`, a run manifest, and `reports/summary_report.md`.

## Real models

MVP plan: `gpt-5-mini` (OpenAI) + `qwen-3` (OpenRouter). To enable:
1. `pip install -r requirements.txt` (uncomment the SDK).
2. Copy `.env.example` to `.env`, add your key. Never commit `.env`.
3. Implement the provider in `runner/models/<name>.py` (an OpenAI-compatible
   client covers both OpenAI and OpenRouter) and register it in
   `runner/models/__init__.py`.
4. `python run.py --model gpt-5-mini --scenarios data/scenarios.csv`

## Data & schema

CSV columns and JSONL shape are fixed by the spec; see `docs/GDEF_SPEC.md`.
One CSV row = one (scenario, turn). Experiment B has 15 rows per scenario.
Regenerate the placeholder sample with `python scripts/make_sample_dataset.py`.

## Reproducibility

Re-runnable protocol + preserved artifacts + statistical stability (not
bit-identical: LLMs are non-deterministic). Pin model version, temperature 0.2,
seed; the run manifest records all parameters.

## Layout

```
run.py                 CLI
runner/                engine, io, reporting, schemas, controlled_lists, templates, models
scripts/               sample dataset generator
data/ outputs/ docs/   dataset, results (gitignored), the contract + PDF
CLAUDE.md              auto-loaded context for Claude Code
```
