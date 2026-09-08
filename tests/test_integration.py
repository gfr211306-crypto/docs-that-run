from io import StringIO
import json
from pathlib import Path

import pytest

from docs_that_run import cli
from docs_that_run.executor import create_working_directory, execute_block, find_bash
from docs_that_run.parser import parse_markdown
from docs_that_run.reporter import report_result, report_summary


EXAMPLE = Path(__file__).parents[1] / "examples" / "sample_readme.md"
README = Path(__file__).parents[1] / "README.md"


@pytest.mark.parametrize(
    "abbreviation",
    ["--a", "--allow", "--allow-e"],
)
def test_cli_rejects_allow_exec_abbreviations(
    abbreviation: str,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("executor must not be reached")

    monkeypatch.setattr(cli, "create_working_directory", forbidden)
    monkeypatch.setattr(cli, "execute_block", forbidden)

    with pytest.raises(SystemExit) as error:
        cli.main(
            [str(EXAMPLE), abbreviation],
            input_func=lambda _: pytest.fail("confirmation must not be reached"),
        )

    assert error.value.code == 2
    assert f"unrecognized arguments: {abbreviation}" in capsys.readouterr().err


def test_example_markdown_executes_in_order_and_reports_results() -> None:
    blocks = parse_markdown(EXAMPLE)
    assert [block.language for block in blocks] == [
        "python",
        "bash",
        "python",
        "python",
    ]

    if find_bash() is None:
        return

    workdir = create_working_directory()
    output = StringIO()
    try:
        results = []
        for index, current_block in enumerate(blocks, start=1):
            result = execute_block(current_block, workdir)
            results.append(result)
            report_result(
                result,
                index=index,
                total=len(blocks),
                stream=output,
            )
        report_summary(results, workdir, stream=output)

        assert all(result.success for result in results)
        assert results[2].stdout == "Read from shared file: Hello from bash\n"
        report = output.getvalue()
        assert "執行摘要" in report
        assert "✅ 成功: 4" in report
        assert f"📁 工作目錄: {workdir}" in report
    finally:
        for child in workdir.iterdir():
            if child.is_file():
                child.unlink()
        workdir.rmdir()


def test_readme_contains_no_executable_blocks() -> None:
    assert parse_markdown(README) == []


def test_cli_does_not_execute_without_allow_exec(tmp_path: Path) -> None:
    marker = tmp_path / "must-not-exist.txt"
    markdown = tmp_path / "safe.md"
    markdown.write_text(
        "```python dtr-run\n"
        f"from pathlib import Path; Path({str(marker)!r}).write_text('ran')\n"
        "```\n",
        encoding="utf-8",
    )
    output = StringIO()

    exit_code = cli.main([str(markdown)], stdout=output)

    assert exit_code == 0
    assert not marker.exists()
    assert "未提供 --allow-exec" in output.getvalue()


def test_cli_requires_confirmation_even_with_allow_exec(
    tmp_path: Path,
) -> None:
    marker = tmp_path / "must-not-exist.txt"
    markdown = tmp_path / "safe.md"
    markdown.write_text(
        "```python dtr-run\n"
        f"from pathlib import Path; Path({str(marker)!r}).write_text('ran')\n"
        "```\n",
        encoding="utf-8",
    )
    output = StringIO()

    exit_code = cli.main(
        [str(markdown), "--allow-exec"],
        input_func=lambda _: "n",
        stdout=output,
    )

    assert exit_code == 0
    assert not marker.exists()
    assert "已取消執行" in output.getvalue()


def test_cli_executes_after_flag_and_confirmation(tmp_path: Path) -> None:
    markdown = tmp_path / "success.md"
    markdown.write_text(
        "```python dtr-run\nprint('integration success')\n```\n",
        encoding="utf-8",
    )
    output = StringIO()

    exit_code = cli.main(
        [str(markdown), "--allow-exec"],
        input_func=lambda _: "y",
        stdout=output,
    )

    assert exit_code == 0
    report = output.getvalue()
    assert "integration success" in report
    assert "✅ 成功: 1" in report


def test_cli_returns_failure_when_a_block_fails(tmp_path: Path) -> None:
    markdown = tmp_path / "failure.md"
    markdown.write_text(
        "```python dtr-run\nraise SystemExit(7)\n```\n",
        encoding="utf-8",
    )
    output = StringIO()

    exit_code = cli.main(
        [str(markdown), "--allow-exec"],
        input_func=lambda _: "y",
        stdout=output,
    )

    assert exit_code == 1
    assert "❌ 失敗: 1" in output.getvalue()


def test_cli_yes_without_allow_exec_is_rejected(tmp_path: Path) -> None:
    marker = tmp_path / "must-not-exist.txt"
    markdown = tmp_path / "safe.md"
    markdown.write_text(
        "```python dtr-run\n"
        f"from pathlib import Path; Path({str(marker)!r}).write_text('ran')\n"
        "```\n",
        encoding="utf-8",
    )
    errors = StringIO()

    exit_code = cli.main(
        [str(markdown), "--yes"],
        input_func=lambda _: pytest.fail("confirmation must not be reached"),
        stdout=StringIO(),
        stderr=errors,
    )

    assert exit_code == 2
    assert not marker.exists()
    assert "--yes 必須與 --allow-exec 併用" in errors.getvalue()


def test_cli_yes_skips_confirmation_and_executes(tmp_path: Path) -> None:
    markdown = tmp_path / "ci.md"
    markdown.write_text(
        "```python dtr-run\nprint('non interactive success')\n```\n",
        encoding="utf-8",
    )
    output = StringIO()

    exit_code = cli.main(
        [str(markdown), "--allow-exec", "--yes"],
        input_func=lambda _: pytest.fail("confirmation must not be reached"),
        stdout=output,
    )

    assert exit_code == 0
    report = output.getvalue()
    assert "略過互動確認" in report
    assert "non interactive success" in report
    assert "✅ 成功: 1" in report


def test_cli_yes_still_ignores_unmarked_blocks(tmp_path: Path) -> None:
    marker = tmp_path / "must-not-exist.txt"
    markdown = tmp_path / "unmarked.md"
    markdown.write_text(
        "```python\n"
        f"from pathlib import Path; Path({str(marker)!r}).write_text('ran')\n"
        "```\n",
        encoding="utf-8",
    )
    output = StringIO()

    exit_code = cli.main(
        [str(markdown), "--allow-exec", "--yes"],
        input_func=lambda _: pytest.fail("confirmation must not be reached"),
        stdout=output,
    )

    assert exit_code == 0
    assert not marker.exists()
    assert "找不到標記為可執行的程式碼區塊" in output.getvalue()


def test_cli_cancels_when_confirmation_input_is_unavailable(
    tmp_path: Path,
) -> None:
    """Without --yes a non-interactive run must cancel instead of executing."""

    marker = tmp_path / "must-not-exist.txt"
    markdown = tmp_path / "safe.md"
    markdown.write_text(
        "```python dtr-run\n"
        f"from pathlib import Path; Path({str(marker)!r}).write_text('ran')\n"
        "```\n",
        encoding="utf-8",
    )

    def no_stdin(_: str) -> str:
        raise EOFError

    output = StringIO()

    exit_code = cli.main(
        [str(markdown), "--allow-exec"],
        input_func=no_stdin,
        stdout=output,
    )

    assert exit_code == 0
    assert not marker.exists()
    assert "已取消執行" in output.getvalue()


def test_json_scan_only_report_is_machine_readable(tmp_path: Path) -> None:
    markdown = tmp_path / "scan.md"
    markdown.write_text(
        "```python dtr-run\nprint('one')\n```\n",
        encoding="utf-8",
    )
    output = StringIO()
    errors = StringIO()

    exit_code = cli.main(
        [str(markdown), "--json"],
        stdout=output,
        stderr=errors,
    )

    assert exit_code == 0
    report = json.loads(output.getvalue())
    assert report["schema_version"] == 1
    assert report["executed"] is False
    assert report["summary"] == {
        "total": 1,
        "executed": 0,
        "succeeded": 0,
        "failed": 0,
        "timed_out": 0,
    }
    block = report["blocks"][0]
    assert block["language"] == "python"
    assert block["line"] == 1
    assert block["code"] == "print('one')"
    assert block["executed"] is False
    # Human-readable text must never contaminate the JSON on stdout.
    assert "掃描檔案" in errors.getvalue()


def test_json_report_carries_failure_details_for_diagnosis(
    tmp_path: Path,
) -> None:
    markdown = tmp_path / "broken.md"
    markdown.write_text(
        "```bash dtr-run\necho ok\n```\n"
        "\n"
        "```python dtr-run\n"
        "import sys; print('boom', file=sys.stderr); raise SystemExit(3)\n"
        "```\n",
        encoding="utf-8",
    )
    output = StringIO()
    errors = StringIO()

    exit_code = cli.main(
        [str(markdown), "--allow-exec", "--yes", "--json"],
        input_func=lambda _: pytest.fail("confirmation must not be reached"),
        stdout=output,
        stderr=errors,
    )

    assert exit_code == 1
    report = json.loads(output.getvalue())
    assert report["executed"] is True
    assert report["summary"]["failed"] == 1
    assert report["working_directory"]

    failed = [block for block in report["blocks"] if not block["success"]]
    assert len(failed) == 1
    assert failed[0]["language"] == "python"
    assert failed[0]["exit_code"] == 3
    assert "boom" in failed[0]["stderr"]
    assert failed[0]["timed_out"] is False


def test_json_report_records_a_cancelled_run(tmp_path: Path) -> None:
    markdown = tmp_path / "cancelled.md"
    markdown.write_text(
        "```python dtr-run\nprint('never')\n```\n",
        encoding="utf-8",
    )
    output = StringIO()

    exit_code = cli.main(
        [str(markdown), "--allow-exec", "--json"],
        input_func=lambda _: "n",
        stdout=output,
        stderr=StringIO(),
    )

    assert exit_code == 0
    report = json.loads(output.getvalue())
    assert report["executed"] is False
    assert report["blocks"][0]["executed"] is False


def test_cli_rejects_non_markdown_files(tmp_path: Path) -> None:
    text_file = tmp_path / "example.txt"
    text_file.write_text("text", encoding="utf-8")
    errors = StringIO()

    exit_code = cli.main([str(text_file)], stderr=errors)

    assert exit_code == 2
    assert "只支援 .md" in errors.getvalue()
