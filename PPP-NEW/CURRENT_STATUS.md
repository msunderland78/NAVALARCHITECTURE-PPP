# PPP Current Status

Version 1.0, May 10, 2026

## Implemented

- Legacy evidence notes for supplied files.
- Legacy `.PPP` import for the observed OLE `Contents` stream layout.
- Modern case JSON save/load.
- Source-safe partial calculation core:
  - Hull derivations
  - Speed sweep
  - Froude number
  - Speed-length ratio
  - Displacement volume and mass
  - Inverse B/T and B/L ratios
  - Midship and waterplane areas
  - Length-displacement volume ratio
  - Reynolds number
  - ITTC-1957 friction coefficient
  - Frictional resistance
  - Percent appendage resistance
  - Equivalent-area appendage resistance from `SAPP(1+K2)`
  - Design margin resistance
  - Partial total resistance
  - Effective power
  - Explicit modeling source values for wetted surface and half angle of entrance
  - LCB converted to meters and percent LWL from forward perpendicular
  - Explicit placeholders for unimplemented legacy report columns
- Legacy applicability checks:
  - `Fn`
  - `B/T`
  - `LWL/B`
  - `CP`
- API validation for invalid physical inputs.
- API validation rejects unsupported estimated wetted-surface and half-angle modes until formulas are implemented.
- API validation rejects unsupported stern, propulsion, and water types.
- API validation rejects hull coefficients greater than 1.
- API validation rejects invalid feature, propulsion, and modeling dimensions.
- API validation rejects duplicate multi-point speed sweeps caused by zero speed increment.
- Browser workspace with:
  - Editable sample case
  - Water-property presets
  - Legacy `.PPP` import
  - Candidate legacy `IN` export
  - Legacy `OUT` comparison upload
  - Modern case JSON import/export
  - CSV and JSON result export
  - Applicability panel
  - Derived hydrostatic summary
  - Result table
  - Explicit user-mode controls for wetted surface and half angle
  - HTML min/max constraints aligned with backend numeric validation
  - Canvas plot
  - Letter-size print/PDF layout
- Dependency-free Python backend.
- Dockerfile, Docker Compose, and NGINX reverse-proxy scaffold.
- Static notes for the legacy temporary `IN` writer.
- Candidate legacy `IN` generator for controlled oracle experiments.
- Candidate legacy `IN` CLI for terminal-based oracle experiments.
- Pinned candidate legacy `IN` fixture for the normalized sample case.
- Pinned current modern sample result fixture for regression baselining.
- Fixture manifest distinguishing source, representative, modern baseline, and future oracle artifacts.
- Reproducible legacy oracle runner that stages copied executables outside `PPP-NEW`.
- Reusable legacy oracle option sweep helper for bounded `IN` format probes, including unresolved appendage fields.
- Legacy oracle sweep options now include alternate first-record ordering probes.
- Legacy oracle sweep attempt summaries now include generated `IN` SHA-256, line count, and first record.
- Legacy oracle sweep CLI for JSON summaries and captured `OUT` artifacts from controlled probes.
- Legacy `OUT` text parser for future oracle fixtures.
- Representative legacy `OUT` text fixture for parser and comparison regression tests.
- Legacy `OUT` to modern-result comparison diagnostics with status counts, max absolute delta, and max relative delta summaries.
- Legacy `OUT` comparison CLI for JSON delta reports and optional absolute/relative pass/fail gates.
- Modern evaluation CLI for reproducible result fixture refreshes.
- Candidate `IN` field map recovered from GUI writer/report cross-references.

## Verification

Current test command:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=PPP-NEW/app/backend python3 -m unittest discover PPP-NEW/app/backend/tests
```

Current result:

```text
56 tests OK
```

Local HTTP smoke testing passes for `/health`, `/`, `/api/evaluate`, `/api/import/out`, and `/api/export/legacy-in-candidate` with a temporary backend server. API route tests cover `/api/compare/out`. The legacy oracle CLI reproduces the current `DOMAIN error` in `/tmp`. `docker-compose config` validates. Runtime Docker smoke testing is pending Docker socket permission.

## Known Limits

- Full Holtrop and Mennen resistance components are not complete.
- Current resistance totals are explicitly marked `partial_source_safe_components`.
- Wave, form, bulb, transom, correlation allowance, air resistance, propulsion factors, relative rotative efficiency, and required thrust remain to be implemented.
- Legacy `OUT` oracle is not generated yet.
- Legacy `OUT` parser and comparison diagnostics are ready, but no real legacy `OUT` fixture has been captured yet.
- `PPPFTRN.EXE` starts under Wine and attempts to read working-directory file `IN`; a candidate `IN` now advances from EOF to a Fortran `DOMAIN error`. A bounded enum/value sweep did not produce `OUT`, so exact record ordering and appendage/model candidate fields remain the oracle blocker.

## Next Best Work

1. Recover the legacy `IN` file format written by `PPP.EXE`.
2. Generate a legacy `OUT` oracle from the supplied sample.
3. Parse and compare `OUT` into golden regression fixtures.
4. Implement Holtrop and Mennen component formulas against primary sources and oracle deltas.
5. Run Docker smoke tests from a Docker-enabled account.
