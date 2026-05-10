# PPP Backend

This backend contains the first modern PPP calculation modules.

## Current Scope

Implemented:

- Legacy `.PPP` `Contents` stream import for the observed sample layout
- Candidate legacy `IN` generator for controlled oracle experiments
- Reproducible legacy oracle runner for isolated compatibility tests outside `PPP-NEW`
- Reusable legacy oracle option sweep helper for bounded `IN` format probes
- Legacy oracle sweep CLI for JSON summaries of controlled probes
- Legacy `OUT` text parser for future oracle fixtures
- Legacy `OUT` to modern-result comparison diagnostics
- Minimal OLE Compound Document stream extraction
- Hull derivations
- Speed sweep terms
- ITTC-1957 friction coefficient
- Frictional resistance `RF`
- Percent appendage resistance based on currently implemented bare-hull resistance
- Equivalent-area appendage resistance from `SAPP(1+K2)`
- Design-margin resistance
- Partial total resistance and effective power
- Explicit null placeholders for unrecovered legacy report columns
- Legacy applicability checks
- CSV export for speed rows
- Dependency-free HTTP routes
- API validation for invalid physical inputs

Not yet implemented:

- Full Holtrop and Mennen resistance components
- Propulsion factors
- Required thrust
- A real captured legacy `OUT` oracle fixture

## Run Tests

From the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=PPP-NEW/app/backend python3 -m unittest discover PPP-NEW/app/backend/tests
```

## Run Development Server

From the repository root:

```sh
PYTHONPATH=PPP-NEW/app/backend python3 PPP-NEW/app/backend/server.py
```

Default URL:

```text
http://127.0.0.1:8000/health
```

## Run Legacy Oracle Sweep

Use only copied legacy executables outside `PPP-NEW`:

```sh
PYTHONPATH=PPP-NEW/app/backend python3 -m ppp_core.legacy_sweep_cli PPP-NEW/tests/fixtures/pppin_sample_import.json /tmp/PPPFTRN.EXE /tmp/ppp-sweep --output /tmp/ppp-sweep-summary.json
```

Current routes:

- `GET /`
- `GET /health`
- `POST /api/evaluate`
- `POST /api/export/csv`
- `POST /api/export/json`
- `POST /api/export/legacy-in-candidate`
- `POST /api/import/ppp`
- `POST /api/import/out`
- `POST /api/compare/out`

The frontend is in `PPP-NEW/app/frontend` and is served by the backend. It currently supports direct sample-case editing, water-property presets, modern case JSON save/load, legacy `.PPP` import for the observed sample layout, candidate legacy `IN` export, legacy `OUT` comparison upload, API-backed evaluation, applicability checks, a speed table, a canvas plot, CSV/JSON result download, and browser print/PDF output formatted for 8.5 by 11 inch paper with 1 inch margins.
