"""User-facing message catalogue for docs-that-run.

English is the default. Set ``DTR_LANG`` to ``zh-TW`` (``zh`` and ``zh_TW`` are
also accepted) for Traditional Chinese. Any other value falls back to English.

Only human-facing text lives here. The JSON report produced by ``--json`` is a
stable contract for other tools, so its field names are never translated, and
neither is the output of the code being executed.
"""

from __future__ import annotations

import os


EN: dict[str, str] = {
    # cli
    "cli.description": (
        "Run the Python and Bash code blocks in Markdown that you marked with "
        "dtr-run."
    ),
    "cli.help.files": "Markdown files to check. Defaults to README.md.",
    "cli.help.allow_exec": (
        "Allow the blocks marked dtr-run to run, after you confirm."
    ),
    "cli.help.yes": (
        "Skip the interactive confirmation and run immediately. Must be "
        "combined with --allow-exec. Intended for CI and other environments "
        "that cannot answer a prompt; use it only on documentation you trust."
    ),
    "cli.help.json": (
        "Write a JSON report to stdout for other tools or agents. "
        "Human-readable messages go to stderr instead, so stdout carries only "
        "the JSON."
    ),
    "error.yes_without_allow_exec": (
        "Error: --yes must be combined with --allow-exec. On its own it runs "
        "nothing."
    ),
    "error.not_markdown": "Error: only .md Markdown files are supported: {path}",
    "error.file_not_found": "Error: file not found: {path}",
    "error.read_failed": "Error: could not read {path}: {error}",
    "scan.only": (
        "🔒 Scan only. --allow-exec was not supplied, so nothing was executed."
    ),
    "exec.yes_notice": (
        "⚠️  --yes supplied: skipping the confirmation and running the code "
        "above."
    ),
    "exec.prompt": "⚠️  About to run the code above. Continue? (y/n): ",
    "exec.cancelled": "Execution cancelled.",
    # scan report
    "scan.file": "📄 Scanning: {path}",
    "scan.none": "No code blocks marked as executable were found.",
    "scan.found": "Found {count} executable code block{s}:",
    "scan.entry": "  [{index}] {language} (line {line})",
    "scan.about_to_run": "Code that will run:",
    "scan.empty_block": "      (empty block)",
    # execution report
    "result.header": "[{index}/{total}] Running {language} block ({location})",
    "result.success": "✅ Success ({duration:.2f}s)",
    "result.timeout": "❌ Timeout ({duration:.2f}s)",
    "result.failure": "❌ Failed (exit code {code}) ({duration:.2f}s)",
    "result.exit_code_unavailable": "unavailable",
    "result.stdout": "Output:",
    "result.stderr": "Errors:",
    # summary
    "summary.title": "📊 Summary",
    "summary.total": "Total: {count} block{s}",
    "summary.succeeded": "✅ Succeeded: {count}",
    "summary.failed": "❌ Failed: {count}",
    "summary.workdir": "📁 Working directory: {path}",
    "summary.workdir_note": "   (files created during the run are kept here)",
    # executor
    "exec.launch_failed": "Could not start the interpreter: {error}",
    "exec.timeout_message": (
        "Execution exceeded {timeout:g}s and was terminated."
    ),
    "exec.bash_not_found": (
        "No Bash interpreter found. Please install Bash and try again."
    ),
    "exec.unsupported_language": "Unsupported language: {language}",
}


ZH_TW: dict[str, str] = {
    # cli
    "cli.description": (
        "掃描 Markdown 中標記 dtr-run 的 Python 與 Bash 程式碼區塊。"
    ),
    "cli.help.files": "要掃描的 Markdown 檔案；未指定時使用 README.md",
    "cli.help.allow_exec": "允許在確認後執行標記 dtr-run 的區塊",
    "cli.help.yes": (
        "略過互動確認直接執行；必須與 --allow-exec 併用。"
        "供 CI 等無法互動的環境使用，只對你信任的文件使用。"
    ),
    "cli.help.json": (
        "以 JSON 輸出結果供其他工具或 agent 使用；"
        "人類可讀的訊息改送 stderr，stdout 只會有 JSON。"
    ),
    "error.yes_without_allow_exec": (
        "錯誤: --yes 必須與 --allow-exec 併用；單獨使用不會執行任何程式碼。"
    ),
    "error.not_markdown": "錯誤: 只支援 .md Markdown 檔案: {path}",
    "error.file_not_found": "錯誤: 找不到檔案: {path}",
    "error.read_failed": "錯誤: 無法讀取 {path}: {error}",
    "scan.only": "🔒 僅完成掃描；未提供 --allow-exec，不會執行任何程式碼。",
    "exec.yes_notice": "⚠️  已指定 --yes，略過互動確認並直接執行以上程式碼。",
    "exec.prompt": "⚠️  即將執行以上程式碼，是否繼續? (y/n): ",
    "exec.cancelled": "已取消執行。",
    # scan report
    "scan.file": "📄 掃描檔案: {path}",
    "scan.none": "找不到標記為可執行的程式碼區塊。",
    "scan.found": "找到 {count} 個標記為可執行的程式碼區塊:",
    "scan.entry": "  [{index}] {language} (第 {line} 行)",
    "scan.about_to_run": "即將執行的程式碼:",
    "scan.empty_block": "      (空白區塊)",
    # execution report
    "result.header": "[{index}/{total}] 執行 {language} 區塊 ({location})",
    "result.success": "✅ 成功 ({duration:.2f}s)",
    "result.timeout": "❌ Timeout ({duration:.2f}s)",
    "result.failure": "❌ 失敗 (exit code {code}) ({duration:.2f}s)",
    "result.exit_code_unavailable": "unavailable",
    "result.stdout": "輸出:",
    "result.stderr": "錯誤:",
    # summary
    "summary.title": "📊 執行摘要",
    "summary.total": "總共: {count} 個區塊",
    "summary.succeeded": "✅ 成功: {count}",
    "summary.failed": "❌ 失敗: {count}",
    "summary.workdir": "📁 工作目錄: {path}",
    "summary.workdir_note": "   (執行過程中產生的檔案保存在此目錄)",
    # executor
    "exec.launch_failed": "無法啟動執行器: {error}",
    "exec.timeout_message": "執行超過 {timeout:g} 秒，已中止。",
    "exec.bash_not_found": "找不到 Bash 執行器；請先在本機安裝 Bash。",
    "exec.unsupported_language": "不支援的語言: {language}",
}


CATALOGUES: dict[str, dict[str, str]] = {
    "en": EN,
    "zh-tw": ZH_TW,
}

_ZH_ALIASES = {"zh", "zh-tw", "zh_tw", "zh-hant", "zh_hant"}


def current_language() -> str:
    """Return the catalogue key selected by ``DTR_LANG``.

    The environment is read on every call so that a process can change language
    mid-run, which is what the tests rely on.
    """

    raw = os.environ.get("DTR_LANG", "").strip().lower()
    if raw in _ZH_ALIASES:
        return "zh-tw"
    return "en"


def t(key: str, **kwargs: object) -> str:
    """Look up ``key`` in the active catalogue and format it.

    Unknown keys raise :class:`KeyError` rather than returning the key, so a
    typo fails a test instead of shipping to a user.
    """

    catalogue = CATALOGUES[current_language()]
    try:
        template = catalogue[key]
    except KeyError:
        template = EN[key]
    return template.format(**kwargs)


def plural(count: int) -> str:
    """Return the English plural suffix; empty for other languages."""

    if current_language() != "en":
        return ""
    return "" if count == 1 else "s"
