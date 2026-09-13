# docs-that-run

[![CI](https://github.com/gfr211306-crypto/docs-that-run/actions/workflows/ci.yml/badge.svg)](https://github.com/gfr211306-crypto/docs-that-run/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/docs-that-run.svg)](https://pypi.org/project/docs-that-run/)
[![Python Version](https://img.shields.io/pypi/pyversions/docs-that-run.svg)](https://pypi.org/project/docs-that-run/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Test the quickstart in your README — not just the code snippets.**

Most documentation-testing tools run Python blocks in isolation. `docs-that-run` also runs **Bash**, and every block in a run **shares one working directory**, so it can validate a real multi-step tutorial:

```
pip install yourtool  →  yourtool init  →  yourtool run  →  check the output
```

That sequence is the part of a README that breaks most often — a renamed flag, a changed default, a moved config file — and it is the part nothing else tests.

It only runs blocks you explicitly mark with `dtr-run`, and only after you confirm.

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

### Non-interactive runs (CI)

There is no one to answer the prompt in CI, so a run without a terminal cancels instead of executing. Add `--yes` to waive the prompt:

```bash
dtr README.md --allow-exec --yes
```

`--yes` must be combined with `--allow-exec`; on its own it exits with code 2 and runs nothing. Use it only on documentation you control — see [SECURITY.md](SECURITY.md).

## GitHub Action

Validate your documentation on every push:

```yaml
name: Docs
on: [push, pull_request]

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: gfr211306-crypto/docs-that-run@v0.1.3
        with:
          files: README.md
```

| Input | Default | Description |
| --- | --- | --- |
| `files` | `README.md` | Markdown files to check, separated by spaces |
| `execute` | `true` | Set to `false` to scan only and never run anything |
| `version` | latest | Pin a specific `docs-that-run` release |
| `python-version` | `3.12` | Python used to run the examples |

The step fails when any marked block fails, so a broken quickstart shows up as a red check instead of an issue from a confused user.

### Machine-readable output

`--json` writes a structured report to stdout and moves every human-readable message to stderr, so the result can be piped into another tool:

```bash
dtr README.md --allow-exec --yes --json > report.json
```

```json
{
  "schema_version": 1,
  "executed": true,
  "summary": { "total": 2, "executed": 2, "succeeded": 1, "failed": 1, "timed_out": 0 },
  "blocks": [
    {
      "index": 2,
      "file": "README.md",
      "line": 67,
      "language": "bash",
      "code": "yourtool init --config demo.yaml",
      "executed": true,
      "success": false,
      "exit_code": 2,
      "stderr": "error: unrecognized argument --config",
      "timed_out": false
    }
  ]
}
```

The action exposes the same document as a step output, and produces it **even when the step fails** — so the failing block, its exact code, and its stderr can be handed to an agent that explains the drift and proposes the fix:

```yaml
- uses: gfr211306-crypto/docs-that-run@v0.1.3
  id: docs
  with:
    files: README.md

- name: Diagnose the drift
  if: failure()
  env:
    REPORT: ${{ steps.docs.outputs.report }}
  run: echo "$REPORT" | your-agent-step
```

Detect the drift, diagnose it, propose the fix, verify again — the report is what makes the loop machine-driven instead of a human reading a log.

**Do not** run this on `pull_request_target`, or on any workflow that checks out a fork's contents, with `execute: true`. That would let anyone execute code on your runner by opening a pull request.

## Used by

- [StudyForge](https://github.com/gfr211306-crypto/StudyForge) — runs the action on every push to check that its documented public API still imports.

## Use with Codex

This repository is also a Codex plugin, so an agent can run the checks for you
and explain what broke. Install it straight from the repository:

```bash
git clone https://github.com/gfr211306-crypto/docs-that-run.git
```

Then point Codex at the clone; the manifest lives at
`.codex-plugin/plugin.json` and the skill at `skills/docs-that-run/SKILL.md`.

The skill keeps the same trust boundary as the CLI: it scans by default, it
never adds `--allow-exec` on its own, and it leaves the confirmation prompt to
you rather than answering it on your behalf.

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
