# Legacy Oracle Notes

Version 1.0, May 10, 2026

## Purpose

This note tracks attempts to use the legacy executables as temporary calculation oracles. Oracle work is for preservation and validation only. The production web application must not require the legacy executables.

## Wine Startup Check

`wine-9.0 (Ubuntu 9.0~repack-4build3)` is available on the current system.

Test method:

1. Copied `PPP-OLD/PPPFTRN.EXE` to `/tmp/ppp-oracle/PPPFTRN.EXE`.
2. Ran the copy under Wine from `/tmp/ppp-oracle`.
3. Used a Wine prefix outside the repository at `/home/sundema/.cache/ppp-wine/prefix`.
4. Did not modify `PPP-OLD`.

Observed command behavior:

```text
forrtl: severe (24): end-of-file during read, unit 4, file Z:\tmp\ppp-oracle\IN
```

Observed temporary files:

```text
IN 0
PPPFTRN.EXE 257536
```

## Interpretation

The Fortran calculation engine starts under Wine and opens an input file named `IN` on Fortran unit 4. With an empty `IN`, it exits with a DEC Fortran runtime end-of-file error.

This confirms:

- Wine startup is not the immediate blocker.
- The engine expects a working-directory file named `IN`.
- Recovering the exact legacy `IN` layout is required before a legacy `OUT` oracle can be generated.

## Candidate `IN` Run

A candidate `IN` was generated in `/tmp/ppp-oracle-candidate` from the static writer order documented in `PPP-NEW/analysis/in-format-notes.md`. The copied Fortran engine was run under Wine with a 20-second timeout.

Reproducible oracle support now exists in `PPP-NEW/app/backend/ppp_core/legacy_oracle.py`, with sweep and candidate-input CLIs under `PPP-NEW/app/backend/ppp_core`. The tools stage copied executables and generated `IN` files under `/tmp` by default, run Wine with a timeout, and capture stdout, stderr, optional `OUT`, and parsed `OUT` data. They must not be pointed at a destination inside `PPP-NEW`.

Smoke command:

```sh
python3 PPP-NEW/tools/run_legacy_oracle.py --exe PPP-OLD/PPPFTRN.EXE --workdir /tmp/ppp-oracle-runner-smoke --wineprefix /home/sundema/.cache/ppp-wine/prefix --timeout 5
```

Console-mode Wine experiments can be made reproducible by passing one or more explicit Wine arguments. The resulting JSON records the exact command used.

```sh
python3 PPP-NEW/tools/run_legacy_oracle.py --exe PPP-OLD/PPPFTRN.EXE --workdir /tmp/ppp-oracle-console --wineprefix /home/sundema/.cache/ppp-wine/prefix --wine wineconsole --wine-arg=--backend=curses --timeout 5
```

The older candidate reproduced return code `3`, no `OUT`, and a Fortran `DOMAIN error`.

Observed behavior:

```text
forrtl: severe (6201): **: DOMAIN error
```

No `OUT` was produced. The result indicates that the candidate text format and record count are close enough to move beyond file-open and end-of-file failure. The next recovery pass should focus on enum encodings and candidate fields including stern correction, appendage model total, pitch-diameter ratio, propulsion type code, and water type code.

A bounded 27-attempt sweep varied stern correction (`0`, `-10`, `10`), `P/Dp` (`0`, `0.8`, `1.0`), and water type code (`1`, `2`, `3`). Every attempt produced the same Fortran `DOMAIN error`; no `OUT` was captured. This reduces the likelihood that those simple values alone are the blocker.

Direct writer disassembly later corrected the propeller/wetted-surface row from `Dp, wetted surface, half angle` to `wetted surface, half angle, Dp`. A single bounded Wine attempt with the corrected candidate did not reproduce the `DOMAIN error`; it failed earlier with a console output handle error:

```text
forrtl: severe (38): error during write, unit 6, file CONOUT$
```

No `OUT` was produced. This suggests the corrected numerical input may have moved past the prior domain failure, but Wine console handling now needs to be controlled before treating the result as a successful oracle run.

Local `wineconsole --backend=curses` probes still fail before the Fortran engine completes in the current headless shell because Wine tries to create a display-backed window. Those probes are now reproducible through `--wine wineconsole --wine-arg=--backend=curses`, but they are not yet a working oracle path. The confirmed CLI probe returned code `2`, recorded command `wineconsole --backend=curses /tmp/ppp-oracle-console-repro/PPPFTRN.EXE`, and produced no `OUT`.

## Next Oracle Tasks

1. Resolve Wine/Fortran console output handling for `CONOUT$`.
2. Rerun the corrected candidate `IN` under a controlled console environment.
3. If `OUT` is generated, capture only the plain text and parsed oracle fixture under `PPP-NEW/tests/fixtures/`.
4. If `OUT` is still absent, continue static recovery of remaining unresolved `IN` fields.

Do not add the legacy executables to `PPP-NEW` or git.
