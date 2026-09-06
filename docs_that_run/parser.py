"""Markdown fenced-code-block parser for docs-that-run."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


_OPENING_FENCE = re.compile(
    r"^(?P<indent> {0,3})(?P<fence>`{3,}|~{3,})(?P<info>[^\r\n]*)$"
)
_LIST_ITEM = re.compile(
    r"^(?P<indent> *)(?P<marker>[*+-]|\d{1,9}[.)])"
    r"(?P<spacing> {1,4})(?=\S)"
)
_RAW_HTML_TAG = re.compile(
    r"^</?[A-Za-z][A-Za-z0-9-]*(?:\s|/?>|$)"
)
_RAW_HTML_SCRIPT_TAG = re.compile(
    r"^<(?P<tag>script|pre|style|textarea)(?:\s|>|$)",
    re.IGNORECASE,
)
_HTML_DECLARATION = re.compile(r"^<![A-Z]")
_LANGUAGE_ALIASES = {
    "python": "python",
    "py": "python",
    "bash": "bash",
    "sh": "bash",
}


@dataclass(frozen=True)
class CodeBlock:
    """An executable fenced code block found in a Markdown document."""

    language: str
    code: str
    line_number: int
    source: Path | None = None

    @property
    def display_language(self) -> str:
        """Return the language name used in terminal reports."""

        return "Python" if self.language == "python" else "Bash"


def parse_markdown(path: str | Path) -> list[CodeBlock]:
    """Read *path* as UTF-8 Markdown and return marked executable blocks."""

    markdown_path = Path(path)
    text = markdown_path.read_text(encoding="utf-8")
    return parse_markdown_text(text, source=markdown_path)


def parse_markdown_text(
    text: str,
    *,
    source: str | Path | None = None,
) -> list[CodeBlock]:
    """Parse Markdown text and return supported blocks marked ``dtr-run``.

    Only fenced blocks whose first info-string token is one of ``python``,
    ``py``, ``bash``, or ``sh`` and whose remaining tokens include the exact
    marker ``dtr-run`` are returned.
    """

    source_path = Path(source) if source is not None else None
    blocks: list[CodeBlock] = []

    fence_character: str | None = None
    fence_length = 0
    fence_indent = 0
    opening_line = 0
    language: str | None = None
    is_executable = False
    code_lines: list[str] = []
    html_end_marker: str | None = None
    html_until_blank_line = False
    list_content_indent: int | None = None
    fence_container_indent = 0

    for line_number, line in enumerate(text.splitlines(), start=1):
        if fence_character is None:
            if html_end_marker is not None:
                if html_end_marker in line.lower():
                    html_end_marker = None
                continue

            if html_until_blank_line:
                if not line.strip():
                    html_until_blank_line = False
                continue

            html_block = _html_block_start(line)
            if html_block is not None:
                end_marker, search_from = html_block
                if end_marker is None:
                    html_until_blank_line = True
                elif end_marker not in line[search_from:].lower():
                    html_end_marker = end_marker
                continue

            item_indent = _list_item_content_indent(line, list_content_indent)
            if item_indent is not None:
                list_content_indent = item_indent
            elif line.strip() and list_content_indent is not None:
                line_indent = len(line) - len(line.lstrip(" "))
                if line_indent < list_content_indent:
                    list_content_indent = None

            fence_line = _remove_container_indent(line, list_content_indent)
            match = _OPENING_FENCE.match(fence_line)
            if match is None:
                continue

            fence = match.group("fence")
            info = match.group("info").strip()
            if fence.startswith("`") and "`" in info:
                continue

            info_tokens = info.split()
            raw_language = info_tokens[0].lower() if info_tokens else ""

            fence_character = fence[0]
            fence_length = len(fence)
            fence_container_indent = list_content_indent or 0
            fence_indent = fence_container_indent + len(match.group("indent"))
            opening_line = line_number
            language = _LANGUAGE_ALIASES.get(raw_language)
            is_executable = (
                language is not None and "dtr-run" in info_tokens[1:]
            )
            code_lines = []
            continue

        closing_line = _remove_container_indent(line, fence_container_indent)
        if _is_closing_fence(
            closing_line,
            fence_character,
            fence_length,
        ):
            if is_executable and language is not None:
                blocks.append(
                    CodeBlock(
                        language=language,
                        code="\n".join(code_lines),
                        line_number=opening_line,
                        source=source_path,
                    )
                )

            fence_character = None
            fence_length = 0
            fence_indent = 0
            fence_container_indent = 0
            opening_line = 0
            language = None
            is_executable = False
            code_lines = []
            continue

        if is_executable:
            code_lines.append(_remove_fence_indent(line, fence_indent))

    # CommonMark treats an unclosed fence as extending to end-of-document.
    if fence_character is not None and is_executable and language is not None:
        blocks.append(
            CodeBlock(
                language=language,
                code="\n".join(code_lines),
                line_number=opening_line,
                source=source_path,
            )
        )

    return blocks


def _html_block_start(line: str) -> tuple[str | None, int] | None:
    stripped = line.lstrip(" ")
    indent = len(line) - len(stripped)
    if indent > 3:
        return None

    lowered = stripped.lower()
    if stripped.startswith("<!--"):
        return "-->", len("<!--")
    script_match = _RAW_HTML_SCRIPT_TAG.match(stripped)
    if script_match is not None:
        return f"</{script_match.group('tag').lower()}>", script_match.end()
    if lowered.startswith("<?"):
        return "?>", len("<?")
    if lowered.startswith("<![cdata["):
        return "]]>", len("<![cdata[")
    if _HTML_DECLARATION.match(stripped):
        return ">", len("<!")
    if _RAW_HTML_TAG.match(stripped):
        return None, 0

    return None


def _list_item_content_indent(
    line: str,
    current_indent: int | None,
) -> int | None:
    match = _LIST_ITEM.match(line)
    if match is None:
        return None

    marker_indent = len(match.group("indent"))
    if current_indent is None:
        if marker_indent > 3:
            return None
    elif marker_indent > 3 and not (
        current_indent <= marker_indent <= current_indent + 3
    ):
        return None

    return (
        marker_indent
        + len(match.group("marker"))
        + len(match.group("spacing"))
    )


def _remove_container_indent(line: str, indent: int | None) -> str:
    if not indent:
        return line
    if not line.startswith(" " * indent):
        return line
    return line[indent:]


def _is_closing_fence(line: str, character: str, minimum_length: int) -> bool:
    stripped = line.lstrip(" ")
    indent = len(line) - len(stripped)
    if indent > 3 or not stripped.startswith(character * minimum_length):
        return False

    fence_size = 0
    for current_character in stripped:
        if current_character != character:
            break
        fence_size += 1

    return fence_size >= minimum_length and stripped[fence_size:].strip() == ""


def _remove_fence_indent(line: str, indent: int) -> str:
    removable = 0
    while removable < min(indent, len(line)) and line[removable] == " ":
        removable += 1
    return line[removable:]
