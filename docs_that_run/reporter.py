"""Terminal reporting for docs-that-run."""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Iterable, TextIO

from .executor import ExecutionResult
from .parser import CodeBlock


SEPARATOR = "━" * 43


def report_scan(
    path: str | Path,
    blocks: list[CodeBlock],
    *,
    stream: TextIO = sys.stdout,
) -> None:
    """Display executable blocks found in one Markdown file."""

    print(f"📄 掃描檔案: {path}", file=stream)
    print(file=stream)

    count = len(blocks)
    if count == 0:
        print("找不到標記為可執行的程式碼區塊。", file=stream)
        print(file=stream)
        return

    print(f"找到 {count} 個標記為可執行的程式碼區塊:", file=stream)
    for index, block in enumerate(blocks, start=1):
        print(
            f"  [{index}] {block.display_language} (第 {block.line_number} 行)",
            file=stream,
        )

    print(file=stream)
    print("即將執行的程式碼:", file=stream)
    for index, block in enumerate(blocks, start=1):
        print(
            f"  [{index}] {block.display_language} (第 {block.line_number} 行)",
            file=stream,
        )
        if block.code:
            for code_line in block.code.splitlines():
                print(f"      {code_line}", file=stream)
        else:
            print("      (空白區塊)", file=stream)
    print(file=stream)


def report_result(
    result: ExecutionResult,
    *,
    index: int,
    total: int,
    stream: TextIO = sys.stdout,
) -> None:
    """Display one block execution result."""

    block = result.block
    print(SEPARATOR, file=stream)
    print(
        f"[{index}/{total}] 執行 {block.display_language} 區塊 "
        f"(第 {block.line_number} 行)",
        file=stream,
    )
    print(SEPARATOR, file=stream)

    if result.success:
        print(f"✅ 成功 ({result.duration:.2f}s)", file=stream)
    elif result.timed_out:
        print(f"❌ Timeout ({result.duration:.2f}s)", file=stream)
    else:
        print(f"❌ 失敗 ({result.duration:.2f}s)", file=stream)

    if result.stdout:
        print("輸出:", file=stream)
        print(result.stdout.rstrip(), file=stream)
    if result.stderr:
        print("錯誤:", file=stream)
        print(result.stderr.rstrip(), file=stream)
    print(file=stream)


def report_summary(
    results: Iterable[ExecutionResult],
    working_directory: str | Path,
    *,
    stream: TextIO = sys.stdout,
) -> None:
    """Display the final execution summary and retained workspace path."""

    result_list = list(results)
    succeeded = sum(result.success for result in result_list)
    failed = len(result_list) - succeeded

    print(SEPARATOR, file=stream)
    print("📊 執行摘要", file=stream)
    print(SEPARATOR, file=stream)
    print(f"總共: {len(result_list)} 個區塊", file=stream)
    print(f"✅ 成功: {succeeded}", file=stream)
    print(f"❌ 失敗: {failed}", file=stream)
    print(file=stream)
    print(f"📁 工作目錄: {Path(working_directory)}", file=stream)
    print("   (執行過程中產生的檔案保存在此目錄)", file=stream)
