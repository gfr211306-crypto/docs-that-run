"""Language selection for user-facing messages."""

from __future__ import annotations

import io

import pytest

from docs_that_run.cli import main
from docs_that_run.messages import current_language, plural, t


@pytest.fixture(autouse=True)
def clear_language(monkeypatch: pytest.MonkeyPatch) -> None:
    """Start every test from the default language."""

    monkeypatch.delenv("DTR_LANG", raising=False)


def test_default_language_is_english() -> None:
    assert current_language() == "en"
    assert t("summary.title") == "📊 Summary"


@pytest.mark.parametrize("value", ["zh-TW", "zh", "zh_TW", "ZH-tw", " zh-tw "])
def test_chinese_aliases_select_traditional_chinese(
    monkeypatch: pytest.MonkeyPatch,
    value: str,
) -> None:
    monkeypatch.setenv("DTR_LANG", value)
    assert current_language() == "zh-tw"
    assert t("summary.title") == "📊 執行摘要"


@pytest.mark.parametrize("value", ["", "fr", "klingon", "en"])
def test_unknown_languages_fall_back_to_english(
    monkeypatch: pytest.MonkeyPatch,
    value: str,
) -> None:
    monkeypatch.setenv("DTR_LANG", value)
    assert current_language() == "en"
    assert t("summary.title") == "📊 Summary"


def test_english_pluralises_but_chinese_does_not(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert plural(1) == ""
    assert plural(2) == "s"

    monkeypatch.setenv("DTR_LANG", "zh-TW")
    assert plural(1) == ""
    assert plural(2) == ""


def test_placeholders_are_formatted() -> None:
    assert t("scan.file", path="README.md") == "📄 Scanning: README.md"


def test_scan_output_is_english_by_default(tmp_path) -> None:
    document = tmp_path / "README.md"
    document.write_text(
        '# demo\n\n```python dtr-run\nprint("hi")\n```\n',
        encoding="utf-8",
    )

    output = io.StringIO()
    exit_code = main([str(document)], stdout=output, stderr=output)

    assert exit_code == 0
    text = output.getvalue()
    assert "Scanning:" in text
    assert "Found 1 executable code block:" in text
    assert "--allow-exec was not supplied" in text


def test_scan_output_honours_dtr_lang(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DTR_LANG", "zh-TW")
    document = tmp_path / "README.md"
    document.write_text(
        '# demo\n\n```python dtr-run\nprint("hi")\n```\n',
        encoding="utf-8",
    )

    output = io.StringIO()
    exit_code = main([str(document)], stdout=output, stderr=output)

    assert exit_code == 0
    text = output.getvalue()
    assert "掃描檔案" in text
    assert "找到 1 個標記為可執行的程式碼區塊" in text
    assert "未提供 --allow-exec" in text
