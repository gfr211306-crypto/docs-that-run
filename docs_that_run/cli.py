"""Command-line interface for docs-that-run."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Callable, Optional, Sequence, TextIO

from .executor import create_working_directory, execute_block
from .messages import t
from .parser import CodeBlock, parse_markdown
from .reporter import (
    build_json_report,
    report_result,
    report_scan,
    report_summary,
)


InputFunction = Callable[[str], str]


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dtr",
        allow_abbrev=False,
        description=t("cli.description"),
    )
    parser.add_argument(
        "files",
        nargs="*",
        metavar="FILE",
        help=t("cli.help.files"),
    )
    parser.add_argument(
        "--allow-exec",
        action="store_true",
        help=t("cli.help.allow_exec"),
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help=t("cli.help.yes"),
    )
    parser.add_argument(
        "--json",
        dest="json_output",
        action="store_true",
        help=t("cli.help.json"),
    )
    return parser


def main(
    argv: Optional[Sequence[str]] = None,
    *,
    input_func: InputFunction = input,
    stdout: TextIO = sys.stdout,
    stderr: TextIO = sys.stderr,
) -> int:
    """Run the CLI and return a process exit code."""

    _configure_utf8(sys.stdout)
    _configure_utf8(sys.stderr)
    arguments = build_argument_parser().parse_args(argv)

    if arguments.yes and not arguments.allow_exec:
        print(t("error.yes_without_allow_exec"), file=stderr)
        return 2

    # With --json, stdout carries the JSON document and nothing else, so every
    # human-facing message goes to stderr instead.
    human = stderr if arguments.json_output else stdout

    paths = [Path(name) for name in arguments.files] or [Path("README.md")]

    all_blocks: list[CodeBlock] = []
    for path in paths:
        if path.suffix.lower() != ".md":
            print(t("error.not_markdown", path=path), file=stderr)
            return 2
        if not path.is_file():
            print(t("error.file_not_found", path=path), file=stderr)
            return 2

        try:
            blocks = parse_markdown(path)
        except (OSError, UnicodeError) as error:
            print(t("error.read_failed", path=path, error=error), file=stderr)
            return 2

        report_scan(path, blocks, stream=human)
        all_blocks.extend(blocks)

    def emit_json(
        results: Optional[list] = None,
        working_directory: Optional[Path] = None,
    ) -> None:
        """Write the machine-readable report when --json was requested."""

        if not arguments.json_output:
            return
        report = build_json_report(all_blocks, results, working_directory)
        print(
            json.dumps(report, ensure_ascii=False, indent=2),
            file=stdout,
        )

    if not all_blocks:
        emit_json()
        return 0

    if not arguments.allow_exec:
        print(t("scan.only"), file=human)
        emit_json()
        return 0

    if arguments.yes:
        print(t("exec.yes_notice"), file=human)
    else:
        prompt = t("exec.prompt")
        try:
            if arguments.json_output:
                # Keep stdout free of anything but JSON.
                print(prompt, end="", file=human)
                answer = input_func("")
            else:
                answer = input_func(prompt)
        except (EOFError, KeyboardInterrupt):
            print("\n" + t("exec.cancelled"), file=human)
            emit_json()
            return 0

        if answer.strip().lower() not in {"y", "yes"}:
            print(t("exec.cancelled"), file=human)
            emit_json()
            return 0

    working_directory = create_working_directory()
    results = []
    total = len(all_blocks)
    for index, block in enumerate(all_blocks, start=1):
        result = execute_block(block, working_directory)
        results.append(result)
        report_result(
            result,
            index=index,
            total=total,
            stream=human,
        )

    report_summary(results, working_directory, stream=human)
    emit_json(results, working_directory)
    return 0 if all(result.success for result in results) else 1


def _configure_utf8(stream: TextIO) -> None:
    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure is None:
        return
    try:
        reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError, ValueError):
        pass


if __name__ == "__main__":
    raise SystemExit(main())
