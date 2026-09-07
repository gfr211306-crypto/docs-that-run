#!/usr/bin/env python3
"""Run the bundled docs-that-run CLI from any working directory."""

from pathlib import Path
import sys


SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT))

from docs_that_run.cli import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
