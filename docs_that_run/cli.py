"""Command-line interface for docs-that-run."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Callable, Optional, Sequence, TextIO

from .executor import create_working_directory, execute_block
from .parser import CodeBlock, parse_markdown
from .reporter import report_result, report_scan, report_summary


InputFunction = Callable[[str], str]


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dtr",
        allow_abbrev=False,
        description=(
            "掃描 Markdown 中標記 dtr-run 的 Python 與 Bash 程式碼區塊。"
        ),
    )
    parser.add_argument(
        "files",
        nargs="*",
        metavar="FILE",
        help="要掃描的 Markdown 檔案；未指定時使用 README.md",
    )
    parser.add_argument(
        "--allow-exec",
        action="store_true",
        help="允許在確認後執行標記 dtr-run 的區塊",
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
    paths = [Path(name) for name in arguments.files] or [Path("README.md")]

    all_blocks: list[CodeBlock] = []
    for path in paths:
        if path.suffix.lower() != ".md":
            print(f"錯誤: 只支援 .md Markdown 檔案: {path}", file=stderr)
            return 2
        if not path.is_file():
            print(f"錯誤: 找不到檔案: {path}", file=stderr)
            return 2

        try:
            blocks = parse_markdown(path)
        except (OSError, UnicodeError) as error:
            print(f"錯誤: 無法讀取 {path}: {error}", file=stderr)
            return 2

        report_scan(path, blocks, stream=stdout)
        all_blocks.extend(blocks)

    if not all_blocks:
        return 0

    if not arguments.allow_exec:
        print(
            "🔒 僅完成掃描；未提供 --allow-exec，不會執行任何程式碼。",
            file=stdout,
        )
        return 0

    try:
        answer = input_func(
            "⚠️  即將執行以上程式碼，是否繼續? (y/n): "
        )
    except (EOFError, KeyboardInterrupt):
        print("\n已取消執行。", file=stdout)
        return 0

    if answer.strip().lower() not in {"y", "yes"}:
        print("已取消執行。", file=stdout)
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
            stream=stdout,
        )

    report_summary(results, working_directory, stream=stdout)
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
