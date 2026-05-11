# PPP Backend

This backend contains the first modern PPP calculation modules.

## Current Scope

Implemented:

- Legacy `.PPP` `Contents` stream import for the observed sample layout
- Candidate legacy `IN` generator for controlled oracle experiments
- Reproducible legacy oracle runner for isolated compatibility tests outside `PPP-NEW`
- Reusable legacy oracle option sweep helper for bounded `IN` format probes, including unresolved appendage fields
- Legacy oracle sweep CLI for JSON summaries and captured `OUT` artifacts from controlled probes
- Legacy `OUT` text parser for future oracle fixtures
- Representative legacy `OUT` text fixture for parser and comparison regression tests
- Legacy `OUT` to modern-result comparison diagnostics with status counts and max-delta summary
- Legacy `OUT` comparison CLI for JSON delta reports and optional pass/fail gates
- Pinned current modern sample result fixture for regression baselining
- Fixture manifest distinguishing source, representative, modern baseline, and future oracle artifacts
- Minimal OLE Compound Document stream extraction
- Hull derivations
- Speed sweep terms
- Displacement volume and mass
- LCB in meters and percent LWL from forward perpendicular
- ITTC-1957 friction coefficient
- Frictional resistance `RF`
- Percent appendage resistance based on currently implemented bare-hull resistance
- Equivalent-area appendage resistance from `SAPP(1+K2)`
- Design-margin resistance
- Total resistance, effective power, propulsion factors, and required thrust for the captured sample workflow
- Explicit modeling source values for user-entered or estimated wetted surface and half angle of entrance
- Legacy applicability checks
- CSV export for speed rows
- Modern evaluation CLI for reproducible result fixture refreshes
- Dependency-free HTTP routes
- API validation for invalid physical inputs
- API validation for supported user and estimated wetted-surface and half-angle modes
- API validation for unsupported stern, propulsion, and water types
- API validation for hull coefficients greater than 1
- API validation for invalid feature, propulsion, and modeling dimensions

Not yet implemented:

- Additional oracle fixtures beyond the normalized sample
- Docker runtime smoke test from a Docker-enabled account

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
PYTHONPATH=PPP-NEW/app/backend python3 -m ppp_core.legacy_sweep_cli PPP-NEW/tests/fixtures/pppin_sample_import.json /tmp/PPPFTRN.EXE /tmp/ppp-sweep --appendage-primary-value 0.05 --appendage-primary-value 5 --appendage-model-total 0 --appendage-model-total 0.05 --capture-out /tmp/ppp-oracle.OUT --capture-parsed-out /tmp/ppp-oracle-parsed.json --output /tmp/ppp-sweep-summary.json
```

## Run Modern Evaluation

```sh
PYTHONPATH=PPP-NEW/app/backend python3 -m ppp_core.evaluate_cli PPP-NEW/tests/fixtures/pppin_sample_import.json --point-count 2 --output /tmp/ppp-modern-result.json
```

## Compare Legacy OUT

```sh
PYTHONPATH=PPP-NEW/app/backend python3 -m ppp_core.legacy_compare_cli PPP-NEW/tests/fixtures/pppin_sample_import.json PPP-NEW/tests/fixtures/representative_legacy.OUT --point-count 2 --require-matched-speed-count 2 --max-absolute-delta 100000 --output /tmp/ppp-out-comparison.json
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

The frontend is in `PPP-NEW/app/frontend` and is served by the backend. It currently supports direct sample-case editing, water-property presets, modern case JSON save/load, legacy `.PPP` import for the observed sample layout, candidate legacy `IN` export, legacy `OUT` comparison upload, API-backed evaluation, applicability checks, user and estimated modes for wetted surface and half angle, HTML min/max constraints aligned with backend validation, a speed table, a canvas plot, CSV/JSON result download, and browser print/PDF output formatted for 8.5 by 11 inch paper with 1 inch margins.
