from pathlib import Path
import time

import pytest

from docs_that_run.executor import (
    DEFAULT_TIMEOUT,
    create_working_directory,
    execute_block,
    find_bash,
)
from docs_that_run.parser import CodeBlock


def block(language: str, code: str) -> CodeBlock:
    return CodeBlock(language=language, code=code, line_number=1)


def test_default_timeout_is_30_seconds() -> None:
    assert DEFAULT_TIMEOUT == 30.0


def test_executes_simple_python_block(tmp_path: Path) -> None:
    result = execute_block(
        block("python", 'print("hello from python")'),
        tmp_path,
    )

    assert result.success is True
    assert result.return_code == 0
    assert result.stdout == "hello from python\n"
    assert result.stderr == ""
    assert result.duration >= 0


def test_executes_simple_bash_block(tmp_path: Path) -> None:
    if find_bash() is None:
        pytest.skip("Bash is not installed")

    result = execute_block(
        block("bash", 'printf "%s\\n" "hello from bash"'),
        tmp_path,
    )

    assert result.success is True
    assert result.return_code == 0
    assert result.stdout == "hello from bash\n"
    assert result.stderr == ""


def test_captures_python_failure(tmp_path: Path) -> None:
    result = execute_block(
        block("python", 'raise RuntimeError("expected failure")'),
        tmp_path,
    )

    assert result.success is False
    assert result.return_code != 0
    assert "RuntimeError: expected failure" in result.stderr


def test_records_stdout_and_stderr(tmp_path: Path) -> None:
    code = """\
import sys
print("standard output")
print("standard error", file=sys.stderr)
"""

    result = execute_block(block("python", code), tmp_path)

    assert result.success is True
    assert result.stdout == "standard output\n"
    assert result.stderr == "standard error\n"


def test_interrupts_block_after_timeout(tmp_path: Path) -> None:
    started_at = time.monotonic()
    result = execute_block(
        block("python", "import time; time.sleep(5)"),
        tmp_path,
        timeout=0.1,
    )
    elapsed = time.monotonic() - started_at

    assert result.success is False
    assert result.timed_out is True
    assert "已中止" in result.stderr
    assert elapsed < 3


def test_blocks_share_files_in_common_working_directory(
    tmp_path: Path,
) -> None:
    write_result = execute_block(
        block(
            "python",
            'from pathlib import Path; Path("shared.txt").write_text("shared")',
        ),
        tmp_path,
    )
    read_result = execute_block(
        block(
            "python",
            'from pathlib import Path; print(Path("shared.txt").read_text())',
        ),
        tmp_path,
    )

    assert write_result.success is True
    assert read_result.success is True
    assert read_result.stdout == "shared\n"


def test_shell_cd_and_export_state_are_not_preserved(tmp_path: Path) -> None:
    if find_bash() is None:
        pytest.skip("Bash is not installed")

    first = execute_block(
        block(
            "bash",
            'mkdir child && cd child && export DTR_VALUE="not-shared"',
        ),
        tmp_path,
    )
    second = execute_block(
        block(
            "bash",
            'printf "%s" "${DTR_VALUE-unset}" > shell_state.txt',
        ),
        tmp_path,
    )

    assert first.success is True
    assert second.success is True
    assert (tmp_path / "shell_state.txt").read_text() == "unset"
    assert not (tmp_path / "child" / "shell_state.txt").exists()


def test_create_working_directory_preserves_directory() -> None:
    workdir = create_working_directory()

    try:
        assert workdir.is_dir()
        assert workdir.name.startswith("dtr_")
    finally:
        workdir.rmdir()
