from io import StringIO
from pathlib import Path

from docs_that_run.executor import ExecutionResult
from docs_that_run.parser import CodeBlock
from docs_that_run.reporter import report_result


def result(
    *,
    success: bool,
    return_code: int | None,
    source: Path,
    line_number: int,
) -> ExecutionResult:
    return ExecutionResult(
        block=CodeBlock(
            language="python",
            code="raise SystemExit(3)",
            line_number=line_number,
            source=source,
        ),
        success=success,
        return_code=return_code,
        stdout="",
        stderr="",
        duration=0.01,
    )


def test_failure_report_includes_exit_code() -> None:
    output = StringIO()

    report_result(
        result(
            success=False,
            return_code=3,
            source=Path("README.md"),
            line_number=42,
        ),
        index=1,
        total=1,
        stream=output,
    )

    assert "失敗 (exit code 3)" in output.getvalue()


def test_execution_report_includes_source_filename_and_line_number() -> None:
    output = StringIO()

    report_result(
        result(
            success=True,
            return_code=0,
            source=Path("docs/README.md"),
            line_number=42,
        ),
        index=1,
        total=1,
        stream=output,
    )

    assert "README.md:42" in output.getvalue()
