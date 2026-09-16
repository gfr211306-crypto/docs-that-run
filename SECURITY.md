# Security Policy

The core function of `docs-that-run` (`dtr`) is **executing code from documentation on your machine**. This document therefore does more than explain how to report a vulnerability: it defines the tool's threat model, stating which protections are guaranteed by design and which are not. Please read the Threat Model section before using it.

## Supported Versions

| Version | Security patches |
| --- | --- |
| 0.2.0 (latest) | ✅ |
| 0.1.x and earlier | ❌ Please upgrade |

The project is still pre-1.0. Only the most recent release receives patches.

## Reporting a Vulnerability

**Please do not report security issues through public issues.**

Use GitHub's private reporting channel:

1. Go to <https://github.com/gfr211306-crypto/docs-that-run/security/advisories>
2. Click **Report a vulnerability**
3. Describe the affected versions, the steps to reproduce, and which of the security properties below you believe is broken

If private reporting is unavailable, open an issue that contains **no reproduction details**, stating that you need to contact the maintainer privately, and a channel will be provided.

After reporting, you can expect:

- An acknowledgement **within 7 days**
- Once confirmed, a discussion in the advisory about the fix and the disclosure timeline
- Credit in the advisory and the changelog when the fix ships, unless you ask to remain anonymous

## Threat Model

### Design assumption

`dtr` assumes you are running **local Markdown files you have already decided to trust**. It is a documentation validator, not a sandbox for untrusted code.

### What is protected today

These are guarantees by design. Bypassing any of them is a vulnerability:

- **Nothing executes by default.** Without `--allow-exec`, `dtr` only scans and reports.
- **Two gates.** Even with `--allow-exec`, you must answer `y` at an interactive prompt. Any other input — or an unreadable input stream (EOF, Ctrl+C) — cancels the run.
- **`--yes` is an explicit exception, not a default.** `--yes` waives the interactive prompt for environments such as CI that cannot answer it. It **must be combined with `--allow-exec`**: supplied on its own it exits with code 2 and runs nothing. Using `--yes` moves the judgement that the prompt was asking for onto whoever wrote the command, so it belongs only on documentation you control.
- **Only explicitly marked blocks run.** Only `python` / `py` / `bash` / `sh` blocks whose language tag is followed by `dtr-run` (case-sensitive) are recognised and executed. Every other block is ignored and never appears in the list of blocks to run.
- **No network sources are touched.** `dtr` reads local `.md` files only. It does not download remote documents, clone repositories, or install dependencies.
- **No extra shell string assembly.** Subprocesses are launched from an argument array, never with `shell=True`; the code is passed straight to the interpreter (`python -c` / `bash -c`). Bash blocks themselves still undergo normal Bash semantics — variable expansion, globbing and command substitution.
- **One process per block.** Python variables, environment changes and `cd` do not persist between blocks.
- **Timeout termination.** Each block is capped at 30 seconds by default. On timeout the tool attempts to terminate the process group or process tree (`killpg` on POSIX; `taskkill /T` first on Windows). If the whole tree cannot be killed on Windows, it falls back to terminating the interpreter process it started directly.

### What is **not** protected today

These are known and deliberate limitations. Behaviour within this scope is **not a vulnerability**, but it should still be documented clearly:

- **No filesystem isolation.** Code starts in a temporary working directory, but that is a working directory, not a cage. A block can read and write any path your account can reach, including `~/.ssh`, `~/.aws` and your project source.
- **The environment is inherited in full.** Subprocesses receive a copy of the current process environment. **Code in a document can read your API keys, tokens and credentials.**
- **No network restrictions.** Executed code can make outbound connections freely — including sending out whatever it read above.
- **No resource quotas.** There are no CPU, memory, disk or process-count limits. The timeout caps only the *wall-clock time* of a single block.
- **Background processes can survive.** If a block spawns a detached process and then exits immediately, the block does not time out, process-group termination is never triggered, and the background process keeps running.
- **The temporary working directory is not deleted.** It is kept after the run so you can inspect the output, and its path is printed in the report. It may contain sensitive data; clean it up yourself.

### In scope

- Any code execution without `--allow-exec`
- Execution when `--yes` is supplied on its own, without `--allow-exec`
- Bypassing the interactive confirmation prompt without `--yes`
- Causing a block **not** marked `dtr-run` to execute — for example through parsing ambiguity in fences, indentation, HTML comments or language aliases
- A timeout that never attempts to terminate the foreground interpreter process after the limit. Background processes that have escaped the process group are a known limitation listed above, not a vulnerability
- Arbitrary code execution in `dtr` itself during parsing, for example while handling a malicious `.md`
- The Bash interpreter discovery logic loading an unintended executable. On Windows it looks for `bash.exe` or `sh.exe` under the Git installation directory, `ProgramFiles`, `LOCALAPPDATA` and `PATH`, and prepends the chosen interpreter's directory to the subprocess `PATH`
- Permissions on the temporary working directory that let other users on the same machine read or write it

### Out of scope

- "I ran `--allow-exec` against a malicious document and answered `y`, and it did something bad." That is the designed behaviour, not a vulnerability.
- The absence of sandboxing, resource limits or network isolation — these are the known limitations listed above.
- Consequences of using `--allow-exec --yes` in CI. That is the deliberately provided non-interactive mode, and responsibility rests with whoever configured the workflow.

## Recommended Usage

If you are running this against documentation **you did not write**:

- Run it in a container or VM, not on your daily development machine
- Scan first without `--allow-exec` and read every block that would run
- Use a clean environment — for example `env -i` or a dedicated minimal shell
- Do not add `--allow-exec --yes` to CI that runs on external pull requests. Running `--yes` from `pull_request_target`, or from any workflow that checks out a fork's contents, lets anyone execute code on your runner by opening a pull request

## Roadmap

Sandboxing and resource limits are known gaps. If you have ideas or want to contribute an implementation, please open an issue to discuss the design before sending a pull request.
