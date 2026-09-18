"""Execute marked Markdown code blocks."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from typing import Optional, Union

from .messages import t
from .parser import CodeBlock


DEFAULT_TIMEOUT = 30.0


@dataclass(frozen=True)
class ExecutionResult:
    """The captured result of running one code block."""

    block: CodeBlock
    success: bool
    return_code: Optional[int]
    stdout: str
    stderr: str
    duration: float
    timed_out: bool = False


def create_working_directory() -> Path:
    """Create and preserve a temporary directory for one CLI run."""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return Path(tempfile.mkdtemp(prefix=f"dtr_{timestamp}_"))


def execute_block(
    block: CodeBlock,
    working_directory: Union[str, Path],
    *,
    timeout: float = DEFAULT_TIMEOUT,
) -> ExecutionResult:
    """Execute one supported block inside *working_directory*.

    A new process is created for every block. Files are shared through the
    common working directory, while Python state, shell environment variables,
    and shell directory changes are not retained between blocks.
    """

    if timeout <= 0:
        raise ValueError("timeout must be greater than zero")

    workdir = Path(working_directory)
    workdir.mkdir(parents=True, exist_ok=True)

    try:
        command = _command_for_block(block)
    except RuntimeError as error:
        return ExecutionResult(
            block=block,
            success=False,
            return_code=None,
            stdout="",
            stderr=str(error),
            duration=0.0,
        )

    popen_options: dict[str, object] = {
        "cwd": str(workdir),
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
        "text": True,
        "encoding": "utf-8",
        "errors": "replace",
        "env": _environment_for_command(block, command),
    }
    if os.name == "nt":
        popen_options["creationflags"] = (
            subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW
        )
    else:
        popen_options["start_new_session"] = True

    started_at = time.monotonic()
    try:
        process = subprocess.Popen(command, **popen_options)
    except OSError as error:
        return ExecutionResult(
            block=block,
            success=False,
            return_code=None,
            stdout="",
            stderr=t("exec.launch_failed", error=error),
            duration=time.monotonic() - started_at,
        )

    try:
        stdout, stderr = process.communicate(timeout=timeout)
        duration = time.monotonic() - started_at
        return ExecutionResult(
            block=block,
            success=process.returncode == 0,
            return_code=process.returncode,
            stdout=stdout,
            stderr=stderr,
            duration=duration,
        )
    except subprocess.TimeoutExpired:
        _terminate_process_tree(process)
        stdout, stderr = process.communicate()
        duration = time.monotonic() - started_at
        timeout_message = t("exec.timeout_message", timeout=timeout)
        stderr = f"{stderr.rstrip()}\n{timeout_message}".lstrip()
        return ExecutionResult(
            block=block,
            success=False,
            return_code=process.returncode,
            stdout=stdout,
            stderr=stderr,
            duration=duration,
            timed_out=True,
        )


def find_bash() -> Optional[str]:
    """Locate a Bash-compatible executable without downloading anything."""

    candidates: list[Path] = []

    if os.name == "nt":
        git = shutil.which("git")
        if git:
            git_path = Path(git).resolve()
            candidates.extend(
                [
                    git_path.parents[1] / "bin" / "bash.exe",
                    git_path.parents[1] / "usr" / "bin" / "bash.exe",
                    git_path.parents[1] / "usr" / "bin" / "sh.exe",
                ]
            )

        program_files = [
            os.environ.get("ProgramFiles"),
            os.environ.get("ProgramFiles(x86)"),
            os.environ.get("LOCALAPPDATA"),
        ]
        for base in filter(None, program_files):
            candidates.extend(
                [
                    Path(base) / "Git" / "bin" / "bash.exe",
                    Path(base) / "Git" / "usr" / "bin" / "bash.exe",
                    Path(base) / "Git" / "usr" / "bin" / "sh.exe",
                ]
            )

        path_sh = shutil.which("sh")
        if path_sh:
            candidates.append(Path(path_sh))
    else:
        path_bash = shutil.which("bash")
        if path_bash:
            candidates.append(Path(path_bash))
        path_sh = shutil.which("sh")
        if path_sh:
            candidates.append(Path(path_sh))

    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)

    # Keep the Windows WSL launcher as a last resort because it may be present
    # even when no WSL distribution is available.
    path_bash = shutil.which("bash")
    return path_bash


def find_python() -> str:
    """Locate the Python a documented `pip install` would install into.

    A Bash block that runs ``pip install X`` installs into whichever Python is
    first on ``PATH``. If the following Python block ran under
    ``sys.executable`` instead, it could be a different environment — the
    interpreter dtr itself was installed into — and the documented sequence
    ``pip install x`` then ``import x`` would fail even though the docs are
    correct. So the block runs under the ``PATH`` interpreter, falling back to
    ``sys.executable`` when there is none.
    """

    names = ("python", "python3") if os.name == "nt" else ("python3", "python")
    for name in names:
        found = shutil.which(name)
        if found:
            return found
    return sys.executable


def _command_for_block(block: CodeBlock) -> list[str]:
    if block.language == "python":
        return [find_python(), "-c", block.code]
    if block.language == "bash":
        bash = find_bash()
        if bash is None:
            raise RuntimeError(
                t("exec.bash_not_found")
            )
        return [bash, "-c", block.code]
    raise RuntimeError(
        t("exec.unsupported_language", language=block.language)
    )


def _environment_for_command(
    block: CodeBlock,
    command: list[str],
) -> dict[str, str]:
    environment = os.environ.copy()
    # On Windows the Bash interpreter is usually Git Bash, whose own utilities
    # live beside it and are not otherwise on PATH, so its directory is added.
    # On POSIX the interpreter was found through PATH already, and prepending
    # its directory would push /usr/bin ahead of an active virtualenv — which
    # would send a documented `pip install` to the wrong Python.
    if block.language == "bash" and os.name == "nt":
        interpreter_directory = str(Path(command[0]).resolve().parent)
        existing_path = environment.get("PATH", "")
        environment["PATH"] = (
            interpreter_directory
            if not existing_path
            else interpreter_directory + os.pathsep + existing_path
        )
    return environment


def _terminate_process_tree(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return

    if os.name == "nt":
        try:
            completed = subprocess.run(
                [
                    "taskkill",
                    "/F",
                    "/T",
                    "/PID",
                    str(process.pid),
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            if completed.returncode == 0:
                return
        except OSError:
            pass

        process.kill()
        return

    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    except OSError:
        process.kill()
