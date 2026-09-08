"""docs-that-run package."""

from .executor import DEFAULT_TIMEOUT, ExecutionResult, create_working_directory, execute_block
from .parser import CodeBlock, parse_markdown, parse_markdown_text

__all__ = [
    "CodeBlock",
    "DEFAULT_TIMEOUT",
    "ExecutionResult",
    "create_working_directory",
    "execute_block",
    "parse_markdown",
    "parse_markdown_text",
]

__version__ = "0.1.3"
