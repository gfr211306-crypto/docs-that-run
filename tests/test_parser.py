from pathlib import Path

from docs_that_run.parser import parse_markdown, parse_markdown_text


FIXTURES = Path(__file__).parent / "fixtures"


def test_recognizes_marked_python_and_bash_blocks() -> None:
    blocks = parse_markdown(FIXTURES / "valid.md")

    assert [block.language for block in blocks] == ["python", "bash"]
    assert [block.line_number for block in blocks] == [3, 7]
    assert blocks[0].code == 'print("python")'
    assert blocks[1].code == 'echo "bash"'


def test_ignores_unmarked_and_unsupported_blocks() -> None:
    blocks = parse_markdown(FIXTURES / "mixed.md")

    assert len(blocks) == 2
    assert blocks[0].language == "python"
    assert blocks[0].line_number == 11
    assert blocks[0].code == 'print("marked python")'
    assert blocks[1].language == "bash"
    assert blocks[1].line_number == 15
    assert blocks[1].code == 'echo "marked bash"'


def test_returns_no_blocks_when_markers_are_absent() -> None:
    assert parse_markdown(FIXTURES / "no_markers.md") == []


def test_ignores_python_fence_inside_html_comment() -> None:
    blocks = parse_markdown(FIXTURES / "html_comments.md")

    assert all("commented python" not in block.code for block in blocks)


def test_ignores_bash_fence_inside_html_comment() -> None:
    blocks = parse_markdown(FIXTURES / "html_comments.md")

    assert all("commented bash" not in block.code for block in blocks)


def test_ignores_fence_inside_raw_html_block() -> None:
    blocks = parse_markdown(FIXTURES / "raw_html.md")

    assert all("inside raw html" not in block.code for block in blocks)


def test_recognizes_normal_fences_after_html_blocks() -> None:
    comment_blocks = parse_markdown(FIXTURES / "html_comments.md")
    raw_html_blocks = parse_markdown(FIXTURES / "raw_html.md")

    assert [block.language for block in comment_blocks] == ["python"]
    assert comment_blocks[0].code == 'print("real after comment")'
    assert [block.language for block in raw_html_blocks] == ["bash"]
    assert raw_html_blocks[0].code == 'echo "real after raw html"'


def test_supports_language_aliases_and_exact_marker_token() -> None:
    text = """\
```py dtr-run
print("py")
```
```sh dtr-run
echo sh
```
```python dtr-run-extra
print("ignored")
```
"""

    blocks = parse_markdown_text(text)

    assert [block.language for block in blocks] == ["python", "bash"]


def test_extracts_opening_fence_line_and_removes_fence_indent() -> None:
    text = """\
intro

  ```python dtr-run
  print("first")
    print("keeps two spaces")
  ```
"""

    block = parse_markdown_text(text)[0]

    assert block.line_number == 3
    assert block.code == 'print("first")\n  print("keeps two spaces")'


def test_unclosed_marked_fence_extends_to_end_of_document() -> None:
    blocks = parse_markdown_text("```python dtr-run\nprint('end')")

    assert len(blocks) == 1
    assert blocks[0].code == "print('end')"


def test_recognizes_marked_fence_inside_ordered_list_item() -> None:
    text = """\
10. Install
    ```bash dtr-run
    pip install foo
    ```
"""

    blocks = parse_markdown_text(text)

    assert len(blocks) == 1
    assert blocks[0].language == "bash"
    assert blocks[0].line_number == 2
    assert blocks[0].code == "pip install foo"


def test_inline_escaped_comment_opener_does_not_hide_later_fence() -> None:
    text = """\
Use \\<!-- in ordinary prose to describe an HTML comment opener.

```python dtr-run
print("still visible")
```
"""

    blocks = parse_markdown_text(text)

    assert len(blocks) == 1
    assert blocks[0].code == 'print("still visible")'


def test_dtr_run_marker_is_case_sensitive() -> None:
    text = """\
```python DTR-RUN
print("must be ignored")
```
"""

    assert parse_markdown_text(text) == []
