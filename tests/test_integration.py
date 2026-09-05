from io import StringIO
from pathlib import Path

import pytest

from docs_that_run import cli
from docs_that_run.executor import create_working_directory, execute_block, find_bash
from docs_that_run.parser import parse_markdown
from docs_that_run.reporter import report_result, report_summary


EXAMPLE = Path(__file__).parents[1] / "examples" / "sample_readme.md"


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


def test_cli_rejects_non_markdown_files(tmp_path: Path) -> None:
    text_file = tmp_path / "example.txt"
    text_file.write_text("text", encoding="utf-8")
    errors = StringIO()

    exit_code = cli.main([str(text_file)], stderr=errors)

    assert exit_code == 2
    assert "只支援 .md" in errors.getvalue()
