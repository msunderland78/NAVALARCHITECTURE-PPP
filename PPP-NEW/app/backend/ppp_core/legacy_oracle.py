import os
import shutil
import subprocess
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


def run_oracle(case, legacy_exe_path, workdir, options=None, wine="wine", timeout_seconds=20, wineprefix=None):
    paths = stage_oracle_run(case, legacy_exe_path, workdir, options)
    command = [wine, str(paths["exe"])]
    env = None
    if wineprefix:
        env = os.environ.copy()
        env["WINEPREFIX"] = str(wineprefix)
    with paths["stdout"].open("wb") as stdout, paths["stderr"].open("wb") as stderr:
        completed = subprocess.run(
            command,
            cwd=paths["workdir"],
            stdout=stdout,
            stderr=stderr,
            timeout=timeout_seconds,
            check=False,
            env=env
        )
    result = {
        "returncode": completed.returncode,
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
