# Governance Pressure Testing runner

Sends a list of prompts (from a CSV) to a model, one by one, and stores the
responses in files so the governance/policy team can review them by hand.

**Main rule:** the script only *collects evidence*. It does not decide whether
drift, severity or risk occurred. Those fields are left empty for people to fill in.

Experiment type: `E_GOVERNANCE_PRESSURE_TESTING`.

## Files

- `governance_pressure_runner.py` — the script.
- `data/pressure_tests_30.csv` — 30 scenarios (15 Colombia / 15 Brazil), one
  pressure prompt per row, covering 7 pressure types.
- `.env` — configuration (model, endpoint, key, filters).
- `requirements.txt` — only needed if you want the findings matrix as `.xlsx`.
- `examples/` — sample outputs generated with `--dry-run`.
- `outputs/` — where the results of real runs are written.

## Configuration

All configuration lives in `.env`. What you normally change:

```
MODEL=gpt-oss:20b
API_KEY=ollama
BASE_URL=http://localhost:11434/v1
```

- **Local Ollama:** the default values above.
- **OpenAI:** `BASE_URL=https://api.openai.com/v1`, `API_KEY=sk-...`, `MODEL=gpt-4o-mini`.

Do not commit `.env` to GitHub, since it holds the key.

## How to run it

```bash
pip install -r requirements.txt            # only if you use FINDINGS_FORMAT=xlsx
py -m pip install openpyxl                 # same thing, on Windows

python governance_pressure_runner.py --dry-run     # test the flow without calling the model
python governance_pressure_runner.py               # real run, all 30 prompts
python governance_pressure_runner.py --country Brazil   # Brazil only
python governance_pressure_runner.py --num 4            # quick test, first 4 prompts
```

Anything in `.env` can be overridden on the command line
(`--model`, `--base-url`, `--input`, `--country`, `--language`, `--num`, etc.).

## What it generates (in `outputs/`)

1. **raw_outputs.csv** — the raw response of each prompt with its data:
   `run_id, scenario_id, base_question_id, country, jurisdiction, language,
   domain, user_role, experiment_type, turn_number, pressure_type, prompt,
   response, model, timestamp, status` (+ `latency_seconds, completion_tokens,
   finish_reason, error`).
2. **findings_matrix.xlsx** — the automatic fields above + the **empty** review
   columns: `drift_observed, drift_type, severity_score, evidence_quote,
   reviewer_notes, reviewer, review_date`. The script never fills these in.
   (If you prefer CSV: `FINDINGS_FORMAT=csv`.)
3. **run_summary.csv** — run summary: `run_id, input_file, experiment_type,
   model, total_prompts, successful_calls, failed_calls, started_at, finished_at`.

`raw_outputs.csv` is saved row by row, so if you interrupt the run (Ctrl+C)
whatever was already answered stays saved.

## Architecture
 
The runner is a small, linear pipeline with one guiding principle:
**the machine collects, humans interpret.** It never scores or judges responses.
 
Flow of a run:
 
```
.env / CLI  ->  read CSV  ->  filter  ->  for each prompt:  call model  ->  write raw row
                                                                              |
                                          (at the end)  ->  findings matrix + run summary
```
 
Key design choices:
 
- **Configuration is external.** Model, endpoint and filters live in `.env`
  (or CLI flags). The code has no hard-coded model, so switching providers
  never means editing the script.
- **Stateless calls.** Each prompt is sent in its own clean conversation, with
  no memory between prompts, so one answer can't influence the next. This keeps
  every scenario independent and comparable.
- **Provider-agnostic.** It talks to any OpenAI-compatible endpoint (Ollama,
  OpenAI, others) through the same `/chat/completions` call, so the same script
  works across backends.
- **Evidence vs. judgment, kept separate.** `raw_outputs.csv` holds the facts
  (prompt, response, timing, status). The findings matrix adds empty review
  columns that only the governance team fills in. The script writes the
  automatic fields and never touches the review ones.
- **Fault tolerant.** Rows are written to `raw_outputs.csv` as they arrive, so
  an interrupted run keeps what it already collected; the findings matrix and
  summary are written on exit (including after Ctrl+C).
- **Fails early and clearly.** Missing input file, no valid prompts, or a bad
  filter stop the run with a readable message instead of a deep stack trace.
In code terms, each stage is a small function: `read_scenarios` (load CSV),
`select` (apply filters), `call_model` (one API call), `build_raw_row` /
`write_findings` / `write_summary` (outputs), all orchestrated by `run`, with
`build_config` resolving `.env` + CLI into a single config.