"""CLI entry point for the GDEF evaluation runner.

Examples
--------
# Offline  test (no API key):
python run.py --model mock-llm --scenarios data/scenarios_sample.csv

# Just estimate interaction counts:
python run.py --scenarios data/scenarios_sample.csv --dry-run

# Validate the dataset against the controlled lists:
python run.py --scenarios data/scenarios_sample.csv --validate

# One MVP model once the provider is wired up + key set:
python run.py --model gpt-5-mini --scenarios data/scenarios.csv
"""

from __future__ import annotations

import argparse
import sys
import uuid
from datetime import datetime

from runner.controlled_lists import validate_scenario
from runner.core import estimate_interactions, run_evaluation
from runner.io_utils import load_scenarios
from runner.logging_setup import setup_logging
from runner.models import get_provider
from runner.templates import DEFAULT_TEMPERATURE, SYSTEM_PROMPT

EXP_PREFIX = {"A": "A_", "B": "B_", "C": "C_"}


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="GDEF evaluation runner")
    p.add_argument("--model", default="mock-llm",
                   help="mock-llm | gpt-5-mini | qwen-3 (spec section 8)")
    p.add_argument("--scenarios", default="data/scenarios_sample.csv")
    p.add_argument("--output", default="outputs")
    p.add_argument("--experiment", default="all",
                   help="all, or filter by A / B / C (comma-separated)")
    p.add_argument("--reps", type=int, default=1)
    p.add_argument("--temperature", type=float, default=DEFAULT_TEMPERATURE)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--no-system-prompt", action="store_true",
                   help="Send no system prompt (test the model 'bare')")
    p.add_argument("--dry-run", action="store_true",
                   help="Print interaction counts; do not call the model")
    p.add_argument("--validate", action="store_true",
                   help="Validate dataset against controlled lists, then exit")
    return p.parse_args(argv)


def filter_experiments(scenarios, value):
    if value.strip().lower() == "all":
        return scenarios
    prefixes = tuple(EXP_PREFIX[c.strip().upper()] for c in value.split(",")
                     if c.strip().upper() in EXP_PREFIX)
    return [s for s in scenarios if s.experiment_type.startswith(prefixes)]


def main(argv=None) -> int:
    args = parse_args(argv)
    scenarios = filter_experiments(load_scenarios(args.scenarios), args.experiment)

    if args.validate:
        warns = [w for s in scenarios for w in validate_scenario(s)]
        if warns:
            print(f"{len(warns)} validation warning(s):")
            for w in warns:
                print("  -", w)
        else:
            print("All scenarios valid against the controlled lists.")
        return 1 if warns else 0

    if args.dry_run:
        print("Estimated interactions (turns x units x reps):")
        for k, v in estimate_interactions(scenarios, args.reps).items():
            print(f"  {k}: {v}")
        return 0

    run_id = f"RUN_{datetime.now():%Y%m%d_%H%M%S}_{uuid.uuid4().hex[:4]}"
    logger = setup_logging(log_path=f"{args.output}/{run_id}.log")
    logger.info("Run %s | model=%s | reps=%d", run_id, args.model, args.reps)

    provider = get_provider(args.model, temperature=args.temperature, seed=args.seed)
    system_prompt = None if args.no_system_prompt else SYSTEM_PROMPT
    manifest = run_evaluation(scenarios=scenarios, provider=provider,
                              output_dir=args.output, repetitions=args.reps,
                              run_id=run_id, logger=logger,
                              system_prompt=system_prompt)
    logger.info("Done. Total interactions: %d", manifest["total_interactions"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
