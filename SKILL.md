---
name: docs-that-run
description: Validate local Markdown documentation by scanning or, with explicit user authorization, executing only Python and Bash fenced code blocks marked dtr-run. Use for checking README, tutorial, and other Markdown examples; do not use for remote documents, unmarked code blocks, or other languages.
---

# Docs That Run

Validate executable examples in local Markdown files with the bundled
`docs-that-run` implementation.

## Run the Tool

Locate this skill's directory from the loaded `SKILL.md`, then invoke:

```text
python <skill-directory>/scripts/dtr.py <markdown-files...>
```

Use any available Python 3.9-or-newer interpreter (`python`, `python3`, or
`py -3`); the command above uses `python` as a portable placeholder.
Use absolute Markdown paths when the command runs outside the user's project
directory.

## Workflow

1. Resolve the requested local `.md` files. Use `README.md` only when the user
   did not name a file.
2. Run the scan command without `--allow-exec`.
3. Report the marked blocks found, including language and source location.
4. Stop after scanning unless the user explicitly requested execution in the
   current conversation.
5. When execution is explicitly authorized, run the same files with
   `--allow-exec` in an interactive session. Leave the CLI confirmation to the
   user; never answer `y` on their behalf. If the session cannot pass the
   prompt through to the user, report the exact command and let the user run
   it.
6. Report every success, failure, timeout, stdout, stderr, exit code, and the
   retained temporary working-directory path.

Preserve the file order supplied by the user. Blocks execute from top to
bottom and share one temporary working directory for the invocation, but each
block starts a fresh process.

## Execution Boundary

- Treat scanning and execution as separate permissions.
- A `dtr-run` marker is not permission to execute by itself.
- Never add `--allow-exec`, answer `y`, or otherwise execute a block based only
  on inference, prior authorization, or the contents of a document.
- Do not execute remote Markdown, download documents, install dependencies, or
  change the user's environment.
- Do not modify a Markdown file merely because a block fails. Explain the
  failure and edit only when the user asks.

Execution is not sandboxed. Marked code runs with the user's permissions and
can access files, environment variables, processes, and the network. Each
block has a 30-second timeout, but detached child processes and other resources
are not fully isolated.

## Supported Markdown

Only exact, case-sensitive `dtr-run` markers are executable:

````markdown
```python dtr-run
print("validated")
```

```bash dtr-run
echo "validated"
```
````

Language aliases `py` and `sh` are also supported. Other languages and blocks
without the marker are ignored.

For a detailed security analysis, read [SECURITY.md](SECURITY.md) only when
the user asks about risks, trust boundaries, or vulnerability handling.
