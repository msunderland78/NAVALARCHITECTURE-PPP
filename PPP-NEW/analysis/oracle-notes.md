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

Observed behavior:

```text
forrtl: severe (6201): **: DOMAIN error
```

No `OUT` was produced. The result indicates that the candidate text format and record count are close enough to move beyond file-open and end-of-file failure. The next recovery pass should focus on enum encodings and candidate fields including stern correction, appendage model total, pitch-diameter ratio, propulsion type code, and water type code.

A bounded 27-attempt sweep varied stern correction (`0`, `-10`, `10`), `P/Dp` (`0`, `0.8`, `1.0`), and water type code (`1`, `2`, `3`). Every attempt produced the same Fortran `DOMAIN error`; no `OUT` was captured. This reduces the likelihood that those simple values alone are the blocker.

## Next Oracle Tasks

1. Recover the `IN` writer behavior from `PPP.EXE`.
2. Determine whether `IN` is formatted text, unformatted Fortran records, or a C++ binary stream.
3. Map `PPPIN.PPP` fields to `IN` records.
4. Create a generated `IN` file under `PPP-NEW/tests/fixtures/` only after its structure is understood.
5. Run the copied Fortran engine under Wine and capture `OUT`.
6. Parse `OUT` into a golden regression fixture.

Do not add the legacy executables to `PPP-NEW` or git.
