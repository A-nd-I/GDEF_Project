"""Console + file logging."""

from __future__ import annotations

import logging
from pathlib import Path


def setup_logging(log_path: str | Path | None = None,
                  level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger("governance_evals")
    logger.setLevel(level)
    logger.handlers.clear()

    fmt = logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s")

    console = logging.StreamHandler()
    console.setFormatter(fmt)
    logger.addHandler(console)

    if log_path:
        Path(log_path).parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(fmt)
        logger.addHandler(file_handler)

    return logger
