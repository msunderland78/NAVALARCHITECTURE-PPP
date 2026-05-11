import errno
import os
import pty
import shutil
import signal
import select
import subprocess
import time
import tty
from math import isfinite
from pathlib import Path

from .legacy_in import generate_candidate_legacy_in
from .legacy_out import parse_legacy_out


def stage_oracle_run(case, legacy_exe_path, workdir, options=None):
    workdir = Path(workdir)
    legacy_exe_path = Path(legacy_exe_path)
    workdir.mkdir(parents=True, exist_ok=True)
    staged_exe = workdir / "PPPFTRN.EXE"
    shutil.copy2(legacy_exe_path, staged_exe)
    input_text = generate_candidate_legacy_in(case, options)
    input_path = workdir / "IN"
    input_path.write_text(input_text, encoding="ascii")
    return {
        "workdir": workdir,
        "exe": staged_exe,
        "input": input_path,
        "output": workdir / "OUT",
        "stdout": workdir / "wine.stdout",
        "stderr": workdir / "wine.stderr"
    }


def run_oracle(case, legacy_exe_path, workdir, options=None, wine="wine", wine_args=None, timeout_seconds=20, wineprefix=None, use_pty=False):
    timeout_seconds = validate_timeout_seconds(timeout_seconds)
    paths = stage_oracle_run(case, legacy_exe_path, workdir, options)
    command = [wine, *(wine_args or []), str(paths["exe"])]
    env = None
    if wineprefix:
        env = os.environ.copy()
        env["WINEPREFIX"] = str(wineprefix)
    if use_pty:
        returncode, timed_out = run_command_pty(command, paths["workdir"], paths["stdout"], paths["stderr"], timeout_seconds, env)
    else:
        returncode, timed_out = run_command_piped(command, paths["workdir"], paths["stdout"], paths["stderr"], timeout_seconds, env)
    result = {
        "returncode": returncode,
        "timed_out": timed_out,
        "command": [str(part) for part in command],
        "workdir": str(paths["workdir"]),
        "input": paths["input"].read_text(encoding="ascii"),
        "stdout": paths["stdout"].read_text(encoding="utf-8", errors="replace"),
        "stderr": paths["stderr"].read_text(encoding="utf-8", errors="replace"),
        "out_exists": paths["output"].exists(),
        "out_text": None,
        "parsed_out": None
    }
    if paths["output"].exists():
        result["out_text"] = paths["output"].read_text(encoding="utf-8", errors="replace")
        result["parsed_out"] = parse_legacy_out(result["out_text"], "OUT")
    return result


def validate_timeout_seconds(timeout_seconds):
    if isinstance(timeout_seconds, bool) or not isinstance(timeout_seconds, (int, float)) or not isfinite(timeout_seconds) or timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be a positive finite number")
    return timeout_seconds


def run_command_piped(command, workdir, stdout_path, stderr_path, timeout_seconds, env):
    timed_out = False
    with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
        try:
            completed = subprocess.run(
                command,
                cwd=workdir,
                stdout=stdout,
                stderr=stderr,
                timeout=timeout_seconds,
                check=False,
                env=env
            )
            returncode = completed.returncode
        except subprocess.TimeoutExpired:
            timed_out = True
            returncode = None
    return returncode, timed_out


def run_command_pty(command, workdir, stdout_path, stderr_path, timeout_seconds, env):
    output = bytearray()
    deadline = time.monotonic() + timeout_seconds
    sent_return = False
    timed_out = False
    status = None
    pid, fd = pty.fork()
    if pid == 0:
        child_env = os.environ.copy() if env is None else env
        os.chdir(workdir)
        os.execvpe(command[0], command, child_env)
    tty.setraw(fd)
    try:
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                timed_out = True
                os.kill(pid, signal.SIGKILL)
                _, status = os.waitpid(pid, 0)
                break
            ready, _, _ = select.select([fd], [], [], min(0.1, remaining))
            if ready:
                chunk = read_pty_chunk(fd)
                if chunk:
                    output.extend(chunk)
                    if not sent_return and b"Hit Return to Continue" in output:
                        os.write(fd, b"\r")
                        sent_return = True
                else:
                    break
            waited_pid, waited_status = os.waitpid(pid, os.WNOHANG)
            if waited_pid == pid:
                status = waited_status
                drain_pty(fd, output)
                break
        if status is None:
            _, status = os.waitpid(pid, 0)
    finally:
        os.close(fd)
    stdout_path.write_bytes(bytes(output))
    stderr_path.write_bytes(b"")
    return None if timed_out else os.waitstatus_to_exitcode(status), timed_out


def read_pty_chunk(fd):
    try:
        return os.read(fd, 4096)
    except OSError as error:
        if error.errno == errno.EIO:
            return b""
        raise


def drain_pty(fd, output):
    while True:
        ready, _, _ = select.select([fd], [], [], 0)
        if not ready:
            return
        chunk = read_pty_chunk(fd)
        if not chunk:
            return
        output.extend(chunk)
