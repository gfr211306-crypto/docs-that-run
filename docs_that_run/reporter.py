"""Terminal reporting for docs-that-run."""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Iterable, Optional, TextIO, Union

from .executor import ExecutionResult
from .messages import plural, t
from .parser import CodeBlock


SEPARATOR = "━" * 43


def report_scan(
    path: Union[str, Path],
    blocks: list[CodeBlock],
    *,
    stream: TextIO = sys.stdout,
) -> None:
    """Display executable blocks found in one Markdown file."""

    print(t("scan.file", path=path), file=stream)
    print(file=stream)

    count = len(blocks)
    if count == 0:
        print(t("scan.none"), file=stream)
        print(file=stream)
        return

    print(t("scan.found", count=count, s=plural(count)), file=stream)
    for index, block in enumerate(blocks, start=1):
        print(_scan_entry(index, block), file=stream)

    print(file=stream)
    print(t("scan.about_to_run"), file=stream)
    for index, block in enumerate(blocks, start=1):
        print(_scan_entry(index, block), file=stream)
        if block.code:
            for code_line in block.code.splitlines():
                print(f"      {code_line}", file=stream)
        else:
            print(t("scan.empty_block"), file=stream)
    print(file=stream)


def _scan_entry(index: int, block: CodeBlock) -> str:
    return t(
        "scan.entry",
        index=index,
        language=block.display_language,
        line=block.line_number,
    )


def build_json_report(
    blocks: list[CodeBlock],
    results: Optional[list[ExecutionResult]] = None,
    working_directory: Optional[Union[str, Path]] = None,
) -> dict:
    """Build a machine-readable report of one run.

    ``results`` is ``None`` for a scan-only run. The returned mapping is
    JSON-serialisable and is the contract other tools and agents consume, so
    ``schema_version`` is bumped whenever a field changes meaning.
    """

    from . import __version__

    executed_run = results is not None
    entries: list[dict] = []

    for index, block in enumerate(blocks, start=1):
        entry: dict = {
            "index": index,
            "file": str(block.source) if block.source is not None else None,
            "line": block.line_number,
            "language": block.language,
            "code": block.code,
            "executed": False,
        }
        if executed_run and index <= len(results or []):
            result = (results or [])[index - 1]
            entry.update(
                {
                    "executed": True,
                    "success": result.success,
                    "exit_code": result.return_code,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "duration_seconds": round(result.duration, 3),
                    "timed_out": result.timed_out,
                }
            )
        entries.append(entry)

    executed_entries = [entry for entry in entries if entry["executed"]]
    failed = [entry for entry in executed_entries if not entry["success"]]
    timed_out = [entry for entry in executed_entries if entry["timed_out"]]

    files: list[str] = []
    for entry in entries:
        name = entry["file"]
        if name is not None and name not in files:
            files.append(name)

    return {
        "schema_version": 1,
        "tool_version": __version__,
        "executed": executed_run,
        "files": files,
        "summary": {
            "total": len(entries),
            "executed": len(executed_entries),
            "succeeded": len(executed_entries) - len(failed),
            "failed": len(failed),
            "timed_out": len(timed_out),
        },
        "working_directory": (
            str(working_directory) if working_directory is not None else None
        ),
        "blocks": entries,
    }


def report_result(
    result: ExecutionResult,
    *,
    index: int,
    total: int,
    stream: TextIO = sys.stdout,
) -> None:
    """Display one block execution result."""

    block = result.block
    source_location = _source_location(block)
    print(SEPARATOR, file=stream)
    print(
        t(
            "result.header",
            index=index,
            total=total,
            language=block.display_language,
            location=source_location,
        ),
        file=stream,
    )
    print(SEPARATOR, file=stream)

    if result.success:
        print(t("result.success", duration=result.duration), file=stream)
    elif result.timed_out:
        print(t("result.timeout", duration=result.duration), file=stream)
    else:
        exit_code = (
            str(result.return_code)
            if result.return_code is not None
            else t("result.exit_code_unavailable")
        )
        print(
            t("result.failure", code=exit_code, duration=result.duration),
            file=stream,
        )

    if result.stdout:
        print(t("result.stdout"), file=stream)
        print(result.stdout.rstrip(), file=stream)
    if result.stderr:
        print(t("result.stderr"), file=stream)
        print(result.stderr.rstrip(), file=stream)
    print(file=stream)


def report_summary(
    results: Iterable[ExecutionResult],
    working_directory: Union[str, Path],
    *,
    stream: TextIO = sys.stdout,
) -> None:
    """Display the final execution summary and retained workspace path."""

    result_list = list(results)
    succeeded = sum(result.success for result in result_list)
    failed = len(result_list) - succeeded

    total = len(result_list)
    print(SEPARATOR, file=stream)
    print(t("summary.title"), file=stream)
    print(SEPARATOR, file=stream)
    print(t("summary.total", count=total, s=plural(total)), file=stream)
    print(t("summary.succeeded", count=succeeded), file=stream)
    print(t("summary.failed", count=failed), file=stream)
    print(file=stream)
    print(t("summary.workdir", path=Path(working_directory)), file=stream)
    print(t("summary.workdir_note"), file=stream)


def _source_location(block: CodeBlock) -> str:
    source_name = block.source.name if block.source is not None else "<unknown>"
    return f"{source_name}:{block.line_number}"
