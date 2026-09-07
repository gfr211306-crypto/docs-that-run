# docs-that-run

[![CI](https://github.com/gfr211306-crypto/docs-that-run/actions/workflows/ci.yml/badge.svg)](https://github.com/gfr211306-crypto/docs-that-run/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/docs-that-run.svg)](https://pypi.org/project/docs-that-run/)
[![Python Version](https://img.shields.io/pypi/pyversions/docs-that-run.svg)](https://pypi.org/project/docs-that-run/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Validate code examples in your documentation by actually running them.**

`docs-that-run` parses Markdown files and executes explicitly marked Python and Bash code blocks to verify your documentation stays accurate. It only runs code you explicitly mark with `dtr-run`, and only after you confirm.

## Quick Start

```bash
pip install docs-that-run
```

Mark executable code blocks in your Markdown:

````markdown
```python dtr-run
print("This will be validated")
```
````

Scan your documentation (shows what would run, but doesn't execute):

```bash
dtr README.md
```

Actually execute the marked blocks (requires confirmation):

```bash
dtr README.md --allow-exec
```

## How It Works

1. **Opt-in only**: Only code blocks marked with `dtr-run` are recognized
2. **Scan by default**: Without `--allow-exec`, dtr only reports what it found
3. **Explicit confirmation**: With `--allow-exec`, you must type `y` to proceed
4. **Sequential execution**: Blocks run in document order, sharing a temp directory
5. **Clear reporting**: See stdout, stderr, timing, and success/failure for each block

## Marking Syntax

Add `dtr-run` after the language identifier:

The `dtr-run` marker is case-sensitive and must be lowercase.

````markdown
```python dtr-run
print("Hello from docs-that-run")
```

```bash dtr-run
echo "This will be executed" > output.txt
```

```python dtr-run
# Blocks share a working directory
with open("output.txt") as f:
    print(f.read())
```
````

Blocks without `dtr-run` are ignored:

````markdown
```python
# This is just documentation, won't be executed
print("Example only")
```
````

## Installation

From PyPI:

```bash
pip install docs-that-run
```

From source:

```bash
git clone https://github.com/gfr211306-crypto/docs-that-run.git
cd docs-that-run
pip install -e ".[test]"
```

## Usage

Scan `README.md` (default):

```bash
dtr
```

Scan specific files:

```bash
dtr docs/tutorial.md examples/quickstart.md
```

Execute marked blocks (requires `--allow-exec` flag AND interactive confirmation):

```bash
dtr README.md --allow-exec
```

Type `y` to proceed. Any other input cancels execution.

## Requirements

- Python 3.9 or newer
- Bash (for bash blocks; Windows users can use Git for Windows)

## Security Warning

**⚠️ `--allow-exec` executes code directly on your machine with no sandboxing.**

v0.1 has **no isolation**:
- No CPU, memory, or filesystem limits
- No network restrictions
- Full access to your user account's permissions

**Only use `--allow-exec` on Markdown files you trust completely.**

Do not run untrusted documentation, third-party examples, or files from unknown sources.

## Example

Try the included example:

```bash
dtr examples/sample_readme.md --allow-exec
```

## Testing

Run the test suite:

```bash
pytest
```

All tests are in `tests/`, with test fixtures in `tests/fixtures/`.

## v0.1 Limitations

- **Languages**: Only Python and Bash
- **Sources**: Local Markdown files only (no remote URLs or repos)
- **Dependencies**: Doesn't install packages or manage virtual environments
- **Isolation**: No sandboxing, resource limits, or permission controls
- **State**: Each block runs in a fresh process; Python variables and shell state (cd, export) are not preserved between blocks
- **Filesystem**: Blocks share a single temp directory for the session
- **Interactivity**: No support for interactive programs or GUIs
- **Output**: Terminal only (no HTML, JSON, or JUnit reports)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, testing, and how to submit issues or pull requests.

## Security

See [SECURITY.md](SECURITY.md) for security considerations and how to report vulnerabilities.

## License

MIT
