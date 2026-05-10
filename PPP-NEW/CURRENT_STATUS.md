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
  - Reynolds number
  - ITTC-1957 friction coefficient
  - Frictional resistance
  - Percent appendage resistance
  - Equivalent-area appendage resistance from `SAPP(1+K2)`
  - Design margin resistance
  - Partial total resistance
  - Effective power
- Legacy applicability checks:
  - `Fn`
  - `B/T`
  - `LWL/B`
  - `CP`
- API validation for invalid physical inputs.
- Browser workspace with:
  - Editable sample case
  - Water-property presets
  - Legacy `.PPP` import
  - Modern case JSON import/export
  - CSV and JSON result export
  - Applicability panel
  - Result table
  - Canvas plot
  - Letter-size print/PDF layout
- Dependency-free Python backend.
- Dockerfile, Docker Compose, and NGINX reverse-proxy scaffold.
- Static notes for the legacy temporary `IN` writer.

## Verification

Current test command:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=PPP-NEW/app/backend python3 -m unittest discover PPP-NEW/app/backend/tests
```

Current result:

```text
19 tests OK
```

Local HTTP smoke testing passes for `/health`, `/`, and `/api/evaluate` with a temporary backend server. `docker-compose config` validates. Runtime Docker smoke testing is pending Docker socket permission.

## Known Limits

- Full Holtrop and Mennen resistance components are not complete.
- Current resistance totals are explicitly marked `partial_source_safe_components`.
- Wave, form, bulb, transom, correlation allowance, air resistance, propulsion factors, relative rotative efficiency, and required thrust remain to be implemented.
- Legacy `OUT` oracle is not generated yet.
- `PPPFTRN.EXE` starts under Wine and attempts to read working-directory file `IN`; static writer shape is partially recovered, but exact column semantics remain the oracle blocker.

## Next Best Work

1. Recover the legacy `IN` file format written by `PPP.EXE`.
2. Generate a legacy `OUT` oracle from the supplied sample.
3. Parse `OUT` into golden regression fixtures.
4. Implement Holtrop and Mennen component formulas against primary sources and oracle checks.
5. Run Docker smoke tests from a Docker-enabled account.
